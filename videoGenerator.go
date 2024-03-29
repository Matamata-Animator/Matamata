package main

import (
	"encoding/json"
	"fmt"
	"image"
	"image/color"
	"image/jpeg"
	"log"
	"math"
	"os"
	"path/filepath"
	"runtime/debug"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/disintegration/imaging"
	"github.com/gosuri/uiprogress"
	"github.com/jmoiron/jsonq"
	"github.com/mitchellh/mapstructure"
	"golang.org/x/image/draw"
)

type FrameRequest struct {
	pose      Pose
	mouthPath string
	duration  float64
	parts     []Part
}
type VideoRequest struct {
	gentle_stamps  GentleResponse
	audio_path     string
	character_path string
	phonemes_path  string
	timestamps     []Timestamp
}

func getString(j *jsonq.JsonQuery, key string) string {
	s, e := j.String(key)
	if e != nil {
		fmt.Println("Error reading ", key, " from json")
		Fatal(e)
	}
	return s
}

type Part struct {
	Path  string
	X     int16
	Y     int16
	Scale float32
}

func getParts(partsMap map[string]string, character *jsonq.JsonQuery, characterDir string) []Part {
	var parts []Part
	for k, v := range partsMap {
		if v == "None" {
			continue
		}

		imageName, e := character.String(k, "images", v)
		if e != nil {
			Fatal(e)
		}
		path := filepath.Join(characterDir, k, imageName)

		scale, _ := character.Float(k, "scale")
		x, _ := character.Int(k, "x")
		y, _ := character.Int(k, "y")

		parts = append(parts, Part{
			path, int16(x), int16(y), float32(scale),
		})
	}
	return parts
}

type Pose struct {
	Image      string  `json:"image"`
	X          int16   `json:"x"`
	Y          int16   `json:"y"`
	FacingLeft bool    `json:"facingLeft"`
	MouthScale float32 `json:"mouthScale"`
}

func getPose(poseName string, character *jsonq.JsonQuery, characterDir string) Pose {
	p, e := character.Object("poses", poseName)
	if e != nil {
		fmt.Println("Error getting pose:", poseName)
		Fatal(e)
	}
	var pose Pose
	mapstructure.Decode(p, &pose)
	pose.Image = filepath.Join(characterDir, "poses", pose.Image)
	default_scale, e := character.Float("poses", "defaultMouthScale")
	if e != nil {
		Fatal(e)
	}
	pose.MouthScale *= float32(default_scale)
	return pose
}

func genImageSequence(req VideoRequest) {
	expectedPhonemeSchema := 5
	expectedCharacterSchema := 5

	jsonPath := filepath.Join(req.character_path, "character.json")
	characterJsonRaw, e := os.ReadFile(jsonPath)
	if e != nil {
		fmt.Println("Could not open character file")
		Fatal(e)
	}
	characterJson := map[string]interface{}{}
	dec := json.NewDecoder(strings.NewReader(string(characterJsonRaw)))
	dec.Decode(&characterJson)
	character := jsonq.NewQuery(characterJson)
	schema, e := character.Int("schema")
	if e != nil || schema != expectedCharacterSchema {
		fmt.Print("Mismatched character schema versions. Expected: ", expectedCharacterSchema, " Found: ")
		fmt.Println(schema)
		Fatal(e)
	}

	phonemesJsonRaw, e := os.ReadFile(req.phonemes_path)
	if e != nil {
		fmt.Println("Could not open phonemes file at ", req.phonemes_path)
		Fatal(e)
	}
	phonemesJson := map[string]interface{}{}
	dec = json.NewDecoder(strings.NewReader(string(phonemesJsonRaw)))
	dec.Decode(&phonemesJson)
	phonemes := jsonq.NewQuery(phonemesJson)
	schema, e = phonemes.Int("schema")
	if e != nil || schema != expectedPhonemeSchema {
		fmt.Print("Mismatched phoneme schema versions. Expected: ", expectedPhonemeSchema, " Found: ")
		fmt.Println(schema)
		Fatal(e)
	}

	logM(3, "phonemes:", phonemes)
	placeableParts := make(map[string]string)

	defaultPose, e := character.String("poses", "defaultPose")
	if e != nil {
		fmt.Println("No default pose set")
		Fatal(e)
	}
	timestamp := Timestamp{
		Time: 0,
		Name: defaultPose,
		Type: "poses",
	}
	//Set values for first frame
	for _, t := range req.timestamps {
		if t.Time > 0 {
			continue
		}
		if t.Type == "poses" {
			timestamp = t
		} else {
			placeableParts[t.Type] = t.Name
			if t.Name == "None" {
				delete(placeableParts, t.Type)
			}
		}
	}
	pose := getPose(timestamp.Name, character, req.character_path)

	logM(1, "Generating and Writing Frames (Parallel)")

	entireAudioDuration := getAudioFileDuration(req.audio_path)
	var currentTime float64 = 0
	closedPath := filepath.Join(req.character_path, "mouths/", getString(phonemes, "closed"))
	mouthPath := closedPath

	img := openImage(pose.Image)
	dimensions := [2]int{img.Bounds().Dx(), img.Bounds().Dy()}

	totCount := int(entireAudioDuration * 100)
	bar := uiprogress.AddBar(totCount).AppendCompleted().PrependElapsed()
	bar.PrependFunc(func(b *uiprogress.Bar) string {
		time.Sleep(100 * time.Millisecond)
		return ""
		//return fmt.Sprintf("Frames Generated (%d/%d)", b.Current(), totCount)
	})
	uiprogress.Start()

	//var bar *uiprogress.Bar = nil
	var frameRequestsWG sync.WaitGroup
	var frameCounter uint64 = 0

	for _, word := range req.gentle_stamps.Words {
		// Rest Frames //
		mouthPath = closedPath
		duration := math.Max(0, math.Round(100*(word.Start-currentTime))/100.0)
		if duration > 0 {
			currentTime += duration
		}

		f := FrameRequest{
			pose, mouthPath, duration, getParts(placeableParts, character, req.character_path),
		}

		frameRequestsWG.Add(1)
		go func(r2 FrameRequest, fc uint64, d [2]int) {
			defer frameRequestsWG.Done()

			writeFrame(r2, fc, d, bar)

		}(f, frameCounter, dimensions)
		frameCounter += uint64(math.Round(f.duration * 100))

		//swap pose
		for _, t := range req.timestamps {
			if t.Time <= uint32(currentTime*1000) {
				if t.Type == "poses" {
					timestamp = t
				} else {
					placeableParts[t.Type] = t.Name
					if t.Name == "None" {
						delete(placeableParts, t.Type)
					}
				}
			}
		}
		pose = getPose(timestamp.Name, character, req.character_path)

		for _, p := range word.Phones {
			p.Phone = strings.Split(p.Phone, "_")[0]
			p.Duration = math.Max(0, math.Round(100*p.Duration)/100)
			mouthPath = filepath.Join(req.character_path, "mouths/", getString(phonemes, p.Phone))
			f = FrameRequest{
				pose, mouthPath, p.Duration, getParts(placeableParts, character, req.character_path),
			}

			frameRequestsWG.Add(1)
			go func(r2 FrameRequest, fc uint64, d [2]int) {
				defer frameRequestsWG.Done()

				writeFrame(r2, fc, d, bar)
			}(f, frameCounter, dimensions)
			frameCounter += uint64(math.Round(f.duration * 100))

			currentTime += p.Duration

		}
		debug.FreeOSMemory()
	}

	timeRemaining := math.Max(entireAudioDuration-currentTime, 0.01)
	f := FrameRequest{
		pose, closedPath, timeRemaining, getParts(placeableParts, character, req.character_path),
	}
	frameRequestsWG.Add(1)

	go func(r2 FrameRequest, fc uint64, d [2]int) {
		defer frameRequestsWG.Done()

		writeFrame(r2, fc, d, bar)

	}(f, frameCounter, dimensions)
	frameCounter += uint64(math.Round(f.duration * 100))
	currentTime += timeRemaining

	frameRequestsWG.Wait()

	if bar != nil {
		uiprogress.Stop()
	}
}

func writeFrame(r FrameRequest, frameCounter uint64, dimensions [2]int, bar *uiprogress.Bar) {
	bgImg := image.NewRGBA(image.Rect(0, 0, dimensions[0], dimensions[1]))
	draw.Draw(bgImg, bgImg.Bounds(), &image.Uniform{color.RGBA{0, 0, 0, 0}}, image.ZP, draw.Src)

	//base pose
	imgUnscaled := openImage(r.pose.Image)
	img := image.NewRGBA(image.Rect(0, 0, dimensions[0], dimensions[1]))

	draw.NearestNeighbor.Scale(img, img.Rect, imgUnscaled, imgUnscaled.Bounds(), draw.Over, nil)
	offset := image.Pt(0, 0) //combine the image
	draw.Draw(bgImg, img.Bounds().Add(offset), img, image.ZP, draw.Over)
	img = nil
	imgUnscaled = nil

	//mouth
	imgUnscaled = openImage(r.mouthPath)
	if r.pose.FacingLeft {
		imgUnscaled = (*image.RGBA)(imaging.FlipH(imgUnscaled))
	}
	img = image.NewRGBA(image.Rect(0, 0, int(float32(imgUnscaled.Bounds().Dx())*r.pose.MouthScale), int(float32(imgUnscaled.Bounds().Dy())*r.pose.MouthScale)))
	if r.pose.MouthScale != 1 {
		draw.NearestNeighbor.Scale(img, img.Rect, imgUnscaled, imgUnscaled.Bounds(), draw.Over, nil)
	}

	offset = image.Pt(int(r.pose.X)-img.Bounds().Dx()/2, int(r.pose.Y)-img.Bounds().Dy()/2) //combine the image
	draw.Draw(bgImg, img.Bounds().Add(offset), img, image.ZP, draw.Over)

	img = nil
	imgUnscaled = nil
	//placeable parts
	for _, p := range r.parts {
		imgUnscaled = openImage(p.Path)
		img = image.NewRGBA(image.Rect(0, 0, int(float32(imgUnscaled.Bounds().Dx())*p.Scale), int(float32(imgUnscaled.Bounds().Dy())*p.Scale)))
		draw.NearestNeighbor.Scale(img, img.Rect, imgUnscaled, imgUnscaled.Bounds(), draw.Over, nil)
		offset = image.Pt(int(p.X)-img.Bounds().Dx()/2, int(p.Y)-img.Bounds().Dy()/2) //combine the image
		draw.Draw(bgImg, img.Bounds().Add(offset), img, image.ZP, draw.Over)
	}
	img = nil
	imgUnscaled = nil
	var wg sync.WaitGroup
	for i := frameCounter; i < frameCounter+uint64(math.Round(r.duration*100)); i++ {
		path := filepath.Join(generateDir, "frames/", strconv.FormatUint(i, 10)+".jpg")
		f, err := os.Create(path)
		if err != nil {
			Fatal(err)

		}
		if bar != nil {
			bar.Incr()
		}
		wg.Add(1)
		go func(f2 *os.File, b *image.RGBA) {
			defer wg.Done()
			defer f2.Close()

			if err = jpeg.Encode(f, b, nil); err != nil {
				log.Printf("failed to encode: %v", err)
			}
		}(f, bgImg)
	}
	wg.Wait()

	bgImg = nil
	img = nil
	imgUnscaled = nil
}

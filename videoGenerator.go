package main

import (
	"encoding/json"
	"fmt"
	"github.com/jmoiron/jsonq"
	"github.com/mitchellh/mapstructure"
	"image"
	"image/color"
	"image/draw"
	"image/jpeg"
	"log"
	"math"
	"os"
	"path/filepath"
	"strconv"
	"strings"
)

type FrameRequest struct {
	pose           Pose
	mouthPath      string
	duration       float64
	placeableParts map[string]string
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
		log.Fatal(e)
	}
	return s
}

type Pose struct {
	Image      string  `json:"image"`
	X          int16   `json:"x"`
	Y          int16   `json:"y"`
	FacingLeft bool    `json:"facingLeft"`
	scale      float32 `json:"scale"`
}

func getPose(poseName string, character *jsonq.JsonQuery, characterDir string) Pose {
	p, e := character.Object("poses", poseName)
	if e != nil {
		fmt.Println("Error getting pose ", poseName)
		log.Fatal(e)
	}
	var pose Pose
	mapstructure.Decode(p, &pose)
	pose.Image = filepath.Join(characterDir, "poses", pose.Image)

	return pose
}

func genImageSequence(req VideoRequest) {
	expectedPhonemeSchema := 5
	expectedCharacterSchema := 5

	jsonPath := filepath.Join(req.character_path, "character.json")
	characterJsonRaw, e := os.ReadFile(jsonPath)
	if e != nil {
		fmt.Println("Could not open character file")
		log.Fatal(e)
	}
	characterJson := map[string]interface{}{}
	dec := json.NewDecoder(strings.NewReader(string(characterJsonRaw)))
	dec.Decode(&characterJson)
	character := jsonq.NewQuery(characterJson)
	schema, e := character.Int("schema")
	if e != nil || schema != expectedCharacterSchema {
		fmt.Print("Mismatched character schema versions. Expected: ", expectedCharacterSchema, " Found: ")
		fmt.Println(schema)
		log.Fatal(e)
	}

	phonemesJsonRaw, e := os.ReadFile(req.phonemes_path)
	if e != nil {
		fmt.Println("Could not open phonemes file at ", req.phonemes_path)
		log.Fatal(e)
	}
	phonemesJson := map[string]interface{}{}
	dec = json.NewDecoder(strings.NewReader(string(phonemesJsonRaw)))
	dec.Decode(&phonemesJson)
	phonemes := jsonq.NewQuery(phonemesJson)
	schema, e = phonemes.Int("schema")
	if e != nil || schema != expectedPhonemeSchema {
		fmt.Print("Mismatched phoneme schema versions. Expected: ", expectedPhonemeSchema, " Found: ")
		fmt.Println(schema)
		log.Fatal(e)
	}

	logM(3, "phonemes:", phonemes)
	placeableParts := make(map[string]string)

	fmt.Println(placeableParts)

	defaultPose, _ := character.String("default_pose")

	timestamp := Timestamp{
		Time: 0,
		Name: defaultPose,
		Type: "poses",
	}
	logM(5, timestamp)
	//Set values for first frame
	for _, t := range req.timestamps {
		if t.Time > 0 {
			continue
		}
		if t.Type == "poses" {
			timestamp = t
		}
		placeableParts[t.Type] = t.Name
		if t.Name == "None" {
			delete(placeableParts, t.Type)
		}
	}
	pose := getPose(timestamp.Name, character, req.character_path)

	logM(1, "Generating Frame Requests")

	var frameRequests []FrameRequest
	var currentTime float64 = 0
	for _, word := range req.gentle_stamps.Words {
		fmt.Println("len: ", len(frameRequests))

		// Rest Frames //
		mouthPath := filepath.Join(req.character_path, "mouths/", getString(phonemes, "closed"))
		duration := math.Round(100*(word.Start-currentTime)) / 100.0
		if duration > 0 {
			currentTime += duration
		}
		frameRequests = append(frameRequests, FrameRequest{
			pose, mouthPath, duration, copyMap(placeableParts),
		})

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
			p.Duration = math.Round(100*p.Duration) / 100
			mouthPath = filepath.Join(req.character_path, "mouths/", getString(phonemes, p.Phone))
			frameRequests = append(frameRequests, FrameRequest{
				pose, mouthPath, p.Duration, copyMap(placeableParts),
			})
			currentTime += p.Duration

		}
	}

	logM(1, "Writing Frames...")
	//var frames []any
	frameCounter := 0
	var genLock *int = new(int)
	*genLock = 0
	for _, r := range frameRequests {
		go writeFrame(r, frameCounter, genLock)
		frameCounter += int(math.Round(r.duration * 100))
		fmt.Println("fc ", r.mouthPath, r.duration)
	}
	for *genLock > 0 {
	}
	fmt.Println("Done")
}

func writeFrame(r FrameRequest, frameCounter int, lock *int) {
	*lock++
	bgImg := image.NewRGBA(image.Rect(0, 0, 1280, 720))
	draw.Draw(bgImg, bgImg.Bounds(), &image.Uniform{color.RGBA{227, 0, 0, 100}}, image.ZP, draw.Src)

	//basepose
	img := openImage(r.pose.Image)
	offset := image.Pt(0, 0) //combine the image
	draw.Draw(bgImg, img.Bounds().Add(offset), img, image.ZP, draw.Over)

	//mouth
	img = openImage(r.mouthPath)
	offset = image.Pt(int(r.pose.X)-img.Bounds().Dx()/2, int(r.pose.Y)-img.Bounds().Dy()/2) //combine the image
	draw.Draw(bgImg, img.Bounds().Add(offset), img, image.ZP, draw.Over)

	for i := frameCounter; i < frameCounter+int(r.duration*100); i++ {
		path := filepath.Join(generateDir, "frames/", strconv.Itoa(i)+".jpg")
		f, err := os.Create(path)
		if err != nil {
			panic(err)
		}
		defer f.Close()
		if err = jpeg.Encode(f, bgImg, nil); err != nil {
			log.Printf("failed to encode: %v", err)
		}
	}
	*lock--
}

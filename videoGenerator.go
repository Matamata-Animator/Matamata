package main

import (
	"encoding/json"
	"fmt"
	"github.com/jmoiron/jsonq"
	"log"
	"math"
	"os"
	"path/filepath"
	"strings"
)

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

	logM(1, "Generating Frame Requests")

	var currentTime float64 = 0
	for _, word := range req.gentle_stamps.Words {

		// Rest Frames //
		mouth_path := filepath.Join(req.character_path, "mouths/", getString(phonemes, "closed"))
		duration := math.Round(float64(100*(word.Start-currentTime))) / 100.0
		if duration > 0 {
			currentTime += duration
		}
		fmt.Println(mouth_path)
		//TODO: Push frame

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

		//TODO:     pose = await getPose(timestamp.pose_name, character);
		for _, p := range word.Phones {
			p.Phone = strings.Split(p.Phone, "_")[0]
			p.Duration = math.Round(100*p.Duration) / 100
			mouth_path = filepath.Join(req.character_path, "mouths/", getString(phonemes, p.Phone))
			fmt.Println(mouth_path)
			//TODO: Creat frame request
			currentTime += p.Duration
		}
	}

}

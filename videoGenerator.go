package main

import (
	"encoding/json"
	"fmt"
	"github.com/jmoiron/jsonq"
	"log"
	"log/slog"
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
	expectedSchema := 5
	if e != nil || schema != expectedSchema {
		fmt.Print("Mismatched schema versions. Expected: ", expectedSchema, " Found: ")
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

	logM(3, "phonemes:", phonemes)
	placeableParts := make(map[string]string)

	slog.Warn("test")
	fmt.Println(placeableParts)

	defaultPose, _ := character.String("default_pose")

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
		}
		placeableParts[t.Type] = t.Name
		if t.Name == "None" {
			delete(placeableParts, t.Type)
		}
	}

	logM(1, "Generating Frame Requests")

	var currentTime float32 = 0
	for _, word := range req.gentle_stamps.Words {

		// Rest Frames //
		mouth_path := filepath.Join(req.character_path, "mouths/", getString(phonemes, "closed"))
		duration := float32(int(100*(word.Start-currentTime))) / 100.0
		if duration > 0 {
			currentTime += duration
		}

	}

}

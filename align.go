package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"mime/multipart"
	"net/http"
	"os"
	"strconv"
	"strings"
)

type GentlePhone struct {
	Duration float64 `json:"duration"`
	Phone    string  `json:"phone"`
}
type GentleWord struct {
	AlignedWord string        `json:"alignedWord"`
	Case        string        `json:"case"`
	End         float64       `json:"end"`
	EndOffset   int32         `json:"endOffset"`
	Phones      []GentlePhone `json:"phones"`
	Start       float64       `json:"start"`
	StartOffset int32         `json:"startOffset"`
	Word        string        `json:"word"`
}

type GentleResponse struct {
	Transcript string       `json:"transcript"`
	Words      []GentleWord `json:"words"`
}

func cleanGentle(res GentleResponse) {
	isSuccess := func(w GentleWord) bool { return w.Case == "Success" }
	res.Words = filter(res.Words, isSuccess)
}

func gentleAlign(url, audioFilePath, transcriptContent string) (GentleResponse, error) {
	// Open the audio file
	audioFile, err := os.Open(audioFilePath)
	if err != nil {
		log.Fatal(err)
	}
	defer audioFile.Close()

	// Create a buffer to store the request body
	body := &bytes.Buffer{}

	// Create a multipart writer
	writer := multipart.NewWriter(body)

	// Add audio file
	audioPart, err := writer.CreateFormFile("audio", "audio.mp3")
	if err != nil {
		log.Fatal(err)
	}
	io.Copy(audioPart, audioFile)

	// Add transcript content
	transcriptPart, err := writer.CreateFormFile("transcript", "words.txt")
	if err != nil {
		log.Fatal(err)
	}
	io.WriteString(transcriptPart, transcriptContent)

	// Close the multipart writer
	writer.Close()

	// Create the request
	request, err := http.NewRequest("POST", url, body)
	if err != nil {
		log.Fatal(err)
	}

	// Set the content type header
	request.Header.Set("Content-Type", writer.FormDataContentType())

	// Make the request
	client := &http.Client{}
	response, err := client.Do(request)
	if err != nil {
		log.Fatal("MAKE SURE GENTLE IS LAUNCHED\n", err)
	}
	defer response.Body.Close()

	// Read the response body
	responseBody, err := io.ReadAll(response.Body)

	var gentleRes GentleResponse
	err = json.Unmarshal(responseBody, &gentleRes)
	if err != nil {
		log.Fatal("Error unmarshalling JSON:", err)
	}
	cleanGentle(gentleRes)
	return gentleRes, nil
}

type Timestamp struct {
	Time uint32
	Name string
	Type string
}

func parseTimestamps(timestampsPath string) []Timestamp {
	if timestampsPath == "" {
		//return []Timestamp{{0, args.defaultPose, "pose"}}
		return []Timestamp{}

	}

	content, err := os.ReadFile(timestampsPath)
	if err != nil {
		log.Fatal(err)
	}

	lines := strings.Split(string(content), "\n")

	var timestamps []Timestamp
	for _, l := range lines {
		parts := strings.Split(l, " ")
		var newStamp Timestamp
		time, err := strconv.Atoi(parts[0])
		if err != nil {
			fmt.Println("Error parsing int in Timestamps file:", parts[0])
			log.Fatal(err)
		}
		newStamp.Time = uint32(time)
		newStamp.Name = parts[1]
		if len(parts) > 2 {
			newStamp.Type = parts[2]
		} else {
			newStamp.Type = "poses"
		}

		timestamps = append(timestamps, newStamp)
	}
	return timestamps

}

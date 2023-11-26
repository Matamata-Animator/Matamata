package main

import (
	"bytes"
	"encoding/json"
	"io"
	"log"
	"mime/multipart"
	"net/http"
	"os"
)

type GentlePhone struct {
	Duration float32 `json:"duration"`
	Phone    string  `json:"phone"`
}
type GentleWord struct {
	AlignedWord string        `json:"alignedWord"`
	Case        string        `json:"case"`
	End         float32       `json:"end"`
	EndOffset   int8          `json:"endOffset"`
	Phones      []GentlePhone `json:"phones"`
	Start       float32       `json:"start"`
	StartOffset int8          `json:"startOffset"`
	Word        string        `json:"word"`
}

type GentleResponse struct {
	Transcript string       `json:"transcript"`
	Words      []GentleWord `json:"words"`
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
	return gentleRes, nil
}

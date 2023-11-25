package main

import (
	"context"
	"github.com/sashabaranov/go-openai"
	"io"
	"log"
)

type AudioRequest struct {
	Model string

	// FilePath is either an existing file in your filesystem or a filename representing the contents of Reader.
	FilePath string

	// Reader is an optional io.Reader when you do not want to use an existing file.
	Reader io.Reader

	Prompt      string // For translation, it should be in English
	Temperature float32
	Language    string // For translation, just do not use it. It seems "en" works, not confirmed...
}

func transcribe(audioPath string, api_url string, key string) string {

	config := openai.DefaultAzureConfig(key, api_url)
	config.APIType = "OPEN_AI"
	client := openai.NewClientWithConfig(config)

	resp, err := client.CreateTranscription(
		context.Background(),
		openai.AudioRequest{
			Model:    openai.Whisper1,
			FilePath: audioPath,
		},
	)
	if err != nil {
		log.Fatal(err)
	}
	return resp.Text
}

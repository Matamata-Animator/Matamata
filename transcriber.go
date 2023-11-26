package main

import (
	"context"
	"github.com/sashabaranov/go-openai"
	"log"
)

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

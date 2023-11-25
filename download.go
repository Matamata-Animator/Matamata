package main

import (
	//"fmt"
	"github.com/schollz/progressbar/v3"
	"io"
	"net/http"
	"os"
	//"time"

	//"github.com/cavaliergopher/grab/v3"
	//"github.com/schollz/progressbar/v3"
	"github.com/xyproto/unzip"
)

func downloadModel() string {
	// create client
	modelUrl := "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
	//modelUrl := "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
	req, _ := http.NewRequest("GET", modelUrl, nil)
	resp, _ := http.DefaultClient.Do(req)
	defer resp.Body.Close()

	f, _ := os.OpenFile("model.zip", os.O_CREATE|os.O_WRONLY, 0644)
	defer f.Close()

	bar := progressbar.DefaultBytes(
		resp.ContentLength,
		"downloading",
	)
	io.Copy(io.MultiWriter(f, bar), resp.Body)
	return "model.zip"
}

func getModel() {
	filename := "vosk-model-small-en-us-0.15.zip"
	filename = downloadModel()

	err := unzip.Extract(filename, "model/")
	if err != nil {
		return
	}
}

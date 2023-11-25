package main

import (
	"fmt"

	"github.com/schollz/progressbar/v3"
	"io"
	"net/http"
	"os"
	"path/filepath"

	"github.com/xyproto/unzip"
)

func downloadFile(url string, targetPath string) string {
	// create client
	req, _ := http.NewRequest("GET", url, nil)
	resp, _ := http.DefaultClient.Do(req)
	defer resp.Body.Close()

	f, _ := os.OpenFile(targetPath, os.O_CREATE|os.O_WRONLY, 0644)
	defer f.Close()

	bar := progressbar.DefaultBytes(
		resp.ContentLength,
		"downloading",
	)
	io.Copy(io.MultiWriter(f, bar), resp.Body)
	return targetPath
}
func pathExists(path string) (bool, error) {
	_, err := os.Stat(path)
	if err == nil {
		return true, nil
	}
	if os.IsNotExist(err) {
		return false, nil
	}
	return false, err
}

func downloadModel() {
	cacheDir, _ := os.UserCacheDir()
	matamataPath := filepath.Join(cacheDir, "matamata/")
	matamataPathExists, _ := pathExists(matamataPath)
	if !matamataPathExists {
		os.Mkdir(matamataPath, 0777)
	}

	modelPath := filepath.Join(matamataPath, "model/")
	fmt.Println("Modelpath: ", modelPath)
	modelDownloaded, _ := pathExists(modelPath)
	if modelDownloaded {
		return
	}
	fmt.Println("Downloading Vosk model, this only needs to happen the first time you run the program")

	//modelUrl := "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
	modelUrl := "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"

	zipTarget := filepath.Join(matamataPath, "model.zip")
	filename := downloadFile(modelUrl, zipTarget)

	err := unzip.Extract(filename, modelPath)
	if err != nil {
		return
	}
}

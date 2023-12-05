package main

import (
	"bufio"
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/exec"
	"runtime"
)

func transcriberResultHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")

	r.ParseForm()
	voskTranscription = r.Form["text"][0]
	srv.Shutdown(context.TODO())
}

func getAudioHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	f, err := RetrieveROM(voskAudioPath)
	if err != nil {
		panic(err)
	}
	w.Write(f)

}

var srv *http.Server
var voskTranscription string
var voskAudioPath string

func handleRequests() {
	srv = &http.Server{Addr: ":8000"}

	http.HandleFunc("/transcriber_result", transcriberResultHandler)
	http.HandleFunc("/audio_file", getAudioHandler)
	// always returns error. ErrServerClosed on graceful close
	if err := srv.ListenAndServe(); err != http.ErrServerClosed {
		// unexpected error. port in use?
		log.Fatalf("ListenAndServe(): %v", err)
	}

}
func openbrowser(url string) {
	var err error

	switch runtime.GOOS {
	case "linux":
		err = exec.Command("xdg-open", url).Start()
	case "windows":
		err = exec.Command("rundll32", "url.dll,FileProtocolHandler", url).Start()
	case "darwin":
		err = exec.Command("open", url).Start()
	default:
		err = fmt.Errorf("unsupported platform")
	}
	if err != nil {
		log.Fatal(err)
	}

}
func RetrieveROM(filename string) ([]byte, error) {
	file, err := os.Open(filename)

	if err != nil {
		return nil, err
	}
	defer file.Close()

	stats, statsErr := file.Stat()
	if statsErr != nil {
		return nil, statsErr
	}

	var size int64 = stats.Size()
	bytes := make([]byte, size)

	bufr := bufio.NewReader(file)
	_, err = bufr.Read(bytes)

	return bytes, err
}
func getVoskTranscription(audioPath string, transcriberUrl string) string {
	voskAudioPath = audioPath
	openbrowser(transcriberUrl)
	handleRequests()
	return voskTranscription
}

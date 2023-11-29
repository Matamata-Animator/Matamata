package main

import (
	"embed"
	"flag"
	"log"
	"math/rand"
	"os"
	"path/filepath"
	"strconv"
	"time"
)

//go:embed all:defaults
var defaults embed.FS

type Args struct {
	audioPath         string
	characterPath     string
	timestamps        string
	verbose           int8
	outputPath        string
	transcriberUrl    string
	transcriberApiKey string
	alignerUrl        string
	phonemesPath      string
	debugging         bool
}

func parseArgs() Args {
	//_a, _ := defaults.ReadFile("defaults/default_timestamps.txt")
	//a:= string(_a)
	//fmt.Println(a)
	openAiUrl := "https://api.openai.com/v1/"
	audio := flag.String("a", "", "audio path")
	character := flag.String("c", "", "character path")
	timestamps := flag.String("t", "", "timestamps file path")

	verbose := flag.Int("v", 1, "verbose level")
	output := flag.String("o", "output.mov", "output file path")
	transcriber_key := flag.String("k", "", "OpenAI API Key")
	transcribe_url := flag.String("api_url", openAiUrl, "Can be subsituted for the LocalAI url")
	aligner_url := flag.String("aligner_url", "http://localhost:8765/transcriptions?async=false", "Gentle server url")
	phonemes_path := flag.String("phonemes", "", "Custom phonemes JSON path")
	debugging := flag.Bool("debugging", false, "Skips transcription and replaces with pangram text")

	flag.Parse()
	generateDir = filepath.Join(os.TempDir(), "matamata/", "run"+strconv.Itoa(int(time.Now().Unix()))+"-"+strconv.Itoa(rand.Int()))
	os.MkdirAll(filepath.Join(generateDir, "frames/"), 0777)
	if *character == "" || *phonemes_path == "" {

		if *character == "" {
			*character = filepath.Join(generateDir, "defaults/SampleCharacter/")
		}
		if *phonemes_path == "" {
			*phonemes_path = filepath.Join(generateDir, "defaults/phonemes.json")
		}
		go unwrapEmbeddedDefaultCharacter()
	}

	args := Args{
		audioPath:         *audio,
		characterPath:     *character,
		timestamps:        *timestamps,
		verbose:           int8(*verbose),
		outputPath:        *output,
		transcriberApiKey: *transcriber_key,
		transcriberUrl:    *transcribe_url,
		alignerUrl:        *aligner_url,
		phonemesPath:      *phonemes_path,
		debugging:         *debugging,
	}
	loglevel = args.verbose
	if args.audioPath == "" {
		log.Fatal("Audio path is required")
	}
	if args.transcriberUrl == openAiUrl && args.transcriberApiKey == "" {
		log.Fatal("Please provide an OpenAI API key or use LocalAI")
	}
	return args
}

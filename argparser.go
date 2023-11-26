package main

import (
	"embed"
	"flag"
	"log"
	"os"
	"path/filepath"
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
}

func parseArgs() Args {
	//_a, _ := defaults.ReadFile("defaults/default_timestamps.txt")
	//a:= string(_a)
	//fmt.Println(a)
	audio := flag.String("a", "", "audio path")
	character := flag.String("c", "", "character path")
	timestamps := flag.String("t", "", "timestamps file path")

	verbose := flag.Int("v", 1, "verbose level")
	output := flag.String("o", "output.mov", "output file path")
	transcriber_key := flag.String("k", "", "OpenAI API Key")
	transcribe_url := flag.String("api_url", "https://api.openai.com/v1/", "Can be subsituted for the LocalAI url")
	aligner_url := flag.String("aligner_url", "http://localhost:8765/transcriptions?async=false", "Gentle server url")
	phonemes_path := flag.String("phonemes", "", "Custom phonemes JSON path")

	flag.Parse()

	if *character == "" || *phonemes_path == "" {
		cacheDir, _ := os.UserCacheDir()
		if *character == "" {
			*character = filepath.Join(cacheDir, "matamata/defaults/SampleCharacter")
		}
		if *phonemes_path == "" {
			*phonemes_path = filepath.Join(cacheDir, "matamata/defaults/phonemes.json")
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
	}
	loglevel = args.verbose
	if args.audioPath == "" {
		log.Fatal("Audio path is required")
	}
	return args
}

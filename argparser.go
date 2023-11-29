package main

import (
	"embed"
	"encoding/json"
	"flag"
	"io"
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
	AudioPath         string `json:"audioPath"`
	CharacterPath     string `json:"characterPath"`
	Timestamps        string `json:"timestamps"`
	Verbose           int8   `json:"verbose"`
	OutputPath        string `json:"outputPath"`
	TranscriberUrl    string `json:"transcriberUrl"`
	TranscriberApiKey string `json:"transcriberApiKey"`
	AlignerUrl        string `json:"alignerUrl"`
	PhonemesPath      string `json:"phonemesPath"`
	Debugging         bool   `json:"debugging"`
}

func loadDefaults() Args {
	cacheDir, _ := os.UserCacheDir()
	matamataPath := filepath.Join(cacheDir, "matamata/")

	//make new cachedir if it doesnt exist
	matamataPathExists, _ := pathExists(matamataPath)
	if !matamataPathExists {
		logM(1, "Making New Cache Dir")
		os.Mkdir(matamataPath, 0777)
	}

	defaultsPath := filepath.Join(matamataPath, "defaultArguments.json")
	defaultsPathExists, _ := pathExists(defaultsPath)
	if !defaultsPathExists {
		logM(1, "Writing new defaults json")
		embeddedFile, _ := defaults.Open("defaults/defaultArguments.json")
		defer embeddedFile.Close()
		destinationFile, _ := os.Create(defaultsPath)
		defer destinationFile.Close()
		_, e := io.Copy(destinationFile, embeddedFile)
		if e != nil {
			log.Fatal("Error copying file:", e)
		}
	}

	logM(1, "Reading defaults json from ", defaultsPath)
	configFile, err := os.ReadFile(defaultsPath)
	if err != nil {
		log.Fatal(err)

	}
	defArgs := Args{}
	err = json.Unmarshal(configFile, &defArgs)
	if err != nil {
		log.Fatal(err)
	}

	return defArgs

}

func parseArgs() Args {
	//_a, _ := defaults.ReadFile("defaults/default_timestamps.txt")
	//a:= string(_a)
	//fmt.Println(a)
	defArgs := loadDefaults()

	audio := flag.String("a", defArgs.AudioPath, "audio path")
	character := flag.String("c", defArgs.CharacterPath, "character path")
	timestamps := flag.String("t", defArgs.Timestamps, "Timestamps file path")

	verbose := flag.Int("v", int(defArgs.Verbose), "Verbose level")
	output := flag.String("o", defArgs.OutputPath, "output file path")
	transcriber_key := flag.String("k", defArgs.TranscriberApiKey, "OpenAI API Key")
	transcribe_url := flag.String("api_url", defArgs.TranscriberUrl, "Can be subsituted for the LocalAI url")
	aligner_url := flag.String("aligner_url", defArgs.AlignerUrl, "Gentle server url")
	phonemes_path := flag.String("phonemes", defArgs.PhonemesPath, "Custom phonemes JSON path")
	debugging := flag.Bool("debugging", defArgs.Debugging, "Skips transcription and replaces with pangram text")

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
		AudioPath:         *audio,
		CharacterPath:     *character,
		Timestamps:        *timestamps,
		Verbose:           int8(*verbose),
		OutputPath:        *output,
		TranscriberApiKey: *transcriber_key,
		TranscriberUrl:    *transcribe_url,
		AlignerUrl:        *aligner_url,
		PhonemesPath:      *phonemes_path,
		Debugging:         *debugging,
	}
	loglevel = args.Verbose
	if args.AudioPath == "" {
		log.Fatal("Audio path is required")
	}
	openAiUrl := "https://api.openai.com/v1/"
	if args.TranscriberUrl == openAiUrl && args.TranscriberApiKey == "" {
		log.Fatal("Please provide an OpenAI API key or use LocalAI")
	}
	return args
}

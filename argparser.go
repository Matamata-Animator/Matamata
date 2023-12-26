package main

import (
	"embed"
	"encoding/json"
	"flag"
	"fmt"
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
var ARGS_SCHEMA_VERSION = 1

type Args struct {
	Schema            int    `json:"schema"`
	AudioPath         string `json:"audioPath"`
	CharacterPath     string `json:"characterPath"`
	Timestamps        string `json:"timestamps"`
	Verbose           int8   `json:"verbose"`
	OutputPath        string `json:"outputPath"`
	WhisperUrl        string `json:"whisperUrl"`
	VoskUrl           string `json:"voskUrl"`
	TranscriberApiKey string `json:"transcriberApiKey"`
	AlignerUrl        string `json:"alignerUrl"`
	PhonemesPath      string `json:"phonemesPath"`
	SkipTranscriber   bool   `json:"skipTranscriber"`
	CheckForUpdates   bool   `json:"checkForUpdates"`
	RunProfiler       bool   `json:"runProfiler"`
	Transcriber       string `json:"transcriber"`
}

func loadDefaults() (Args, string) {
	cacheDir, _ := os.UserCacheDir()
	matamataPath := filepath.Join(cacheDir, "matamata/")

	//make new cachedir if it doesn't exist
	matamataPathExists, _ := pathExists(matamataPath)
	if !matamataPathExists {
		logM(1, "Making New Cache Dir")
		os.MkdirAll(matamataPath, 0777)
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
			fmt.Println(defaultsPath)
			log.Fatal("Error copying file:", e)
		}
	}

	logM(1, "Reading defaults json from:", defaultsPath)
	configFile, err := os.ReadFile(defaultsPath)
	if err != nil {
		log.Fatal(err)

	}
	defArgs := Args{}
	err = json.Unmarshal(configFile, &defArgs)
	if err != nil {
		log.Fatal(err)
	}

	return defArgs, defaultsPath

}

func parseArgs() Args {
	defArgs, defaultsPath := loadDefaults()
	if defArgs.CheckForUpdates {
		checkForUpdates()
	}
	if defArgs.Schema != ARGS_SCHEMA_VERSION {
		colorReset := "\033[0m"
		colorRed := "\033[31m"
		fmt.Println(string(colorRed)+"You are using an outdated default argument schema("+strconv.Itoa(defArgs.Schema)+" -> "+strconv.Itoa(ARGS_SCHEMA_VERSION)+") Please update or delete the file:", defaultsPath, string(colorReset))
		fmt.Println("Please note, deleting the file will reset your default arguments")
		os.Exit(1)
	}

	audio := flag.String("a", defArgs.AudioPath, "audio path")
	character := flag.String("c", defArgs.CharacterPath, "character path")
	timestamps := flag.String("t", defArgs.Timestamps, "Timestamps file path")

	verbose := flag.Int("v", int(defArgs.Verbose), "Verbose level")
	output := flag.String("o", defArgs.OutputPath, "output file path")
	transcriber_key := flag.String("k", defArgs.TranscriberApiKey, "OpenAI API Key")
	whisper_url := flag.String("whisper_url", defArgs.WhisperUrl, "Can be subsituted for the LocalAI url")
	vosk_url := flag.String("vosk_url", defArgs.VoskUrl, "If using vosk and a different transcriber website")

	aligner_url := flag.String("aligner_url", defArgs.AlignerUrl, "Gentle server url")
	phonemes_path := flag.String("phonemes", defArgs.PhonemesPath, "Custom phonemes JSON path")
	run_profiler := flag.Bool("run_profiler", defArgs.RunProfiler, "Run pprof server")

	//dev settings
	skipTranscriber := flag.Bool("skipTranscriber", defArgs.SkipTranscriber, "Skips transcription and replaces with pangram text")
	transcriber := flag.String("transcriber", defArgs.Transcriber, "Transcriber to use (Whisper | LocalAI | Vosk)")

	flag.Parse()

	generateDir = filepath.Join(os.TempDir(), "matamata/", "run"+strconv.Itoa(int(time.Now().Unix()))+"-"+strconv.Itoa(rand.Int()))
	logM(2, "Generate Dir:", generateDir)
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
		Transcriber:       *transcriber,
		TranscriberApiKey: *transcriber_key,
		WhisperUrl:        *whisper_url,
		VoskUrl:           *vosk_url,
		AlignerUrl:        *aligner_url,
		PhonemesPath:      *phonemes_path,
		SkipTranscriber:   *skipTranscriber,
		CheckForUpdates:   defArgs.CheckForUpdates,
		RunProfiler:       *run_profiler,
	}
	loglevel = args.Verbose
	if args.AudioPath == "" {
		log.Fatal("Audio path is required")
	}

	openAiUrl := "https://api.openai.com/v1/"
	if args.Transcriber == "Whisper" && args.WhisperUrl == "" {
		args.WhisperUrl = openAiUrl
	} else if args.Transcriber == "LocalAI" && args.WhisperUrl == "" {
		args.WhisperUrl = "http://localhost:8080/v1/"
	} else if args.Transcriber == "Vosk" && args.VoskUrl == "" {
		args.VoskUrl = "https://matamata.org/web-vosk-transcriber/"
	}

	if args.WhisperUrl == openAiUrl && args.TranscriberApiKey == "" {
		log.Fatal("Please provide an OpenAI API key or use a different transcriber")
	}
	return args
}

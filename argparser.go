package main

import (
	"embed"
	"flag"
	"log"
)

//go:embed all:defaults
var defaults embed.FS

type Args struct {
	audioPath     string
	characterPath string
	verbose       int8
	outputPath    string
}

func parseArgs() Args {
	//_a, _ := defaults.ReadFile("defaults/default_timestamps.txt")
	//a:= string(_a)
	//fmt.Println(a)
	audio := flag.String("a", "", "audio path")
	character := flag.String("c", "", "character path")
	verbose := flag.Int("v", 1, "verbose level")
	output := flag.String("o", "output.mov", "output file path")

	flag.Parse()

	args := Args{
		audioPath:     *audio,
		characterPath: *character,
		verbose:       int8(*verbose),
		outputPath:    *output,
	}
	loglevel = args.verbose
	if args.audioPath == "" {
		log.Fatal("Audio path is required")
	}
	return args
}

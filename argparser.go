package main

import (
	// "flag"
	"embed"
	"fmt"
)

//go:embed all:defaults
var defaults embed.FS

type Args struct {
	audioPath     string
	characterPath string
	verbose       int
	outputPath    string
}

func parseArgs() Args {
	//_a, _ := defaults.ReadFile("defaults/default_timestamps.txt")
	//a:= string(_a)
	//fmt.Println(a)
	args := Args{
		audioPath:     "",
		characterPath: "",
		verbose:       0,
		outputPath:    "output.mov",
	}

	return args
}

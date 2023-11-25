package main

import (
	"fmt"
)

var loglevel int8 = 1

func logM(message any, level int8) {
	if loglevel >= level {
		fmt.Println(message)
	}
}

func main() {
	args := parseArgs()
	logM(args, 3)

	//downloadModel()

	text := transcribe(args.audioPath, args.transcriberURL, args.transcriberApiKey)
	logM("Transcription: ", 2)
	logM(text, 2)

}

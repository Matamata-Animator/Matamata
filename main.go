package main

import (
	"fmt"
	"log"
	"os"
	"os/exec"
)

var args Args

var generateDir string

func main() {
	args = parseArgs()

	logM(3, "Args:", args)

	var text string
	if !args.Debugging {
		logM(1, "Transcribing Audio...")

		text = transcribe(args.AudioPath, args.TranscriberUrl, args.TranscriberApiKey)
	} else {
		logM(1, "Using Stored Transcription...")
		//cache transcription to save time durinng development
		text = "That quick beige fox jumped in the air over each thin dog. Look out, I shout, for he's foiled you again, creating chaos."
	}
	logM(2, "Transcription:", text)
	logM(1, "Aligning Audio...")

	gentleResponse, err := gentleAlign(args.AlignerUrl, args.AudioPath, text)
	if err != nil {
		panic(err)
	}
	logM(3, gentleResponse)

	logM(1, "Parsing Timestamps...")
	timestamps := parseTimestamps(args.Timestamps)
	logM(3, "Timestamps:", timestamps)
	genImageSequence(
		VideoRequest{
			gentleResponse,
			args.AudioPath,
			args.CharacterPath,
			args.PhonemesPath,
			timestamps,
		})

	logM(1, "Combining Frames...")

	ffmpegCmd := exec.Command("ffmpeg", "-i", args.AudioPath, "-r", "100", "-i", generateDir+"/frames/%d.jpg", "-c:v",
		"libx264", "-pix_fmt", "yuv420p", args.OutputPath, "-y")
	//ffmpegCmd.Stderr = os.Stderr
	//ffmpegCmd.Stdout = os.Stdout
	err = ffmpegCmd.Run()
	if err != nil {
		log.Fatal(err)
	}

	logM(1, "Removing Old Files...")

	err = os.RemoveAll(generateDir)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println("Done")

}

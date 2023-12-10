package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"os/exec"
	"runtime"
	"time"

	_ "net/http/pprof"
)

var args Args

var generateDir string

func main() {
	runtime.GOMAXPROCS(runtime.NumCPU())
	start := time.Now()
	args = parseArgs()

	if args.RunProfiler {
		go func() {
			http.ListenAndServe("localhost:6060", nil)
		}()
	}
	logM(3, "Args:", args)
	logM(1, "Parsing Timestamps...")
	timestamps := parseTimestamps(args.Timestamps)
	logM(2, "Timestamps:", timestamps)
	var text string
	if !args.SkipTranscriber {
		logM(1, "Transcribing Audio...")

		if args.Transcriber == "Vosk" {
			text = getVoskTranscription(args.AudioPath, args.VoskUrl)
		} else if args.Transcriber == "Whisper" || args.Transcriber == "LocalAI" {
			text = transcribe(args.AudioPath, args.WhisperUrl, args.TranscriberApiKey)
		} else {
			log.Fatal("Invalid Transcriber:", args.Transcriber)
		}
	} else {
		logM(1, "Using Stored Transcription...")
		//cache transcription to save time durinng development
		text = "That quick beige fox jumped in the air over each thin dog. Look out, I shout, for he's foiled you again, creating chaos."
		text = "TikTok, and Instagram account, along with some basic artwork and description to go along with each of them. I'll check back in two weeks to see how this is going. Okay, so it's two weeks later, starting with the Instagram. I posted the first video, woke up the next day, and had zero views. I don't know if this is something wrong with my account setup, but Instagram was doing zero promotion for it. And honestly, I'm fine not making content for the Zuck anyway, so I dropped that channel. As for the other two, in total, the videos amassed over 20,000 views and 1,400 likes. In two weeks. It did that in two weeks. It took me three years on my main channel to get that. It took me three years on this channel to reach that. But the really interesting part, what did the viewers think? TikTok was so much better than the view-to-like ratio. But before I reveal the amazing comment section, if you liked this video, please remember to like, share, subscribe, and comment something to give the algorithm a little nudge. Huge thank you to my patrons like FudgePop01 for supporting the channel. Links to Discord and the code in the description. Now let's read some of the comments. Okay, that's fair. He's popular, but not super recognizable outside of people who know the game. Aw, that's so nice. Well, my friend, you are the Scott Pilgrim fan. The bot's video included this fact. The bot's video included this fact. This interesting tidbit was also pointed out in a movie from 2010 called Scott Pilgrim Long Mario. These are all so funny. What a comical AI. What else did the people say? Oh. Well, that's a conversation about AI that's well beyond the scope of this video. Especially since his transition happened well after the data cutoff, but at the same time, large language models are just regurgitating the language that they see, and what chatGPT sees is news articles that aren't retroactively being edited. Point is cancel open AI and not me. Thank you. Point is cancel open AI and not me. Point is cancel open AI and not me. And finally, people seem to not accept the fact that the proper pronunciation is Mario. Bye now."

	}
	logM(2, "Transcription:", text)
	logM(1, "Aligning Audio...")

	gentleResponse, err := gentleAlign(args.AlignerUrl, args.AudioPath, text)
	if err != nil {
		panic(err)
	}
	logM(3, gentleResponse)

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
	t := time.Now()
	fmt.Println("Completed in", t.Sub(start))

	if args.RunProfiler {
		fmt.Println("Run the pprof now")
		select {}
	}
}

package main

var args Args

func main() {
	args = parseArgs()
	logM(3, "Args:", args)

	logM(1, "Transcribing Audio...")

	//text := transcribe(args.audioPath, args.transcriberUrl, args.transcriberApiKey)
	//cache transcription to save time durinng development
	text := "That quick beige fox jumped in the air over each thin dog. Look out, I shout, for he's foiled you again, creating chaos."

	logM(2, "Transcription:", text)
	logM(1, "Aligning Audio...")

	gentleResponse, err := gentleAlign(args.alignerUrl, args.audioPath, text)
	if err != nil {
		panic(err)
	}
	logM(3, gentleResponse)

	logM(1, "Parsing Timestamps...")
	timestamps := parseTimestamps(args.timestamps)
	logM(3, "Timestamps:", timestamps)

}

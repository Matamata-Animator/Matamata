var vosk = require("vosk");

import fs from "fs";
import { Readable } from "stream";
import wav from "wav";
import { join } from "path";

interface VoskTimestamp {}
interface VoskOut {
  confidence: number;
  result: VoskTimestamp[];
  text: string;
}

export async function getTranscribedText(
  audio_path: string,
  model_path: string
): Promise<string> {
  return await (
    await transcribeAudio(audio_path, model_path)
  ).text;
}
export async function transcribeAudio(
  audio_path: string,
  model_path: string
): Promise<VoskOut> {
  if (process.argv.length > 2) audio_path = process.argv[2];

  vosk.setLogLevel(-1);
  const model = new vosk.Model(model_path);

  const wfReader = new wav.Reader();
  const wfReadable = new Readable().wrap(wfReader);

  let transcription: Promise<VoskOut> = new Promise((resolve, reject) => {
    wfReader.on("format", async ({ audioFormat, sampleRate, channels }) => {
      if (audioFormat != 1 || channels != 1) {
        console.error("Audio file must be WAV format mono PCM.");
        process.exit(1);
      }
      const rec = new vosk.Recognizer({ model: model, sampleRate: sampleRate });
      rec.setMaxAlternatives(1);
      rec.setWords(true);

      let results: any[] = [];
      for await (const data of wfReadable) {
        const end_of_speech = rec.acceptWaveform(data);
        if (end_of_speech) {
          results.push(rec.result());
          // console.log(JSON.stringify(rec.result(), null, 4));
        }
      }

      results.push(rec.finalResult(rec));
      rec.free();
      resolve(results[0].alternatives[0]);
    });
  });

  fs.createReadStream(audio_path, { highWaterMark: 4096 })
    .pipe(wfReader)
    .on("finish", function (err) {
      model.free();
    });

  return transcription;
}

if (require.main === module) {
  transcribeAudio("/Users/human/Desktop/test.wav", "model").then((t: any) =>
    console.log(t)
  );
}

var vosk = require("vosk");
// import vosk from "vosk";
import fs from "fs";
import { Readable } from "stream";
import wav from "wav";
import { join } from "path";

export async function transcribeAudio(audio_path: string, model_path: string) {
  let path_cache = audio_path;

  // let model_path = join(__dirname, "..", "model");
  if (!fs.existsSync(model_path)) {
    console.log(
      "Please download the model from https://alphacephei.com/vosk/models and unpack as " +
        model_path +
        " in the current folder."
    );
    process.exit();
  }

  if (process.argv.length > 2) audio_path = process.argv[2];

  vosk.setLogLevel(-1);
  const model = new vosk.Model(model_path);

  const wfReader = new wav.Reader();
  const wfReadable = new Readable().wrap(wfReader);

  let transcribed = new Promise((resolve, reject) => {
    wfReader.on("format", async (fileInfo: wav.Format) => {
      if (fileInfo.audioFormat != 1 || fileInfo.channels != 1) {
        console.error("Audio file must be WAV format mono PCM.");
        process.exit(1);
      }
      const rec = new vosk.Recognizer({
        model: model,
        sampleRate: fileInfo.sampleRate,
      });
      rec.setMaxAlternatives(10);
      rec.setWords(true);
      for await (const data of wfReadable) {
        const end_of_speech = rec.acceptWaveform(data);
        if (end_of_speech) {
          rec.result();
        }
      }
      let json = rec.finalResult(rec);
      // console.log(json.alternatives[0].result);
      resolve(json.alternatives[0].text);

      rec.free();
    });
  });

  audio_path = path_cache;
  fs.createReadStream(audio_path, { highWaterMark: 4096 })
    .pipe(wfReader)
    .on("finish", function (err: string) {
      model.free();
    });

  return transcribed;
}

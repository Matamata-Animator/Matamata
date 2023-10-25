import fs from "fs";
import { Readable } from "stream";
import wav from "wav";
import { join } from "path";
import { execSync } from "child_process";

interface VoskTimestamp {
  start: number;
  end: number;
  word: string;
}
interface VoskOut {
  confidence: number;
  result: VoskTimestamp[];
  text: string;
}

export async function getTranscribedText(
  transcriber: "vosk"|"watson",
  audio_path: string,
  model_path: string,
  watson_api_key: string,
): Promise<string> {
  if (transcriber == 'vosk'){
    return await (
      await voskTranscribe(audio_path, model_path)
    ).text;
  }else{
    return watsonTranscribe(watson_api_key, audio_path);
  }
}

export async function watsonTranscribe(
  watson_api_key: string,
  audio_path:string){
    const fs = require('fs');
    const SpeechToTextV1 = require('ibm-watson/speech-to-text/v1');
    const { IamAuthenticator } = require('ibm-watson/auth');
    
    const speechToText = new SpeechToTextV1({
      authenticator: new IamAuthenticator({ apikey: watson_api_key }),
      serviceUrl: 'https://api.us-south.speech-to-text.watson.cloud.ibm.com'
    });
    
    const params = {
      // From file
      audio: fs.createReadStream(audio_path),
      contentType: 'audio/l16; rate=44100'
    };
    
    let transcription: Promise<string> = new Promise((resolve, reject) => {
      speechToText.recognize(params)
        .then((response: { result: any; }) => {
          let script = '';
          for(let block of response.result.results){
            script += block.alternatives[0].transcript
          }
          console.log(script)
          resolve(script)
        })
        .catch((err: any) => {
          console.log(err);
        });
    });
    return transcription
  }




export async function voskTranscribe(
  audio_path: string,
  model_path: string,

): Promise<VoskOut> {
  var vosk = require("vosk");

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
      let results: any[] = [];
      const rec = new vosk.Recognizer({model: model, sampleRate: sampleRate});
      rec.setMaxAlternatives(10);
      rec.setWords(true);
      rec.setPartialWords(true);
      for await (const data of wfReadable) {
        const end_of_speech = rec.acceptWaveform(data);
        if (end_of_speech) {
          let r = rec.result()
          results.push(r);
          // console.log(JSON.stringify(r, null, 4));
          // console.log(Date.now(), r)
        }
      }

      results.push(rec.finalResult(rec));
      rec.free();
      

      let out: VoskOut = {
        confidence: results[0].confidence,
        result: [],
        text: ''
      }

      for (let r of results){
        if(r.alternatives.length >= 1){
        out.text += r.alternatives[0].text;
        out.result = [...out.result, r.alternatives[0].result]
        }else{
          console.log("No text found")
          console.log(JSON.stringify(r, null, 4));
        }
      }

      resolve(out);
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
  voskTranscribe("/home/human/Desktop/test.wav", "model").then((t: any) =>
    console.log(t)
  );
}

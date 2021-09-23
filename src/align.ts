import { Curl } from "node-libcurl";
import { gentle_log } from "./logger";

import { exec } from "child_process";

let url = "http://localhost:8765/transcriptions?async=false";

interface Phoneme {
  duration: number;
  phone: string;
}
interface AlignedWord {
  alignedWord: string;
  case: string;
  end: number;
  endOffset: number;
  phones: Phoneme[];
  start: number;
  startOffset: number;
  word: string;
}
export interface GentleOut {
  // transcript: string;
  words: AlignedWord[];
}

export async function gentleAlign(audio_path: string, script_path: string) {
  let gentle_out = new Promise<GentleOut>((resolve, reject) => {
    const curl = new Curl();

    curl.setOpt(Curl.option.URL, url);
    curl.setOpt(Curl.option.HTTPPOST, [
      { name: "audio", file: audio_path },
      { name: "transcript", file: script_path },
    ]);

    curl.on("end", function (statusCode, data, headers) {
      resolve(JSON.parse(data as unknown as string));
    });
    curl.on("error", (err) => {
      console.log(err);
      curl.close.bind(curl);
    });
    curl.perform();
  });

  return gentle_out;
}

export async function cleanGentle(gentle_stamps: GentleOut) {
  gentle_stamps.words.filter((word) => {
    return word.case == "success";
  });
  return gentle_stamps;
}

export async function allosaurusAlign(audio_path: string) {}

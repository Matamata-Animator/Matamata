import { gentle_log } from "./logger";

import { exec, execSync } from "child_process";
import { transcribeAudio } from "./transcriber";
import { time } from "console";
import { TIMEOUT } from "dns";

let url = "http://localhost:8765/transcriptions?async=false";

interface Phoneme {
  duration: number;
  phone: string;
}
interface AlignedWord {
  alignedWord: string;
  case: string;
  end: number;
  endOffset?: number;
  phones: Phoneme[];
  start: number;
  startOffset?: number;
  word: string;
}
export interface GentleOut {
  // transcript: string;
  words: AlignedWord[];
}

export async function gentleAlign(audio_path: string, script_path: string) {
  const { Curl } = require("node-libcurl");

  let gentle_out = new Promise<GentleOut>((resolve, reject) => {
    const curl = new Curl();

    curl.setOpt(Curl.option.URL, url);
    curl.setOpt(Curl.option.HTTPPOST, [
      { name: "audio", file: audio_path },
      { name: "transcript", file: script_path },
    ]);

    curl.on("end", function (statusCode: any, data: any, headers: any) {
      resolve(JSON.parse(data as unknown as string));
    });
    curl.on("error", (err: any) => {
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

interface AlloPhone {
  start: number;
  phoneme: string;
}

export async function allosaurusAlign(audio_path: string, model_path: string) {
  let command = `python -m allosaurus.run -i ${audio_path} --lang eng --model eng2102 --timestamp=True`;
  let timestampsPromise = transcribeAudio(audio_path, model_path);

  let phonesStrings = execSync(command).toString().split(/\n/g);

  phonesStrings.pop();
  let phones: AlloPhone[] = [];
  phonesStrings.forEach((str) => {
    let parts = str.split(" ");
    let phone: AlloPhone = {
      start: Number(parts[0]),
      phoneme: parts[2],
    };
    phones.push(phone);
  });

  let timestamps = (await timestampsPromise).result;

  let words: AlignedWord[] = [];
  for (
    let wordCounter = 0;
    wordCounter < timestamps.length && phones.length > 0;
    wordCounter++
  ) {
    let word: AlignedWord = {
      alignedWord: timestamps[wordCounter].word,
      word: timestamps[wordCounter].word,
      start: timestamps[wordCounter].start,
      end: timestamps[wordCounter].end,
      case: "success",
      phones: [],
    };

    // Find which phonemes are in the word
    let includedPhones: AlloPhone[] = [];
    for (let p = 0; p < phones.length && phones[p].start < word.end; p++) {
      includedPhones.push(phones[p]);
    }

    for (let p = 0; p < includedPhones.length - 1; p++) {
      let phone: Phoneme = {
        phone: includedPhones[p].phoneme,
        duration: includedPhones[p + 1].start - includedPhones[p].start,
      };
      word.phones.push(phone);
    }

    if (includedPhones.length > 0) {
      let last = includedPhones.pop();
      word.phones.push({
        phone: last!.phoneme,
        duration: word.end - last!.start,
      });
      phones = phones.slice(word.phones.length);
    } else {
      let fillerPhone: Phoneme = {
        duration: word.end - word.start,
        phone: "ʌ",
      };
      word.phones.push(fillerPhone);
    }

    words.push(word);
  }

  let gentleOut: GentleOut = {
    words: words,
  };
  return gentleOut;
  console.log(JSON.stringify(words, null, 4));
}

if (require.main === module) {
  allosaurusAlign("/Users/human/Desktop/test.wav", "model");
}

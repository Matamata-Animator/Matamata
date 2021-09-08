import { Curl } from "node-libcurl";

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
}
export interface GentleOut {
  transcript: string;
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
      resolve(data as unknown as GentleOut);
    });
    curl.on("error", (err) => {
      console.log(err);
      curl.close.bind(curl);
    });
    curl.perform();
  });
  return gentle_out;
}

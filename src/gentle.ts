import { rejects } from "assert/strict";
import { Curl } from "node-libcurl";
import { resolve } from "path/posix";

let url = "http://localhost:8765/transcriptions?async=false";

export async function gentleAlign(audio_path: string, script_path: string) {
  let gentle_out = new Promise<unknown>((resolve, reject) => {
    const curl = new Curl();
    const close = curl.close.bind(curl);

    curl.setOpt(Curl.option.URL, url);
    curl.setOpt(Curl.option.HTTPPOST, [
      { name: "audio", file: audio_path },
      { name: "transcript", file: script_path },
    ]);

    curl.on("end", function (statusCode, data, headers) {
      resolve(data);
    });
    curl.on("error", close);
    curl.perform();
  });
  return gentle_out;
}

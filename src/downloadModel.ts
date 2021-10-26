import download from "download";
import { rm, move, existsSync } from "fs-extra";

import { terminal } from "terminal-kit";

import path from "path/posix";
import extract from "extract-zip";

let baseUrl = "http://alphacephei.com/vosk/models/";
let large = "vosk-model-en-us-0.21";
let small = "vosk-model-small-en-us-0.15";

export async function downloadModel(downloadPath: string, zipName: string) {
  terminal(
    "^r^+This is downloading a 1.6gb voice model, this will take a while.^:^g Go grab a coffee, or enjoy some quality content: ^_^+https://youtube.com/c/AI-Spawn\n^:"
  );

  let temp = "modeltmp";
  await download(`${baseUrl}${zipName}.zip`, temp);

  await extract(path.join(temp, `${zipName}.zip`), {
    dir: path.join(process.cwd(), `${temp}2`),
  });

  await move(
    path.join(process.cwd(), `${temp}2/${zipName}/`),
    path.join(downloadPath),
    { overwrite: true }
  );

  await rm("modeltmp/", { recursive: true });
  await rm("modeltmp2/", { recursive: true });
}

if (require.main === module) {
  downloadModel("model", large);
}

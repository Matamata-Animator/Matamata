import download from "download";
import { rm, move, existsSync } from "fs-extra";

import { terminal } from "terminal-kit";

let path: any;
try {
  path = require("path/posix");
} catch (e) {
  path = require("path");
}
import extract from "extract-zip";

let baseUrl = "http://alphacephei.com/vosk/models/";
let large = "vosk-model-en-us-0.22";
let small = "vosk-model-small-en-us-0.15";

export async function downloadModel(
  downloadPath: string,
  folderName: string,
  zipName: string
) {
  terminal(
    "^r^+This is downloading a 1.8gb voice model, this will take a while.^:^g Go grab a coffee, or enjoy some quality content: ^_^+https://youtube.com/c/AI-Spawn\n^:"
  );

  let temp = "modeltmp";
  await download(`${baseUrl}${zipName}.zip`, path.join(downloadPath, temp));

  await extract(path.join(downloadPath, temp, `${zipName}.zip`), {
    dir: path.join(downloadPath, `${temp}2`),
  });

  await move(
    path.join(downloadPath, `${temp}2/${zipName}/`),
    path.join(downloadPath, folderName),
    { overwrite: true }
  );

  await rm(path.join(downloadPath, "modeltmp/"), { recursive: true });
  await rm(path.join(downloadPath, "modeltmp2/"), { recursive: true });
}

if (require.main === module) {
  downloadModel(process.cwd(), "model", large);
}

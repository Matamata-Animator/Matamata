console.log("REEEEEEEEEEEEEEEEEEEEEEEEEEEE");

import download from "download";
import { rm, move, existsSync } from "fs-extra";

import path from "path/posix";
import extract from "extract-zip";

let baseUrl = "http://alphacephei.com/vosk/models/";
let large = "vosk-model-en-us-0.21";
let small = "vosk-model-small-en-us-0.15";
async function downloadModel(downloadPath: string, zipName: string) {
  let temp = "modeltmp";
  console.log(process.cwd());
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

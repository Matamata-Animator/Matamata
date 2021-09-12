console.log("REEEEEEEEEEEEEEEEEEEEEEEEEEEE");

import download from "download";
import { rm, move, existsSync } from "fs-extra";

import path from "path/posix";
import extract from "extract-zip";

let baseUrl = "http://alphacephei.com/vosk/models/";
let large = "vosk-model-en-us-0.21";
let small = "vosk-model-small-en-us-0.15";
async function downloadModel(downloadPath: string, zipName: string) {
  console.log(process.cwd());
  await download(`${baseUrl}${zipName}.zip`, downloadPath);

  await extract(path.join(downloadPath, `${zipName}.zip`), {
    dir: path.join(process.cwd(), `${downloadPath}2`),
  });

  await move(
    path.join(process.cwd(), `${downloadPath}2/${zipName}/`),
    `model/`,

    { overwrite: true }
  );

  await rm("modeltmp/", { recursive: true });
  await rm("modeltmp2/", { recursive: true });
}

if (require.main === module) {
  downloadModel("modeltmp", small);
}

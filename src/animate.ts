import { getArgs } from "./argparse";
import { setVerbose, banner, log } from "./logger";

import { removeOld, launchContainer } from "./docker";

import { transcribeAudio } from "./transcriber";
import { json } from "stream/consumers";
import { readFile } from "fs/promises";
import { parseTimestamps, Timestamp } from "./poseParser";

const args = getArgs();
async function main() {
  //////////////////////////////////////////////////////////////
  // Create Banner, Load Audio, Load Script, Transcribe Audio //
  //////////////////////////////////////////////////////////////

  let stupidpromisearray: Promise<any>[] = [];
  setVerbose(args.verbose);
  await banner();
  log("Full Verbose", 2);

  await removeOld(args.container_name);

  let gentle_launched = launchContainer(args.container_name, args.image_name);

  stupidpromisearray.push(gentle_launched);

  //TODO: Create generate folders if needed
  let scriptPromise: Promise<unknown>;
  if (args.text == "") {
    scriptPromise = transcribeAudio(args.audio);
    stupidpromisearray.push(scriptPromise);
  } else {
    scriptPromise = readFile(args.text);
    stupidpromisearray.push(scriptPromise);
  }

  let script = (await Promise.all(stupidpromisearray))[1];
  log("Docker Ready...", 1);

  log(`Script:${script}`, 2);

  ///////////////////////////////
  // Parse TestFile into Poses //
  ///////////////////////////////
  let timestamps: Timestamp[] = [];
  if (args.timestamps != "") {
    timestamps = await parseTimestamps(args.timestamps);
  }
}

if (require.main === module) {
  main();
}

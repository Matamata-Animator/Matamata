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

  setVerbose(args.verbose);
  await banner();
  log("Full Verbose", 2);

  let containerKilled = removeOld(args.container_name);

  //TODO: Create generate folders if needed
  let scriptPromise: Promise<unknown>;
  if (args.text == "") {
    log("Transcribing Audio...", 1);
    scriptPromise = transcribeAudio(args.audio);
  } else {
    scriptPromise = readFile(args.text);
  }

  await Promise.all([containerKilled, scriptPromise]);
  let script = await scriptPromise;

  log(`Script:${script}`, 2);

  await launchContainer(args.container_name, args.image_name);
  log("Docker Ready...", 1);
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

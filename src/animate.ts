import { getArgs } from "./argparse";
import { setVerbose, banner, log } from "./logger";

import { removeOld, launchContainer } from "./docker";

import { transcribeAudio } from "./transcriber";
import { json } from "stream/consumers";
import { readFile } from "fs/promises";
import { rmSync, mkdirSync, existsSync, writeFileSync } from "fs";
import { parseTimestamps, Timestamp } from "./poseParser";

let generate_dir = "generate";

const args = getArgs();
async function main() {
  //////////////////////////////////////////////////////////////
  // Create Banner, Load Audio, Load Script, Transcribe Audio //
  //////////////////////////////////////////////////////////////

  setVerbose(args.verbose);
  await banner();
  log("Full Verbose", 2);

  let containerKilled = removeOld(args.container_name);

  let scriptPromise: Promise<unknown>;
  if (args.text == "") {
    log("Transcribing Audio...", 1);
    scriptPromise = transcribeAudio(args.audio, args.vosk_model);
  } else {
    scriptPromise = readFile(args.text);
  }

  if (existsSync(generate_dir)) {
    rmSync(generate_dir, { recursive: true });
  }
  mkdirSync(generate_dir);

  await Promise.all([containerKilled, scriptPromise]);
  let script = await scriptPromise;

  log(`Script:${script}`, 2);
  writeFileSync(`${generate_dir}/script.txt`, script as string);

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

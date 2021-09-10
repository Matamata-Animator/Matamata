import { getArgs } from "./argparse";
import { setVerbose, banner, log, gentle_log } from "./logger";

import { removeOld, launchContainer } from "./docker";

import { transcribeAudio } from "./transcriber";
import { json } from "stream/consumers";
import { readFile } from "fs/promises";
import { rmSync, mkdirSync, existsSync, writeFileSync } from "fs";
import { parseTimestamps, Timestamp } from "./poseParser";
import { gentleAlign } from "./gentle";
import { gen_video, VideoRequest } from "./videoGenerator";

let generate_dir = "generate";
var start = Date.now();
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
  log(`Container Killed: ${await containerKilled}`, 3);

  let script = await scriptPromise;

  log(`Script:${script}`, 2);
  writeFileSync(`${generate_dir}/script.txt`, String(script));

  if (await containerKilled) {
    await launchContainer(args.container_name, args.image_name);
  }
  log("Docker Ready...", 1);
  ///////////////////////////////
  // Parse TestFile into Poses //
  ///////////////////////////////
  let timestamps: Timestamp[] = [];
  if (args.timestamps != "") {
    timestamps = await parseTimestamps(args.timestamps);
  } else {
    timestamps = [
      {
        time: 0,
        pose_name: args.default_pose,
      },
    ];
  }

  let gentle_json = await gentleAlign(args.audio, `${generate_dir}/script.txt`);

  log(gentle_json, 3);
  let video_request: VideoRequest = {
    gentle_stamps: gentle_json,
    audio_path: args.audio,
    mouths_path: args.mouths,
    characters_path: args.character,
    timestamps: timestamps,
  };

  video_request.dimensions = [0, 0];
  if (args.dimensions != "") {
    let dimensions_split = args.dimensions.split(":");
    video_request.dimensions = [
      Number(dimensions_split[1]),
      Number(dimensions_split[0]),
    ];
  }
  log("Starting Video Generation...", 1);
  gen_video(video_request);
}

if (require.main === module) {
  main().catch((err) => {
    console.log("SOMETHING WENT WRONG");
    console.log(err);
  });
}

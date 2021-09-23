var start = Date.now();

import { Args, getArgs } from "./argparse";
import { setVerbose, banner, log, gentle_log } from "./logger";

import { removeOld, launchContainer } from "./docker";

import { transcribeAudio } from "./transcriber";

import { readFile } from "fs/promises";
import { rmSync, mkdirSync, existsSync, writeFileSync } from "fs";
import { parseTimestamps, Timestamp } from "./poseParser";
import { gentleAlign } from "./align";
import {
  combine_images,
  gen_image_sequence,
  VideoRequest,
} from "./videoGenerator";

let generate_dir = "generate";

async function removeGenerateFolder(generate_dir: string) {
  if (existsSync(generate_dir)) {
    rmSync(generate_dir, { recursive: true });
  }
}
async function main(args: Args) {
  //////////////////////////////////////////////////////////////
  // Create Banner, Load Audio, Load Script, Transcribe Audio //
  //////////////////////////////////////////////////////////////

  setVerbose(args.verbose);
  await banner();
  log("Full Verbose", 3);

  let scriptPromise: Promise<unknown>;

  if (args.aligningAlgorithm == "gentle") {
    let containerKilled = removeOld(args.container_name);
    if (args.text == "") {
      log("Transcribing Audio...", 1);
      scriptPromise = transcribeAudio(args.audio, args.vosk_model);
    } else {
      scriptPromise = readFile(args.text);
    }

    await removeGenerateFolder(generate_dir);
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
  }
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
        type: "poses",
      },
    ];
  }
  log(timestamps, 2);

  let gentle_json = await gentleAlign(args.audio, `${generate_dir}/script.txt`);

  log(gentle_json, 3);

  let dimensions = [0, 0];
  if (args.dimensions != "") {
    let dimensions_split = args.dimensions.split(":");
    dimensions = [Number(dimensions_split[1]), Number(dimensions_split[0])];
  }
  let video_request: VideoRequest = {
    gentle_stamps: gentle_json,
    audio_path: args.audio,
    mouths_path: args.mouths,
    characters_path: args.character,
    timestamps: timestamps,
    default_pose: args.default_pose,
    dimensions: dimensions,
  };

  log("Starting Video Generation...", 1);
  let num_images = await gen_image_sequence(video_request);
  // await combine_images(generate_dir, args.audio, args.output);
  await combine_images(
    "C:/Users/human-w/Desktop/Matamata-Core/generate",
    args.audio,
    args.output,
    num_images
  );
  await removeGenerateFolder(generate_dir);

  return 0;
}

if (require.main === module) {
  const yargs = getArgs();

  main(yargs)
    .then(() => {
      log(`Done in ${(Date.now() - start) / 1000} seconds`, 1);
    })
    .catch((err) => {
      console.log("SOMETHING WENT WRONG");
      console.log(err);
    });
}

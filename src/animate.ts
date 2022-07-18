var start = Date.now();

import { Args, getArgs } from "./argparse";
import { setVerbose, banner, log } from "./logger";

import { removeOld, launchContainer } from "./docker";

import { getTranscribedText } from "./transcriber";

import { readFile } from "fs/promises";
import { rmSync, mkdirSync, existsSync, writeFileSync } from "fs";
import { parseTimestamps, Timestamp } from "./poseParser";
import { allosaurusAlign, gentleAlign, GentleOut } from "./align";
import {
  combine_images,
  gen_image_sequence,
  VideoRequest,
} from "./videoGenerator";

import {getAudioDurationInSeconds} from "get-audio-duration"

let generate_dir = "generate";

function removeGenerateFolder(generate_dir: string) {
  if (existsSync(generate_dir)) {
    rmSync(generate_dir, { recursive: true });
  }
}
async function createGenerateFolder(generate_dir: string) {
  await removeGenerateFolder(generate_dir);
  mkdirSync(generate_dir);
}

export async function main(args: Args) {
  //////////////////////////////////////////////////////////////
  // Create Banner, Load Audio, Load Script, Transcribe Audio //
  //////////////////////////////////////////////////////////////
  setVerbose(args.verbose);
  log(args, 3);

  await banner();
  log("Full Verbose", 3);

  await createGenerateFolder(generate_dir);
  let gentlePromise: Promise<GentleOut>;
  if (args.aligning_algorithm == "allosaurus") {
    gentlePromise = allosaurusAlign(args.audio, args.vosk_model);
  } else if (args.aligning_algorithm == "gentle") {

    if (!args.no_docker){
      let containerKilled = removeOld(args.container_name);
      await containerKilled;
      log(`Container Killed: ${await containerKilled}`, 3);
      if (await containerKilled) {
        await launchContainer(args.container_name, args.image_name);
      }
    }
    let scriptPromise: Promise<unknown>;
  
    if (args.text == "") {
      log(`Transcribing audio using ${args.transcriber}...`, 1);
      scriptPromise = getTranscribedText(args.transcriber,args.audio, args.vosk_model, args.watson_api_key);
    } else {
      scriptPromise = readFile(args.text);
    }

    await removeGenerateFolder(generate_dir);
    mkdirSync(generate_dir);

    await scriptPromise;

    let script = await scriptPromise;

    log(`Script:${script}`, 2);
    writeFileSync(`${generate_dir}/script.txt`, String(script));


    log("Docker Ready...", 1);
    
    gentlePromise = gentleAlign(args.audio, `${generate_dir}/script.txt`);
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
  log("Aligning Audio...", 1)
  let gentle_json = await gentlePromise!;
  log(timestamps, 2);

  log(gentle_json, 3);

  let dimensions = [0, 0];
  if (args.dimensions != "") {
    let dimensions_split = args.dimensions.split(":");
    dimensions = [Number(dimensions_split[1]), Number(dimensions_split[0])];
  }
  let duration = await getAudioDurationInSeconds(args.audio);
  let video_request: VideoRequest = {
    gentle_stamps: gentle_json,
    audio_path: args.audio,
    mouths_path: args.mouths,
    characters_path: args.character,
    timestamps: timestamps,
    default_pose: args.default_pose,
    dimensions: dimensions,
    duration: duration
  };

  log("Generating Frames...", 1);
  let num_images = await gen_image_sequence(video_request);

  log("Combing Frames...", 1);
  await combine_images(
    args.audio,
    args.output,
    num_images
  );
  removeGenerateFolder(generate_dir);
  return 0;
}

if (require.main === module) {
  const yargs = getArgs();
  main(yargs).then(()=>{
    console.log('Done')
    process.exit(0);
  });
}


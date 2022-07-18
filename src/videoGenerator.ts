import { readFileSync } from "fs";

import { cleanGentle, GentleOut } from "./align";
import { Timestamp } from "./poseParser";
import Jimp from "jimp";
import path from "path";

import fs from "fs";
import { createFFmpeg, fetchFile } from "@ffmpeg/ffmpeg";
import { time } from "console";
import { log } from "./logger";

const ffmpeg = createFFmpeg({ log: false });

let ffmpeg_loaded = ffmpeg.load();

interface FrameRequest {
  face_path: string;
  mouth_path: string;
  mouth_scale: number;
  mouth_x: number;
  mouth_y: number;
  duration: number;
  mirror_face: boolean;
  mirror_mouth: boolean;
  dimensions: number[];
  placeableParts: Map<string, string>;
  character: any;
}
export interface VideoRequest {
  gentle_stamps: GentleOut;
  audio_path: string;

  mouths_path: string;
  characters_path: string;

  timestamps: Timestamp[];
  dimensions: number[];

  default_pose: string;

  duration: number;
}
interface Pose {
  image: string;
  x: number;
  y: number;
  facingLeft?: boolean;
  scale?: number;
  mirror_face?: boolean;
  mirror_mouth?: boolean;
}

async function getDimensions(image_path: string) {
  let image = await Jimp.read(image_path);
  return [image.getHeight(), image.getWidth()];
}

async function getPose(pose_name: string, character: any) {
  if (!character.poses.hasOwnProperty(pose_name)) {
    throw `Pose "${pose_name}" does not exist`;
  }
  let pose: Pose = JSON.parse(JSON.stringify(character.poses[pose_name])); //creates an unlinked copy of pose

  let split = pose_name.split("-");
  let mirror = false;
  if (split.length == 2) {
    let left = split[1].toLowerCase() in ["l", "left"];
    mirror = left == pose.facingLeft;
  }
  pose.mirror_face = mirror;
  let mirror_mouth = false;
  if (pose.facingLeft || (!pose.facingLeft && pose.mirror_face)) {
    mirror_mouth = true;
  }
  pose.mirror_mouth = mirror_mouth;

  pose.image = path.join(character.poses.imagesFolder ?? "", pose.image);
  if (!("scale" in pose)) {
    pose.scale = 1;
  }
  return pose;
}

async function createFrameRequest(
  pose: Pose,
  dimensions: number[],
  duration: number,
  mouth_path: string,
  placeableParts: Map<string, string>,
  character: any
) {
  let frame: FrameRequest = {
    face_path: pose.image,
    mouth_path: mouth_path,
    mouth_scale: (pose.scale ?? 1) * (character.poses.default_scale ?? 1),
    mouth_x: pose.x,
    mouth_y: pose.y,
    duration: duration,
    mirror_face: pose.mirror_face!,
    mirror_mouth: pose.mirror_mouth!,
    dimensions: dimensions,
    placeableParts: new Map(placeableParts),
    character: character,
  };
  return frame;
}
async function overlayImage(base: Jimp, top: Jimp, x: number, y: number) {
  base.composite(top, x, y);
}

async function generateFrame(frame: FrameRequest) {
  let face = await Jimp.read(frame.face_path);
  face.scaleToFit(frame.dimensions[1], frame.dimensions[0]);

  let mouth = await Jimp.read(frame.mouth_path);
  mouth.scale(frame.mouth_scale);

  if (frame.mirror_face) {
    face = face.flip(true, false);
  }
  if (frame.mirror_mouth) {
    mouth = mouth.flip(true, false);
  }
  for (const [type, name] of frame.placeableParts) {
    let partData = frame.character[type];
    let basePath: string = partData.imagesFolder;
    let specPath = partData.images[name];

    let part = await Jimp.read(path.join(basePath, specPath));
    part.scale(partData.scale);

    let x: number = partData.x;
    let y: number = partData.y;
    overlayImage(face, part, x - part.getWidth() / 2, y - part.getHeight() / 2);
  }
  overlayImage(
    face,
    mouth,
    frame.mouth_x - mouth.getWidth() / 2,
    frame.mouth_y - mouth.getHeight() / 2
  );

  return face;
}

export async function combine_images(
  audio_path: string,
  output_path: string,
  num_images: number
) { //TODO: resolve promise
  await ffmpeg_loaded;
  ffmpeg.FS("writeFile", "audio.wav", await fetchFile(audio_path));
  await ffmpeg.run(
    "-framerate",
    "100",
    "-i",
    `%d.png`,
    "-i",
    `audio.wav`,
    "-c:v",
    "libx264",
    "-pix_fmt",
    "yuv420p",
    "out.mp4",
    "-y"
  );

  log("Finalizing Video...", 1)
  await fs.promises.writeFile(output_path, ffmpeg.FS("readFile", "out.mp4"));
  log('Video Out', 1)
}

export async function gen_image_sequence(video: VideoRequest) {
  await cleanGentle(video.gentle_stamps);

  let character = JSON.parse(readFileSync(video.characters_path).toString());

  if (!("default_scale" in character)) {
    character.default_scale = 1;
  }

  let phonemes: {
    closed: string;
    phonemes: any;
  } = JSON.parse(readFileSync(video.mouths_path).toString());

  let timestamp: Timestamp = {
    time: 0,
    pose_name: video.default_pose,
    type: "poses",
  };

  let placeableParts: Map<string, string> = new Map();

  for (const t of video.timestamps) {
    if (t.time <= 0) {
      if (t.type == "poses") {
        timestamp = t;
      } 
      else if (t.type == ' '){
        timestamp.time = t.time
        timestamp.pose_name = t.pose_name
      }
      else {
        placeableParts.set(t.type, t.pose_name);
        if (t.pose_name == "None") {
          placeableParts.delete(t.type);
        }
      }
    }
  }
  let pose = await getPose(timestamp.pose_name, character);


  if (video.dimensions[0] == 0) {
    video.dimensions = (await getDimensions(pose.image)) as number[];
  }

  let currentTime = 0;
  let frame_request_promises: Promise<FrameRequest>[] = [];


  ///////////////////////////
  // Create Frame Requests //
  ///////////////////////////
  for (const word of video.gentle_stamps.words) {
    if (word.case != "success") {
      log('Warning: Found an unaligned word', 1)
      continue
    };
    // Rest Frames //
    let mouth_path = path.join(character.mouthsPath, phonemes.closed);
    let duration = Math.round(100 * (word.start - currentTime)) / 100;
    if (duration > 0) {
      currentTime += duration;
    }

    let frame = createFrameRequest(
      pose,
      video.dimensions,
      duration,
      mouth_path,
      placeableParts,
      character
    );
    frame_request_promises.push(frame);

    // Swap pose //
    for (const t of video.timestamps) {
      if (t.time <= currentTime * 1000) {
        if (t.type == "poses") {
          timestamp = t;
        } else {
          placeableParts.set(t.type, t.pose_name);
          if (t.pose_name == "None") {
            placeableParts.delete(t.type);
          }
        }
      }
    }
    pose = await getPose(timestamp.pose_name, character);
    // Talking Frames //
    for (const p of word.phones) {
      p.phone = p.phone.split("_")[0];
      p.duration = Math.round(100 * p.duration) / 100;

      mouth_path = path.join(
        character.mouthsPath,
        phonemes.phonemes[p.phone].image
      );
      let frame = createFrameRequest(
        pose,
        video.dimensions,
        p.duration,
        mouth_path,
        placeableParts,
        character
      );
      currentTime += p.duration;

      frame_request_promises.push(frame);
    }
  }
  // Final closed frame
  let time_remaining = Math.max(video.duration - currentTime, 0.01);
  let frame = createFrameRequest(
    pose,
    video.dimensions,
    time_remaining,
    path.join(character.mouthsPath, phonemes.closed),
    placeableParts,
    character
  );
  currentTime += 0.1;
  frame_request_promises.push(frame);

  /////////////////////////////
  // Render and Write Frames //
  /////////////////////////////

  let frame_requests = await Promise.all(frame_request_promises);
  let frame_counter = 0;
  await ffmpeg_loaded;

  let frames: Promise<void>[] = [];
  for (const frame_request of frame_requests) {
    let frame_promise = writeFrame(frame_request, frame_counter);
    frames.push(frame_promise);
    frame_counter += Math.round(frame_request.duration * 100);
  }
  await Promise.all(frames);

  return frame_counter;
}

async function writeFrame(frame_request: FrameRequest, frame_counter: number) {
  let rendered = await generateFrame(frame_request);
  let buffer = await rendered.getBufferAsync(Jimp.MIME_PNG);

  for (let i = 0; i < Math.round(frame_request.duration * 100); i++) {
    ffmpeg.FS("writeFile", `${frame_counter + i}.png`, buffer);
  }
}

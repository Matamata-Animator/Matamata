import { readFileSync } from "fs";
import { json } from "stream/consumers";
import { boolean } from "yargs";
import { cleanGentle, GentleOut } from "./gentle";
import { Timestamp } from "./poseParser";
import Jimp from "jimp";
import { CurlVersionInfoNativeBindingObject } from "node-libcurl/dist/types";
import path from "path";
import { time } from "console";

import { GifUtil } from "gifwrap";

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
}
export interface VideoRequest {
  gentle_stamps: GentleOut;
  audio_path: string;

  mouths_path: string;
  characters_path: string;

  timestamps: Timestamp[];
  dimensions: number[];

  default_pose: string;
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
  if (!character.hasOwnProperty(pose_name)) {
    throw `Pose "${pose_name}" does not exist`;
  }
  let pose: Pose = JSON.parse(JSON.stringify(character[pose_name])); //creates an unlinked copy of pose

  let split = pose_name.split("-");
  let mirror = false;
  if (split.length == 2) {
    let left = split[1].toLowerCase() in ["l", "left"];
    mirror = !left == pose.facingLeft;
  }
  pose.mirror_face = mirror;
  let mirror_mouth = true;
  if (pose.facingLeft || (!pose.facingLeft && pose.mirror_face)) {
    mirror_mouth = true;
  }
  pose.mirror_mouth = mirror_mouth;

  pose.image = path.join(character.facesFolder ?? "", pose.image);

  if (!("scale" in pose)) {
    pose.scale = 1;
  }
  return pose;
}

async function createFrameRequest(
  pose: Pose,
  dimensions: number[],
  duration: number,
  mouth_path: string
) {
  let frame: FrameRequest = {
    face_path: pose.image,
    mouth_path: mouth_path,
    mouth_scale: pose.scale ?? 1,
    mouth_x: pose.x,
    mouth_y: pose.y,
    duration: duration,
    mirror_face: pose.mirror_face!,
    mirror_mouth: pose.mirror_mouth!,
    dimensions: dimensions,
  };
  return frame;
}

async function generateFrame(frame: FrameRequest) {
  let face = await Jimp.read(frame.face_path);
  face.scaleToFit(frame.dimensions[1], frame.dimensions[0]);

  let mouth = await Jimp.read(frame.mouth_path);
  mouth.scale(frame.mouth_scale);

  face.composite(
    mouth,
    frame.mouth_x - mouth.getWidth() / 2,
    frame.mouth_y - mouth.getHeight() / 2
  );

  return face;
}

export async function gen_video(video: VideoRequest) {
  await cleanGentle(video.gentle_stamps);

  let character = JSON.parse(readFileSync(video.characters_path).toString());

  if (!("default_scale" in character)) {
    character.default_scale = 1;
  }

  let phonemes: {
    closed: string;
    phonemes: any;
    mouthsPath: any;
  } = JSON.parse(readFileSync(video.mouths_path).toString());

  let pose = await getPose(video.timestamps[0].pose_name, character);

  if (video.dimensions[0] == 0) {
    video.dimensions = (await getDimensions(pose.image)) as number[];
  }

  let currentTime = 0;
  let frame_request_promises: Promise<FrameRequest>[] = [];

  ///////////////////////////
  // Create Frame Requests //
  ///////////////////////////
  for (const word of video.gentle_stamps.words) {
    // Swap pose //
    let timestamp: Timestamp = { time: 0, pose_name: video.default_pose };
    for (const t of video.timestamps) {
      if (t.time <= currentTime) {
        timestamp = t;
      }
    }
    pose = await getPose(timestamp.pose_name, character);

    // Rest Frames //
    let mouth_path = path.join(phonemes.mouthsPath, phonemes.closed);
    let duration = Math.round(100 * (word.start - currentTime)) / 100;
    console.log(`Rest: ${duration}`);
    currentTime += duration;
    console.log(`Current Time: ${currentTime}`);

    let frame = createFrameRequest(
      pose,
      video.dimensions,
      duration,
      mouth_path
    );
    frame_request_promises.push(frame);

    // Talking Frames //
    for (const p of word.phones) {
      console.log(p);
      p.phone = p.phone.split("_")[0];
      p.duration = Math.round(100 * p.duration) / 100;
      mouth_path = path.join(
        phonemes.mouthsPath,
        phonemes.phonemes[p.phone].image
      );
      console.log(mouth_path);
      let frame = createFrameRequest(
        pose,
        video.dimensions,
        p.duration,
        mouth_path
      );
      currentTime += p.duration;

      frame_request_promises.push(frame);
    }
  }
  // Final closed frame
  let frame = createFrameRequest(
    pose,
    video.dimensions,
    0.01,
    path.join(phonemes.mouthsPath, phonemes.closed)
  );
  frame_request_promises.push(frame);

  ///////////////////
  // Create Frames //
  ///////////////////
  let frame_requests = await Promise.all(frame_request_promises);
  let frames_promises: Promise<Jimp>[] = [];
  for (const frame_request of frame_requests) {
    let frame = generateFrame(frame_request);
    for (let i = 0; i < frame_request.duration * 100; i++) {
      frames_promises.push(frame);
    }
  }

  let frames = await Promise.all(frames_promises);

  ////////////////////////////
  // Write Frames to Folder //
  ////////////////////////////
  frames.forEach((frame, counter) => {
    frame.quality(100).write(`generate/${counter}.png`);
  });
  // frames[0].quality(100).write(`generate/${0}.png`);
  // console.log(frames[0].bitmap.);
}

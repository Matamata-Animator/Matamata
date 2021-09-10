import { readFileSync } from "fs";
import { json } from "stream/consumers";
import { boolean } from "yargs";
import { cleanGentle, GentleOut } from "./gentle";
import { Timestamp } from "./poseParser";
import Jimp from "jimp";
import { CurlVersionInfoNativeBindingObject } from "node-libcurl/dist/types";
import path from "path";
import { time } from "console";
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
  phonemes: any,
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

export async function gen_video(video: VideoRequest) {
  await cleanGentle(video.gentle_stamps);

  let character = JSON.parse(readFileSync(video.characters_path).toString());

  if (!("default_scale" in character)) {
    character.default_scale = 1;
  }

  let phonemes = JSON.parse(readFileSync(video.mouths_path).toString());

  let frame_counter = 0;

  let pose = await getPose(video.timestamps[0].pose_name, character);

  if (video.dimensions[0] == 0) {
    video.dimensions = (await getDimensions(pose.image)) as number[];
  }

  // let frame = await createFrameRequest(pose, phonemes, video.dimensions);

  let currentTime = 0;
  let framePromises: Promise<FrameRequest>[] = [];

  for (const word of video.gentle_stamps.words) {
    ///////////////
    // Swap pose //
    ///////////////
    let timestamp: Timestamp = { time: 0, pose_name: video.default_pose };
    for (const t of video.timestamps) {
      if (t.time <= currentTime) {
        timestamp = t;
      }
    }
    pose = await getPose(timestamp.pose_name, character);

    /////////////////
    // Rest Frames //
    /////////////////
    let duration = word.start - currentTime;
    currentTime += duration;
    let frame = createFrameRequest(
      pose,
      phonemes,
      video.dimensions,
      duration,
      phonemes["closed"]
    );
    framePromises.push(frame);
  }

  ////////////////////
  // Talking Frames //
  ////////////////////
}

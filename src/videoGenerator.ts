import { readFileSync } from "fs";
import { json } from "stream/consumers";
import { boolean } from "yargs";
import { GentleOut } from "./gentle";
import { Timestamp } from "./poseParser";
import Jimp from "jimp";
import { CurlVersionInfoNativeBindingObject } from "node-libcurl/dist/types";
import path from "path";
interface FrameRequest {
  face_path: string;
  mouth_path: string;
  mouth_scale: string;
  mouth_x: number;
  mouth_y: number;
  duration: number;
  mirror_face: boolean;
  mirror_mouth: boolean;
  frame: number;
  folder_name: string;
  dimensions: number[];
}
export interface VideoRequest {
  gentle_stamps: GentleOut;
  audio_path: string;

  mouths_path: string;
  characters_path: string;

  timestamps: Timestamp[];

  dimensions?: number[];
}
interface Pose {
  image: string;
  x: number;
  y: number;
  facingLeft?: boolean;
  scale?: number;
  mirror?: boolean;
}

async function getDimensions(image_path: string) {
  console.log(image_path);
  let image = await Jimp.read(image_path);
  console.log(`Image: ${image}`);
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
  pose.mirror = mirror;

  pose.image = path.join(character.facesFolder ?? "", pose.image);

  if (!("scale" in pose)) {
    pose.scale = 1;
  }
  return pose;
}

export async function gen_video(video: VideoRequest) {
  let character = JSON.parse(readFileSync(video.characters_path).toString());

  if (!("default_scale" in character)) {
    character.default_scale = 1;
  }

  let phonemes = JSON.parse(readFileSync(video.mouths_path).toString());
  console.log(character);

  let frame_counter = 0;

  let pose = await getPose(video.timestamps[0].pose_name, character);

  if (video.dimensions![0] == 0) {
    video.dimensions = await getDimensions(pose.image);
  }
  console.log(`Dimensions: ${video.dimensions}`);
}

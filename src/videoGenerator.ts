import { GentleOut } from "./gentle";
import { Timestamp } from "./poseParser";

export interface VideoRequest {
  gentle_stamps: GentleOut;
  audio_path: string;

  mouths_path: string;
  characters_path: string;

  timestamps: Timestamp[];
}

export async function gen_video(req: VideoRequest) {}

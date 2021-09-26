import fs from "fs";
import { Readable } from "stream";
import wav from "wav";
import { join } from "path";
import { execSync } from "child_process";

interface VoskTimestamp {
  start: number;
  end: number;
  word: string;
}
interface VoskOut {
  confidence: number;
  result: VoskTimestamp[];
  text: string;
}

export async function getTranscribedText(
  audio_path: string,
  model_path: string
): Promise<string> {
  return await (
    await transcribeAudio(audio_path, model_path)
  ).text;
}
export async function transcribeAudio(
  audio_path: string,
  model_path: string
): Promise<VoskOut> {
  let transcription = JSON.parse(
    execSync(`python3 transcribe.py ${audio_path} ${model_path}`).toString()
  );

  return transcription;
}

if (require.main === module) {
  transcribeAudio("/Users/human/Desktop/test.wav", "model").then((t: any) =>
    console.log(t)
  );
}

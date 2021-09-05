import { readFile } from "fs/promises";
export interface Timestamp {
  time: number;
  pose_name: string;
}

export async function parseTimestamps(text: string) {
  let wholefile = (await readFile(text)).toString();
  wholefile = wholefile.replace(/\r/g, "\n");
  let lines = wholefile.split("\n");

  lines = lines.filter((line) => line != "");

  let timestamps: Timestamp[] = [];

  for (const line of lines) {
    let s = line.split(" ");
    timestamps.push({
      time: Number(s[0]),
      pose_name: s[1],
    });
  }

  return timestamps;
}

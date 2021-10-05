import { readFile } from "fs/promises";
export interface Timestamp {
  time: number;
  type: string;
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

    let time = Number(s[0]);

    let name = s[1];
    let type = "poses";

    if (s.length >= 3) {
      type = s[2];
    }

    timestamps.push({
      time: time,
      pose_name: name,
      type: type,
    });
  }
  console.log(timestamps);
  return timestamps;
}

import { terminal } from "terminal-kit";
import { createWriteStream } from "fs";
export const gentle_log = createWriteStream("gentle.log");

var figlet = require("figlet");
let verboseLevel: number = 1;

export function setVerbose(level: number) {
  verboseLevel = level;
}
export async function banner() {
  let bannerDone = new Promise((resolve, reject) => {
    figlet("Matamata", function (err: string, data: string) {
      if (err) {
        console.log("Something went wrong...");
        console.dir(err);
        reject(1);
        return;
      }
      if (verboseLevel >= 1) {
        terminal.green(
          `${data}\n Version ${process.env.npm_package_version}\n`
        );
      }
      resolve(0);
    });
  });
  return bannerDone;
}

export function log(data: any, thresh: number) {
  if (verboseLevel >= thresh) {
    console.log(data);
  }
}

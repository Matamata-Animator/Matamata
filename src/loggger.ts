var figlet = require("figlet");
let verboseLevel: number = 1;

export function setVerbose(level: number) {
  verboseLevel = level;
}
export function banner() {
  figlet("Matamata", function (err: string, data: string) {
    if (err) {
      console.log("Something went wrong...");
      console.dir(err);
      return;
    }
    if (verboseLevel >= 1) {
      console.log(`${data}\n Version ${process.env.npm_package_version}`);
    }
  });
}

export function log(data: any, thresh: number) {
  if (verboseLevel >= thresh) {
    console.log(data);
  }
}

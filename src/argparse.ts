import yargs from "yargs";
import { hideBin } from "yargs/helpers";

const default_args = require("../defaults/default_args.json");
var argv = yargs(hideBin(process.argv))
  .usage("Usage: $0 yarn animate [options]")
  .example(
    "$0 yarn animate --audio C:/Users/User/Desktop/myaudio",
    "Create a basic animation using the default character"
  )
  // .demandOption(['f'])
  .help("h")

  .alias("h", "help");

for (const option in default_args) {
  argv = argv.option(option, default_args[option]);
}
let args = argv.argv as unknown as Args;
export function getArgs() {
  return args;
}

export interface Args {
  audio: string;
  timestamps: string;
  text: string;
  output: string;
  character: string;
  mouths: string;
  dimensions: string;
  dimension_scaler: number;
  verbose: boolean;
  no_docker: boolean;
  codec: string;
  container_name: string;
}

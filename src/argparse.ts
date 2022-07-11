import { existsSync, fstat, readFileSync } from "fs";
import yargs from "yargs";
import { hideBin } from "yargs/helpers";

const default_args = require("../defaults/default_args.json");
var argv = yargs(hideBin(process.argv))
  .usage("Usage: $0 npm run animate [options]")
  .example(
    "$0 npm run animate --audio C:/Users/User/Desktop/myaudio",
    "Create a basic animation using the default character"
  )
  // .demandOption(['f'])
  .help("h")

  .alias("h", "help");

let config_path = "config.json";
let config: any = {};
if (existsSync(config_path)) {
  config = JSON.parse(readFileSync(config_path).toString());
}

for (const option in default_args) {
  if (option in config) {
    default_args[option].default = config[option];
    default_args[option].required = false;
  }
  argv = argv.option(option, default_args[option]);
}

export function getArgs() {
  let args = argv.argv as unknown as Args;

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
  verbose: number;
  no_docker: boolean;
  codec: string;
  container_name: string;
  image_name: string;
  vosk_model: string;
  default_pose: string;
  config: string;
  aligning_algorithm: "allosaurus" | "gentle";
}

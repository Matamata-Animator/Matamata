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
let args = argv.argv;
export function getArgs() {
  return args;
}

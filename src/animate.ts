import { getArgs } from "./argparse";
import { setVerbose, banner, log } from "./loggger";

import { removeOld, launchContainer } from "./docker";
const args = getArgs();

async function main() {
  setVerbose(args.verbose);
  await banner();
  log("Full Verbose", 2);

  await removeOld(args.container_name);

  console.log("reeeeeeeee");

  await launchContainer(args.container_name, args.image_name);
}
main();

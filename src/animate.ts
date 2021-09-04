import { getArgs } from "./argparse";
import { setVerbose, banner, log } from "./loggger";

import { removeOld, launchContainer } from "./docker";

const args = getArgs();
async function main() {
  setVerbose(args.verbose);
  await banner();
  log("Full Verbose", 2);

  await removeOld(args.container_name);

  await launchContainer(args.container_name, args.image_name);

  console.log("based");
}
main();

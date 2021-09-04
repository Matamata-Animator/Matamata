import { getArgs } from "./argparse";
import { setVerbose, banner, log } from "./loggger";

import { removeOld, launchContainer } from "./docker";
const args = getArgs();

setVerbose(args.verbose);
banner();
log("Full Verbose", 2);

removeOld(args.container_name);
launchContainer(args.container_name);

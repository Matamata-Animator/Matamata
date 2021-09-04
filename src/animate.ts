import { getArgs } from "./argparse";
import { setVerbose, banner, log } from "./loggger";
const args = getArgs();

setVerbose(args.verbose);
banner();
log("Full Verbose", 2);

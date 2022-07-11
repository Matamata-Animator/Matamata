// var Docker = require("dockerode");
import Docker from "dockerode";

import { gentle_log } from "./logger";

const docker = new Docker(); //defaults to above if env variables are not used

export async function removeOld(container_name: string) {
  let shouldLaunch = true;
  let containers = await docker.listContainers({ all: true });

  for (const container of containers) {
    if (container.Names.includes(`/${container_name}`)) {
      shouldLaunch = false;
      let old = docker.getContainer(container.Id);
      if (container.State != "running") {
        if (container.State != "exited") {
          await old.kill();
        }
        await old.remove();
        shouldLaunch = true;
      }
    }
  }
  return shouldLaunch;
}

export function launchContainer(container_name: string, image_name: string) {
  let gentleReady = new Promise<void>((resolve, reject) => {
    docker
      .run(
        image_name,
        [],
        gentle_log,
        {
          name: container_name,
          HostConfig: {
            PortBindings: {
              "8765/tcp": [{ HostPort: "8765" }],
            },
          },
        },
        () => {}
      )
      .on("container", () => {
        resolve();
      });
  });

  return gentleReady;
}

if (require.main === module) {
  launchContainer("gentle", "lowerquality/gentle");
}

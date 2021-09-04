// var Docker = require("dockerode");
import { rejects } from "assert";
import Docker from "dockerode";
import { resolve } from "path/posix";
import { log } from "./loggger";

var docker = new Docker({ port: 8765 }); //defaults to above if env variables are not used

async function findAndKill(
  container_name: string,
  containers: Docker.ContainerInfo[]
) {
  for (const containerInfo of containers) {
    if (containerInfo.Names.includes(`/${container_name}`)) {
      let c = docker.getContainer(containerInfo.Id);
      await c.stop();
      await c.remove();
    }
  }
}

export async function removeOld(container_name: string) {
  let containerKilled = new Promise((resolve, reject) => {
    docker.listContainers(
      async (err: any, containers: Docker.ContainerInfo[]) => {
        await findAndKill(container_name, containers);
        resolve(0);
      }
    );
  });
  return containerKilled;
}

async function pullIfMissing(image_name: string) {
  let imagePulled = new Promise(async (resolve, reject) => {
    const images = await docker.listImages();
    for (const img of images) {
      if (img.RepoTags.includes(image_name)) {
        log("Image Found", 3);
        resolve(0);
        return 0;
      }
    }
    log(
      "Image Missing. Pulling image form DockerHub. This may take a while...",
      1
    );

    await docker.pull(image_name, function (err: any, stream: any) {
      docker.modem.followProgress(stream, onFinished, onProgress);

      function onFinished(err: any, output: any) {
        resolve(100);
      }
      function onProgress(event: any) {}
    });
  });
  return imagePulled;
}

export async function launchContainer(
  container_name: string,
  image_name: string
) {
  let pull = await pullIfMissing(image_name);
  if (pull == 100) {
    log("Pull Complete", 1);
  }

  await docker.run(
    image_name,
    [],
    process.stdout, //TODO: change this to empty writeable stream
    { name: container_name },
    function (err: any, data: any, container: any) {
      // Do stuff
    }
  );
}

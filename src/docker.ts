// var Docker = require("dockerode");
import { rejects } from "assert";
import Docker from "dockerode";
import { log } from "./loggger";

var docker = new Docker(); //defaults to above if env variables are not used
export async function removeOld(container_name: string) {}

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

    await docker.pull(
      "lowerquality/gentle:latest",
      function (err: any, stream: any) {
        docker.modem.followProgress(stream, onFinished, onProgress);

        function onFinished(err: any, output: any) {
          resolve(100);
        }
        function onProgress(event: any) {}
      }
    );
  });
  return imagePulled;
}

export async function launchContainer(container_name: string) {
  let pull = await pullIfMissing("lowerquality/gentle:latest");
  if (pull == 100) {
    log("Pull Complete", 1);
  }
  //   docker.run(
  //     "lowerquality/gentle",
  //     ["bash", "-c", "uname -a"],
  //     process.stdout,
  //     function (err: any, data: any, container: any) {
  //       //   console.log(data.StatusCode);
  //     }
  //   );
}

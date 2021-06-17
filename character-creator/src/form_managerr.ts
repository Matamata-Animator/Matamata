//@ts-nocheck
interface Pose {
  image: string;
  x: number;
  y: number;
  scale?: number;
}

function addPose() {
  if (!character) {
    alert("Please upload a pose image");
  }
  if (!json) {
    alert("Please upload a characters.json");
  }
  let gc: Map<string, number> = new Map();
  var x = document.getElementById("form").elements;
  for (const i of x) {
    gc.set(i.name, i.value);
  }

  let pose: Pose = {
    image: img_name,
    x: mouth_pos[0],
    y: mouth_pos[1],
    scale: mScale,
  };
  json["facesFolder"] = gc.get("facesFolder");

  json[gc.get("pose_name")] = pose;
}

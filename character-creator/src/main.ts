let dropzone: p5.Element;
let mdrop: p5.Element;

let cnv: p5.Renderer;
let json_made: boolean = false;

let border = 10;

let mouse_down = false;
let character: any;
let img_name: string;
let json_name: string = "characters.json";
let json: any = {};

let mouth_pos: [number, number] = [0, 0];

let mouth_image: any;
let mScale: number = 1;
function setup() {
  cnv = createCanvas(0, 0);
  cnv.parent("canvas");

  stroke(0);
  strokeWeight(1);

  //@ts-ignore
  dropzone = select("#dropzone");
  dropzone.dragOver(highlight);
  dropzone.dragLeave(unhighlight);
  dropzone.drop(gotFile, unhighlight);

  //@ts-ignore
  mdrop = select("#mdrop");
  mdrop.dragOver(mhighlight);
  mdrop.dragLeave(munhighlight);
  mdrop.drop(mgotFile, unhighlight);
  rectMode(CENTER);

  mouth_image = loadImage("mouths/Adown.png");
  // alert("If you upload an image and it does not properly display, upload it again.");
}

function draw() {
  if (character) {
    fill(200, 0, 0);
    rect(0, 0, width * 2, height * 2);
    image(character, border, border);

    target(mouth_pos[0], mouth_pos[1]);
  }

  if (mouse_down && hovering()) {
    mouth_pos = [mouseX, mouseY];
  }
}
function gotFile(file: p5.File) {
  if (file.type === "image") {
    img_name = file.name;
    character = createImg(file.data);
    character.hide();
    background(0);
    cnv = createCanvas(
      character.width + 2 * border,
      character.height + 2 * border
    );
    cnv.parent("canvas");
  } else if (file.type === "application" /*json*/ && !json_made) {
    json = file.data;
    json_name = file.name;

    json_made = true;

    //set form values
    let gc: Map<string, number> = new Map();
    //@ts-ignore
    var x = document.getElementById("form").elements;
    for (const i of x) {
      if (i.name == "facesFolder") {
        i.value = json.facesFolder;
        alert("JSON Loaded Successfully");
      }
    }
  }
}
function mgotFile(file: p5.File) {
  if (file.type === "image") {
    mouth_image = createImg(file.data);
    mouth_image.hide();
  }
}

function mousePressed() {
  mouse_down = true;
}
function mouseReleased() {
  mouse_down = false;
}
function target(x: number, y: number) {
  imageMode(CENTER);
  image(
    mouth_image,
    x,
    y,
    mouth_image.width * mScale,
    mouth_image.height * mScale
  );
  imageMode(CORNER);
}

function highlight() {
  dropzone.style("background-color", "#ccc");
}

function unhighlight() {
  dropzone.style("background-color", "#fff");
}
function mhighlight() {
  mdrop.style("background-color", "#ccc");
}

function munhighlight() {
  mdrop.style("background-color", "#fff");
}
function hovering() {
  return (
    border < mouseX &&
    mouseX < width - border &&
    border < mouseY &&
    mouseY < height - border
  );
}
function mouseWheel(event: WheelEvent) {
  if (hovering()) {
    mScale -= event.deltaY / 1000;
  }
}

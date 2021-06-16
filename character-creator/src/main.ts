var dropzone: p5.Element;
let cnv: p5.Renderer;
var json_made: boolean = false;

let border = 10;

let character: any;
let img_name: string;
let json_name: string;
let json: any;

let mouth_pos: [number, number] = [0, 0];

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
  rectMode(CENTER);

  // alert("If you upload an image and it does not properly display, upload it again.");
}

function draw() {
  if (character) {
    fill(200, 0, 0);
    rect(0, 0, width * 2, height * 2);
    image(character, border, border);

    target(mouth_pos[0], mouth_pos[1]);
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
    if (json.facesFolder) {
      alert("JSON Loaded Successfully");
    }
    json_made = true;
  }
}

function highlight() {
  dropzone.style("background-color", "#ccc");
}

function unhighlight() {
  dropzone.style("background-color", "#fff");
}

function mousePressed() {
  if (
    border < mouseX &&
    mouseX < width - border &&
    border < mouseY &&
    mouseY < height - border
  ) {
    mouth_pos = [mouseX, mouseY];
  }
}

function target(x: number, y: number) {
  fill(0, 200, 0);
  rect(x, y, 40, 3);
  rect(x, y, 3, 20);
}

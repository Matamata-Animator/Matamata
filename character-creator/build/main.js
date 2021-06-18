"use strict";
function addPose() {
    if (!character) {
        alert("Please upload a pose image");
    }
    if (!json) {
        alert("Please upload a characters.json");
    }
    let gc = new Map();
    var x = document.getElementById("form").elements;
    for (const i of x) {
        gc.set(i.name, i.value);
    }
    let pose = {
        image: img_name,
        x: mouth_pos[0] - border,
        y: mouth_pos[1] - border,
        scale: int(mScale.value()) / 100,
        facingRight: !mirror_mouth,
    };
    if (gc.get("closed_mouth") + "") {
        pose["closed_mouth"] = gc.get("closed_mouth");
    }
    json["facesFolder"] = gc.get("facesFolder");
    json[gc.get("pose_name")] = pose;
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
    return (border < mouseX &&
        mouseX < width - border &&
        border < mouseY &&
        mouseY < height - border);
}
function mouseWheel(event) {
    if (hovering()) {
        mScale.value(int(mScale.value()) - event.deltaY / 10);
    }
}
function mousePressed() {
    mouse_down = true;
}
function mouseReleased() {
    mouse_down = false;
}
let dropzone;
let mdrop;
let cnv;
let json_made = false;
let border = 10;
let mouse_down = false;
let character;
let img_name;
let json_name = "characters.json";
let json = {};
let mouth_pos = [0, 0];
let mouth_image;
let mirror_mouth = false;
let mScale;
function setup() {
    mScale = createSlider(1, 1000, 100);
    mScale.parent("canvas");
    cnv = createCanvas(0, 0);
    cnv.parent("canvas");
    stroke(0);
    strokeWeight(1);
    dropzone = select("#dropzone");
    dropzone.dragOver(highlight);
    dropzone.dragLeave(unhighlight);
    dropzone.drop(gotFile, unhighlight);
    mdrop = select("#mdrop");
    mdrop.dragOver(mhighlight);
    mdrop.dragLeave(munhighlight);
    mdrop.drop(mgotFile, unhighlight);
    rectMode(CENTER);
    mouth_image = loadImage("mouths/Adown.png");
}
function draw() {
    if (character) {
        fill(200, 0, 0);
        rect(0, 0, width * 2, height * 2);
        image(character, border, border);
        drawMouth(mouth_pos[0], mouth_pos[1]);
    }
    if (mouse_down && hovering()) {
        mouth_pos = [mouseX, mouseY];
    }
    var x = document.getElementById("form").elements;
    if (x["facingLeft"].checked != mirror_mouth) {
        mirror_mouth = !mirror_mouth;
    }
}
function gotFile(file) {
    if (file.type === "image") {
        img_name = file.name;
        character = createImg(file.data);
        character.hide();
        background(0);
        cnv = createCanvas(character.width + 2 * border, character.height + 2 * border);
        cnv.parent("canvas");
    }
    else if (file.type === "application" && !json_made) {
        json = file.data;
        json_name = file.name;
        json_made = true;
        let gc = new Map();
        var x = document.getElementById("form").elements;
        x["facesFolder"].value = json.facesFolder;
    }
}
function mgotFile(file) {
    if (file.type === "image") {
        mouth_image = createImg(file.data);
        mouth_image.hide();
    }
}
function drawMouth(x, y) {
    imageMode(CENTER);
    if (mirror_mouth) {
        push();
        scale(-1, 1);
        image(mouth_image, -x, y, (mouth_image.width * int(mScale.value())) / 100, (mouth_image.height * int(mScale.value())) / 100);
        pop();
    }
    else {
        image(mouth_image, x, y, (mouth_image.width * int(mScale.value())) / 100, (mouth_image.height * int(mScale.value())) / 100);
    }
    imageMode(CORNER);
}
//# sourceMappingURL=../src/src/main.js.map
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
        x: mouth_pos[0],
        y: mouth_pos[1],
    };
    json[gc.get("pose_name")] = pose;
}
var dropzone;
let cnv;
var json_made = false;
let border = 10;
let character;
let img_name;
let json_name;
let json;
let mouth_pos = [0, 0];
function setup() {
    cnv = createCanvas(0, 0);
    cnv.parent("canvas");
    stroke(0);
    strokeWeight(1);
    dropzone = select("#dropzone");
    dropzone.dragOver(highlight);
    dropzone.dragLeave(unhighlight);
    dropzone.drop(gotFile, unhighlight);
    rectMode(CENTER);
}
function draw() {
    if (character) {
        fill(200, 0, 0);
        rect(0, 0, width * 2, height * 2);
        image(character, border, border);
        target(mouth_pos[0], mouth_pos[1]);
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
    if (border < mouseX &&
        mouseX < width - border &&
        border < mouseY &&
        mouseY < height - border) {
        mouth_pos = [mouseX, mouseY];
    }
}
function target(x, y) {
    fill(0, 200, 0);
    rect(x, y, 40, 3);
    rect(x, y, 3, 20);
}
//# sourceMappingURL=../src/src/main.js.map
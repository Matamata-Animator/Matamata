var dropzone;
var img;
var char_made = false;
var cnv;
var border = 10;
function setup() {
    cnv = createCanvas(500, 500);
    background(0);
    dropzone = select("#dropzone");
    dropzone.dragOver(highlight);
    dropzone.dragLeave(unhighlight);
    dropzone.drop(gotFile, unhighlight);
}
function draw() {
    if (img) {
        fill(200, 0, 0);
        rect(0, 0, width, height);
        image(img, border, border);
        console.log(img.width);
    }
}
function gotFile(file) {
    img = createImg(file.data);
    img.hide();
    cnv = createCanvas(img.width + 2 * border, img.height + 2 * border);
}
function highlight() {
    dropzone.style("background-color", "#ccc");
}
function unhighlight() {
    dropzone.style("background-color", "#fff");
}
//# sourceMappingURL=../src/src/main.js.map
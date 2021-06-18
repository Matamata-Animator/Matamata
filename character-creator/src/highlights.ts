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
    mScale.value(int(mScale.value()) - event.deltaY / 10);
  }
}

function mousePressed() {
  mouse_down = true;
}
function mouseReleased() {
  mouse_down = false;
}

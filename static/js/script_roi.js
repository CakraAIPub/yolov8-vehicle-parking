var canvas = document.querySelector("canvas");
var context = canvas.getContext("2d");
var infoPoints = document.querySelector(".points-info");
var zoomWindow = document.querySelector(".zoom");
var clickPoints = [];
var drawingLine = false; // Menandakan apakah sedang menggambar garis sementara
var polygonCount = 0;
const coordPolygons = [];

canvas.addEventListener("click", handleCanvasClick);
canvas.addEventListener("mousemove", handleCanvasMouseMove);

function handleCanvasClick(evt) {
  const maxPolygons = parseInt(document.getElementById("number").value, 10); // Convert input value to an integer

  if (polygonCount < maxPolygons) {
    // Add the point to clickPoints directly, no need to use push.
    clickPoints.push([evt.offsetX, evt.offsetY]);
    drawDot(evt.offsetX, evt.offsetY); // Pass coordinates to drawDot

    if (clickPoints.length === 4) {
      // Here, we should push a copy of clickPoints to coordPolygons.
      coordPolygons.push([...clickPoints]);
      drawPoly(clickPoints);
      polygonCount++; // Increment polygon count
      if (polygonCount === maxPolygons) {
        canvas.removeEventListener("click", handleCanvasClick); // Remove the click event listener
      }
      // Clear clickPoints after adding to coordPolygons.
      clickPoints.length = 0;
    }

    if (coordPolygons.length === maxPolygons) {
      savePolygon(coordPolygons);
    }
  }
}

function handleCanvasMouseMove(evt) {
  if (clickPoints.length > 0) {
    drawingLine = true;
    redrawCanvas();
    context.beginPath();
    context.moveTo(clickPoints[clickPoints.length - 1][0], clickPoints[clickPoints.length - 1][1]);
    context.lineTo(evt.offsetX, evt.offsetY);
    context.stroke();
  }
}

function redrawCanvas() {
  context.clearRect(0, 0, canvas.width, canvas.height);
  coordPolygons.forEach((polygon) => {
    drawPoly(polygon);
  });
  if (clickPoints.length > 0) {
    drawDot(clickPoints[clickPoints.length - 1][0], clickPoints[clickPoints.length - 1][1]);
  }
}

// draw polygon from a list of 4 points
const drawPoly = (points) => {
  context.lineWidth = 2;

  context.beginPath();
  context.moveTo(points[0][0], points[0][1]);
  for (let i = 1; i < points.length; i++) {
    context.lineTo(points[i][0], points[i][1]);
  }
  context.closePath(); // Menutup polygon
  context.stroke();
};

const savePolygon = (coordinates) => {
  var idUuidHolder = document.getElementById("idUuidHolder");
  var id_uuid = idUuidHolder.getAttribute("data-id_uuid");
  fetch(`/save_coordinates/${id_uuid}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ coordinates: coordinates })
  })
  .then(response => response.json())
  .then(data => {
    console.log(data.message);
  })
  .catch(error => {
    console.error('Error saving polygon:', error);
  });
};

// draw a dot.
const drawDot = (x, y) => {
  context.beginPath();
  context.arc(x, y, 2, 0, 2 * Math.PI);
  context.fill();
};

// resize the canvas for the image
const targetWidth = 1280;
const targetHeight = 720;
const resize = (x, y) => {
  canvas.height = targetHeight;
  canvas.width = targetWidth;
};

// load a new image
var rawImg = new Image();
const newImage = () => {
  var idUuidHolder = document.getElementById("idUuidHolder");
  var id_uuid = idUuidHolder.getAttribute("data-id_uuid");
  var src = `/get_image/${id_uuid}`;
  rawImg.src = src;
  rawImg.onload = () => {
    canvas.style.backgroundImage = "url(" + src + ")";
    zoomWindow.style.backgroundImage = "url(" + src + ")";
    resize(rawImg.width, rawImg.height);
  };
};

newImage();

// move the preview to the mouse
canvas.addEventListener("mousemove", (evt) => {
  drawZoom(evt.clientX, evt.clientY);
});

const drawZoom = (x, y) => {
  zoomWindow.style.backgroundPosition =
    (x / targetWidth) * 100 + "% " + (y / targetHeight) * 100 + "%";
};

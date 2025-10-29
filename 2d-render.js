const hull2DData = {
  sideProfile: [
    { x: 50, y: 100 }, { x: 100, y: 150 }, { x: 150, y: 130 },
    { x: 200, y: 160 }, { x: 250, y: 120 }, { x: 300, y: 100 }
  ],
  halfWidth: [
    { x: 50, y: 250 }, { x: 100, y: 300 }, { x: 150, y: 280 },
    { x: 200, y: 310 }, { x: 250, y: 270 }, { x: 300, y: 250 }
  ]
};

function init2DRender() {
  const canvas = document.getElementById('2d-view');
  const ctx = canvas.getContext('2d');
  
  function resizeCanvas() {
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    render2D();
  }
  resizeCanvas();
  window.addEventListener('resize', resizeCanvas);

  function render2D() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawLine(hull2DData.sideProfile, 'green', '侧面轮廓');
    drawLine(hull2DData.halfWidth, 'blue', '半宽图');
  }

  function drawLine(points, color, label) {
    if (points.length < 2) return;
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    points.forEach(p => ctx.lineTo(p.x, p.y));
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.fillStyle = color;
    ctx.font = '14px Arial';
    ctx.fillText(label, points[0].x, points[0].y - 10);
  }

  render2D();
  return { update: (newData) => { Object.assign(hull2DData, newData); render2D(); } };
}

const renderer2D = init2DRender();
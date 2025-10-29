
import * as THREE from 'three';

// ========== 1. 初始化场景、相机、渲染器 ==========
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('renderer-container').appendChild(renderer.domElement);

// 模拟 Hull3DWireframeData 数据（3D 线框顶点和索引）
const hull3DData = {
  vertices: [
    -1, -1, -1,
    1, -1, -1,
    1, 1, -1,
    -1, 1, -1,
    -1, -1, 1,
    1, -1, 1,
    1, 1, 1,
    -1, 1, 1,
  ],
  indices: [
    0, 1, 1, 2, 2, 3, 3, 0, // 前面
    4, 5, 5, 6, 6, 7, 7, 4, // 后面
    0, 4, 1, 5, 2, 6, 3, 7, // 侧面
  ],
};

// ========== 2. 3D 线框渲染函数 ==========
function render3DWireframe(data) {
  // 清除场景中原有内容
  scene.remove(...scene.children);

  // 提取顶点和索引
  const { vertices, indices } = data;
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));

  // 处理线段索引
  const lineIndices = [];
  for (let i = 0; i < indices.length; i += 2) {
    lineIndices.push(indices[i], indices[i + 1]);
  }
  geometry.setIndex(lineIndices);

  // 线框材质
  const material = new THREE.LineBasicMaterial({ color: 0x00ff00, linewidth: 2 });
  const wireframe = new THREE.LineSegments(geometry, material);
  scene.add(wireframe);

  // 相机位置
  camera.position.z = 5;
}

// ========== 3. 实时更新与交互联动 ==========
// 模拟数据更新（可替换为实际业务中接收数据的逻辑）
function onDataUpdate(newData) {
  render3DWireframe(newData);
  renderer.render(scene, camera);
}

// 初始渲染
render3DWireframe(hull3DData);

// 窗口 resize 适配
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.render(scene, camera);
});

// 动画循环（确保实时渲染）
function animate() {
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}
animate();

// 模拟交互修改（示例：2秒后更新线框颜色）
setTimeout(() => {
  hull3DData.indices = [
    0, 2, 2, 1, 1, 3, 3, 0, // 前面（索引顺序修改）
    4, 6, 6, 5, 5, 7, 7, 4, // 后面（索引顺序修改）
    0, 5, 1, 4, 2, 7, 3, 6, // 侧面（索引顺序修改）
  ];
  onDataUpdate(hull3DData);
}, 2000);
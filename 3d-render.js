document.addEventListener('DOMContentLoaded', () => {
  // 关键修复：将OrbitControls绑定到THREE对象
  THREE.OrbitControls = OrbitControls;

  // 3D线框数据
  const hull3DData = {
    vertices: [
      -5, -3, -3,   5, -3, -3,   5, 3, -3,  -5, 3, -3,  // 前面
      -5, -3, 3,    5, -3, 3,    5, 3, 3,   -5, 3, 3     // 后面
    ],
    indices: [
      0,1, 1,2, 2,3, 3,0, // 前面
      4,5, 5,6, 6,7, 7,4, // 后面
      0,4, 1,5, 2,6, 3,7  // 侧面
    ]
  };

  function init3DRender() {
    const container = document.getElementById('3d-view');
    const scene = new THREE.Scene();

    // 相机
    const camera = new THREE.PerspectiveCamera(
      75,
      container.offsetWidth / container.offsetHeight,
      0.1,
      1000
    );
    camera.position.z = 15; // 拉远相机，确保模型在视野内

    // 渲染器
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.offsetWidth, container.offsetHeight);
    container.appendChild(renderer.domElement);

    // 轨道控制器（已修复绑定问题）
    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.1;

    // 网格辅助线
    const gridHelper = new THREE.GridHelper(20, 20);
    scene.add(gridHelper);

    // 渲染3D模型
    function render3D(data) {
      scene.remove(...scene.children.filter(child => child.type === 'LineSegments'));
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute('position', new THREE.Float32BufferAttribute(data.vertices, 3));
      geometry.setIndex(data.indices);
      const material = new THREE.LineBasicMaterial({ color: 0xff0000, linewidth: 2 });
      const wireframe = new THREE.LineSegments(geometry, material);
      scene.add(wireframe);
    }

    // 动画循环
    function animate() {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    }
    animate();

    // 窗口 resize 适配
    window.addEventListener('resize', () => {
      const width = container.offsetWidth;
      const height = container.offsetHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    });

    render3D(hull3DData);
    return { update: (newData) => render3D(newData) };
  }

  const renderer3D = init3DRender();

  // 模拟实时更新
  setTimeout(() => {
    const newData = JSON.parse(JSON.stringify(hull3DData));
    newData.vertices[1] = -1; // 修改顶点
    renderer3D.update(newData);
  }, 3000);
});
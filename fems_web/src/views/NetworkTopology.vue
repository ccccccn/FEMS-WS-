<template>
  <div class="digital-twin">
    <div ref="sceneContainer" class="scene-container"></div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const sceneContainer = ref(null);

onMounted(() => {
  // 创建场景
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0d0d0d);

  // 创建相机
  const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.set(0, 2, 5);

  // 创建渲染器
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  sceneContainer.value.appendChild(renderer.domElement);

  // 添加轨道控制
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;

  // 添加环境光
  const ambientLight = new THREE.AmbientLight(0x404040, 2);
  scene.add(ambientLight);

  // 添加点光源
  const pointLight = new THREE.PointLight(0xffffff, 1);
  pointLight.position.set(5, 5, 5);
  scene.add(pointLight);

  // 添加立方体
  const cubeGeometry = new THREE.BoxGeometry();
  const cubeMaterial = new THREE.MeshStandardMaterial({ color: 0x00ff00, metalness: 0.5, roughness: 0.1 });
  const cube = new THREE.Mesh(cubeGeometry, cubeMaterial);
  scene.add(cube);

  // 添加地板
  const planeGeometry = new THREE.PlaneGeometry(100, 100);
  const planeMaterial = new THREE.ShadowMaterial({ opacity: 0.2 });
  const plane = new THREE.Mesh(planeGeometry, planeMaterial);
  plane.rotation.x = -Math.PI / 2;
  plane.position.y = -1;
  scene.add(plane);

  // 添加粒子效果
  const particlesGeometry = new THREE.BufferGeometry();
  const particlesCount = 1000;
  const posArray = new Float32Array(particlesCount * 3);

  for (let i = 0; i < particlesCount * 3; i++) {
    posArray[i] = (Math.random() - 0.5) * 20;
  }

  particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));

  const particlesMaterial = new THREE.PointsMaterial({
    size: 0.05,
    color: 0xffffff,
  });

  const particles = new THREE.Points(particlesGeometry, particlesMaterial);
  scene.add(particles);

  // 动画循环
  const animate = function () {
    requestAnimationFrame(animate);

    cube.rotation.x += 0.01;
    cube.rotation.y += 0.01;

    controls.update();
    renderer.render(scene, camera);
  };

  animate();

  // 处理窗口大小调整
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
});
</script>

<style scoped>
.digital-twin {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.scene-container {
  width: 100%;
  height: 100%;
}
</style> 
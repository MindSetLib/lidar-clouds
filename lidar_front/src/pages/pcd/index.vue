<template>
  <div>
    <div
      class="loading-snackbar"
      style="position: fixed; left: 50%; top: 20px; transform: translateX(-50%)"
    >
      Вы можете посмотреть исходный файл, пока идет обработка
    </div>
    <div id="container"></div>
    <input
      v-if="!processing"
      style="
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
      "
      type="file"
      @change="upload"
    />
    <div
      v-if="uploading"
      class="loading-snackbar"
      style="
        width: fit-content;
        position: fixed;
        right: 20px;
        bottom: 20px;
        z-index: 50;
      "
    >
      Загружаем файл на сервер
    </div>
    <div
      v-if="processing && !uploading"
      class="loading-snackbar"
      style="
        width: fit-content;
        position: fixed;
        right: 20px;
        bottom: 20px;
        z-index: 50;
      "
    >
      Идет обработка файла...
    </div>
    <button
      class="loading-snackbar"
      style="position: fixed; top: 20px; right: 20px; padding: 0px; display: flex; justify-content: center; align-items: center; width: 32px; height: 32px; border: none"
      :style="{
        backgroundColor: currentTheme === 'light' ? '#202020' : '#f0f0f0',
      }"
      @click="applyTheme()"
    >
      <svg
        v-show="currentTheme === 'light'"
        xmlns="http://www.w3.org/2000/svg"
        x="0px"
        y="0px"
        width="20"
        height="20"
        viewBox="0 0 30 30"
      >
        <path
          fill="#ffffff"
          d="M 14.984375 0.98632812 A 1.0001 1.0001 0 0 0 14 2 L 14 5 A 1.0001 1.0001 0 1 0 16 5 L 16 2 A 1.0001 1.0001 0 0 0 14.984375 0.98632812 z M 5.796875 4.7988281 A 1.0001 1.0001 0 0 0 5.1015625 6.515625 L 7.2226562 8.6367188 A 1.0001 1.0001 0 1 0 8.6367188 7.2226562 L 6.515625 5.1015625 A 1.0001 1.0001 0 0 0 5.796875 4.7988281 z M 24.171875 4.7988281 A 1.0001 1.0001 0 0 0 23.484375 5.1015625 L 21.363281 7.2226562 A 1.0001 1.0001 0 1 0 22.777344 8.6367188 L 24.898438 6.515625 A 1.0001 1.0001 0 0 0 24.171875 4.7988281 z M 15 8 A 7 7 0 0 0 8 15 A 7 7 0 0 0 15 22 A 7 7 0 0 0 22 15 A 7 7 0 0 0 15 8 z M 2 14 A 1.0001 1.0001 0 1 0 2 16 L 5 16 A 1.0001 1.0001 0 1 0 5 14 L 2 14 z M 25 14 A 1.0001 1.0001 0 1 0 25 16 L 28 16 A 1.0001 1.0001 0 1 0 28 14 L 25 14 z M 7.9101562 21.060547 A 1.0001 1.0001 0 0 0 7.2226562 21.363281 L 5.1015625 23.484375 A 1.0001 1.0001 0 1 0 6.515625 24.898438 L 8.6367188 22.777344 A 1.0001 1.0001 0 0 0 7.9101562 21.060547 z M 22.060547 21.060547 A 1.0001 1.0001 0 0 0 21.363281 22.777344 L 23.484375 24.898438 A 1.0001 1.0001 0 1 0 24.898438 23.484375 L 22.777344 21.363281 A 1.0001 1.0001 0 0 0 22.060547 21.060547 z M 14.984375 23.986328 A 1.0001 1.0001 0 0 0 14 25 L 14 28 A 1.0001 1.0001 0 1 0 16 28 L 16 25 A 1.0001 1.0001 0 0 0 14.984375 23.986328 z"
        ></path>
      </svg>
      <svg
        v-show="currentTheme === 'dark'"
        id="Layer_1"
        height="32"
        version="1.1"
        viewBox="0 0 512 512"
        width="32"
        xml:space="preserve"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M349.852,343.15c-49.875,49.916-131.083,49.916-181,0c-49.916-49.918-49.916-131.125,0-181.021  c13.209-13.187,29.312-23.25,47.832-29.812c5.834-2.042,12.293-0.562,16.625,3.792c4.376,4.375,5.855,10.833,3.793,16.625  c-12.542,35.375-4,73.666,22.25,99.917c26.209,26.228,64.5,34.75,99.916,22.25c5.792-2.062,12.271-0.582,16.625,3.793  c4.376,4.332,5.834,10.812,3.771,16.625C373.143,313.838,363.06,329.941,349.852,343.15z M191.477,184.754  c-37.438,37.438-37.438,98.354,0,135.771c40,40.021,108.125,36.416,143-8.168c-35.959,2.25-71.375-10.729-97.75-37.084  c-26.375-26.354-39.333-61.771-37.084-97.729C196.769,179.796,194.039,182.192,191.477,184.754z"
          fill="#1D1D1B"
        />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import axios from "axios";
import { ref } from "vue";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";
import { PCDLoader } from "three/examples/jsm/loaders/PCDLoader";
import { PointerLockControls } from 'three/examples/jsm/controls/PointerLockControls.js';
const axiosInstance = axios.create({});

const processing = ref<boolean>(false);
const uploading = ref<boolean>(false);
const currentTheme = ref<"light" | "dark">("dark");
const pointCloud = ref(null);

// === Темы ===
const themes = {
  light: {
    background: 0xf0f0f0,
    points: 0x111111,
    button: "Тёмная тема",
  },
  dark: {
    background: 0x202020,
    points: 0xffffff,
    button: "Светлая тема",
  },
};

function applyTheme() {
  const theme = (currentTheme.value =
    currentTheme.value === "light" ? "dark" : "light");
  scene.background = new THREE.Color(themes[theme].background);
  if (pointCloud.value) {
    pointCloud.value?.material.color.set(themes[theme].points);
  }
}

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x111111);
scene.background = new THREE.Color(0x202020);

const camera = new THREE.PerspectiveCamera(
  60,
  window.innerWidth / window.innerHeight,
  0.1,
  1000,
);
camera.position.set(0, 0, 5);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.domElement.style.position = "fixed";
renderer.domElement.style.top = "0";
renderer.domElement.style.left = "0";

const controls = new OrbitControls(camera, renderer.domElement);
scene.rotation.order = "YXZ"; // порядок вращений
scene.rotation.x = -Math.PI / 2; // повернули облако, ось Z стала вверх

// === Добавим BBoxes ===
// функция для добавления бокса по координатам
function addBBox(center, size, color = 0xff0000) {
  const geometry = new THREE.BoxGeometry(size[0], size[1], size[2]);
  const edges = new THREE.EdgesGeometry(geometry);
  const material = new THREE.LineBasicMaterial({ color: color });
  const box = new THREE.LineSegments(edges, material);
  box.position.set(center[0], center[1], center[2]);
  scene.add(box);
}

// === Загружаем PCD ===
const loader = new PCDLoader();

const uploadPCD = async (file) => {
  const formData = new FormData();

  if (file instanceof File) {
    formData.append("file", file);
  }

  const { data } = await axiosInstance.post(
    "http://78.136.221.218:40023/api/upload_pcd",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress: function (progressEvent) {
        console.log(progressEvent);
      },
    },
  );
  return data || null;
};

const upload = async (f) => {
  const urlObject = URL.createObjectURL(f.target.files[0]);
  uploading.value = true;
  uploadPCD(f.target.files[0])
    .then((data) => console.log(data))
    .finally(() => {
      uploading.value = false;
      processing.value = true;
      console.log("finally");
    });
  loader.load(urlObject, function (points) {
    document.getElementById("container").appendChild(renderer.domElement);
    points.material.size = 0.1; // крупнее точки
    points.material.color.set(0xffffff);
    // points.material.color.set(0x111111);
    scene.add(points);
    pointCloud.value = points;

    // 1) получаем Box3 и центр/размер
    const box = new THREE.Box3().setFromObject(points);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());

    // 2) визуализируем его с помощью Box3Helper
    const boxHelper = new THREE.Box3Helper(box, 0x00ff00); // цвет зелёный
    scene.add(boxHelper);

    // 2) радиус "окружающей" сферы (диагональ/2) — надёжный для всех форм
    const radius = size.length() * 0.5;

    // 3) вычисляем вертикальный и горизонтальный FOV (в радианах)
    const vFOV = THREE.MathUtils.degToRad(camera.fov);
    const aspect = camera.aspect;
    const hFOV = 2 * Math.atan(Math.tan(vFOV / 2) * aspect);

    // 4) находим минимальную дистанцию, чтобы сфера влезла по высоте и ширине
    const distanceV = radius / Math.sin(vFOV / 2);
    const distanceH = radius / Math.sin(hFOV / 2);
    let distance = Math.max(distanceV, distanceH);

    // немного отдалим, чтобы объект не упёрся в края
    distance *= 1.15;

    // 5) направление, в котором сейчас «смотрит» камера (чтобы не менять ориентацию)
    let dir = new THREE.Vector3();
    if (controls && controls.target) {
      dir.copy(camera.position).sub(controls.target).normalize();
    } else {
      dir.copy(camera.position).sub(center).normalize();
    }
    // если dir нулевой (камера в центре), поставим вдоль Z
    if (dir.length() < 1e-6) dir.set(0, 0, 1);

    // 6) ставим позицию камеры, обновляем проекцию и controls
    camera.position.copy(center.clone().add(dir.multiplyScalar(distance)));
    camera.up.set(0, 1, 0); // стандартно
    camera.lookAt(center);

    camera.near = Math.max(0.001, distance * 0.001);
    camera.far = Math.max(1000, distance * 10);
    camera.updateProjectionMatrix();

    if (controls) {
      controls.target.copy(center);
      controls.update();
    }

    // 7) --- debug helpers (раскомментируй, если нужно посмотреть bbox/центр) ---
    // const boxHelper = new THREE.BoxHelper(points, 0xff0000); scene.add(boxHelper); boxHelper.update();
    // const centerMesh = new THREE.Mesh(new THREE.SphereGeometry(radius*0.03,8,8), new THREE.MeshBasicMaterial({color:0x00ff00})); centerMesh.position.copy(center); scene.add(centerMesh);

    // Выведем в консоль для диагностики
    console.log(
      "PCD center:",
      center,
      "size:",
      size,
      "radius:",
      radius,
      "camera distance:",
      distance,
    );
    addBBox([0, 0, 0], [1, 1, 1], 0x00ff00);
  });
};

// Пример: бокс в центре облака
// addBBox([0,0,0], [1,1,1], 0x00ff00);

// Скорость движения
const moveSpeed = 1;
const keys = {};

// обработка нажатий
document.addEventListener("keydown", (e) => { keys[e.code] = true; });
document.addEventListener("keyup", (e) => { keys[e.code] = false; });

function updateMovement() {
  const dir = new THREE.Vector3();
  camera.getWorldDirection(dir);
  dir.y = 0; // чтобы не улетать вверх/вниз

  if (keys["KeyW"]) {
    camera.position.addScaledVector(dir, moveSpeed);
    controls.target.addScaledVector(dir, moveSpeed); // двигаем и target
  }
  if (keys["KeyS"]) {
    camera.position.addScaledVector(dir, -moveSpeed);
    controls.target.addScaledVector(dir, -moveSpeed);
  }
  if (keys["KeyA"]) {
    const left = new THREE.Vector3().crossVectors(camera.up, dir).normalize();
    camera.position.addScaledVector(left, moveSpeed);
    controls.target.addScaledVector(left, moveSpeed);
  }
  if (keys["KeyD"]) {
    const right = new THREE.Vector3().crossVectors(dir, camera.up).normalize();
    camera.position.addScaledVector(right, moveSpeed);
    controls.target.addScaledVector(right, moveSpeed);
  }
}

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

function animate() {
  requestAnimationFrame(animate);
  updateMovement();
  renderer.render(scene, camera);
}
animate();
</script>
<style>
.loading-snackbar {
  background-color: #3a3434;
  color: #faf1e9;
  font-family: Gordita, sans-serif;
  font-size: 16px;
  font-style: normal;
  font-weight: 500;
  line-height: 20px;
  text-align: center;
  padding: 10px;
  border-radius: 6px;
  z-index: 1000;
  display: flex;
  gap: 4px;
  justify-content: end;
}
</style>

<template>
  <div style="width: 100vw; height: 100vh; background: #202020">
    <div
        v-show="(uploading || processing || renderingUpload) && !done && !error"
        class="loading-snackbar"
        style="position: fixed; left: 50%; top: 20px; transform: translateX(-50%)"
    >
      Вы можете посмотреть исходный файл, пока идет обработка
    </div>
    <div id="container"></div>
    <div
        v-show="!processing && !uploading && !error && !lockFileUpload"
        style="
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 320px;
      "
    >
      <UiFileField @change="upload" />
      <div
          v-if="localPCDList && Object.keys(localPCDList).length"
          style="
          margin-top: 10px;
          border-radius: 0.5rem;
          cursor: pointer;
          background-color: #191919;
          padding: 10px;
        "
      >
        <div style="color: white; font-size: 12px">
          <div>Ранее загруженные файлы:</div>
          <div style="color: rgb(159 168 186); margin-top: 10px">
            <div v-for="item in localPCDList">
              <ui-badge
                  :color="
                  item?.status?.status === 'ready' ? 'success' : 'warning'
                "
                  @click="() => item?.uid && loadById(item?.uid)"
              >{{ item?.status?.src_filename }}</ui-badge
              >
            </div>
          </div>
        </div>
      </div>
    </div>
    <UiBadge
        v-show="uploading"
        color="warning"
        style="
        width: fit-content;
        position: fixed;
        top: 72px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 50;
      "
    >
      Загружаем файл на сервер: {{ loadingPercent }}%
    </UiBadge>
    <UiBadge
        v-show="renderingUpload"
        color="warning"
        style="
        width: fit-content;
        position: fixed;
        top: 72px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 50;
      "
    >
      Загружаем файл для отображения: {{ loadingForRepresentPercent }}%
    </UiBadge>
    <UiBadge
        v-show="processing && !uploading && !renderingUpload"
        color="warning"
        style="
        width: fit-content;
        position: fixed;
        top: 72px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 50;
      "
    >
      Идет обработка файла...
    </UiBadge>

    <UiBadge
        v-show="done && !renderingUpload"
        color="success"
        style="
        width: fit-content;
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 50;
        font-size: 14px;
        padding: 8px;
      "
    >
      Готово! Теперь вы работаете с обработанным файлом
    </UiBadge>
    <UiBadge
        v-show="error"
        color="error"
        style="
        width: fit-content;
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 50;
        font-size: 14px;
        padding: 8px;
      "
    >
      Ошибка обработки файла
    </UiBadge>
    <div
        style="
        position: fixed;
        left: 50%;
        bottom: 20px;
        transform: translateX(-50%);
        display: flex;
        gap: 10px;
        align-items: center;
      "
    >
      <button
          class="loading-snackbar"
          style="
          cursor: pointer;
          padding: 0px;
          display: flex;
          justify-content: center;
          align-items: center;
          width: 32px;
          height: 32px;
          border: none;
        "
          :style="{
          backgroundColor: currentTheme === 'light' ? '#3a3434' : '#f0f0f0',
        }"
          @click="helpModal = !helpModal"
      >
        <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            :stroke="currentTheme === 'dark' ? '#202020' : '#f0f0f0'"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
        >
          <rect x="2" y="5" width="20" height="14" rx="2" />
          <path d="M7 9h.01M11 9h.01M15 9h.01M19 9h.01M7 13h10" />
        </svg>
      </button>
      <button
          class="loading-snackbar"
          style="
          cursor: pointer;
          padding: 0px;
          display: flex;
          justify-content: center;
          align-items: center;
          width: 32px;
          height: 32px;
          border: none;
        "
          :style="{
          backgroundColor: currentTheme === 'light' ? '#3a3434' : '#f0f0f0',
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
      <button
          class="loading-snackbar"
          style="
          cursor: pointer;
          padding: 0px;
          display: flex;
          justify-content: center;
          align-items: center;
          width: 32px;
          height: 32px;
          border: none;
        "
          :style="{
          backgroundColor: currentTheme === 'light' ? '#3a3434' : '#f0f0f0',
        }"
          @click="
          () => {
            zoomIn ? smoothZoomOutToFit() : zoomToTarget();
            zoomIn = !zoomIn;
          }
        "
      >
        <svg
            width="24"
            height="24"
            viewBox="0 0 100 100"
            xmlns="http://www.w3.org/2000/svg"
            aria-hidden="true"
            role="img"
            class="iconify iconify--gis"
            preserveAspectRatio="xMidYMid meet"
            :fill="currentTheme === 'dark' ? '#202020' : '#f0f0f0'"
        >
          <path
              d="M49.798 23.592c-7.834.001-15.596 3.368-14.78 10.096l2 14.624c.351 2.573 2.09 6.688 4.687 6.688h.185l2.127 24.531c.092 1.104.892 2 2 2h8c1.108 0 1.908-.896 2-2L58.144 55h.186c2.597 0 4.335-4.115 4.687-6.688l2-14.624c.524-6.734-7.384-10.098-15.219-10.096z"
          ></path>
          <path
              d="M50.024 50.908l-.048.126c.016-.038.027-.077.043-.115l.005-.011z"
          ></path>
          <circle cx="50" cy="10.5" r="10.5"></circle>
          <path
              d="M60.922 69.092c-.085.972-.175 1.942-.26 2.914C69.614 73.27 76.25 76.138 77 79.686c1.117 5.276-16.142 7.65-27.26 7.539c-11.118-.112-28.059-2.263-26.578-7.54c.972-3.463 7.512-6.274 16.23-7.583c-.087-.975-.186-1.95-.27-2.924c-11.206 1.236-20.542 4.279-24.272 8.246H2.229L0 82.047h13.166c1.023 5.44 12.427 10.136 28.734 11.322L41.342 100h16.14l-.162-6.63c16.39-1.187 28.117-5.883 29.514-11.323H100l-1.91-4.623H85.469c-3.543-4.067-13.048-7.16-24.547-8.332z"
          ></path>
        </svg>
      </button>
      <!--
      <div>
        <input
          class="loading-snackbar"
          :style="{
            backgroundColor: currentTheme === 'dark' ? '#f0f0f0' : '#3a3434',
            color: currentTheme === 'dark' ? 'black' : 'white'
          }"
          style="width: 64px; height: 32px; padding: 0px; border: none;"
          :value="moveSpeed"
          type="number"
          max="10"
          min="0"
          step="0.5"
          @input="e => setSpeed(e.target.value)"
        >
      </div>
      -->
    </div>
    <HelpButton v-show="helpModal" @close="() => (helpModal = false)" />
  </div>
</template>

<script setup lang="ts">
import axios, { AxiosProgressEvent } from "axios";
import { onMounted, ref } from "vue";
import { wait } from "@/shared/utils/time";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";
import { PCDLoader } from "three/examples/jsm/loaders/PCDLoader";
import { UiFileField } from "@/shared/ui/ui-file-field/";
import HelpButton from "@/pages/pcd/ui/HelpButton/HelpButton.vue";
import { UiBadge } from "@/shared/ui/ui-badge/";
// import { PointerLockControls } from "three/examples/jsm/controls/PointerLockControls.js";
const axiosInstance = axios.create({});

const done = ref<boolean>(false);
const error = ref<boolean>(false);
const localPCDList = ref<object>({});
const processing = ref<boolean>(false);
const uploading = ref<boolean>(false);
const currentTheme = ref<"light" | "dark">("dark");
const pointCloud = ref(null);
const loadingPercent = ref<number>(0);
const renderingUpload = ref<boolean>(false);
const loadingForRepresentPercent = ref<number>(0);
const helpModal = ref<boolean>(false);

const zoomIn = ref<boolean>(false);
const lockFileUpload = ref<boolean>(false);

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

let initialPosition = camera.position.clone();
let initialTarget = controls.target.clone();

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

const renderPCD = async (url: string) => {
  renderingUpload.value = true;
  return new Promise((resolve, reject) => {
    loader.load(
        url,
        function (points) {
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
          renderingUpload.value = false;
          resolve(points);
        },
        (progressEvent) => {
          if (progressEvent.loaded && progressEvent.total) {
            loadingForRepresentPercent.value = Math.round(
                (progressEvent.loaded / progressEvent.total) * 100,
            );
          }
        },
        (error) => {
          renderingUpload.value = false;
          reject(error);
        },
    );
  });
};

const uploadPCD = async (file: File) => {
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
        onUploadProgress: function (progressEvent: AxiosProgressEvent) {
          if (progressEvent) {
            loadingPercent.value = Math.round(progressEvent.progress * 100);
          }
        },
      },
  );
  return data || null;
};

const waitUntilLoad = (obj) => {
  processing.value = true;
  return new Promise(async (resolve, reject) => {
    let lastInfo = null;
    while (!lastInfo || lastInfo?.status?.status === "processing") {
      const info = await axiosInstance.get(
          "http://78.136.221.218:40023/api/status?uid=" + obj.uid,
      );
      lastInfo = info.data;
      try {
        const data = JSON.parse(localStorage.getItem("data")) || {};
        data[lastInfo.uid] = lastInfo;
        localStorage.setItem("data", JSON.stringify(data));
      } finally {
      }
      await wait(5000);
    }
    processing.value = false;
    if (lastInfo?.status?.status === "ready") {
      resolve(lastInfo);
    } else {
      reject(lastInfo);
    }
  });
};

const uploadPSDToServer = async (file: File) => {
  uploading.value = true;
  uploadPCD(file)
      .then((data) => {
        loadById(data.uid);
      })
      .finally(() => {
        uploading.value = false;
      });
};

const loadById = (id: string) => {
  lockFileUpload.value = true;
  waitUntilLoad({ uid: id })
      .then((res) => {
        renderPCD(res?.status?.result_filename)
            .then(() => {
              done.value = true;
            })
            .catch(() => {
              done.value = false;
              error.value = true;
            });
      })
      .catch((err) => {
        console.log("PROGRAM DONE (ERROR)", err.message);
      });
};

const upload = async (f) => {
  const urlObject = URL.createObjectURL(f.target.files[0]);

  lockFileUpload.value = true;
  uploadPSDToServer(f.target.files[0]);
  /*
  loadById("799b7f36199649f9ab1b83f9568a90a6");
   */

  renderPCD(urlObject).finally(() => {
    initialPosition = camera.position.clone();
    initialTarget = controls.target.clone();
    // addBBox([0, 0, 0], [1, 1, 1], 0x00ff00);
  });
};

// Пример: бокс в центре облака
// addBBox([0,0,0], [1,1,1], 0x00ff00);

// Скорость движения
let moveSpeed = 1;
const keys = {};

const setSpeed = (speed) => {
  const speedNumber = Number(speed);
  if (!isNaN(speedNumber)) {
    moveSpeed = speed;
  }
};

// обработка нажатий
document.addEventListener("keydown", (e) => {
  keys[e.code] = true;
});
document.addEventListener("keyup", (e) => {
  keys[e.code] = false;
});

/**
 * Плавное отдаление камеры, чтобы весь объект поместился в кадр
 * @param {THREE.Object3D} object - объект сцены/облако точек
 * @param {number} duration - время анимации в мс
 * @param {number} padding - коэффициент запаса (1.0 = ровно, >1 = с запасом)
 */
function smoothZoomOutToFit(
    object = pointCloud.value,
    duration = 600,
    padding = 1.5,
) {
  if (!object) return;

  const box = new THREE.Box3().setFromObject(object);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3()).length();

  // текущие параметры
  const startPos = camera.position.clone();
  const startTarget = controls.target.clone();

  // направление от target к камере
  let dir = new THREE.Vector3().subVectors(startPos, startTarget);
  const curDist = dir.length();

  if (curDist < 1e-6) {
    const fwd = new THREE.Vector3();
    camera.getWorldDirection(fwd);
    dir.copy(fwd.length() < 1e-6 ? new THREE.Vector3(0, 0, 1) : fwd.negate());
  }
  dir.normalize();

  // новое расстояние
  const endDist = size * padding;
  const endPos = center.clone().addScaledVector(dir, endDist);

  // анимация
  const t0 = performance.now();
  function tick(now) {
    const t = Math.min(1, (now - t0) / duration);
    const ease = 1 - Math.pow(1 - t, 3); // easeOutCubic
    camera.position.lerpVectors(startPos, endPos, ease);
    controls.target.lerpVectors(startTarget, center, ease);
    camera.updateMatrixWorld();
    controls.update();
    if (t < 1) requestAnimationFrame(tick);
    else {
      camera.position.copy(endPos);
      controls.target.copy(center);
      camera.updateMatrixWorld();
      controls.update();
    }
  }
  requestAnimationFrame(tick);
}

// Возможно, порождает лаги при движени
function zoomToTarget(duration = 400, minDistanceOverride) {
  const start = performance.now();
  const startPos = camera.position.clone();
  const target = controls.target.clone();

  // вычислим направление (как в instant)
  const dir = new THREE.Vector3().subVectors(startPos, target);
  if (dir.length() < 1e-6) {
    const fwd = new THREE.Vector3();
    camera.getWorldDirection(fwd);
    dir.copy(fwd.length() < 1e-6 ? new THREE.Vector3(0, 0, 1) : fwd.negate());
  }
  dir.normalize();

  const minDist = Math.max(
      typeof minDistanceOverride === "number"
          ? minDistanceOverride
          : controls.minDistance || 0.1,
      1e-4,
  );
  const endPos = target.clone().addScaledVector(dir, minDist);

  function tick(now) {
    const t = Math.min(1, (now - start) / duration);
    const ease = 1 - Math.pow(1 - t, 3); // сглаженный easeOutCubic
    camera.position.lerpVectors(startPos, endPos, ease);
    camera.updateMatrixWorld();
    controls.update();
    if (t < 1) requestAnimationFrame(tick);
    else {
      // финальная корректировка
      camera.position.copy(endPos);
      camera.updateProjectionMatrix();
      controls.update();
    }
  }
  requestAnimationFrame(tick);
}

const fitModel = () => {
  const box = new THREE.Box3().setFromObject(pointCloud.value);
  const size = box.getSize(new THREE.Vector3()).length();
  const center = box.getCenter(new THREE.Vector3());

  // центрируем
  controls.target.copy(center);

  // ставим камеру так, чтобы объект полностью влезал
  const distance = size * 1.5; // коэффициент 1.5 — чтобы с запасом
  const dir = new THREE.Vector3(0, 0, 1); // направление камеры (вперёд по Z)
  camera.position.copy(center.clone().addScaledVector(dir, distance));

  camera.near = size / 100;
  camera.far = size * 10;
  camera.updateProjectionMatrix();

  controls.update();
};

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
  // поднимаем/опускаем по оси Y
  if (keys["Space"]) {
    // вверх
    camera.position.y += moveSpeed;
    controls.target.y += moveSpeed;
    controls.update();
  }
  if (keys["ShiftLeft"]) {
    // вниз
    camera.position.y -= moveSpeed;
    controls.target.y -= moveSpeed;
  }
  if (keys["KeyR"]) {
    // сброс к начальному положению
    camera.position.copy(initialPosition);
    controls.target.copy(initialTarget);
    controls.update();
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

onMounted(() => {
  document.getElementById("container").appendChild(renderer.domElement);
  animate();
  const data = JSON.parse(window.localStorage.getItem("data")) || {};
  if (data instanceof Object) {
    localPCDList.value = data;
  }
});
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

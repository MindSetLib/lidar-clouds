<template>
  <div
    id="controlsBackdrop"
    class="controls-backdrop"
    role="dialog"
    aria-modal="true"
    aria-labelledby="controlsTitle"
  >
    <div
      class="controls-modal"
      role="document"
      aria-describedby="controlsList"
      tabindex="-1"
    >
      <div class="controls-header">
        <div>
          <div id="controlsTitle" class="controls-title">Управление сценой</div>
          <div class="controls-sub">
            Мышь + клавиатура — быстрое перемещение и фокус
          </div>
        </div>
        <div
          style="display: flex; gap: 6px; align-items: center"
          @click="() => emit('close')"
        >
          <button
            id="controlsCloseBtn"
            class="controls-close"
            aria-label="Закрыть"
          >
            <!-- simple X -->
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <div id="controlsList" class="controls-list">
        <!-- MOUSE: rotate -->
        <div class="controls-item">
          <div class="controls-icon" aria-hidden="true">
            <!-- mouse rotate icon -->
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#cfe6ff"
              stroke-width="1.6"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <rect x="6" y="2" width="12" height="20" rx="6" />
              <path d="M12 6v4" />
            </svg>
          </div>
          <div class="controls-desc">
            Поворот сцены (Orbit):
            <span class="controls-keys"
              >Левая кнопка мыши — тянуть/вращать</span
            >
          </div>
        </div>

        <!-- MOUSE: pan -->
        <div class="controls-item">
          <div class="controls-icon" aria-hidden="true">
            <!-- pan icon -->
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#cfe6ff"
              stroke-width="1.6"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M12 2v20" />
              <path d="M5 9h14" />
              <path d="M5 15h14" />
            </svg>
          </div>
          <div class="controls-desc">
            Панорамирование (перемещение плоскости):
            <span class="controls-keys"
              >Правая кнопка мыши — тянуть (или средняя/колёсико + drag)</span
            >
          </div>
        </div>

        <!-- MOUSE: zoom -->
        <div class="controls-item">
          <div class="controls-icon" aria-hidden="true">
            <!-- zoom icon -->
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#cfe6ff"
              stroke-width="1.6"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle cx="11" cy="11" r="6" />
              <path d="M21 21l-4.35-4.35" />
            </svg>
          </div>
          <div class="controls-desc">
            Масштаб (Zoom):
            <span class="controls-keys"
              >Колёсико мыши — прокрутка / Средняя кнопка — перетянуть</span
            >
          </div>
        </div>

        <!-- KEYBOARD: WASD -->
        <div class="controls-item">
          <div class="controls-icon" aria-hidden="true">
            <!-- keyboard icon -->
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#cfe6ff"
              stroke-width="1.6"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <rect x="2" y="5" width="20" height="14" rx="2" />
              <path d="M7 9h.01M11 9h.01M15 9h.01M19 9h.01M7 13h10" />
            </svg>
          </div>
          <div class="controls-desc">
            Перемещение камеры:
            <span class="controls-keys"
              >W / A / S / D — вперед/влево/назад/вправо (двигают камеру и центр
              фокуса)</span
            >
          </div>
        </div>

        <!-- KEYBOARD: SPACE/SHIFT -->
        <div class="controls-item">
          <div class="controls-icon" aria-hidden="true">
            <!-- space icon -->
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#cfe6ff"
              stroke-width="1.6"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <rect x="3" y="10" width="18" height="4" rx="2" />
            </svg>
          </div>
          <div class="controls-desc">
            Вертикальное смещение фокуса:
            <span class="controls-keys"
              >Space — поднять, Shift (левая) — опустить</span
            >
          </div>
        </div>

        <!-- KEYBOARD: other helpful -->
        <div class="controls-item">
          <div class="controls-icon" aria-hidden="true">
            <!-- info icon -->
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#cfe6ff"
              stroke-width="1.6"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle cx="12" cy="12" r="10" />
              <path d="M12 16v-4" />
              <path d="M12 8h.01" />
            </svg>
          </div>
          <div class="controls-desc">
            Полезно:
            <span class="controls-keys"
              >R — сброс позиции камеры
              <!--/ F — «fit to object» (по желанию
              реализовать)--></span
            >
          </div>
        </div>
      </div>

      <div class="controls-footer">
        Коротко: <strong>мышь</strong> — осмотр;
        <strong>WASD + Space/Shift</strong> — перемещение и поднятие/опускание
        фокуса.
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
const emit = defineEmits(["close"]);
</script>
<style scoped lang="scss">
/* --- Сама карточка --- */
.controls-modal {
  position: fixed;
  z-index: 50;
  left: 20px;
  bottom: 20px;
  width: 360px;
  max-width: calc(100% - 40px);
  background: #3a3434;
  color: white;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(2, 6, 23, 0.7);
  font-family: Inter, Roboto, "Helvetica Neue", Arial, sans-serif;
  overflow: hidden;
  transform: translateY(8px);
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.controls-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.015), transparent);
}
.controls-title {
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.2px;
}
.controls-sub {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 2px;
  font-weight: 500;
}

/* --- Список команд --- */
.controls-list {
  padding: 10px 10px 14px 10px;
  display: grid;
  gap: 8px;
}
.controls-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  padding: 8px;
  border-radius: 8px;
  transition: background 0.12s ease;
}
.controls-item:hover {
  background: rgba(255, 255, 255, 0.02);
}
.controls-icon {
  width: 36px;
  height: 36px;
  flex: 0 0 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.02),
    rgba(255, 255, 255, 0.01)
  );
  box-shadow: inset 0 -1px 0 rgba(255, 255, 255, 0.01);
}
.controls-desc {
  font-size: 13px;
  color: #dfe9fb;
  line-height: 1.2;
}
.controls-keys {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: #9ca3af;
}

/* --- Close button --- */
.controls-close {
  background: transparent;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: background 0.12s;
}
.controls-close:hover {
  background: rgba(255, 255, 255, 0.02);
}

/* --- Footer hint --- */
.controls-footer {
  padding: 10px 14px;
  font-size: 12px;
  color: #8fa6cf;
  border-top: 1px solid rgba(255, 255, 255, 0.02);
  background: linear-gradient(180deg, transparent, rgba(255, 255, 255, 0.01));
}
</style>
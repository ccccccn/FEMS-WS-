<template>
  <div class="system-monitor">
    <div class="grid-container">
      <div v-for="row in 5" :key="row" class="grid-row">
        <div v-for="col in 12" :key="col" class="grid-item" @click="handleGridClick(row, col)">
          <!-- 储能设备图片 -->
          <template v-if="isImageColumn(col)">
            <div class="device-container">
              <div class="device-title">{{ getFlywheelTitle(col, row) }}</div>
              <div class="device-image" :class="{ 'mirror': isMirrorColumn(col) }">
                <img :src="images.flywheel" alt="储能设备" />
              </div>
            </div>
          </template>
          <!-- 箱变图片 -->
          <template v-else-if="isBoxImage(col)">
            <div class="device-container">
              <div class="device-title">{{ getTransformerTitle(col, row) }}</div>
              <div class="box-image" :class="{ 'mirror': isBoxMirror(col) }">
                <img :src="images.box" alt="箱变" />
              </div>
            </div>
          </template>
          <!-- 状态信息显示 -->
          <template v-else-if="isStatusColumn(col)">
            <div class="status-info">
              <div class="status-header">
                <div class="status-row">
                  <span class="status-label">系统模式</span>
                  <span class="status-divider">|</span>
                  <span class="status-value">{{ systemStatus.mode }}</span>
                </div>
                <div class="status-row">
                  <span class="status-label">系统状态</span>
                  <span class="status-divider">|</span>
                  <span class="status-value">{{ systemStatus.status }}</span>
                </div>
              </div>
              <div class="status-row comm-row">
                <div class="comm-item">
                  <span class="comm-label">C-A</span>
                  <span class="comm-value">{{ systemStatus.commCA }}</span>
                </div>
                <div class="comm-item">
                  <span class="comm-label">M-A</span>
                  <span class="comm-value">{{ systemStatus.commMA }}</span>
                </div>
                <div class="comm-item">
                  <span class="comm-label">M-B</span>
                  <span class="comm-value">{{ systemStatus.commMB }}</span>
                </div>
              </div>
            </div>
          </template>
          <!-- 其他网格项 -->
          <template v-else>
            <div class="grid-content">
              <div class="grid-section">
                <span class="section-label">高压框架</span>
                <div class="alarm-light" :class="getAlarmClass(getValue(row, col, 'param'))">
                  <div class="light-dot"></div>
                </div>
              </div>
              <div class="grid-section">
                <span class="section-label">低压框架QF1</span>
                <div class="alarm-light" :class="getAlarmClass(getValue(row, col, 'status'))">
                  <div class="light-dot"></div>
                </div>
              </div>
              <div class="grid-section">
                <span class="section-label">低压框架QF2</span>
                <div class="alarm-light" :class="getAlarmClass(getValue(row, col, 'value'))">
                  <div class="light-dot"></div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- 弹出层 -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedDevice }} 内部监控</h3>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="monitor-content">
            <div class="device-layout">
              <!-- PCS -->
              <div class="pcs-group">
                <div class="pcs-item">
                  <div class="device-info">
                    <div class="info-title">PCS状态</div>
                    <div class="info-row">
                      <span class="info-label">运行状态</span>
                      <span class="info-value">正常</span>
                    </div>
                    <div class="info-row">
                      <span class="info-label">功率</span>
                      <span class="info-value">80kW</span>
                    </div>
                  </div>
                  <div class="device-content">
                    <img :src="images.pcs" alt="PCS" />
                    <span class="device-label">PCS</span>
                  </div>
                  <div class="connection-lines">
                    <svg class="connection-svg">
                      <polyline v-for="(line, index) in pcsLines" 
                               :key="index"
                               :points="line"
                               class="connection-line" />
                    </svg>
                  </div>
                </div>
              </div>
              
              <!-- IPM组 -->
              <div class="ipm-group">
                <div class="ipm-row">
                  <div class="ipm-item" v-for="i in 4" :key="`ipm-${i}`">
                    <div class="device-info">
                      <div class="info-title">IPM{{ i }}状态</div>
                      <div class="info-row">
                        <span class="info-label">运行状态</span>
                        <span class="info-value">正常</span>
                      </div>
                      <div class="info-row">
                        <span class="info-label">温度</span>
                        <span class="info-value">45℃</span>
                      </div>
                    </div>
                    <div class="device-content">
                      <img :src="images.ipm" :alt="`IPM${i}`" />
                      <span class="device-label">IPM{{ i }}</span>
                    </div>
                    <div class="connection-lines">
                      <svg class="connection-svg">
                        <polyline :points="`10,0 10,30 0,60`" class="connection-line" />
                        <polyline :points="`90,0 90,30 100,60`" class="connection-line" />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 飞轮组 -->
              <div class="flywheel-group">
                <div class="flywheel-row">
                  <div class="flywheel-item" v-for="i in 8" :key="`flywheel-${i}`">
                    <div class="device-info">
                      <div class="info-title">飞轮{{ i }}状态</div>
                      <div class="info-row">
                        <span class="info-label">转速</span>
                        <span class="info-value">12000rpm</span>
                      </div>
                      <div class="info-row">
                        <span class="info-label">温度</span>
                        <span class="info-value">42℃</span>
                      </div>
                    </div>
                    <div class="device-content">
                      <img :src="images.flywheelInner" :alt="`飞轮${i}`" />
                      <span class="device-label">飞轮{{ i }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
// 引入图片
import boxImage from '@/assets/img/monitor/监控_变压器.png';
import flywheelImage from '@/assets/img/monitor/监控_飞轮舱.png';
import ipmImage from '@/assets/img/monitor/监控_IPM.png';
import pcsImage from '@/assets/img/monitor/监控_PCS.png';
import flywheelInnerImage from '@/assets/img/monitor/监控_飞轮.png';

// 系统状态数据
const systemStatus = ref({
  mode: '正常运行',
  status: '在线',
  commCA: '正常',
  commMA: '正常',
  commMB: '正常'
});

// 添加状态数据
const frameStatus = ref({});

// 定时器
let timer = null;

// 随机生成状态
const getRandomStatus = () => {
  return Math.random() > 0.5 ? 'normal' : 'error';
};

// 更新框架状态
const updateFrameStatus = () => {
  const allCells = 5 * 12; // 总网格数
  for(let i = 1; i <= allCells; i++) {
    frameStatus.value[i] = {
      param: getRandomStatus(),
      status: getRandomStatus(),
      value: getRandomStatus()
    };
  }
};

// 获取状态值
const getValue = (row, col, type) => {
  const id = (row-1)*12 + col;
  return frameStatus.value[id]?.[type] || 'normal';
};

// 设置定时刷新
onMounted(() => {
  updateFrameStatus(); // 初始化状态
  timer = setInterval(updateFrameStatus, 5000); // 每5秒更新一次
});

// 清理定时器
onUnmounted(() => {
  if (timer) clearInterval(timer);
});

// 判断是否为飞轮舱图片列
const isImageColumn = (col) => {
  return [2, 4, 9, 11].includes(col);
};

// 判断是否为箱变图片列
const isBoxImage = (col) => {
  return [6, 7].includes(col);
};

// 判断是否需要镜像
const isMirrorColumn = (col) => {
  return [9, 11].includes(col);
};

// 判断箱变是否需要镜像
const isBoxMirror = (col) => {
  return col === 7;
};

// 判断是否为状态信息列
const isStatusColumn = (col) => {
  return [1, 3, 10, 12].includes(col);  // 包含第1列
};

// 弹窗控制
const showModal = ref(false);
const selectedDevice = ref('');

// 处理飞轮舱点击
const handleFlywheelClick = (col, row) => {
  selectedDevice.value = getFlywheelTitle(col, row);
  showModal.value = true;
};

// 关闭弹窗
const closeModal = () => {
  showModal.value = false;
  selectedDevice.value = '';
};

// 修改原有的点击处理函数
const handleGridClick = (row, col) => {
  if (isImageColumn(col)) {
    handleFlywheelClick(col, row);
  }
};

// 提供图片路径
const images = {
  box: boxImage,
  flywheel: flywheelImage,
  flywheelInner: flywheelInnerImage,
  ipm: ipmImage,
  pcs: pcsImage
};

// 获取飞轮舱标题
const getFlywheelTitle = (col, row) => {
  const flywheelMap = {
    2: {
      1: '飞轮舱1A',
      2: '飞轮舱3A',
      3: '飞轮舱5A',
      4: '飞轮舱7A',
      5: '飞轮舱9A'
    },
    4: {
      1: '飞轮舱1B',
      2: '飞轮舱3B',
      3: '飞轮舱5B',
      4: '飞轮舱7B',
      5: '飞轮舱9B'
    },
    9: {
      1: '飞轮舱2B',
      2: '飞轮舱4B',
      3: '飞轮舱6B',
      4: '飞轮舱8B',
      5: '飞轮舱10B'
    },
    11: {
      1: '飞轮舱2A',
      2: '飞轮舱4A',
      3: '飞轮舱6A',
      4: '飞轮舱8A',
      5: '飞轮舱10A'
    }
  };
  return flywheelMap[col]?.[row] || '';
};

// 获取变压器标题
const getTransformerTitle = (col, row) => {
  const transformerMap = {
    6: {
      1: '变压器1',
      2: '变压器3',
      3: '变压器5',
      4: '变压器7',
      5: '变压器9'
    },
    7: {
      1: '变压器2',
      2: '变压器4',
      3: '变压器6',
      4: '变压器8',
      5: '变压器10'
    }
  };
  return transformerMap[col]?.[row] || '';
};

// 获取报警灯状态类名
const getAlarmClass = (status) => {
  return {
    'light-normal': status === 'normal',
    'light-error': status === 'error'
  };
};

// 计算PCS连接线的位置
const pcsLines = [
  "20,0 20,30 0,60",
  "40,0 40,20 20,60",
  "60,0 60,20 80,60",
  "80,0 80,30 100,60"
];
</script>

<style lang="scss" scoped>
.system-monitor {
  width: 100%;
  height: 100%;
  padding: 10px;
  background: transparent;
}

.grid-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.grid-row {
  flex: 1;
  display: flex;
  gap: 10px;
}

.grid-item {
  flex: 1;
  padding: 5px;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  
  background: transparent;
  border: none;

  &:hover {
    box-shadow: 0 0 10px rgba(24, 144, 255, 0.2);
  }
}

.grid-content {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.grid-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  border-bottom: 1px solid rgba(24, 144, 255, 0.2);

  &:last-child {
    border-bottom: none;
  }

  .section-label {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.65);
    flex: 1;
    padding-right: 10px;
  }
}

.alarm-light {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3px;
  
  .light-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    transition: all 0.3s ease;
  }
  
  &.light-normal .light-dot {
    background: #52c41a;
    box-shadow: 0 0 15px #52c41a;
    animation: blink-normal 2s ease-in-out infinite;
  }
  
  &.light-error .light-dot {
    background: #ff4d4f;
    box-shadow: 0 0 15px #ff4d4f;
    animation: blink-error 2s ease-in-out infinite;
  }
}

.device-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0;
  position: relative;
}

.device-title {
  color: #ffe818;
  font-size: 14px;
  font-weight: 500;
  text-shadow: 0 0 10px rgba(24, 144, 255, 0.3);
  padding: 0;
  position: absolute;
  top: 20px;
  z-index: 1;
}

.device-image,
.box-image {
  flex: 1;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 5px;
  padding-bottom: 5px;
  
  &.mirror {
    transform: scaleX(-1);
  }
  
  img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    object-position: center;
    transition: transform 0.3s ease;
    
    &:hover {
      transform: scale(1.02);
    }
  }
}

.status-info {
  width: 100%;
  height: 100%;
  padding: 8px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
}

.status-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.status-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-width: 160px;
  
  .status-label {
    color: rgba(255, 255, 255, 0.65);
    font-size: 12px;
    width: 60px;
    text-align: right;
  }
  
  .status-divider {
    color: rgba(255, 255, 255, 0.2);
    font-size: 12px;
    padding: 0 2px;
  }
  
  .status-value {
    color: #1890ff;
    font-size: 12px;
    width: 60px;
    text-align: left;
  }
}

.comm-row {
  display: flex;
  justify-content: center;
  padding-top: 4px;
  margin-top: 4px;
  border-top: 1px solid rgba(24, 144, 255, 0.1);
  width: 100%;
  gap: 12px;
}

.comm-item {
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
  padding: 0;
  min-width: 32px;
  
  .comm-label {
    font-size: 10px;
    color: rgba(255, 255, 255, 0.65);
    transform: scale(0.9);
    transform-origin: center;
  }
  
  .comm-value {
    font-size: 12px;
    color: #1890ff;
    &.status-normal {
      color: #52c41a;
    }
    &.status-error {
      color: #ff4d4f;
    }
    &.status-offline {
      color: #8c8c8c;
    }
  }
}

@keyframes blink-normal {
  0% { opacity: 1; box-shadow: 0 0 15px #52c41a; }
  50% { opacity: 0.7; box-shadow: 0 0 5px #52c41a; }
  100% { opacity: 1; box-shadow: 0 0 15px #52c41a; }
}

@keyframes blink-error {
  0% { opacity: 1; box-shadow: 0 0 15px #ff4d4f; }
  50% { opacity: 0.7; box-shadow: 0 0 5px #ff4d4f; }
  100% { opacity: 1; box-shadow: 0 0 15px #ff4d4f; }
}

// 添加渐变边框效果
.status-info {
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border: 1px solid rgba(24, 144, 255, 0.2);
    border-radius: 4px;
    pointer-events: none;
  }
  
  &::after {
    content: '';
    position: absolute;
    top: -1px;
    left: -1px;
    right: -1px;
    height: 2px;
    background: linear-gradient(90deg, 
      transparent, 
      rgba(24, 144, 255, 0.5), 
      transparent
    );
  }
}

// 优化状态值显示
.status-value {
  position: relative;
  padding: 2px 6px;
  border-radius: 2px;
  background: rgba(24, 144, 255, 0.1);
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: 2px;
    border: 1px solid rgba(24, 144, 255, 0.2);
    pointer-events: none;
  }
}

// 弹出层样式
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

.modal-content {
  background: rgba(0, 21, 41, 0.3);
  border: 1px solid rgba(24, 144, 255, 0.3);
  border-radius: 8px;
  width: 95%;
  max-width: 1600px;
  min-height: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  animation: slideIn 0.3s ease;
  box-shadow: 0 0 20px rgba(24, 144, 255, 0.2);
  backdrop-filter: blur(8px);
}

.modal-header {
  background: rgba(0, 21, 41, 0.5);
  padding: 16px 24px;
  border-bottom: 1px solid rgba(24, 144, 255, 0.2);
  
  h3 {
    color: rgba(24, 144, 255, 0.9);
    text-shadow: 0 0 10px rgba(24, 144, 255, 0.3);
  }
  
  .close-btn {
    background: none;
    border: none;
    color: rgba(255, 255, 255, 0.65);
    font-size: 24px;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 4px;
    transition: all 0.3s ease;
    
    &:hover {
      color: #fff;
      background: rgba(24, 144, 255, 0.1);
    }
  }
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.monitor-content {
  color: rgba(255, 255, 255, 0.85);
  min-height: 400px;
}

// 动画
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

// 修改设备图片的鼠标样式
.device-image,
.box-image {
  cursor: pointer;
  
  &:hover {
    img {
      transform: scale(1.02);
      filter: brightness(1.2);
    }
  }
}

.device-layout {
  display: flex;
  flex-direction: column;
  gap: 80px;
  padding: 40px 60px;
  height: 100%;
  justify-content: space-between;
}

// PCS 样式
.pcs-group {
  display: flex;
  justify-content: center;
  
  .pcs-item {
    width: 120px;  // PCS稍大一些
  }
}

// IPM 样式
.ipm-group {
  .ipm-row {
    display: flex;
    justify-content: space-around;
    gap: 140px;
  }
  
  .ipm-item {
    width: 90px;  // 减小IPM尺寸
    text-align: center;
    position: relative;
    
    img {
      width: 100%;
      height: auto;
    }
    
    .connection-lines {
      position: absolute;
      bottom: -40px;
      left: 0;
      right: 0;
      
      .line-to-flywheel {
        position: absolute;
        width: 2px;
        height: 40px;
        background: #1890ff;
        
        &.left {
          left: 25%;
          transform: rotate(15deg);
        }
        
        &.right {
          right: 25%;
          transform: rotate(-15deg);
        }
      }
    }
  }
}

// 飞轮组样式
.flywheel-group {
  .flywheel-row {
    display: flex;
    justify-content: space-between;  // 改为两端对齐
    flex-wrap: nowrap;  // 禁止换行
    gap: 60px;
    padding: 0 40px;
  }
  
  .flywheel-item {
    width: 80px;  // 减小飞轮尺寸
    flex: 0 0 auto;
    text-align: center;
    
    img {
      width: 100%;
      height: auto;
      transition: all 0.3s ease;
      filter: brightness(1.1);  // 稍微提高亮度
      
      &:hover {
        transform: scale(1.05);
        filter: brightness(1.3);
      }
    }
  }
}

.device-label {
  margin-top: 6px;
  font-size: 12px;
}

// 连接线样式调整
.connection-svg {
  height: 40px;  // 减小连接线高度
}

.connection-line {
  stroke-width: 1.5;  // 减小线条粗细
}

// 连接线动画
@keyframes flowLine {
  0% { opacity: 0.3; }
  50% { opacity: 1; }
  100% { opacity: 0.3; }
}

.line-to-flywheel,
.line-to-ipm {
  animation: flowLine 2s infinite;
}

.device-content {
  position: relative;
  width: 100px;  // 减小设备图片尺寸
  margin: 0 auto;
  
  img {
    width: 100%;
    height: auto;
    object-fit: contain;
  }
}

.device-info {
  position: absolute;
  left: -160px;  // 减小偏移
  top: 50%;
  transform: translateY(-50%);
  width: 140px;  // 减小信息框宽度
  background: rgba(0, 21, 41, 0.3);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(24, 144, 255, 0.2);
  border-radius: 4px;
  padding: 8px;  // 减小内边距
  box-shadow: 0 0 10px rgba(24, 144, 255, 0.1);
  
  .info-title {
    font-size: 12px;  // 减小标题字号
    margin-bottom: 6px;
  }
  
  .info-row {
    margin-bottom: 3px;
    
    .info-label,
    .info-value {
      font-size: 11px;  // 减小文字大小
    }
  }
}

// 响应式调整
@media screen and (max-width: 1400px) {
  .device-info {
    left: -140px;
    width: 120px;
    
    .info-title {
      font-size: 11px;
    }
    
    .info-row {
      .info-label,
      .info-value {
        font-size: 10px;
      }
    }
  }
  
  .device-content {
    width: 90px;
  }
  
  .flywheel-group .flywheel-row {
    gap: 30px;
  }
  
  .ipm-group .ipm-row {
    gap: 100px;
  }
}

@media screen and (max-width: 1200px) {
  .device-layout {
    gap: 40px;
    padding: 20px;
  }
  
  .device-info {
    position: relative;
    left: 0;
    top: 0;
    transform: none;
    width: 100%;
    margin-bottom: 8px;
  }
}
</style>
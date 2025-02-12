<template>
  <div class="show-center">
    <div class="grid-container">
      <!-- 项目基本信息 -->
      <div class="grid-item basic-info">
        <div class="chart-box">
          <div class="chart-title">项目基本信息</div>
          <div class="info-list">
            <div class="info-item" v-for="(value, key) in basicInfo" :key="key">
              <span class="label">{{ key }}</span>
              <span class="value">{{ value }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 调用次数和SOC排名 -->
      <div class="grid-item">
        <div class="chart-box">
          <div class="chart-title">调用次数和SOC排名</div>
          <div :ref="el => chartRefs[0] = el" class="chart"></div>
        </div>
      </div>

      <!-- 动作次数统计 -->
      <div class="grid-item">
        <div class="chart-box">
          <div class="chart-title">动作次数统计</div>
          <div class="action-stats">
            <div class="stat-item" v-for="(stat, index) in actionStats" :key="index">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 能量流动监控 -->
      <div class="grid-item large-chart">
        <div class="chart-box">
          <div class="chart-title">能量流动监控</div>
          <div :ref="el => chartRefs[1] = el" class="chart"></div>
        </div>
      </div>

      <!-- 可用情况 -->
      <div class="grid-item">
        <div class="chart-box">
          <div class="chart-title">可用情况</div>
          <div class="status-panel">
            <div class="status-item" v-for="(status, index) in statusInfo" :key="index">
              <div class="status-label">{{ status.label }}</div>
              <div class="status-value" :class="status.class">{{ status.value }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 总功率和总量曲线 -->
      <div class="grid-item">
        <div class="chart-box">
          <div class="chart-title">总功率和总量曲线</div>
          <div :ref="el => chartRefs[2] = el" class="chart"></div>
        </div>
      </div>

      <!-- 阵列实时调用情况 -->
      <div class="grid-item flywheel-array">
        <div class="chart-box">
          <div class="chart-title">阵列实时调用情况</div>
          <div class="flywheel-grid">
            <div 
              v-for="n in 20" 
              :key="n" 
              class="flywheel-cell"
              :class="getFlywheelStatus(n)"
            >
              {{ n }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import * as echarts from 'echarts';

const chartRefs = ref([]);
const charts = ref([]);

// 基本信息数据
const basicInfo = ref({
  '主变压器额定功率': '100 MW',
  '飞轮额定功率': '20 MW',
  '电池额定功率': '20 MW',
  '电压等级': '220 kV',
  '飞轮能量': '172 kWh',
  '电池能量': '20 MWh'
});

// 动作次数统计
const actionStats = ref([
  { label: '日充电次数', value: 279 },
  { label: '日放电次数', value: 200 },
  { label: '今日动作次数', value: 479 },
  { label: '近30日动作次数', value: 2400 },
  { label: '近一年动作次数', value: 2400 }
]);

// 系统状态信息
const statusInfo = ref([
  { label: '场站总SOC', value: '00%', class: 'normal' },
  { label: '电网频率', value: '50.1 Hz', class: 'normal' },
  { label: '总指令功率', value: '-5000.0 kW', class: 'warning' },
  { label: '总反馈功率', value: '144.0 kW', class: 'normal' }
]);

// 飞轮状态判断
const getFlywheelStatus = (id) => {
  // 模拟不同状态，实际应该根据后端数据判断
  const status = Math.random();
  if (status > 0.8) return 'active';
  if (status > 0.6) return 'standby';
  if (status > 0.3) return 'warning';
  return 'fault';
};

// 图表配置和初始化
const initCharts = () => {
  // 调用次数和SOC排名图表
  const usageChart = echarts.init(chartRefs.value[0]);
  usageChart.setOption({
    // ... 配置详情见下一部分
  });
  
  // 能量流动监控图表
  const flowChart = echarts.init(chartRefs.value[1]);
  flowChart.setOption({
    // ... 配置详情见下一部分
  });
  
  // 总功率和总量曲线图表
  const powerChart = echarts.init(chartRefs.value[2]);
  powerChart.setOption({
    // ... 配置详情见下一部分
  });
  
  charts.value = [usageChart, flowChart, powerChart];
};

// ... 其他代码保持不变 ...
</script>

<style lang="scss" scoped>
.show-center {
  width: 100%;
  height: 100%;
  padding: 10px;
  box-sizing: border-box;
  
  .grid-container {
    display: grid;
    grid-template-columns: 30% 40% 30%;
    grid-template-rows: repeat(3, 1fr);
    gap: 15px;
    height: 100%;
    
    .grid-item {
      border-radius: 8px;
      padding: 10px;
      position: relative;
      
      &.large-chart {
        grid-row: span 3;
      }
    }
  }
}

.chart-box {
  position: relative;
  border-radius: 4px;
  padding: 10px;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    border-radius: 6px;
    z-index: -1;
  }
}

.chart-title {
  position: relative;
  background: linear-gradient(120deg, #1890ff, #00c6fb, #1890ff, #00c6fb);
  background-size: 200% auto;
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
  font-size: 18px;
  font-weight: bold;
  padding: 8px 0;
  margin-bottom: 5px;
  border-bottom: 1px solid rgba(24, 144, 255, 0.3);
  text-shadow: 0 0 10px rgba(24, 144, 255, 0.3);
  animation: shine 3s linear infinite;
}

@keyframes shine {
  0% { background-position: 200% center; }
  100% { background-position: -200% center; }
}

// 基本信息样式
.info-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  padding: 10px;
  
  .info-item {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .label {
      color: #8b8b8b;
    }
    
    .value {
      color: #00c6fb;
      font-weight: 500;
    }
  }
}

// 动作次数统计样式
.action-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  padding: 10px;
  
  .stat-item {
    text-align: center;
    
    .stat-value {
      font-size: 20px;
      color: #00c6fb;
      font-weight: bold;
    }
    
    .stat-label {
      font-size: 12px;
      color: #8b8b8b;
      margin-top: 5px;
    }
  }
}

// 飞轮阵列样式
.flywheel-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
  padding: 10px;
  
  .flywheel-cell {
    aspect-ratio: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    font-size: 12px;
    color: white;
    width: 20px;
    height: 40px;
    
    &.active {
      background: rgba(0, 255, 0, 0.3);
      border: 1px solid rgba(0, 255, 0, 0.5);
    }
    
    &.standby {
      background: rgba(0, 198, 251, 0.3);
      border: 1px solid rgba(0, 198, 251, 0.5);
    }
    
    &.warning {
      background: rgba(255, 215, 0, 0.3);
      border: 1px solid rgba(255, 215, 0, 0.5);
    }
    
    &.fault {
      background: rgba(255, 0, 0, 0.3);
      border: 1px solid rgba(255, 0, 0, 0.5);
    }
  }
}

// 状态面板样式
.status-panel {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  padding: 15px;
  
  .status-item {
    text-align: center;
    
    .status-label {
      color: #8b8b8b;
      font-size: 12px;
      margin-bottom: 5px;
    }
    
    .status-value {
      font-size: 18px;
      font-weight: bold;
      
      &.normal { color: #00c6fb; }
      &.warning { color: #ffd700; }
      &.error { color: #ff4d4f; }
    }
  }
}

@media (max-width: 768px) {
  .grid-container {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
  }
}
</style>
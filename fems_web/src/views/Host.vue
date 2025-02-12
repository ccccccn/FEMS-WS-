<template>
  <div class="show-center">
    <div class="grid-container">
      <!-- 左侧列 -->
      <div class="grid-item basic-info">
        <div class="chart-box">
          <div class="chart-title">项目基本信息</div>
          <div class="info-list">
            <div class="info-item" v-for="(value, key) in basicInfo" :key="key">
              <span class="label">{{ key }}:</span>
              <span class="value">{{ value }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="grid-item">
        <div class="chart-box">
          <div class="chart-title">调用次数和SOC排名</div>
          <div :ref="el => chartRefs[0] = el" class="chart"></div>
        </div>
      </div>

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

      <!-- 中间列 -->
      <div class="grid-item large-chart">
        <div class="chart-box">
          <div class="chart-title">能量流动监控</div>
          <div :ref="el => chartRefs[1] = el" class="chart"></div>
        </div>
      </div>

      <!-- 右侧列 -->
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

      <div class="grid-item">
        <div class="chart-box">
          <div class="chart-title">总功率和总量曲线</div>
          <div :ref="el => chartRefs[2] = el" class="chart"></div>
        </div>
      </div>

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
  '变压器功率': '1000kW',
  '飞轮额定功率': '500kW',
  '电池额定功率': '800kW',
  '电压等级': '380V',
  '飞轮能量': '5kWh',
  '电池能量': '1000kWh'
});

// 动作次数统计
const actionStats = ref([
  { label: '日充电次数', value: 125 },
  { label: '日放电次数', value: 98 },
  { label: '今日动作次数', value: 223 },
  { label: '近一月动作次数', value: '6,542' },
  { label: '近一年动作次数', value: '86,123' }
]);

// 系统状态信息
const statusInfo = ref([
  { label: '场站总SOC', value: '85%', class: 'normal' },
  { label: '电网频率', value: '49.98Hz', class: 'warning' },
  { label: '总指令功率', value: '750kW', class: 'normal' },
  { label: '总反馈功率', value: '738kW', class: 'normal' }
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
  
  .grid-container {
    display: grid;
    grid-template-columns: 30% 40% 30%;
    grid-template-rows: repeat(3, 1fr);
    gap: 15px;
    height: 100%;
    
    .grid-item {
      background: rgba(0, 21, 41, 0.7);
      border: 1px solid rgba(0, 198, 251, 0.3);
      border-radius: 8px;
      padding: 10px;
      
      &.large-chart {
        grid-row: span 3;
      }
    }
  }
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
</style>
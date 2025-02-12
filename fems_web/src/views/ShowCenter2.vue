<template>
  <div class="show-center">
    <div class="grid-container">
      <!-- 左侧信息区域 -->
      <div class="grid-item info-panel">
        <!-- 储能电站信息 -->
        <div class="chart-box">
          <div class="chart-title">储能电站信息</div>
          <div class="info-table">
            <div class="info-row">
              <span class="label">储能电站配置:</span>
              <span class="value">20 / 172</span>
              <span class="unit">MW/kWh</span>
            </div>
            <div class="info-row">
              <span class="label">飞轮储能系统配置:</span>
              <span class="value">20 / 172</span>
              <span class="unit">MW/kWh</span>
            </div>
            <!-- 其他信息行 -->
          </div>
        </div>
        
        <!-- 储能电站运行统计数据 -->
        <div class="chart-box">
          <div class="chart-title">储能电站运行统计数据</div>
          <div class="info-table">
            <!-- 运行统计数据内容 -->
          </div>
        </div>
        
        <!-- 储能电站实时数据 -->
        <div class="chart-box">
          <div class="chart-title">储能电站实时数据</div>
          <div class="info-table">
            <!-- 实时数据内容 -->
          </div>
        </div>
      </div>

      <!-- 中间区域 -->
      <div class="grid-item center-panel">
        <!-- 站点标题 -->
        <div class="station-title">微控厂内测试区</div>
        
        <!-- 站点图片 -->
        <div class="station-image">
          <!-- <img src="../assets/station.jpg" alt="储能电站"> -->
        </div>
        
        <!-- 频率对比分析图表 -->
        <div class="chart-box">
          <div class="chart-title">频率对比分析</div>
          <div ref="frequencyChart" class="chart"></div>
        </div>
      </div>

      <!-- 右侧统计图表 -->
      <div class="grid-item stats-panel">
        <!-- 一次调频里程分布 -->
        <div class="chart-box">
          <div class="chart-title">一次调频里程分布</div>
          <div ref="distributionChart1" class="pie-chart"></div>
        </div>
        
        <!-- 单次动作时长分布 -->
        <div class="chart-box">
          <div class="chart-title">单次动作时长分布</div>
          <div ref="distributionChart2" class="pie-chart"></div>
        </div>
        
        <!-- 电站SOC分布 -->
        <div class="chart-box">
          <div class="chart-title">电站SOC分布</div>
          <div ref="distributionChart3" class="pie-chart"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import * as echarts from 'echarts';

const frequencyChart = ref(null);
const distributionChart1 = ref(null);
const distributionChart2 = ref(null);
const distributionChart3 = ref(null);
const charts = [];

// 生成模拟的时间序列数据
const generateTimeData = () => {
  const data = [];
  let now = new Date();
  for (let i = 0; i < 200; i++) {
    now = new Date(now.getTime() - 1000); // 每秒一个数据点
    data.unshift([
      now.getTime(),
      Math.random() * 4 - 2 // 生成-2到2之间的随机数
    ]);
  }
  return data;
};

// 生成饼图数据
const generatePieData = (type) => {
  switch(type) {
    case 'frequency': // 一次调频里程分布
      return [
        { value: 60, name: '0-15%', itemStyle: { color: '#1890ff' } },
        { value: 14, name: '15-25%', itemStyle: { color: '#36cfc9' } },
        { value: 12, name: '25-45%', itemStyle: { color: '#73d13d' } },
        { value: 10, name: '45-75%', itemStyle: { color: '#ffc53d' } },
        { value: 4, name: '75-100%', itemStyle: { color: '#ff4d4f' } }
      ];
    case 'duration': // 单次动作时长分布
      return [
        { value: 46.7, name: '0-1s', itemStyle: { color: '#1890ff' } },
        { value: 20, name: '1-3s', itemStyle: { color: '#36cfc9' } },
        { value: 15.6, name: '3-7s', itemStyle: { color: '#73d13d' } },
        { value: 13.3, name: '7-15s', itemStyle: { color: '#ffc53d' } },
        { value: 4.4, name: '>15s', itemStyle: { color: '#ff4d4f' } }
      ];
    case 'soc': // 电站SOC分布
      return [
        { value: 100, name: '40-60%', itemStyle: { color: '#73d13d' } }
      ];
  }
};

// 初始化图表
onMounted(() => {
  // 频率对比分析图表
  const freqChart = echarts.init(frequencyChart.value);
  freqChart.setOption({
    grid: {
      top: 30,
      bottom: 30,
      left: 60,
      right: 40
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const date = new Date(params[0].value[0]);
        return `${date.toLocaleTimeString()}<br/>
                频率: ${params[0].value[1].toFixed(3)} Hz`;
      }
    },
    xAxis: {
      type: 'time',
      axisLine: { lineStyle: { color: '#1890ff' } },
      axisLabel: { color: '#fff' },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      name: '频率(Hz)',
      nameTextStyle: { color: '#fff' },
      min: -2,
      max: 2,
      interval: 1,
      axisLine: { lineStyle: { color: '#1890ff' } },
      axisLabel: { color: '#fff' },
      splitLine: {
        show: true,
        lineStyle: { color: 'rgba(24, 144, 255, 0.1)' }
      }
    },
    series: [{
      name: '频率',
      type: 'line',
      data: generateTimeData(),
      lineStyle: { color: '#00ff00', width: 1 },
      symbol: 'none',
      animation: false
    }]
  });
  charts.push(freqChart);

  // 饼图通用配置
  const pieOption = (type, title) => ({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}%'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      textStyle: { color: '#fff' },
      formatter: name => {
        const data = generatePieData(type);
        const item = data.find(item => item.name === name);
        return `${name} ${item.value}%`;
      }
    },
    series: [{
      name: title,
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      label: {
        show: true,
        position: 'inside',
        formatter: '{d}%',
        fontSize: 12,
        color: '#fff'
      },
      labelLine: { show: false },
      emphasis: {
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold'
        }
      },
      data: generatePieData(type)
    }]
  });

  // 初始化三个分布饼图
  const pieCharts = [
    { ref: distributionChart1, type: 'frequency', title: '一次调频里程分布' },
    { ref: distributionChart2, type: 'duration', title: '单次动作时长分布' },
    { ref: distributionChart3, type: 'soc', title: '电站SOC分布' }
  ];

  pieCharts.forEach(({ ref, type, title }) => {
    const chart = echarts.init(ref.value);
    chart.setOption(pieOption(type, title));
    charts.push(chart);
  });

  // 添加定时器更新频率图表数据
  const timer = setInterval(() => {
    const data = freqChart.getOption().series[0].data;
    const now = new Date();
    data.shift();
    data.push([
      now.getTime(),
      Math.random() * 4 - 2
    ]);
    freqChart.setOption({
      series: [{
        data: data
      }]
    });
  }, 1000);

  // 组件卸载时清除定时器
  onUnmounted(() => {
    clearInterval(timer);
  });

  // 窗口大小改变时重绘图表
  window.addEventListener('resize', handleResize);
});

// 清理事件监听
onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  charts.forEach(chart => chart.dispose());
});

// 处理窗口大小改变
const handleResize = () => {
  charts.forEach(chart => chart.resize());
};
</script>

<style lang="scss" scoped>
.show-center {
  width: 100%;
  height: 100%;
  color: white;
  
  .grid-container {
    display: grid;
    grid-template-columns: 25% 50% 25%;
    gap: 10px;
    height: 100%;
    padding: 10px;
    
    .grid-item {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
  }
}

.chart-box {
  background: rgba(0, 21, 41, 0.7);
  border: 1px solid #1890ff;
  border-radius: 4px;
  padding: 10px;
  height: 300px;
  
  .chart-title {
    position: relative;
    color: transparent;
    background: linear-gradient(120deg, #1890ff 20%, #00c6fb 40%, #1890ff 60%, #00c6fb 80%);
    background-size: 200% auto;
    background-clip: text;
    -webkit-background-clip: text;
    font-size: 18px;
    font-weight: bold;
    padding: 8px 0;
    margin-bottom: 5px;
    border-bottom: 1px solid rgba(24, 144, 255, 0.3);
    animation: shine 3s linear infinite;
    text-shadow: 0 0 10px rgba(24, 144, 255, 0.3);
    
    &::after {
      content: '';
      position: absolute;
      bottom: -1px;
      left: 0;
      width: 100%;
      height: 2px;
      background: linear-gradient(90deg, 
        transparent,
        #00c6fb,
        #1890ff,
        #00c6fb,
        transparent
      );
      animation: flow 3s linear infinite;
    }
  }
}

@keyframes shine {
  0% { background-position: 200% center; }
  100% { background-position: -200% center; }
}

@keyframes flow {
  0% { background-position: -200% center; }
  100% { background-position: 200% center; }
}

.info-table {
  .info-row {
    display: flex;
    padding: 8px 0;
    
    .label {
      color: #8b8b8b;
      flex: 2;
    }
    
    .value {
      color: #00c6fb;
      flex: 1;
      text-align: right;
    }
    
    .unit {
      color: #8b8b8b;
      margin-left: 5px;
      width: 60px;
    }
  }
}

.station-title {
  text-align: center;
  font-size: 24px;
  color: #00c6fb;
  padding: 10px 0;
}

.station-image {
  flex: 1;
  margin: 10px 0;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 4px;
  }
}

.chart {
  height: 200px;
}

.pie-chart {
  height: 246px;
}
</style>
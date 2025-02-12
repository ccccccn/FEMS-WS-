<template>
  <div class="show-center">
    <div class="grid-container">
      <!-- 左侧信息区域 -->
      <div class="grid-item info-panel">
        <!-- 储能电站信息 -->
        <div class="chart-box">
          <div class="chart-title">储能电站信息</div>
          <div class="info-table">
            <div class="info-row" v-for="(item, key) in stationInfo" :key="key">
              <span class="label">{{ key }}</span>
              <span class="value">{{ item.value }}</span>
              <span class="unit">{{ item.unit }}</span>
            </div>
          </div>
        </div>
        
        <!-- 储能电站运行统计数据 -->
        <div class="chart-box">
          <div class="chart-title">储能电站运行统计数据</div>
          <div class="stats-table">
            <div class="info-row" v-for="(item, key) in stationInfo" :key="key">
                <span class="label">{{ key }}</span>
                <span class="value">{{ item.value }}</span>
                <span class="unit">{{ item.unit }}</span>
            </div>
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
        <div class="station-title">微控厂内测试区</div>
        <div ref="mapContainer" class="station-map"></div>
        
        <!-- 将频率对比分析区域移到地图下方 -->
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
import L from 'leaflet';


const frequencyChart = ref(null);
const distributionChart1 = ref(null);
const distributionChart2 = ref(null);
const distributionChart3 = ref(null);
const charts = [];
const mapContainer = ref(null);

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

// 储能电站信息
const stationInfo = ref({
  '储能电站配置': { value: '20 / 172', unit: 'MW/kWh' },
  '飞轮储能系统配置': { value: '20 / 172', unit: 'MW/kWh' },
  '电化学储能系统配置': { value: '20 / 20', unit: 'MW/kWh' },
  '总储能支路数': { value: '2', unit: '个' },
  '飞轮储能支路数': { value: '1', unit: '个' },
  '电化学储能支路数': { value: '1', unit: '个' },
});

// 储能电站运行统计数据
const stationStats = ref({
  '总充电次数': 500,
  '总放电次数': 480,
  '平均充电功率': '15 MW',
  '平均放电功率': '14 MW',
  '最大充电功率': '20 MW',
  '最大放电功率': '19 MW'
});

// 初始化图表
onMounted(() => {
  console.log('frequencyChart:', frequencyChart.value); // 检查 frequencyChart 是否为 null
  if (frequencyChart.value) {
    const chart = echarts.init(frequencyChart.value);
    chart.setOption({
      tooltip: {
        trigger: 'axis',
        formatter: function(params) {
          const time = new Date(params[0].value[0]).toLocaleTimeString();
          const power = params[0].value[1].toFixed(2);
          const frequency = params[1].value[1].toFixed(3);
          return `${time}<br/>有功功率: ${power} kW<br/>频率: ${frequency} Hz`;
        }
      },
      xAxis: {
        type: 'time',
        axisLine: { lineStyle: { color: '#1890ff' } },
        axisLabel: { color: '#fff' },
        splitLine: { show: false }
      },
      yAxis: [
        {
          type: 'value',
          name: '有功功率 (kW)',
          min: -20,
          max: 20,
          position: 'left',
          axisLine: { lineStyle: { color: '#1890ff' } },
          axisLabel: { color: '#fff' },
          splitLine: { show: false }
        },
        {
          type: 'value',
          name: '频率 (Hz)',
          min: 48,
          max: 52,
          position: 'right',
          axisLine: { lineStyle: { color: '#ff4d4f' } },
          axisLabel: { color: '#fff' },
          splitLine: { show: false }
        }
      ],
      series: [
        {
          name: '有功功率',
          type: 'line',
          data: generatePowerData(),
          lineStyle: { color: '#00c6fb', width: 1 },
          yAxisIndex: 0,
          symbol: 'none',
          animation: false
        },
        {
          name: '频率',
          type: 'line',
          data: generateFrequencyData(),
          lineStyle: { color: '#ff4d4f', width: 1 },
          yAxisIndex: 1,
          symbol: 'none',
          animation: false
        }
      ]
    });

    // Update data every second
    setInterval(() => {
      updateChartData(chart);
    }, 1000);
  }

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

  // 窗口大小改变时重绘图表
  window.addEventListener('resize', handleResize);

  if (mapContainer.value) {
    const map = L.map(mapContainer.value).setView([39.9042, 116.4074], 10);

    L.tileLayer('https://webrd02.is.autonavi.com/appmaptile?style=7&x={x}&y={y}&z={z}', {
      maxZoom: 18,
      attribution: 'Map data © <a href="https://www.amap.com/">高德地图</a>'
    }).addTo(map);

    // 添加标记
    L.marker([39.9042, 116.4074]).addTo(map)
      .bindPopup('储能电站')
      .openPopup();
  }
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

function generatePowerData() {
  const data = [];
  let now = new Date();
  for (let i = 0; i < 200; i++) {
    now = new Date(now.getTime() - 1000);
    data.unshift([now.getTime(), Math.random() * 40 - 20]);
  }
  return data;
}

function generateFrequencyData() {
  const data = [];
  let now = new Date();
  for (let i = 0; i < 200; i++) {
    now = new Date(now.getTime() - 1000);
    data.unshift([now.getTime(), Math.random() * 4 + 48]);
  }
  return data;
}

function updateChartData(chart) {
  const powerData = chart.getOption().series[0].data;
  const frequencyData = chart.getOption().series[1].data;
  const now = new Date();

  powerData.shift();
  powerData.push([now.getTime(), Math.random() * 40 - 20]);

  frequencyData.shift();
  frequencyData.push([now.getTime(), Math.random() * 4 + 48]);

  chart.setOption({
    series: [
      { data: powerData },
      { data: frequencyData }
    ]
  });
}
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
  background: none;
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
    padding: 12px ;
    
    .label {
      color: #fcfcfc;
      flex: 2;
    }
    
    .value {
      color: #00c6fb;
      flex: 1;
      text-align: center;
    }
    
    .unit {
      color: #8b8b8b;
      margin-left: 30px;
      margin-right: 80px;
      width: 10px;
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
  height: 250px;
}

.pie-chart {
  height: 250px;
}

.stats-table {
  .stats-row {
    display: flex;
    padding: 8px 50px;
    
    .label {
      color: #8b8b8b;
      flex: 2;
    }
    
    .value {
      color: #00c6fb;
      flex: 1;
      text-align: right;
    }
  }
}

.station-map {
  height: 552px;
  width: 100%;
  border-radius: 4px;
  overflow: hidden;
}
</style>

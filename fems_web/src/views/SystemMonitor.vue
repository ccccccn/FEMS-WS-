<template>
  <div class="system-monitor">
    <!-- 顶部状态卡片 -->
    <div class="status-cards">
      <div class="status-card" v-for="(stat, index) in systemStats" :key="index">
        <div class="card-icon">
          <component :is="stat.icon" />
        </div>
        <div class="card-info">
          <div class="card-title">{{ stat.title }}</div>
          <div class="card-value" :class="stat.status">{{ stat.value }}</div>
        </div>
      </div>
    </div>

    <!-- 主要监控区域 -->
    <div class="monitor-grid">
      <!-- CPU使用率 -->
      <div class="monitor-card">
        <div class="card-header">
          <h3>CPU使用率</h3>
          <div class="card-extra">
            <a-tag :color="getCpuStatusColor(cpuUsage)">{{ cpuUsage }}%</a-tag>
          </div>
        </div>
        <div class="chart-container" ref="cpuChart"></div>
      </div>

      <!-- 内存使用率 -->
      <div class="monitor-card">
        <div class="card-header">
          <h3>内存使用率</h3>
          <div class="card-extra">
            <a-tag :color="getMemoryStatusColor(memoryUsage)">{{ memoryUsage }}%</a-tag>
          </div>
        </div>
        <div class="chart-container" ref="memoryChart"></div>
      </div>

      <!-- 网络流量 -->
      <div class="monitor-card">
        <div class="card-header">
          <h3>网络流量</h3>
          <div class="card-extra">
            <a-tag color="blue">上行: {{ networkUp }} MB/s</a-tag>
            <a-tag color="green">下行: {{ networkDown }} MB/s</a-tag>
          </div>
        </div>
        <div class="chart-container" ref="networkChart"></div>
      </div>

      <!-- 磁盘使用率 -->
      <div class="monitor-card">
        <div class="card-header">
          <h3>磁盘使用率</h3>
          <div class="card-extra">
            <a-tag :color="getDiskStatusColor(diskUsage)">{{ diskUsage }}%</a-tag>
          </div>
        </div>
        <div class="chart-container" ref="diskChart"></div>
      </div>
    </div>

    <!-- 系统日志 -->
    <div class="system-logs">
      <div class="card-header">
        <h3>系统日志</h3>
        <a-button type="primary" size="small" @click="refreshLogs">刷新</a-button>
      </div>
      <a-table :columns="logColumns" :data-source="logData" :scroll="{ y: 240 }">
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'level'">
            <a-tag :color="getLogLevelColor(record.level)">{{ record.level }}</a-tag>
          </template>
        </template>
      </a-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import * as echarts from 'echarts';
import { 
  DashboardOutlined, 
  CloudServerOutlined, 
  AlertOutlined, 
  CheckCircleOutlined 
} from '@ant-design/icons-vue';

// 系统状态数据
const systemStats = ref([
  { 
    title: '系统状态', 
    value: '正常运行', 
    status: 'normal',
    icon: CheckCircleOutlined 
  },
  { 
    title: '运行时间', 
    value: '7天12小时', 
    status: 'info',
    icon: DashboardOutlined 
  },
  { 
    title: '服务器数量', 
    value: '12台', 
    status: 'info',
    icon: CloudServerOutlined 
  },
  { 
    title: '告警数量', 
    value: '2条', 
    status: 'warning',
    icon: AlertOutlined 
  }
]);

// 使用率数据
const cpuUsage = ref(45);
const memoryUsage = ref(60);
const diskUsage = ref(75);
const networkUp = ref(1.2);
const networkDown = ref(2.5);

// 图表实例
const charts = ref({});
const cpuChart = ref(null);
const memoryChart = ref(null);
const networkChart = ref(null);
const diskChart = ref(null);

// 日志表格列定义
const logColumns = [
  {
    title: '时间',
    dataIndex: 'time',
    key: 'time',
    width: 180
  },
  {
    title: '级别',
    dataIndex: 'level',
    key: 'level',
    width: 100
  },
  {
    title: '内容',
    dataIndex: 'content',
    key: 'content'
  }
];

// 日志数据
const logData = ref([
  {
    key: '1',
    time: '2024-01-20 10:00:00',
    level: 'INFO',
    content: '系统启动成功'
  },
  {
    key: '2',
    time: '2024-01-20 10:01:23',
    level: 'WARNING',
    content: 'CPU使用率超过80%'
  }
  // ... 更多日志数据
]);

// 初始化图表
const initCharts = () => {
  // CPU使用率图表
  const cpuChartInstance = echarts.init(cpuChart.value);
  charts.value.cpu = cpuChartInstance;
  cpuChartInstance.setOption({
    title: { show: false },
    tooltip: { trigger: 'axis' },
    grid: {
      top: 10,
      right: 20,
      bottom: 20,
      left: 50
    },
    xAxis: {
      type: 'category',
      data: Array.from({length: 10}, (_, i) => i),
      axisLabel: { color: '#fff' }
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLabel: { color: '#fff' }
    },
    series: [{
      data: Array.from({length: 10}, () => Math.floor(Math.random() * 100)),
      type: 'line',
      smooth: true,
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(0, 198, 251, 0.5)' },
          { offset: 1, color: 'rgba(0, 198, 251, 0.1)' }
        ])
      },
      lineStyle: { width: 2, color: '#00c6fb' },
      itemStyle: { color: '#00c6fb' }
    }]
  });

  // 内存使用率图表
  const memoryChartInstance = echarts.init(memoryChart.value);
  charts.value.memory = memoryChartInstance;
  memoryChartInstance.setOption({
    series: [{
      type: 'gauge',
      progress: { show: true },
      detail: { 
        valueAnimation: true,
        formatter: '{value}%',
        color: '#fff'
      },
      axisLabel: { color: '#fff' },
      data: [{ value: memoryUsage.value }]
    }]
  });

  // 网络流量图表
  const networkChartInstance = echarts.init(networkChart.value);
  charts.value.network = networkChartInstance;
  networkChartInstance.setOption({
    tooltip: { trigger: 'axis' },
    legend: {
      data: ['上行', '下行'],
      textStyle: { color: '#fff' }
    },
    grid: {
      top: 30,
      right: 20,
      bottom: 20,
      left: 50
    },
    xAxis: {
      type: 'category',
      data: Array.from({length: 10}, (_, i) => i),
      axisLabel: { color: '#fff' }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#fff' }
    },
    series: [
      {
        name: '上行',
        type: 'line',
        data: Array.from({length: 10}, () => Math.random() * 5),
        smooth: true
      },
      {
        name: '下行',
        type: 'line',
        data: Array.from({length: 10}, () => Math.random() * 8),
        smooth: true
      }
    ]
  });

  // 磁盘使用率图表
  const diskChartInstance = echarts.init(diskChart.value);
  charts.value.disk = diskChartInstance;
  diskChartInstance.setOption({
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      label: {
        show: true,
        formatter: '{b}: {c}%',
        color: '#fff'
      },
      data: [
        { value: diskUsage.value, name: '已使用' },
        { value: 100 - diskUsage.value, name: '可用' }
      ]
    }]
  });
};

// 更新图表数据
const updateCharts = () => {
  // 更新CPU数据
  const newCpuData = charts.value.cpu.getOption().series[0].data;
  newCpuData.shift();
  newCpuData.push(Math.floor(Math.random() * 100));
  charts.value.cpu.setOption({
    series: [{ data: newCpuData }]
  });

  // 更新内存数据
  memoryUsage.value = Math.floor(Math.random() * 40 + 40);
  charts.value.memory.setOption({
    series: [{ data: [{ value: memoryUsage.value }] }]
  });

  // 更新网络数据
  const option = charts.value.network.getOption();
  option.series.forEach(series => {
    series.data.shift();
    series.data.push(Math.random() * (series.name === '上行' ? 5 : 8));
  });
  charts.value.network.setOption(option);
};

// 状态颜色
const getCpuStatusColor = (usage) => {
  if (usage > 90) return 'red';
  if (usage > 70) return 'orange';
  return 'green';
};

const getMemoryStatusColor = (usage) => {
  if (usage > 90) return 'red';
  if (usage > 70) return 'orange';
  return 'green';
};

const getDiskStatusColor = (usage) => {
  if (usage > 90) return 'red';
  if (usage > 70) return 'orange';
  return 'green';
};

const getLogLevelColor = (level) => {
  switch (level) {
    case 'ERROR': return 'red';
    case 'WARNING': return 'orange';
    case 'INFO': return 'blue';
    default: return 'default';
  }
};

// 刷新日志
const refreshLogs = () => {
  // 模拟刷新日志
  const newLog = {
    key: Date.now().toString(),
    time: new Date().toLocaleString(),
    level: ['INFO', 'WARNING', 'ERROR'][Math.floor(Math.random() * 3)],
    content: '系统状态更新...'
  };
  logData.value = [newLog, ...logData.value.slice(0, 9)];
};

// 生命周期钩子
let updateTimer = null;

onMounted(() => {
  initCharts();
  updateTimer = setInterval(updateCharts, 3000);
  window.addEventListener('resize', () => {
    Object.values(charts.value).forEach(chart => chart?.resize());
  });
});

onUnmounted(() => {
  clearInterval(updateTimer);
  Object.values(charts.value).forEach(chart => chart?.dispose());
});
</script>

<style lang="scss" scoped>
.system-monitor {
  height: 100%;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  box-sizing: border-box;
  
  .status-cards {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    
    .status-card {
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid rgba(0, 198, 251, 0.3);
      border-radius: 8px;
      padding: 15px;
      display: flex;
      align-items: center;
      gap: 15px;
      
      .card-icon {
        font-size: 24px;
        color: #00c6fb;
      }
      
      .card-info {
        .card-title {
          color: #fff;
          font-size: 14px;
          margin-bottom: 5px;
        }
        
        .card-value {
          font-size: 18px;
          font-weight: bold;
          
          &.normal { color: #52c41a; }
          &.warning { color: #faad14; }
          &.error { color: #f5222d; }
          &.info { color: #00c6fb; }
        }
      }
    }
  }
  
  .monitor-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(2, 1fr);
    gap: 20px;
    flex: 1;
    
    .monitor-card {
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid rgba(0, 198, 251, 0.3);
      border-radius: 8px;
      padding: 15px;
      display: flex;
      flex-direction: column;
      
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        
        h3 {
          color: #FFD700;
          margin: 0;
          font-size: 16px;
        }
        
        .card-extra {
          display: flex;
          gap: 10px;
        }
      }
      
      .chart-container {
        flex: 1;
        min-height: 0;
      }
    }
  }
  
  .system-logs {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(0, 198, 251, 0.3);
    border-radius: 8px;
    padding: 15px;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 15px;
      
      h3 {
        color: #FFD700;
        margin: 0;
        font-size: 16px;
      }
    }
    
    :deep(.ant-table) {
      background: transparent;
      
      .ant-table-thead > tr > th {
        background: rgba(0, 198, 251, 0.1);
        color: #FFD700;
      }
      
      .ant-table-tbody > tr > td {
        border-bottom: 1px solid rgba(0, 198, 251, 0.1);
        color: #fff;
      }
      
      .ant-table-tbody > tr:hover > td {
        background: rgba(0, 198, 251, 0.1);
      }
    }
  }
}
</style> 
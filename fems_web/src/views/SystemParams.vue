<template>
  <div class="system-params">
    <div class="grid-container">
      <!-- 参数配置卡片 -->
      <div class="param-card">
        <div class="card-header">
          <h3>基本参数配置</h3>
          <a-button type="primary" @click="handleSave">保存配置</a-button>
        </div>
        <div class="card-content">
          <a-form :model="formState" layout="vertical">
            <a-row :gutter="16">
              <a-col :span="8">
                <a-form-item label="系统名称">
                  <a-input v-model:value="formState.systemName" />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item label="运行模式">
                  <a-select v-model:value="formState.operationMode">
                    <a-select-option value="auto">自动模式</a-select-option>
                    <a-select-option value="manual">手动模式</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item label="采样频率(Hz)">
                  <a-input-number v-model:value="formState.samplingRate" :min="1" :max="1000" />
                </a-form-item>
              </a-col>
            </a-row>
            
            <a-row :gutter="16">
              <a-col :span="8">
                <a-form-item label="报警阈值">
                  <a-input-number v-model:value="formState.alarmThreshold" :min="0" :max="100" />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item label="数据保存周期(天)">
                  <a-input-number v-model:value="formState.dataSaveDays" :min="1" :max="365" />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item label="备份频率">
                  <a-select v-model:value="formState.backupFrequency">
                    <a-select-option value="daily">每天</a-select-option>
                    <a-select-option value="weekly">每周</a-select-option>
                    <a-select-option value="monthly">每月</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
            </a-row>
          </a-form>
        </div>
      </div>

      <!-- 参数监控图表 -->
      <div class="param-charts">
        <div class="chart-container">
          <div ref="chart1" class="chart"></div>
        </div>
        <div class="chart-container">
          <div ref="chart2" class="chart"></div>
        </div>
      </div>

      <!-- 参数列表 -->
      <div class="param-table">
        <a-table :columns="columns" :data-source="tableData" :pagination="false">
          <template #headerCell="{ column }">
            <template v-if="column.key === 'action'">
              <span>操作</span>
            </template>
          </template>

          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'action'">
              <a-space>
                <a @click="handleEdit(record)">编辑</a>
                <a @click="handleDelete(record)">删除</a>
              </a-space>
            </template>
          </template>
        </a-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import * as echarts from 'echarts';
import { message } from 'ant-design-vue';

// 表单数据
const formState = ref({
  systemName: '飞轮能量管理系统',
  operationMode: 'auto',
  samplingRate: 100,
  alarmThreshold: 80,
  dataSaveDays: 30,
  backupFrequency: 'daily'
});

// 表格列定义
const columns = [
  {
    title: '参数名称',
    dataIndex: 'name',
    key: 'name',
  },
  {
    title: '参数值',
    dataIndex: 'value',
    key: 'value',
  },
  {
    title: '单位',
    dataIndex: 'unit',
    key: 'unit',
  },
  {
    title: '更新时间',
    dataIndex: 'updateTime',
    key: 'updateTime',
  },
  {
    title: '操作',
    key: 'action',
  }
];

// 表格数据
const tableData = ref([
  {
    key: '1',
    name: '系统电压',
    value: '220',
    unit: 'V',
    updateTime: '2024-01-20 10:00:00'
  },
  {
    key: '2',
    name: '系统电流',
    value: '10',
    unit: 'A',
    updateTime: '2024-01-20 10:00:00'
  },
  // ... 更多数据
]);

// 图表实例
const chart1 = ref(null);
const chart2 = ref(null);
let chartInstance1 = null;
let chartInstance2 = null;

// 初始化图表
const initCharts = () => {
  // 第一个图表
  chartInstance1 = echarts.init(chart1.value);
  chartInstance1.setOption({
    title: {
      text: '参数趋势图',
      textStyle: { color: '#fff' }
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      axisLabel: { color: '#fff' }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#fff' }
    },
    series: [{
      data: [820, 932, 901, 934, 1290, 1330, 1320],
      type: 'line',
      smooth: true
    }]
  });

  // 第二个图表
  chartInstance2 = echarts.init(chart2.value);
  chartInstance2.setOption({
    title: {
      text: '参数分布图',
      textStyle: { color: '#fff' }
    },
    tooltip: {
      trigger: 'item'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: [
        { value: 1048, name: '参数A' },
        { value: 735, name: '参数B' },
        { value: 580, name: '参数C' },
        { value: 484, name: '参数D' }
      ]
    }]
  });
};

// 处理保存
const handleSave = () => {
  message.success('配置保存成功');
};

// 处理编辑
const handleEdit = (record) => {
  console.log('编辑:', record);
};

// 处理删除
const handleDelete = (record) => {
  console.log('删除:', record);
};

// 生命周期钩子
onMounted(() => {
  initCharts();
  window.addEventListener('resize', () => {
    chartInstance1?.resize();
    chartInstance2?.resize();
  });
});

onUnmounted(() => {
  window.removeEventListener('resize', () => {
    chartInstance1?.resize();
    chartInstance2?.resize();
  });
  chartInstance1?.dispose();
  chartInstance2?.dispose();
});
</script>

<style lang="scss" scoped>
.system-params {
  height: 100%;
  padding: 20px;
  box-sizing: border-box;
  
  .grid-container {
    display: grid;
    grid-template-rows: auto 1fr auto;
    gap: 20px;
    height: 100%;
    
    .param-card {
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid rgba(0, 198, 251, 0.3);
      border-radius: 8px;
      padding: 20px;
      
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        
        h3 {
          color: #FFD700;
          margin: 0;
        }
      }
      
      .card-content {
        :deep(.ant-form-item-label > label) {
          color: #fff;
        }
        
        :deep(.ant-input),
        :deep(.ant-input-number),
        :deep(.ant-select-selector) {
          background: rgba(255, 255, 255, 0.1);
          border-color: rgba(0, 198, 251, 0.3);
          color: #fff;
          
          &:hover,
          &:focus {
            border-color: #00c6fb;
          }
        }
      }
    }
    
    .param-charts {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      
      .chart-container {
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(0, 198, 251, 0.3);
        border-radius: 8px;
        padding: 20px;
        
        .chart {
          height: 300px;
        }
      }
    }
    
    .param-table {
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid rgba(0, 198, 251, 0.3);
      border-radius: 8px;
      padding: 20px;
      
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
}
</style> 
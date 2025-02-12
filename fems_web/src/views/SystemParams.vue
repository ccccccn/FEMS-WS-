<template>
  <div class="system-params">
    <table class="data-table">
      <thead>
        <tr>
          <th>飞轮舱号</th>
          <th v-for="flywheel in flywheelNumbers" :key="flywheel.id" @click="showDetails(flywheel.id)">飞轮舱{{ flywheel.id }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(info, index) in infoList" :key="info.id">
          <td class="info-cell">{{ info.name }}</td>
          <td v-for="flywheel in flywheelNumbers" :key="flywheel.id" class="data-cell">
            <div v-if="info.id === 22">
              <div class="status-box">RTU</div>
              <div class="status-box">TCP</div>
            </div>
            <div v-if="flywheel.params && flywheel.params[index]?.status" class="status-circle" :class="flywheel.params[index].status"></div>
            <div v-else class="param-value">{{ flywheel.params && flywheel.params[index]?.value }}</div>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="selectedFlywheel" class="modal">
      <div class="modal-content">
        <span class="close" @click="closeDetails">&times;</span>
        <h2>飞轮舱{{ selectedFlywheel.id }} 详细信息</h2>
        <div class="table-container">
          <table class="details-table">
            <thead>
              <tr>
                <th></th>
                <th>F1</th>
                <th>F2</th>
                <th>F3</th>
                <th>F4</th>
                <th>F5</th>
                <th>F6</th>
                <th>F7</th>
                <th>F8</th>
                <th>PCS</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>系统状态</td>
                <td>100</td>
                <td>100</td>
                <td>100</td>
                <td>100</td>
                <td>100</td>
                <td>100</td>
                <td>100</td>
                <td>100</td>
                <td>100</td>
              </tr>
              <tr>
                <td>飞轮状态</td>
                <td>100</td>
                <td>100</td>
                <td>100</td>
                <td>100</td>
                <td>100</td>
                <td>100</td>
                <td>100</td>
                <td>100</td>
              </tr>
              <tr>
                <td>飞轮真空度(mTorr)</td>
                <td>100</td>
                <td>100</td>
                <td>100</td>
                <td>100</td>
                <td>100</td>
                <td>100</td>
                <td>100</td>
                <td>100</td>
              </tr>
              <tr>
                <td>飞轮温度(℃)</td>
                <td>25</td>
                <td>25</td>
                <td>25</td>
                <td>25</td>
                <td>25</td>
                <td>25</td>
                <td>25</td>
                <td>25</td>
              </tr>
              <tr>
                <td>飞轮转速(rpm)</td>
                <td>3000</td>
                <td>3000</td>
                <td>3000</td>
                <td>3000</td>
                <td>3000</td>
                <td>3000</td>
                <td>3000</td>
                <td>3000</td>
              </tr>
              <tr>
                <td>飞轮SOC(%)</td>
                <td>80</td>
                <td>80</td>
                <td>80</td>
                <td>80</td>
                <td>80</td>
                <td>80</td>
                <td>80</td>
                <td>80</td>
              </tr>
              <tr>
                <td>飞轮功率(kW)</td>
                <td>50</td>
                <td>50</td>
                <td>50</td>
                <td>50</td>
                <td>50</td>
                <td>50</td>
                <td>50</td>
                <td>50</td>
              </tr>
              <tr>
                <td>IGBT温度(℃)</td>
                <td>60</td>
                <td>60</td>
                <td>60</td>
                <td>60</td>
                <td>60</td>
                <td>60</td>
                <td>60</td>
                <td>60</td>
              </tr>
              <tr>
                <td>一次电压(V)</td>
                <td>400</td>
                <td>400</td>
                <td>400</td>
                <td>400</td>
                <td>400</td>
                <td>400</td>
                <td>400</td>
                <td>400</td>
              </tr>
              <tr>
                <td>通信状态</td>
                <td>正常</td>
                <td>正常</td>
                <td>正常</td>
                <td>正常</td>
                <td>正常</td>
                <td>正常</td>
                <td>正常</td>
                <td>正常</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// 左侧文字信息
const infoList = ref([
  { id: 1, name: '系统SOC(%)' },
  { id: 2, name: '系统状态' },
  { id: 3, name: '系统模式' },
  { id: 4, name: '一级报警' },
  { id: 5, name: '二级报警' },
  { id: 6, name: '三级报警' },
  { id: 7, name: '四级报警' },
  { id: 8, name: '火警' },
  { id: 9, name: '火警急停' },
  { id: 10, name: '硬件急停' },
  { id: 11, name: '软件急停' },
  { id: 12, name: '最大充电功率(kW)' },
  { id: 13, name: '最大放电功率(kW)' },
  { id: 14, name: '飞轮运行数量（个）' },
  { id: 15, name: '飞轮就绪数量（个）' },
  { id: 16, name: '实时有功功率(kW)' },
  { id: 17, name: '功率给定(kW)' },
  { id: 18, name: '飞轮功率(kW)' },
  { id: 19, name: 'IGBT温度(℃)' },
  { id: 20, name: '一次电压(V)' },
  { id: 21, name: '通讯状态' },
]);

// 飞轮舱实时数据
const flywheelNumbers = ref(Array.from({ length: 20 }, (_, i) => ({
  id: i + 1,
  params: [
    { id: 1, value: `${Math.floor(Math.random() * 100)}` },
    { id: 2, status: 'running', statusText: '本地运行' },
    { id: 3, status: 'running', statusText: 'FCCS协控' },
    { id: 4, status: 'running' },
    { id: 5, status: 'running' },
    { id: 6, status: 'running' },
    { id: 7, status: 'running' },
    { id: 8, status: 'running' },
    { id: 9, status: 'running' },
    { id: 10, status: 'running' },
    { id: 11, status: 'running' },
    { id: 13, value: `${Math.floor(Math.random() * 1000)}` },
    { id: 14, value: `${Math.floor(Math.random() * 1000)}` },
    { id: 15, value: `${Math.floor(Math.random() * 10)}` },
    { id: 16, value: `${Math.floor(Math.random() * 10)}` },
    { id: 17, value: `${Math.floor(Math.random() * 1000)}` },
    { id: 18, value: `${Math.floor(Math.random() * 1000)}` },
    { id: 19, value: `${Math.floor(Math.random() * 1000)}` },
    { id: 20, value: `${Math.floor(Math.random() * 100)}` },
    { id: 21, value: `${Math.floor(Math.random() * 1000)}` },
    { id: 22, value: '' },
  ]
})));

// 选中的飞轮舱
const selectedFlywheel = ref(null);

// 显示详细信息
function showDetails(id) {
  selectedFlywheel.value = flywheelNumbers.value.find(flywheel => flywheel.id === id);
}

// 关闭详细信息
function closeDetails() {
  selectedFlywheel.value = null;
}

// 暴露函数给模板
defineExpose({ showDetails, closeDetails });
</script>

<style scoped>
.system-params {
  color: #fff;
  padding: 10px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  border: 1px solid #08bff7;
  padding: 10.8px;
  text-align: center;
}
td:first-child {
  border: none; /* 取消第一列框线 */
}
th {
  /* background-color: #003366; */
  color: #ffffff;
  font-weight: bold;
  border: none; /* 取消第一行框线 */
}

.info-cell {
  /* background-color: #001529; */
  font-weight: bold;
}

/* .data-cell {
  background-color: #002140;
} */

.status-circle {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  margin: 0 auto;
}

.status-circle.running {
  background-color: #3d5f2c;
}

.status-circle.normal {
  background-color: #1890ff;
}

.status-circle.warning {
  background-color: #ff4d4f;
}

.status-circle.error {
  background-color: #666666;
}
.status-box {
  display: inline-block;
  width: 25px;
  height: 10px;
  background-color: #59ff18;
  color: #fff;
  /* line-height: 2px; */
  margin: 0 2px;
  /* border-radius: 4px; */
  font-size: 10px;
}
.modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);

  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.modal-content {
  width: 100%;
  height: 100%;
  padding: 10px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.close {
  position: absolute;
  top: 10px;
  right: 20px;
  font-size: 24px;
  cursor: pointer;
  color: #fff;
}

.table-container {
  flex: 1;
  overflow: auto;
}

.details-table {
  width: 100%;
  height: 100%;
  border-collapse: collapse;
}

.details-table th, .details-table td {
  border: 1px solid #08bff7;
  padding: 8px;
  text-align: center;
}

.details-table th {
  background-color: #003366;
  color: #ffffff;
  font-weight: bold;
}

.details-table td {
  background-color: #001529;
  color: #ffffff;
}
</style> 
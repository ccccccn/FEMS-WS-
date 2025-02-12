<template>
  <div class="alarm-records">
    <h2>报警记录</h2>
    <table>
      <thead>
        <tr>
          <th>时间</th>
          <th>报警类型</th>
          <th>设备名称</th>
          <th>状态</th>
          <th>处理人</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="record in alarmRecords" :key="record.id">
          <td>{{ record.time }}</td>
          <td>{{ record.type }}</td>
          <td>{{ record.device }}</td>
          <td>{{ record.status }}</td>
          <td>{{ record.handler }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// 示例报警记录数据
const alarmRecords = ref([
  { id: 1, time: '2023-10-01 12:00', type: '温度过高', device: '设备A', status: '未处理', handler: '张三' },
  { id: 2, time: '2023-10-02 14:30', type: '电压异常', device: '设备B', status: '已处理', handler: '李四' },
  { id: 3, time: '2023-10-03 09:15', type: '设备故障', device: '设备C', status: '未处理', handler: '王五' },
  // 添加更多记录...
]);
</script>

<style scoped>
.alarm-records {
  padding: 20px;
  /* background-color: #f9f9f9; */
  border-radius: 8px;
}

h2 {
  margin-bottom: 20px;
  color: #073ff7;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 10px;
  text-align: left;
  border: 1px solid #ddd;
}

th {
  background-color: #f2f2f2;
}
</style> 
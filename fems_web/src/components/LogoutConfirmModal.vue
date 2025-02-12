<template>
  <a-modal
    :visible="visible"
    title="退出确认"
    @ok="handleOk"
    @cancel="handleCancel"
    class="custom-modal"
  >
    <div class="logout-content">
      <warning-outlined class="warning-icon" />
      <p class="logout-message">确定要退出系统吗？</p>
    </div>
  </a-modal>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';
import { WarningOutlined } from '@ant-design/icons-vue';

const props = defineProps({
  visible: {
    type: Boolean,
    required: true
  }
});

const emit = defineEmits(['update:visible', 'confirm']);

const handleOk = () => {
  emit('confirm');
  emit('update:visible', false);
};

const handleCancel = () => {
  emit('update:visible', false);
};
</script>

<style lang="scss" scoped>
.custom-modal {
  :deep(.ant-modal-content) {
    background: rgba(0, 21, 41, 0.9);
    border: 1px solid #1890ff;
    
    .ant-modal-header {
      background: transparent;
      border-bottom: 1px solid rgba(24, 144, 255, 0.3);
      
      .ant-modal-title {
        color: #1890ff;
      }
    }
  }
}

.logout-content {
  text-align: center;
  padding: 20px 0;
  
  .warning-icon {
    font-size: 48px;
    color: #faad14;
    margin-bottom: 16px;
  }
  
  .logout-message {
    font-size: 16px;
    color: #0c0c0c;
    margin: 0;
  }
}
</style> 
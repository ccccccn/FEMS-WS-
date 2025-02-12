<template>
  <a-modal
    :visible="visible"
    title="用户设置"
    @cancel="handleCancel"
    :footer="null"
    width="400px"
    class="custom-modal"
  >
    <div class="settings-content">
      <a-form :model="settingsForm" class="settings-form">
        <a-form-item label="主题设置">
          <a-select v-model:value="settingsForm.theme">
            <a-select-option value="dark">深色主题</a-select-option>
            <a-select-option value="light">浅色主题</a-select-option>
            <a-select-option value="auto">跟随系统</a-select-option>
          </a-select>
        </a-form-item>
        
        <a-form-item label="语言设置">
          <a-select v-model:value="settingsForm.language">
            <a-select-option value="zh">中文</a-select-option>
            <a-select-option value="en">English</a-select-option>
          </a-select>
        </a-form-item>
        
        <a-form-item label="通知设置">
          <a-switch 
            v-model:checked="settingsForm.notifications.alert" 
            checked-children="开" 
            un-checked-children="关"
          />
          <span class="setting-label">系统报警</span>
        </a-form-item>
        
        <a-form-item>
          <a-switch 
            v-model:checked="settingsForm.notifications.message" 
            checked-children="开" 
            un-checked-children="关"
          />
          <span class="setting-label">消息提醒</span>
        </a-form-item>
        
        <a-form-item label="安全设置">
          <a-button type="link" @click="showChangePassword = true">
            修改密码
          </a-button>
        </a-form-item>
      </a-form>

      <div class="action-buttons">
        <a-button type="primary" @click="handleSave">保存设置</a-button>
      </div>
    </div>

    <!-- 修改密码弹窗 -->
    <a-modal
      v-model:visible="showChangePassword"
      title="修改密码"
      @ok="handlePasswordChange"
      @cancel="showChangePassword = false"
      class="custom-modal"
    >
      <a-form :model="passwordForm">
        <a-form-item label="当前密码">
          <a-input-password v-model:value="passwordForm.oldPassword" />
        </a-form-item>
        <a-form-item label="新密码">
          <a-input-password v-model:value="passwordForm.newPassword" />
        </a-form-item>
        <a-form-item label="确认新密码">
          <a-input-password v-model:value="passwordForm.confirmPassword" />
        </a-form-item>
      </a-form>
    </a-modal>
  </a-modal>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue';
import { message } from 'ant-design-vue';

const props = defineProps({
  visible: {
    type: Boolean,
    required: true
  }
});

const emit = defineEmits(['update:visible', 'save']);

const showChangePassword = ref(false);
const settingsForm = ref({
  theme: 'dark',
  language: 'zh',
  notifications: {
    alert: true,
    message: true
  }
});

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
});

const handleCancel = () => {
  emit('update:visible', false);
};

const handleSave = () => {
  message.success('设置保存成功');
  emit('save', settingsForm.value);
  handleCancel();
};

const handlePasswordChange = () => {
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    message.error('两次输入的新密码不一致');
    return;
  }
  message.success('密码修改成功');
  showChangePassword.value = false;
  passwordForm.value = {
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  };
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

.settings-content {
  .settings-form {
    :deep(.ant-form-item-label > label) {
      color: #1890ff;
    }
    
    :deep(.ant-select) {
      width: 100%;
      
      .ant-select-selector {
        background: rgba(0, 21, 41, 0.5);
        border-color: #1890ff;
        color: #fff;
      }
    }
    
    .setting-label {
      margin-left: 8px;
      color: #fff;
    }
  }
  
  .action-buttons {
    text-align: center;
    margin-top: 24px;
  }
}
</style> 
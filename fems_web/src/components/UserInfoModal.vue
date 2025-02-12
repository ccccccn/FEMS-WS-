<template>
  <a-modal
    :visible="visible"
    title="用户信息"
    @cancel="handleCancel"
    @ok="handleSave"
    :footer="null"
    width="400px"
    class="custom-modal"
  >
    <div class="user-info-content">
      <div class="avatar-section">
        <a-upload
          v-model:file-list="fileList"
          name="avatar"
          list-type="picture-card"
          class="avatar-uploader"
          :show-upload-list="false"
          action="https://www.mocky.io/v2/5cc8019d300000980a055e76"
          :before-upload="beforeUpload"
          @change="handleChange"
        >
          <div v-if="imageUrl" class="avatar-wrapper">
            <img :src="imageUrl" alt="avatar" />
          </div>
          <div v-else>
            <loading-outlined v-if="loading"></loading-outlined>
            <plus-outlined v-else></plus-outlined>
            <div class="ant-upload-text">上传头像</div>
          </div>
        </a-upload>
      </div>

      <a-form :model="userForm" class="user-form">
        <a-form-item label="用户名">
          <a-input v-model:value="userForm.username" disabled />
        </a-form-item>
        <a-form-item label="真实姓名">
          <a-input v-model:value="userForm.realName" />
        </a-form-item>
        <a-form-item label="手机号码">
          <a-input v-model:value="userForm.phone" />
        </a-form-item>
        <a-form-item label="电子邮箱">
          <a-input v-model:value="userForm.email" />
        </a-form-item>
        <a-form-item label="所属部门">
          <a-input v-model:value="userForm.department" disabled />
        </a-form-item>
        <a-form-item label="角色权限">
          <a-input v-model:value="userForm.role" disabled />
        </a-form-item>
      </a-form>

      <div class="action-buttons">
        <a-button type="primary" @click="handleSave">保存修改</a-button>
      </div>
    </div>
  </a-modal>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue';
import { message } from 'ant-design-vue';
import { LoadingOutlined, PlusOutlined } from '@ant-design/icons-vue';

const props = defineProps({
  visible: {
    type: Boolean,
    required: true
  }
});

const emit = defineEmits(['update:visible', 'save']);

const fileList = ref([]);
const loading = ref(false);
const imageUrl = ref('');
const userForm = ref({
  username: 'admin',
  realName: '管理员',
  phone: '13800138000',
  email: 'admin@example.com',
  department: '系统管理部',
  role: '超级管理员'
});

const handleCancel = () => {
  emit('update:visible', false);
};

const beforeUpload = (file) => {
  const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png';
  if (!isJpgOrPng) {
    message.error('只能上传 JPG/PNG 格式的图片！');
  }
  const isLt2M = file.size / 1024 / 1024 < 2;
  if (!isLt2M) {
    message.error('图片大小不能超过 2MB！');
  }
  return isJpgOrPng && isLt2M;
};

const handleChange = (info) => {
  if (info.file.status === 'uploading') {
    loading.value = true;
    return;
  }
  if (info.file.status === 'done') {
    getBase64(info.file.originFileObj, (url) => {
      loading.value = false;
      imageUrl.value = url;
    });
  }
};

const getBase64 = (img, callback) => {
  const reader = new FileReader();
  reader.addEventListener('load', () => callback(reader.result));
  reader.readAsDataURL(img);
};

const handleSave = () => {
  message.success('保存成功');
  emit('save', userForm.value);
  handleCancel();
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
    
    .ant-modal-close {
      color: #1890ff;
      
      &:hover {
        color: #40a9ff;
      }
    }
  }
}

.user-info-content {
  .avatar-section {
    text-align: center;
    margin-bottom: 24px;
    
    .avatar-uploader {
      :deep(.ant-upload) {
        width: 128px;
        height: 128px;
        border-radius: 50%;
        
        img {
          width: 100%;
          height: 100%;
          border-radius: 50%;
        }
      }
    }
  }
  
  .user-form {
    :deep(.ant-form-item-label > label) {
      color: #1890ff;
    }
    
    :deep(.ant-input) {
      background: rgba(0, 21, 41, 0.5);
      border-color: #1890ff;
      color: #fff;
      
      &:disabled {
        background: rgba(0, 21, 41, 0.8);
        color: #888;
      }
    }
  }
  
  .action-buttons {
    text-align: center;
    margin-top: 24px;
  }
}
</style> 
<template>
  <div class="login-page">
    <div class="video-bg">
      <video src="../assets/img/login/video.mp4" muted autoplay loop></video>
    </div>
    
    <!-- 左上角 logo -->
    <div class="top-logo">
      <img src="../assets/img/login/logo.png" alt="logo">
    </div>

    <div class="login-box">
      <h2 class="gradient-text">飞轮能量管理系统</h2>
      
      <a-form
        :model="formState"
        @finish="handleFinish"
        autocomplete="off"
      >
        <a-form-item
          name="username"
          :rules="[{ required: true, message: '请输入用户名' }]"
        >
          <a-input 
            v-model:value="formState.username" 
            placeholder="用户名"
            allow-clear
          >
            <template #prefix>
              <UserOutlined />
            </template>
          </a-input>
        </a-form-item>

        <a-form-item
          name="password"
          :rules="[{ required: true, message: '请输入密码' }]"
        >
          <a-input-password 
            v-model:value="formState.password" 
            placeholder="密码"
            allow-clear
          >
            <template #prefix>
              <LockOutlined />
            </template>
          </a-input-password>
        </a-form-item>

        <a-form-item
          name="captcha"
          :rules="[{ required: true, message: '请输入验证码' }]"
        >
          <div class="captcha-container">
            <a-input 
              v-model:value="formState.captcha" 
              placeholder="验证码" 
              allow-clear
            />
            <div class="captcha-box" @click="refreshCaptcha">
              <canvas ref="captchaCanvas" width="100" height="32"></canvas>
            </div>
          </div>
        </a-form-item>

        <a-form-item class="remember-box">
          <a-checkbox v-model:checked="formState.remember">
            记住密码
          </a-checkbox>
        </a-form-item>

        <a-form-item>
          <a-button type="primary" html-type="submit" :loading="loading" block>
            登录
          </a-button>
        </a-form-item>
      </a-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';

const router = useRouter();
const store = useStore();
const loading = ref(false);
const captchaCanvas = ref(null);
const captchaText = ref('');

const formState = reactive({
  username: '',
  password: '',
  captcha: '',
  remember: false
});

// 生成随机验证码
const generateCaptcha = () => {
  const canvas = captchaCanvas.value;
  if (!canvas) return;
  
  const ctx = canvas.getContext('2d');
  const chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
  
  // 清空画布
  ctx.fillStyle = '#f7f7f7';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  
  // 生成随机验证码
  let code = '';
  for(let i = 0; i < 4; i++) {
    const char = chars[Math.floor(Math.random() * chars.length)];
    code += char;
    
    ctx.fillStyle = `rgb(${Math.random() * 100}, ${Math.random() * 100}, ${Math.random() * 100})`;
    ctx.font = 'bold 20px Arial';
    
    const rotate = (Math.random() - 0.5) * 0.3;
    ctx.translate(25 * i + 15, 20);
    ctx.rotate(rotate);
    ctx.fillText(char, 0, 0);
    ctx.rotate(-rotate);
    ctx.translate(-(25 * i + 15), -20);
  }
  
  // 添加干扰线
  for(let i = 0; i < 3; i++) {
    ctx.strokeStyle = `rgb(${Math.random() * 200}, ${Math.random() * 200}, ${Math.random() * 200})`;
    ctx.beginPath();
    ctx.moveTo(Math.random() * canvas.width, Math.random() * canvas.height);
    ctx.lineTo(Math.random() * canvas.width, Math.random() * canvas.height);
    ctx.stroke();
  }
  
  captchaText.value = code;
};

// 刷新验证码
const refreshCaptcha = () => {
  generateCaptcha();
};

// 处理登录
const handleFinish = async () => {
  if (formState.captcha.toLowerCase() !== captchaText.value.toLowerCase()) {
    message.error('验证码错误');
    refreshCaptcha();
    return;
  }

  loading.value = true;
  try {
    // 模拟登录成功
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    store.commit('setUser', {
      username: formState.username,
    });
    
    message.success('登录成功');
    router.push('/show_center');
  } catch (error) {
    message.error('登录失败：' + error.message);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  generateCaptcha();
});
</script>

<style lang="scss" scoped>
.login-page {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.top-logo {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 2;
  
  img {
    height: 40px;
  }
}

.gradient-text {
  font-family: 'Arial Black', 'Helvetica Neue', Arial, sans-serif;
  font-size: 28px;
  background: linear-gradient(45deg, #00c6fb, #005bea);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  margin-bottom: 30px;
  text-align: center;
}

.video-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  
  video {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
  }
}

.login-box {
  width: 400px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 10px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.2);
  position: relative;
  z-index: 1;
}

.captcha-container {
  display: flex;
  gap: 10px;
  
  .ant-input {
    flex: 1;
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.2);
    color: white;
    
    &::placeholder {
      color: rgba(255, 255, 255, 0.5);
    }
    
    &:hover,
    &:focus {
      border-color: #00c6fb !important;
      background: rgba(255, 255, 255, 0.15);
    }
  }
  
  .captcha-box {
    width: 100px;
    height: 32px;
    cursor: pointer;
    
    canvas {
      width: 100%;
      height: 100%;
      border-radius: 4px;
    }
  }
}

.remember-box {
  text-align: left;
  margin-bottom: 24px;
}

:deep(.ant-input),
:deep(.ant-input-password) {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  
  input {
    background: transparent;
    color: white !important;
    
    &::placeholder {
      color: rgba(255, 255, 255, 0.5);
    }
  }
  
  .anticon {
    color: rgba(255, 255, 255, 0.5);
  }

  &:hover,
  &:focus {
    border-color: #00c6fb !important;
    background: rgba(255, 255, 255, 0.15);
  }
}

:deep(.ant-checkbox-wrapper) {
  color: white;
  
  .ant-checkbox-checked .ant-checkbox-inner {
    background-color: #00c6fb;
    border-color: #00c6fb;
  }
  
  &:hover {
    .ant-checkbox-inner {
      border-color: #00c6fb;
    }
  }
}

:deep(.ant-btn-primary) {
  height: 40px;
  font-size: 16px;
  background: linear-gradient(45deg, #00c6fb, #005bea);
  border: none;
  
  &:hover {
    background: linear-gradient(45deg, #005bea, #00c6fb);
  }
}

:deep(.ant-input-clear-icon) {
  color: rgba(255, 255, 255, 0.5);
  
  &:hover {
    color: white;
  }
}

:deep(.ant-input-password-icon) {
  color: rgba(255, 255, 255, 0.5);
  
  &:hover {
    color: white;
  }
}
</style>
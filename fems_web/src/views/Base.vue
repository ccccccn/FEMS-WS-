<template>
  <div class="screen-adapter">
    <div class="screen-content">
      <!-- 顶部 header -->
      <div class="header">
        <div class="header-bg"></div>
        <div class="header-content">
          <div class="header-left">
            <img src="../assets/微控矢量图.png" alt="企业logo" class="logo">
            <div class="alert-info">
              <div class="alert-icons">
                <!-- <warning-filled class="alert-icon pulse" /> -->
                <div class="bell-container">
                  <bell-filled class="alert-icon shake" />
                  <a-badge 
                    :count="alertCount" 
                    :offset="[-8, -8]"
                    :size="'small'"
                    class="alert-badge"
                  />
                </div>
              </div>
              <!-- <span class="alert-text">报警信息</span> -->
            </div>
          </div>
          <div class="header-center">
            <div class="system-title">飞轮能量管理系统</div>
          </div>
          <div class="header-right">
            <div class="user-info">
              <span class="user-name">{{ currentUser }}</span>
              <a-dropdown :trigger="['hover']" placement="bottomRight">
                <a-avatar 
                  :size="32" 
                  class="user-avatar"
                  :src="userAvatar || undefined"
                >
                  <template #icon><UserOutlined /></template>
                </a-avatar>
                <template #overlay>
                  <a-menu class="user-menu">
                    <a-menu-item key="1" @click="handleUserInfo">
                      <UserOutlined />
                      <span>用户信息</span>
                    </a-menu-item>
                    <a-menu-item key="2" @click="handleSettings">
                      <SettingOutlined />
                      <span>用户设置</span>
                    </a-menu-item>
                    <a-menu-divider />
                    <a-menu-item key="3" @click="handleLogout">
                      <LogoutOutlined />
                      <span>退出登录</span>
                    </a-menu-item>
                  </a-menu>
                </template>
              </a-dropdown>
              <span class="divider">|</span>
              <span class="time-info">当前时间：{{ currentTime }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 中间内容区域 -->
      <div class="main-content">
        <router-view></router-view>
      </div>

      <!-- 底部按钮区域 -->
      <div class="footer">
        <div class="button-container">
          <button 
            v-for="menu in menu_list" 
            :key="menu.id" 
            class="footer-btn"
            :class="{ 'active': activeButton === menu.id }"
            @click="handleMenuClick(menu)"
          >
            <span class="btn-text">{{ menu.title }}</span>
            <div class="btn-background"></div>
          </button>
        </div>
      </div>
    </div>
  </div>

  <UserInfoModal
    :visible="showUserInfo"
    @update:visible="showUserInfo = $event"
    @save="handleUserInfoSave"
  />
  
  <UserSettingsModal
    :visible="showSettings"
    @update:visible="showSettings = $event"
    @save="handleSettingsSave"
  />
  
  <LogoutConfirmModal
    :visible="showLogoutConfirm"
    @update:visible="showLogoutConfirm = $event"
    @confirm="confirmLogout"
  />
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { 
  UserOutlined, 
  WarningFilled, 
  BellFilled, 
  SettingOutlined, 
  LogoutOutlined 
} from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import UserInfoModal from '../components/UserInfoModal.vue';
import UserSettingsModal from '../components/UserSettingsModal.vue';
import LogoutConfirmModal from '../components/LogoutConfirmModal.vue';

const router = useRouter();
const route = useRoute();
const currentTime = ref('');
const currentUser = ref('管理员');
const activeButton = ref(1);
const userAvatar = ref(''); // 可以设置默认头像路径

// 添加模态框的状态变量
const showUserInfo = ref(false);
const showSettings = ref(false);
const showLogoutConfirm = ref(false);

// 菜单配置
const menu_list = ref([
  { 
    id: 1, 
    title: '首页', 
    path: '/show_center',
    icon: 'home' 
  },
  { 
    id: 2, 
    title: '能量管理', 
    path: '/host',
    icon: 'thunderbolt'
  },
  { 
    id: 3, 
    title: '系统参数', 
    path: '/system_params',
    icon: 'setting'
  },
  { 
    id: 4, 
    title: '系统监控', 
    path: '/system_monitor',
    icon: 'dashboard'
  },
  { 
    id: 5, 
    title: '线路拓扑', 
    path: '/network_topology',
    icon: 'apartment'
  },
  { 
    id: 6, 
    title: '报警记录', 
    path: '/alarm_records',
    icon: 'warning'
  },
  { 
    id: 7, 
    title: '报表系统', 
    path: '/report_system',
    icon: 'bar-chart'
  },
  { 
    id: 8, 
    title: '散热系统', 
    path: '/cooling_system',
    icon: 'cloud'
  },
  { 
    id: 9, 
    title: '系统管理', 
    path: '/system_management',
    icon: 'control'
  }
]);

// 添加报警数量
const alertCount = ref(2);

// 处理菜单点击
const handleMenuClick = (menu) => {
  activeButton.value = menu.id;
  router.push(menu.path);
};

// 用户信息处理
const handleUserInfo = () => {
  showUserInfo.value = true;
};

const handleUserInfoSave = (info) => {
  console.log('保存用户信息:', info);
  message.success('用户信息保存成功');
  // 这里处理保存逻辑
};

// 用户设置处理
const handleSettings = () => {
  showSettings.value = true;
};

const handleSettingsSave = (settings) => {
  console.log('保存设置:', settings);
  message.success('设置保存成功');
  // 这里处理保存逻辑
};

// 退出登录处理
const handleLogout = () => {
  showLogoutConfirm.value = true;
};

const confirmLogout = () => {
  message.success('退出成功');
  router.push('/login');
};

// 更新时间
const updateTime = () => {
  const now = new Date();
  const options = {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  };
  currentTime.value = now.toLocaleString('zh-CN', options).replace(/\//g, '-');
};

// 计算缩放比例
const calculateScale = () => {
  const screenContent = document.querySelector('.screen-content');
  if (!screenContent) return;

  const targetRatio = 1920 / 1080;
  const windowWidth = window.innerWidth;
  const windowHeight = window.innerHeight;
  const currentRatio = windowWidth / windowHeight;

  let scale;
  if (currentRatio > targetRatio) {
    scale = windowHeight / 1080;
  } else {
    scale = windowWidth / 1920;
  }

  screenContent.style.transform = `scale(${scale})`;
};

// 监听窗口大小变化
const handleResize = () => {
  calculateScale();
};

onMounted(() => {
  calculateScale();
  window.addEventListener('resize', handleResize);
  
  updateTime();
  setInterval(updateTime, 1000);
  
  // 根据当前路由设置激活按钮
  const currentMenu = menu_list.value.find(menu => menu.path === route.path);
  if (currentMenu) {
    activeButton.value = currentMenu.id;
  }
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
</script>

<style lang="scss" scoped>
.screen-adapter {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: #000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.screen-content {
  width: 1920px;
  height: 1080px;
  transform-origin: center center;
  position: relative;
  background: url("../assets/img/base/image.png") no-repeat center center;
  background-size: cover;
  display: flex;
  flex-direction: column;
  // 确保元素不会被压缩
  flex-shrink: 0;
}

// 头部样式
.header {
  height: 60px;
  min-height: 60px;
  position: relative;
  color: white;
  overflow: hidden;

  // 背景层
  &-bg {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: url("../assets/img/top.png");
    background-size: 100% 100%;
    background-position: center;
    z-index: 1;
  }

  // 内容层
  &-content {
    position: relative;
    z-index: 2;
    height: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
  }

  &-left {
    width: 200px;
    display: flex;
    align-items: center;
    gap: 20px;

    .logo {
      height: 40px;
    }

    .alert-info {
      display: flex;
      align-items: center;
      gap: 8px;
      color: #ff4d4f;
      font-weight: 500;
      padding: 6px 12px;
      background: rgba(255, 77, 79, 0.1);
      border-radius: 4px;
      border: 1px solid rgba(255, 77, 79, 0.2);
      cursor: pointer;
      transition: all 0.3s ease;
      
      &:hover {
        background: rgba(255, 77, 79, 0.2);
        border-color: rgba(255, 77, 79, 0.3);
      }
      
      .alert-icons {
        display: flex;
        align-items: center;
        gap: 4px;
      }

      .alert-icon {
        font-size: 18px;
        
        &.pulse {
          animation: pulse 2s infinite;
          color: #ff4d4f;
        }
      }
      
      .bell-container {
        position: relative;
        display: inline-flex;
        
        .alert-icon.shake {
          font-size: 18px;
          color: #ff7875;
          animation: shake 2s infinite;
        }
        
        :deep(.alert-badge) {
          position: absolute;
          
          .ant-badge-count {
            font-size: 12px;
            min-width: 16px;
            height: 16px;
            line-height: 16px;
            padding: 0 4px;
            border-radius: 8px;
            background: #ff4d4f;
            box-shadow: 0 0 0 1px #fff;
          }
        }
      }
      
      .alert-text {
        font-size: 14px;
        color: #ff4d4f;
        font-weight: 500;
      }
    }
  }

  &-center {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    
    .system-title {
      font-size: 40px;
      font-weight: bold;
      font-family: "YouSheBiaoTiHei", "Microsoft YaHei", sans-serif;
      background: linear-gradient(to right, #00c6fb, #005bea, #00c6fb);
      background-size: 200% auto;
      -webkit-background-clip: text;
      background-clip: text;
      -webkit-text-fill-color: transparent;
      animation: shine 3s linear infinite;
      text-shadow: 0 0 10px rgba(0, 198, 251, 0.3);
      letter-spacing: 4px;
      position: relative;
      padding: 0 10px;
      
      // 添加光晕效果
      &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: inherit;
        filter: blur(10px);
        opacity: 0.3;
        z-index: -1;
      }
      
      // 添加底部装饰线
      &::after {
        content: '';
        position: absolute;
        bottom: -8px;
        left: 50%;
        transform: translateX(-50%);
        width: 60%;
        height: 2px;
        background: linear-gradient(90deg, 
          transparent,
          #00c6fb,
          #005bea,
          #00c6fb,
          transparent
        );
      }
    }
  }

  &-right {
    min-width: 400px;
    display: flex;
    justify-content: flex-end;
    padding-right: 20px;

    .user-info {
      display: flex;
      align-items: center;
      gap: 12px;
      background: rgba(0, 198, 251, 0.1);
      padding: 6px 15px;
      border-radius: 20px;
      border: 1px solid rgba(0, 198, 251, 0.2);
      
      .user-name {
        color: #FFD700;
        font-weight: 500;
        font-size: 14px;
      }
      
      .user-avatar {
        background: linear-gradient(45deg, #00c6fb, #005bea);
        border: 2px solid rgba(255, 255, 255, 0.2);
        cursor: pointer;
        transition: all 0.3s ease;
        
        &:hover {
          transform: scale(1.1);
          box-shadow: 0 0 10px rgba(0, 198, 251, 0.5);
        }
      }
      
      .divider {
        color: rgba(255, 255, 255, 0.3);
        margin: 0 8px;
      }
      
      .time-info {
        color: #FFD700;
        font-weight: 500;
        font-size: 14px;
        min-width: 180px;
        text-align: right;
      }
    }
  }
}

// 主内容区域
.main-content {
  flex: 1;
  height: calc(1080px - 60px - 80px); // 1080px减去header和footer的高度
  min-height: 0; // 重要：允许内容区域收缩
  overflow: hidden;
  position: relative;
  padding: 10px 20px;
}

// 底部样式
.footer {
  height: 80px;
  min-height: 80px;
  width: 100%;
  position: relative;
  
  .button-container {
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    padding: 0 20px;
    background: transparent;
  }

  .footer-btn {
    position: relative;
    padding: 12px 30px;
    border: 1px solid #00c6fb;
    background: transparent;
    color: #00c6fb;
    font-size: 16px;
    cursor: pointer;
    overflow: hidden;
    transition: all 0.3s ease;
    border-radius: 4px;
    
    .btn-text {
      position: relative;
      z-index: 2;
    }
    
    .btn-background {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: linear-gradient(45deg, #00c6fb, #005bea);
      transform: translateY(100%);
      transition: transform 0.3s ease;
      z-index: 1;
    }
    
    &:hover {
      color: white;
      box-shadow: 0 0 15px rgba(0, 198, 251, 0.5);
      
      .btn-background {
        transform: translateY(0);
      }
    }
    
    &:active {
      transform: scale(0.95);
    }
    
    &.active {
      color: white;
      border-color: #005bea;
      box-shadow: 0 0 20px rgba(0, 198, 251, 0.6);
      
      .btn-background {
        transform: translateY(0);
      }
      
      &::before {
        content: '';
        position: absolute;
        top: -2px;
        left: 0;
        width: 100%;
        height: 2px;
        background: #00c6fb;
        box-shadow: 0 0 10px #00c6fb;
      }
    }
  }
}

// 确保内容溢出隐藏
html, body {
  margin: 0;
  padding: 0;
  overflow: hidden;
  width: 100%;
  height: 100%;
}

// 添加动画
@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.7;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes shake {
  0%, 100% {
    transform: rotate(0);
  }
  20%, 60% {
    transform: rotate(15deg);
  }
  40%, 80% {
    transform: rotate(-15deg);
  }
}

// 添加渐变动画
@keyframes shine {
  0% {
    background-position: 200% center;
  }
  100% {
    background-position: -200% center;
  }
}

// 添加响应式调整
@media screen and (max-width: 1200px) {
  .header-center {
    .system-title {
      font-size: 28px;
      letter-spacing: 2px;
    }
  }

  .header-right {
    min-width: 350px;
    
    .user-info {
      padding: 4px 12px;
      gap: 8px;
      
      .user-name, .time-info {
        font-size: 12px;
      }
      
      .user-avatar {
        width: 28px;
        height: 28px;
      }
    }
  }
}

// 添加下拉菜单样式
:deep(.user-menu) {
  background: rgba(0, 21, 41, 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 198, 251, 0.2);
  border-radius: 4px;
  padding: 4px 0;
  
  .ant-dropdown-menu-item {
    padding: 8px 16px;
    color: #fff;
    transition: all 0.3s ease;
    
    .anticon {
      margin-right: 8px;
      color: #00c6fb;
    }
    
    &:hover {
      background: rgba(0, 198, 251, 0.1);
    }
  }
  
  .ant-dropdown-menu-divider {
    background-color: rgba(0, 198, 251, 0.2);
    margin: 4px 0;
  }
}

// 优化头像样式
.user-avatar {
  background: linear-gradient(45deg, #00c6fb, #005bea);
  border: 2px solid rgba(255, 255, 255, 0.2);
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: scale(1.1);
    box-shadow: 0 0 10px rgba(0, 198, 251, 0.5);
  }
}
</style>

import {createRouter, createWebHistory} from 'vue-router'

const routes = [
    {
        path: '/',
        component: () => import('../views/Base.vue'),
        children: [
            {
                path: '',
                redirect: '/show_center'
            },
            {
                path: 'show_center',
                name: 'ShowCenter',
                component: () => import('../views/ShowCenter3.vue'),
                meta: { title: '展示中心' }
            },
            {
                path: 'host',
                name: 'Host',
                component: () => import('../views/Host.vue'),
                meta: { title: '资产管理' }
            },
            {
                path: 'system_params',
                name: 'SystemParams',
                component: () => import('../views/SystemParams.vue'),
                meta: { title: '系统参数' }
            },
            {
                path: 'system_monitor',
                name: 'SystemMonitor',
                component: () => import('../views/SystemMonitor.vue'),
                meta: { title: '系统监控' }
            },
            {
                path: 'network_topology',
                name: 'NetworkTopology',
                component: () => import('../views/NetworkTopology.vue'),
                meta: { title: '线路拓扑' }
            },
            {
                path: 'alarm_records',
                name: 'AlarmRecords',
                component: () => import('../views/AlarmRecords.vue'),
                meta: { title: '报警记录' }
            },
            {
                path: 'report_system',
                name: 'ReportSystem',
                component: () => import('../views/ReportSystem.vue'),
                meta: { title: '报表系统' }
            },
            {
                path: 'cooling_system',
                name: 'CoolingSystem',
                component: () => import('../views/CoolingSystem.vue'),
                meta: { title: '散热系统' }
            },
            {
                path: 'system_management',
                name: 'SystemManagement',
                component: () => import('../views/SystemManagement.vue'),
                meta: { title: '系统管理' }
            },
            {
                path: 'console/:host_id',
                name: 'Console',
                component: () => import('../views/Console.vue'),
                meta: {
                    title: 'Console',
                    authenticate: true,
                }
            }
        ]
    },
    {
        path: '/login',
        name: 'Login',
        component: () => import('../views/Login.vue'),
        meta: {
            title: '账户登陆',
            authenticate: false,
        }
    }
];

const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes
})

// 添加路由守卫
router.beforeEach((to, from, next) => {
    // 设置页面标题
    if (to.meta.title) {
        document.title = `${to.meta.title} - 飞轮能量管理系统`;
    }
    next();
});

export default router


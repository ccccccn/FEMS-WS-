# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: mapperConfig.py
 @DateTime: 2025-05-08 16:08
 @SoftWare: PyCharm
"""

system_params_overview_mapped_keys = [
    ("EMS_SYS_SOC", "EMS_SYS_SOC"),
    ("EMS_SYS_State", "EMS_SYS_State"),
    ("EMS_SYS_Mode", "EMS_SYS_Mode"),
    ("一级报警", "EMS_F_WORD_2"),
    ("二级报警", "EMS_F_WORD_3"),
    ("三级报警", "EMS_F_WORD_4"),
    ("四级报警", "EMS_F_WORD_5"),
    ("火警", "EMS_SYS_Fire_STATE"),
    ("火警急停", "EMS_F_WORD_7"),
    ("硬件急停", "EMS_F_WORD_9"),
    ("软件急停", "EMS_I_F_ENABLE"),
    ("最大充电率", "EMS_SYS_AVA_POWER_Cha"),
    ("最大放电率", "EMS_SYS_AVA_POWER_DISCha"),
    ("飞轮运行量", "EMS_FW_Runing_NUM"),
    ("飞轮就绪量", "EMS_SYS_COMMU_STATE2"),
    ("实时有功率", "EMS_Total_discharge"),
    ("功率给定", "EMS_Total_command_charging"),
    ("飞轮功率", "EMS_Total_charging"),
    ("IGBT度", "IGBT_Temp"),
    ("一次电压", "PCS_一次电压"),
    ("通讯状态", "PCS_通讯状态"),
    # ("")
]

system_params_detail_mapped_keys = {
    "FW": [
        ("系统状态", "EMS_SYS_State"),
        ("飞轮状态", "EMS_SYS_Mode"),
        ("真空度", "FW_{}_真空度"),
        ("温度", "FW_{}_飞轮_TE"),
        ("转速", "FW_{}_飞轮转速"),
        ("SOC", "IPM_{}_{}_SOC"),
        ("功率", "IPM_{}_{}_输出功率"),
        ("IGBT温度", "IPM_{}_{}_IGBT_TE"),
        ("一次电压", "IPM_{}_{}_DC_V"),
        ("通信状态", "IPM_{}_{}_通讯状态")
    ],
    "PCS": [
        ("PCS状态", "PCS_State"),
        ("PCS_系统SOC", "PCS_系统SOC"),
        ("PCS_输出有功功率", "PCS_输出有功功率"),
        ("通讯状态", "PCS_通讯状态"),
    ]
}

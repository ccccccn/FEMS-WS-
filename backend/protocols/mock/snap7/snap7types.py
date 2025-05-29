#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 区域类型
S7AreaPE = 0x81
S7AreaPA = 0x82
S7AreaMK = 0x83
S7AreaDB = 0x84
S7AreaCT = 0x1C
S7AreaTM = 0x1D

# 字长
S7WLBit     = 0x01
S7WLByte    = 0x02
S7WLWord    = 0x04
S7WLDWord   = 0x06
S7WLReal    = 0x08
S7WLCounter = 0x1C
S7WLTimer   = 0x1D
S7WLString  = 0x09  # 添加字符串类型

# 连接类型
CONNTYPE_PG    = 0x01  # PG连接
CONNTYPE_OP    = 0x02  # OP连接
CONNTYPE_BASIC = 0x03  # 基本连接

# 错误代码
ERR_NO_ERROR = 0x00000000 
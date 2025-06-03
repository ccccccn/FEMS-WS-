#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IEC 61850 GOOSE协议实现模块
功能：使用Scapy实现GOOSE(Generic Object Oriented Substation Event)协议的封装和解析
主要实现：
- GOOSE报文的编码和解码
- 各种数据类型的处理
- 时间戳生成
- 报文发送
"""

from scapy.packet import Packet, bind_layers
from scapy.fields import XByteField, StrLenField, ShortField, Field
from scapy.layers.l2 import Ether, Dot1Q  # 用于以太网层和VLAN标签
from scapy.compat import raw, orb
import time, struct
from scapy.sendrecv import sendp

def getTimestamp():
    """
    生成GOOSE时间戳
    返回值：包含秒数和纳秒分数的时间戳，按IEC 61850标准格式编码
    格式：4字节秒数 + 3字节纳秒分数 + 1字节品质
    """
    stamp = time.time_ns()  # 获取纳秒级时间戳
    frac = ((stamp/1000000000) - (stamp//1000000000))  # 计算小数部分
    stamp = int(stamp//1000000000)  # 整数秒数
    t = struct.pack(">i", stamp)  # 将秒数打包为4字节
    
    # 将小数部分转换为24位二进制表示
    bits = ''
    n = 0.5
    for i in range(0,24):
        if frac > n:
            bits += '1'
            frac = frac - n 
        else:
            bits += '0'
        n = n/2
    v = int(bits,2)
    
    # 构造时间戳字节数组
    timestamp = bytearray()
    while v:
        timestamp.append(v & 0xff)
        v >>= 8
    timestamp.append(0x18)  # 品质字节，表示时钟同步状态
    t += timestamp
    return t

def vlenq2bytes(val):
    """
    将整数值转换为BER-TLV格式的长度字段
    参数：
        val: 要编码的整数值
    返回值：
        编码后的字节串
    """
    s = list()
    first = 0x80
    s.append(val & 0x7f)  # 最低7位
    val = val >> 7
    count = 1
    while val:  # 处理剩余位
        s.append(0x80 | (val & 0x7F))
        val = val >> 7
        count += 1
    if count > 1:
        s.append(first+count)
        s.reverse()
    return bytes(s)
        
def bytes2vlenq(m):
    """
    将BER-TLV格式的长度字段解码为整数值
    参数：
        m: 要解码的字节串
    返回值：
        (剩余字节串, 解码后的长度值)
    """
    count = l = 0
    i = 1
    longform = m[0] & 0x7f
    if m[0] > 127:  # 长格式
        count = longform
    else:  # 短格式
        l = longform
        i = 1
    for x in range(count):
        l = l << 7
        l = l + x
        i = i + 1
    return m[i:], l
        
class BERLenQField(Field):
    """
    BER编码长度字段类
    用于处理ASN.1 BER编码中的长度字段
    """
    __slots__ = ["fld"]
    
    def __init__(self, name, default, fld):
        """
        初始化BER长度字段
        参数：
            name: 字段名称
            default: 默认值
            fld: 关联的数据字段名
        """
        Field.__init__(self, name, default)
        self.fld = fld
        
    def i2m(self, pkt, x):
        """将内部值转换为机器值（编码）"""
        if x is None:
            f = pkt.get_field(self.fld)
            try:
                x = f.i2len(pkt, pkt.getfieldval(self.fld))
            except:
                x = len(bytes([pkt.getfieldval(self.fld)]))
            x = vlenq2bytes(x)
            test = raw(x)
        return raw(x)
    
    def m2i(self, pkt, x):
        """将机器值转换为内部值（解码）"""
        if x is None:
            return None, 0
        return bytes2vlenq(x)[1]
    
    def addfield(self, pkt, s, val):
        """添加字段到数据包"""
        return s+self.i2m(pkt,val)
    
    def getfield(self, pkt, s):
        """从数据包中获取字段"""
        return bytes2vlenq(s)

class BERTotLenField(Field):
    """
    BER编码总长度字段类
    用于处理GOOSE PDU的总长度字段
    """
    def __init__(self, name, default):
        Field.__init__(self, name, default)
        
    def i2m(self, pkt, x):
        if x is None:
            x = 0
        return raw(x)

    def m2i(self, pkt, x):
        if x is None:
            return None, 0
        return bytes2vlenq(x)[1]
    
    def addfield(self, pkt, s, val):
        return s+self.i2m(pkt,val)
    
    def getfield(self, pkt, s):
        return bytes2vlenq(s)


class GooseBoolean(Packet):
    """GOOSE布尔类型"""
    name = "Boolean"
    fields_desc = [ XByteField("BooleanTag", 0x83),  # 类型标签
                    BERLenQField("BooleanLength", None, "Data"),  # 长度字段
                    StrLenField("Data", "", length_from=lambda x:x.BooleanLength)  # 数据字段
                    ]
    def guess_payload_class(self, payload):
        """根据负载内容推测下一个数据类型"""
        if len(payload) > 0:
            data = orb(payload[0])
            return data_types[data]
        
    
class GooseBitString(Packet):
    """GOOSE位串类型"""
    name = "BitString"
    fields_desc = [ XByteField("BitStringTag", 0x84),
                    BERLenQField("BitStringLength", None, "Data"),
                    StrLenField("Data", "", length_from=lambda x:x.BitStringLength)
                    ]
    def guess_payload_class(self, payload):
        if len(payload) > 0:
            data = orb(payload[0])
            return data_types[data]
        
    
class GooseInteger(Packet):
    """GOOSE整数类型"""
    name = "Integer"
    fields_desc = [ XByteField("IntegerTag", 0x85),
                    BERLenQField("IntegerLength", None, "Data"),
                    StrLenField("Data", "", length_from=lambda x:x.IntegerLength)
                    ]
    def guess_payload_class(self, payload):
        if len(payload) > 0:
            data = orb(payload[0])
            return data_types[data]
        
    
class GooseUnsignedInteger(Packet):
    """GOOSE无符号整数类型"""
    name = "Unsigned Integer"
    fields_desc = [ XByteField("UnsignedTag", 0x86),
                    BERLenQField("UnsignedLength", None, "Data"),
                    StrLenField("Data", "", length_from=lambda x:x.UnsignedLength)
                    ]
    
    def guess_payload_class(self, payload):
        if len(payload) > 0:
            data = orb(payload[0])
            return data_types[data]
        
class GooseFloat(Packet):
    """GOOSE浮点数类型"""
    name = "Float"
    fields_desc = [ XByteField("FloatTag", 0x87),
                    BERLenQField("FloatLength", None, "Data"),
                    StrLenField("Data", "", length_from=lambda x:x.FloatLength)
                    ]
    def guess_payload_class(self, payload):
        if len(payload) > 0:
            data = orb(payload[0])
            return data_types[data]
        
class GooseReal(Packet):
    """GOOSE实数类型"""
    name = "Real"
    fields_desc = [ XByteField("RealTag", 0x88),
                    BERLenQField("RealLength", None, "Data"),
                    StrLenField("Data", "", length_from=lambda x:x.RealLength)
                    ]
    def guess_payload_class(self, payload):
        if len(payload) > 0:
            data = orb(payload[0])
            return data_types[data]

class GooseOctetString(Packet):
    """GOOSE八位字节串类型"""
    name = "OctetString"
    fields_desc = [ XByteField("OctetStringTag", 0x89),
                    BERLenQField("OctetStringLength", None, "Data"),
                    StrLenField("Data", "", length_from=lambda x:x.OctetStringLength)
                    ]
    def guess_payload_class(self, payload):
        if len(payload) > 0:
            data = orb(payload[0])
            return data_types[data]
        
class GooseVisibleString(Packet):
    """GOOSE可见字符串类型"""
    name = "VisibleString"
    fields_desc = [ XByteField("VisibleStringTag", 0x8A),
                    BERLenQField("VisibleStringLength", None, "Data"),
                    StrLenField("Data", "", length_from=lambda x:x.VisibleStringLength)
                    ]
    def guess_payload_class(self, payload):
        if len(payload) > 0:
            data = orb(payload[0])
            return data_types[data]
        
class GooseUTCTime(Packet):
    """GOOSE UTC时间类型"""
    name = "UTCTime"
    fields_desc = [ XByteField("UTCTimeTag", 0x8C),
                    BERLenQField("UTCTimeLength", None, "Data"),
                    StrLenField("Data", "", length_from=lambda x:x.UTCTimeLength)
                    ]
    def guess_payload_class(self, payload):
        if len(payload) > 0:
            data = orb(payload[0])
            return data_types[data]
        
class GooseBCD(Packet):
    name = "BCD"
    fields_desc = [ XByteField("BCDTag", 0x8D),
                    BERLenQField("BCDLength", None, "Data"),
                    StrLenField("Data", "", length_from=lambda x:x.BCDLength)
                    ]
    def guess_payload_class(self, payload):
        if len(payload) > 0:
            data = orb(payload[0])
            return data_types[data]
        
class GooseBooleanArray(Packet):
    name = "BooleanArray"
    fields_desc = [ XByteField("BooleanArrayTag", 0x8E),
                    BERLenQField("BooleanArrayLength", None, "Data"),
                    StrLenField("Data", "", length_from=lambda x:x.BooleanArrayLength)
                    ]
      
class GooseObjectID(Packet):
    name = "ObjectID"
    fields_desc = [ XByteField("ObjectIDTag", 0x8F),
                    BERLenQField("ObjectIDLength", None, "Data"),
                    StrLenField("Data", "", length_from=lambda x:x.ObjectIDLength)
                    ]
    def guess_payload_class(self, payload):
        if len(payload) > 0:
            data = orb(payload[0])
            return data_types[data]
      
class GooseUTF8String(Packet):
    name = "UTF8String"
    fields_desc = [ XByteField("UTF8StringTag", 0x90),
                    BERLenQField("UTF8StringLength", None, "Data"),
                    StrLenField("Data", "", length_from=lambda x:x.UTF8StringLength)
                    ]
    def guess_payload_class(self, payload):
        if len(payload) > 0:
            data = orb(payload[0])
            return data_types[data]

data_types = {
    0x83: GooseBoolean,  
    0x84: GooseBitString, 
    0x85: GooseInteger,  
    0x86: GooseUnsignedInteger, 
    0x87: GooseFloat,  
    0x88: GooseReal, 
    0x89: GooseOctetString, 
    0x8A: GooseVisibleString, 
    0x8C: GooseUTCTime,  
    0x8D: GooseBCD, 
    0x8E: GooseBooleanArray, 
    0x8F: GooseObjectID, 
    0x90: GooseUTF8String,
    } 

class GOOSEDATA(Packet):
    """
    GOOSE数据部分
    包含实际的数据值列表
    """
    name = "GOOSEDATA"
    fields_desc = [
                    XByteField("allData", 0xAB),  # 数据标识符
                    BERTotLenField("allData_Length", None)  # 数据总长度
                ]
    
    def guess_payload_class(self, payload):
        """根据负载内容确定数据类型"""
        if len(payload) > 0:
            data = orb(payload[0])
            return data_types[data]
           
    def post_build(self, p, pay):
        """构建数据包后的处理，计算长度"""
        p += pay
        tmp_bytes = vlenq2bytes(len(pay))
        p = p[:1] + tmp_bytes + p[1:]
        return p  


class GOOSEPDU(Packet):
    """
    GOOSE协议数据单元
    包含GOOSE消息的主要属性和控制信息
    """
    name = "GOOSEPDU"
    fields_desc = [
                    # GOOSE控制块引用
                    XByteField("gocbRef_Tag", 0x80),
                    BERLenQField("gocbRef_Length", None, "gocbRef"),
                    StrLenField("gocbRef", "TestLogic", length_from=lambda x:x.gocbRef_Length),
                    
                    # 允许的存活时间
                    XByteField("timeAllowedtoLive_Tag", 0x81),
                    BERLenQField("timeAllowedtoLive_Length", None, "timeAllowedtoLive"),
                    StrLenField("timeAllowedtoLive", "0", length_from=lambda x:x.timeAllowedtoLive_Length),
                    
                    # 数据集引用
                    XByteField("datSet_Tag", 0x82),
                    BERLenQField("datSet_Length", None, "datSet"),
                    StrLenField("datSet", "SimpleIO", length_from=lambda x:x.datSet_Length),
                    
                    # GOOSE标识符
                    XByteField("goID_Tag", 0x83),
                    BERLenQField("goID_Length", None, "goID"),
                    StrLenField("goID", "TestLogic", length_from=lambda x:x.goID_Length), 
                    
                    # 时间戳
                    XByteField("t_Tag", 0x84),
                    BERLenQField("t_Length", None, "t"),
                    StrLenField("t", getTimestamp(), length_from=lambda x:x.t_Length),                                              

                    # 状态号
                    XByteField("stNum_Tag", 0x85),
                    BERLenQField("stNum_Length", None, "stNum"),
                    StrLenField("stNum", "0", length_from=lambda x:x.stNum_Length),
                    
                    # 序列号
                    XByteField("sqNum_Tag", 0x86),
                    BERLenQField("sqNum_Length", None, "sqNum"),
                    StrLenField("sqNum", "0", length_from=lambda x:x.sqNum_Length),
                    
                    # 测试标志
                    XByteField("test_Tag", 0x87),
                    BERLenQField("test_Length", None, "test"),
                    StrLenField("test", '0', length_from=lambda x:x.test_Length),
                    
                    # 配置版本号
                    XByteField("confRev_Tag", 0x88),
                    BERLenQField("confRev_Length", None, "confRev"),
                    StrLenField("confRev", '0', length_from=lambda x:x.confRev_Length),
                    
                    # 需要调试标志
                    XByteField("ndsCom_Tag", 0x89),
                    BERLenQField("ndsCom_Length", None, "ndsCom"),
                    StrLenField("ndsCom", "", length_from=lambda x:x.ndsCom_Length),
         
                    # 数据集条目数量
                    XByteField("numDataSetEntries_Tag", 0x8A),
                    BERLenQField("numDataSetEntries_Length", None, "numDataSetEntries"),
                    StrLenField("numDataSetEntries", "", length_from=lambda x:x.numDataSetEntries_Length),
                  ]

class GOOSE(Packet):
    """
    GOOSE报文主类
    实现IEC 61850标准中的GOOSE报文格式
    """
    name = "GOOSE"
    fields_desc = [ 
                    ShortField("APPID", 1000),        # 应用标识符
                    ShortField("Length", None),        # 报文长度
                    ShortField("Reserved1", 0),        # 保留字段1
                    ShortField("Reserved2", 0),        # 保留字段2
                    XByteField("goosePDU_Tag", 0x61), # GOOSE PDU标签
                    BERTotLenField("goosePDU_Length", None),  # PDU长度
                  ]
        
    def post_build(self, p, pay):
        """
        构建报文后的处理
        计算并填充长度字段
        """
        pad = bytes(1)
        p += pay
        # 计算总长度
        if self.Length is None:
            tmp_len = len(p) - 2
            tmp_bytes = vlenq2bytes(tmp_len)
            if len(tmp_bytes) == 1:
                p = p[:2] + pad + tmp_bytes + p[4:]
            else:
                p = p[:2] + tmp_bytes + p[4:]
        # 计算PDU长度
        if self.goosePDU_Length is None:
            tmp_len = tmp_len - 5
            tmp_bytes = vlenq2bytes(tmp_len)
            if len(tmp_bytes) == 1:
                p = p[:9] + tmp_bytes + p[9:]
            else:
                p = p[:9] + tmp_bytes + p[9:]
        return p  
    

bind_layers(Ether, GOOSE, type=0x88b8)
bind_layers(GOOSE, GOOSEPDU)
bind_layers(GOOSEPDU, GOOSEDATA)

if __name__ == "__main__":
    a = Ether(dst='01:0c:cd:01:00:01')/Dot1Q(prio=4, vlan=0)/GOOSE(APPID=0x03e8, Reserved1=0, Reserved2=0)/GOOSEPDU(numDataSetEntries=b'\x01')/GOOSEDATA()/GooseInteger(Data=b'\x80')
    a.show()
    sendp(a)

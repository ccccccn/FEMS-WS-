# Mock pymodbus sync client module 
from .tcp import ModbusTcpClient

# 添加ModbusSerialClient类
class ModbusSerialClient(ModbusTcpClient):
    """模拟Modbus串行客户端"""
    
    def __init__(self, method='rtu', port='/dev/ttyS0', **kwargs):
        """初始化客户端
        
        Args:
            method (str): 通信方式，'rtu'或'ascii'
            port (str): 串口名称
            **kwargs: 其他参数
        """
        super().__init__(host='localhost', port=502, **kwargs)
        self.method = method
        self.port = port 
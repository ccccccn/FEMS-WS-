import json
import os
from dataclasses import dataclass, asdict
from typing import List, Optional
from datetime import datetime

@dataclass
class ForwardingProtocol:
    name: str
    type: str
    host: str
    port: str
    topic: Optional[str]
    description: str
    status: str = "未连接"

@dataclass
class ForwardingVariable:
    name: str
    device: str
    data_type: str
    sampling_rate: str
    description: str
    status: str = "未配置"

@dataclass
class ForwardingConfig:
    name: str
    description: str
    status: str
    protocols: List[ForwardingProtocol]
    variables: List[ForwardingVariable]
    created_at: str = None
    updated_at: str = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

class ForwardingManager:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "forwarding_config.json")
        self.forwarding_configs: List[ForwardingConfig] = []
        self.load_configs()

    def load_configs(self):
        """从配置文件加载转发配置"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    configs_data = json.load(f)
                    self.forwarding_configs = []
                    for config_dict in configs_data:
                        protocols = [ForwardingProtocol(**p) for p in config_dict.pop('protocols', [])]
                        variables = [ForwardingVariable(**v) for v in config_dict.pop('variables', [])]
                        config = ForwardingConfig(**config_dict, protocols=protocols, variables=variables)
                        self.forwarding_configs.append(config)
            except Exception as e:
                print(f"加载转发配置失败: {str(e)}")
                self.forwarding_configs = []

    def save_configs(self):
        """保存转发配置到文件"""
        try:
            configs_data = [asdict(config) for config in self.forwarding_configs]
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(configs_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存转发配置失败: {str(e)}")

    def add_config(self, config: ForwardingConfig):
        """添加新的转发配置"""
        self.forwarding_configs.append(config)
        self.save_configs()

    def update_config(self, index: int, config: ForwardingConfig):
        """更新转发配置"""
        if 0 <= index < len(self.forwarding_configs):
            self.forwarding_configs[index] = config
            self.save_configs()

    def delete_config(self, index: int):
        """删除转发配置"""
        if 0 <= index < len(self.forwarding_configs):
            del self.forwarding_configs[index]
            self.save_configs()

    def get_config(self, index: int) -> Optional[ForwardingConfig]:
        """获取指定索引的转发配置"""
        if 0 <= index < len(self.forwarding_configs):
            return self.forwarding_configs[index]
        return None

    def get_all_configs(self) -> List[ForwardingConfig]:
        """获取所有转发配置"""
        return self.forwarding_configs.copy() 
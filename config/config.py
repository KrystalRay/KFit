import os
import yaml
from typing import Dict, Any

class Config:
    """
    配置加载类，负责从YAML文件中加载配置信息
    """
    def __init__(self, config_path: str = None):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径，默认为None，会使用默认路径
        """
        if config_path is None:
            # 默认配置文件路径
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, 'config', 'config.yaml')
        
        self.config_path = config_path
        self.config_data = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        从YAML文件加载配置
        
        Returns:
            Dict[str, Any]: 配置数据字典
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            return config_data
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置键名
            default: 默认值，如果键不存在则返回此值
            
        Returns:
            Any: 配置值
        """
        return self.config_data.get(key, default)
    
    def get_notion_config(self) -> Dict[str, Any]:
        """
        获取Notion相关配置
        
        Returns:
            Dict[str, Any]: Notion配置字典
        """
        return self.config_data.get('notion', {})
    
    def get_garmin_config(self) -> Dict[str, Any]:
        """
        获取Garmin相关配置
        
        Returns:
            Dict[str, Any]: Garmin配置字典
        """
        return self.config_data.get('garmin', {})
    
    def get_model_config(self) -> Dict[str, Any]:
        """
        获取大模型相关配置
        
        Returns:
            Dict[str, Any]: 大模型配置字典
        """
        return self.config_data.get('model', {})
    
    def get_diary_config(self) -> Dict[str, Any]:
        """
        获取日记文件相关配置
        
        Returns:
            Dict[str, Any]: 日记文件配置字典
        """
        return self.config_data.get('diary', {})
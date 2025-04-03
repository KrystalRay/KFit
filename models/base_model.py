from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseModel(ABC):
    """
    大模型接口抽象基类，定义了所有模型实现必须提供的方法
    """
    
    @abstractmethod
    def __init__(self, config: Dict[str, Any]):
        """
        初始化模型
        
        Args:
            config: 模型配置字典
        """
        pass
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        生成文本响应
        
        Args:
            prompt: 输入提示文本
            **kwargs: 其他参数
            
        Returns:
            str: 模型生成的响应文本
        """
        pass
    
    @abstractmethod
    def analyze_health(self, 
                      food_data: Dict[str, Any], 
                      fitness_data: Dict[str, Any], 
                      **kwargs) -> Dict[str, Any]:
        """
        分析健康数据
        
        Args:
            food_data: 饮食数据字典
            fitness_data: 健身数据字典
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 分析结果字典
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            Dict[str, Any]: 包含模型名称、版本等信息的字典
        """
        pass
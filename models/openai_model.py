import openai
from typing import Dict, Any, List, Optional
from .base_model import BaseModel

class OpenAIModel(BaseModel):
    """
    OpenAI模型实现类
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化OpenAI模型
        
        Args:
            config: 模型配置字典
        """
        self.api_key = config.get('api_key')
        self.model = config.get('model', 'gpt-4')
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 1000)
        self.api_base = config.get('api_base', 'https://api.openai.com')
        
        # 不再需要全局设置API密钥和端点，将在每次调用时传入
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        生成文本响应
        
        Args:
            prompt: 输入提示文本
            **kwargs: 其他参数
            
        Returns:
            str: 模型生成的响应文本
        """
        # 合并默认参数和自定义参数
        params = {
            'model': kwargs.get('model', self.model),
            'temperature': kwargs.get('temperature', self.temperature),
            'max_tokens': kwargs.get('max_tokens', self.max_tokens)
        }
        
        try:
            # 调用OpenAI API (适配openai>=1.0.0)
            client = openai.OpenAI(api_key=self.api_key, base_url=self.api_base)
            response = client.chat.completions.create(
                model=params['model'],
                messages=[
                    {"role": "system", "content": "你是一个健康顾问，专注于分析饮食和健身数据。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=params['temperature'],
                max_tokens=params['max_tokens']
            )
            
            # 提取生成的文本
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API调用失败: {e}")
            return f"错误: {str(e)}"
    
    def analyze_health(self, food_data: Dict[str, Any], fitness_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        分析健康数据
        
        Args:
            food_data: 饮食数据字典
            fitness_data: 健身数据字典
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 分析结果字典
        """
        # 构建提示文本
        prompt = self._build_health_analysis_prompt(food_data, fitness_data)
        
        # 调用模型生成分析结果
        analysis_text = self.generate(prompt, **kwargs)
        
        # 解析分析结果
        try:
            # 这里可以根据实际情况进行更复杂的解析
            # 简单示例：将文本分割为不同部分
            parts = analysis_text.split('\n\n')
            
            result = {
                'summary': parts[0] if len(parts) > 0 else '',
                'food_analysis': parts[1] if len(parts) > 1 else '',
                'fitness_analysis': parts[2] if len(parts) > 2 else '',
                'recommendations': parts[3] if len(parts) > 3 else '',
                'raw_response': analysis_text
            }
            
            return result
        except Exception as e:
            print(f"解析分析结果失败: {e}")
            return {'error': str(e), 'raw_response': analysis_text}
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            Dict[str, Any]: 包含模型名称、版本等信息的字典
        """
        return {
            'provider': 'OpenAI',
            'model': self.model,
            'version': 'latest'
        }
    
    def _build_health_analysis_prompt(self, food_data: Dict[str, Any], fitness_data: Dict[str, Any]) -> str:
        """
        构建健康分析提示文本
        
        Args:
            food_data: 饮食数据字典
            fitness_data: 健身数据字典
            
        Returns:
            str: 提示文本
        """
        # 将数据转换为易于阅读的格式
        food_text = "\n".join([f"- {item}" for item in food_data.get('items', [])])
        
        # 构建活动信息
        activities = fitness_data.get('activities', [])
        activity_text = "\n".join([f"- 活动: {a.get('type', '未知')}, 时长: {a.get('duration', 0)}分钟, 消耗: {a.get('calories', 0)}卡路里" 
                                for a in activities])
        
        # 构建其他健身数据
        steps = fitness_data.get('steps', 0)
        calories = fitness_data.get('calories', 0)
        heart_rate = fitness_data.get('heart_rate', {})
        sleep = fitness_data.get('sleep', {})
        
        # 完整提示文本
        prompt = f"""请分析以下健康数据并提供专业的健康建议：

## 饮食数据
{food_text}

## 健身数据
步数: {steps}
消耗卡路里: {calories}

### 活动
{activity_text}

### 心率
平均: {heart_rate.get('avg', '未知')}
最高: {heart_rate.get('max', '未知')}
最低: {heart_rate.get('min', '未知')}

### 睡眠
时长: {sleep.get('duration', '未知')}小时
深睡: {sleep.get('deep', '未知')}小时
浅睡: {sleep.get('light', '未知')}小时

请提供以下分析：
1. 总体健康状况摘要
2. 饮食分析（营养平衡、热量摄入等）
3. 健身分析（活动量、心率、睡眠质量等）
4. 改进建议和健康提示
"""
        
        return prompt
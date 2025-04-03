from datetime import datetime
from typing import Dict, Any

class PromptBuilder:
    @staticmethod
    def build_fitness_prompt(fitness_data: Dict[str, Any]) -> str:
        """构建健身数据分析的Prompt
        
        Args:
            fitness_data: 包含健身数据的字典
            
        Returns:
            构建好的Prompt字符串
        """
        prompt = f"""请根据以下健身数据提供健康分析：
        
        日期: {fitness_data['date']}
        步数: {fitness_data['steps']}
        消耗卡路里: {fitness_data['calories']}
        
        心率:
        平均: {fitness_data['heart_rate']['avg']}
        最低: {fitness_data['heart_rate']['min']}
        最高: {fitness_data['heart_rate']['max']}
        
        睡眠:
        时长: {fitness_data['sleep']['duration']}小时
        深睡: {fitness_data['sleep']['deep']}小时
        浅睡: {fitness_data['sleep']['light']}小时
        REM睡眠: {fitness_data['sleep']['rem']}小时
        清醒时间: {fitness_data['sleep']['awake']}小时
        
        活动:
        """
        
        for activity in fitness_data['activities']:
            prompt += f"- {activity['type']}: {activity['duration']}分钟, 消耗{activity['calories']}卡路里\n"
        
        prompt += "\n请提供以下分析：\n1. 总体健康状况评估\n2. 运动量是否充足\n3. 睡眠质量分析\n4. 改进建议"
        
        return prompt
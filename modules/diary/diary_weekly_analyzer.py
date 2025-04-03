import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from modules.diary.diary_parser import DiaryParser

class DiaryWeeklyAnalyzer:
    """
    日记周分析器类，负责分析一周的日记数据
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化日记周分析器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.diary_parser = DiaryParser(config)
    
    def analyze_weekly_diary(self, file_path: str, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        分析一周的日记数据
        
        Args:
            file_path: 日记文件路径
            end_date: 结束日期，默认为今天
            
        Returns:
            Dict[str, Any]: 一周的饮食数据
        """
        # 设置默认结束日期为今天
        if end_date is None:
            end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 计算开始日期（7天前）
        start_date = end_date - timedelta(days=6)
        
        # 获取日期范围内的饮食数据
        food_data_list = self.diary_parser.get_food_data_range(file_path, start_date, end_date)
        
        # 合并数据
        weekly_food_data = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "items": []
        }
        
        for food_data in food_data_list:
            weekly_food_data["items"].extend(food_data.get("items", []))
        
        return weekly_food_data
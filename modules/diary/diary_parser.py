import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

class DiaryParser:
    """
    日记解析器类，负责读取和解析整个日记文件，并提取特定日期的内容
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化日记解析器
        
        Args:
            config: 配置字典
        """
        self.date_pattern = re.compile(r'#+\s*(\d{4}-\d{2}-\d{2})')
        self.food_pattern = re.compile(r'#+\s*饮食\s*\n([\s\S]*?)(?=\n#+|$)')
        
    def read_diary_file(self, file_path: str) -> str:
        """
        读取整个日记文件
        
        Args:
            file_path: 日记文件路径
            
        Returns:
            str: 日记文件内容
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"读取日记文件失败: {e}")
            return ""
    
    def extract_date_content(self, content: str, target_date: datetime) -> str:
        """
        从日记内容中提取指定日期的内容
        
        Args:
            content: 日记内容
            target_date: 目标日期
            
        Returns:
            str: 指定日期的内容
        """
        target_date_str = target_date.strftime("%Y-%m-%d")
        
        # 按日期分割内容
        date_sections = self.date_pattern.split(content)
        
        # 查找目标日期
        for i, section in enumerate(date_sections):
            if section == target_date_str and i < len(date_sections) - 1:
                return date_sections[i+1]
        
        return ""
    
    def extract_food_items(self, content: str) -> List[str]:
        """
        从日记内容中提取饮食信息
        
        Args:
            content: 日记内容
            
        Returns:
            List[str]: 饮食项目列表
        """
        # 查找饮食部分
        food_match = self.food_pattern.search(content)
        if not food_match:
            return []
        
        # 提取饮食内容
        food_content = food_match.group(1).strip()
        
        # 按行分割并过滤空行
        food_items = [line.strip() for line in food_content.split('\n') if line.strip()]
        
        # 处理列表项（如果有）
        processed_items = []
        for item in food_items:
            # 移除列表标记（如 - 或 * ）
            if item.startswith('-') or item.startswith('*'):
                item = item[1:].strip()
            processed_items.append(item)
        
        return processed_items
    
    def get_food_data(self, file_path: str, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        获取指定日期的饮食数据
        
        Args:
            file_path: 日记文件路径
            date: 日期，默认为今天
            
        Returns:
            Dict[str, Any]: 饮食数据字典
        """
        # 设置默认日期为今天
        if date is None:
            date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 读取日记文件
        content = self.read_diary_file(file_path)
        if not content:
            return {"date": date.strftime("%Y-%m-%d"), "items": []}
        
        # 提取指定日期的内容
        date_content = self.extract_date_content(content, date)
        if not date_content:
            return {"date": date.strftime("%Y-%m-%d"), "items": []}
        
        # 提取饮食信息
        food_items = self.extract_food_items(date_content)
        
        return {
            "date": date.strftime("%Y-%m-%d"),
            "items": food_items
        }
    
    def get_food_data_range(self, file_path: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        获取指定日期范围内的饮食数据
        
        Args:
            file_path: 日记文件路径
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[Dict[str, Any]]: 饮食数据列表
        """
        # 计算日期范围
        days = (end_date - start_date).days + 1
        
        # 读取日记文件
        content = self.read_diary_file(file_path)
        if not content:
            return []
        
        result = []
        current_date = start_date
        
        # 遍历日期范围
        for _ in range(days):
            # 提取当前日期的内容
            date_content = self.extract_date_content(content, current_date)
            
            # 如果找到内容，提取饮食信息
            if date_content:
                food_items = self.extract_food_items(date_content)
                
                result.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "items": food_items
                })
            
            # 移动到下一天
            current_date = current_date.replace(day=current_date.day + 1)
        
        return result
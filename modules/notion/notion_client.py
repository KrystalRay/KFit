from typing import Dict, Any, List, Optional
import requests
import json
from datetime import datetime, timedelta

class NotionClient:
    """
    Notion客户端类，负责与Notion API交互，获取用户的日记内容并提取饮食信息
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化Notion客户端
        
        Args:
            config: Notion配置字典
        """
        self.api_key = config.get('api_key')
        self.database_id = config.get('database_id')
        self.food_property_name = config.get('food_property_name', '饮食')
        self.page_size = config.get('page_size', 10)
        
        # 设置API请求头
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"  # 使用最新的API版本
        }
        
        # API端点
        self.base_url = "https://api.notion.com/v1"
    
    def get_diary_entries(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        获取指定日期范围内的日记条目
        
        Args:
            start_date: 开始日期，默认为今天
            end_date: 结束日期，默认为今天
            
        Returns:
            List[Dict[str, Any]]: 日记条目列表
        """
        # 设置默认日期为今天
        if start_date is None:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if end_date is None:
            end_date = start_date
        
        # 构建查询过滤器
        filter_params = {
            "filter": {
                "and": [
                    {
                        "property": "Date",  # 假设日期属性名为"Date"
                        "date": {
                            "on_or_after": start_date.isoformat()
                        }
                    },
                    {
                        "property": "Date",
                        "date": {
                            "on_or_before": end_date.isoformat()
                        }
                    }
                ]
            },
            "page_size": self.page_size
        }
        
        # 发送请求
        try:
            response = requests.post(
                f"{self.base_url}/databases/{self.database_id}/query",
                headers=self.headers,
                json=filter_params
            )
            
            # 检查响应
            if response.status_code == 200:
                return response.json().get("results", [])
            else:
                print(f"获取日记条目失败: HTTP {response.status_code}, {response.text}")
                return []
        except Exception as e:
            print(f"Notion API请求失败: {e}")
            return []
    
    def get_food_data(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        获取指定日期的饮食数据
        
        Args:
            date: 日期，默认为今天
            
        Returns:
            Dict[str, Any]: 饮食数据字典
        """
        # 设置默认日期为今天
        if date is None:
            date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 获取日记条目
        entries = self.get_diary_entries(date, date)
        
        # 如果没有找到条目，返回空数据
        if not entries:
            return {"date": date.strftime("%Y-%m-%d"), "items": []}
        
        # 提取第一个条目（假设每天只有一个日记条目）
        entry = entries[0]
        
        # 提取饮食信息
        food_items = self._extract_food_items(entry)
        
        return {
            "date": date.strftime("%Y-%m-%d"),
            "items": food_items
        }
    
    def get_food_data_range(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        获取指定日期范围内的饮食数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[Dict[str, Any]]: 饮食数据列表
        """
        # 获取日记条目
        entries = self.get_diary_entries(start_date, end_date)
        
        # 提取每个条目的饮食信息
        result = []
        for entry in entries:
            # 提取日期
            date_str = self._extract_date(entry)
            
            # 提取饮食信息
            food_items = self._extract_food_items(entry)
            
            result.append({
                "date": date_str,
                "items": food_items
            })
        
        return result
    
    def _extract_date(self, entry: Dict[str, Any]) -> str:
        """
        从日记条目中提取日期
        
        Args:
            entry: 日记条目
            
        Returns:
            str: 日期字符串，格式为YYYY-MM-DD
        """
        try:
            # 假设日期属性名为"Date"
            date_property = entry.get("properties", {}).get("Date", {})
            date_value = date_property.get("date", {}).get("start", "")
            
            # 如果日期为空，返回当前日期
            if not date_value:
                return datetime.now().strftime("%Y-%m-%d")
            
            # 如果日期包含时间，只保留日期部分
            if "T" in date_value:
                date_value = date_value.split("T")[0]
            
            return date_value
        except Exception as e:
            print(f"提取日期失败: {e}")
            return datetime.now().strftime("%Y-%m-%d")
    
    def _extract_food_items(self, entry: Dict[str, Any]) -> List[str]:
        """
        从日记条目中提取饮食信息
        
        Args:
            entry: 日记条目
            
        Returns:
            List[str]: 饮食项目列表
        """
        try:
            # 获取饮食属性
            food_property = entry.get("properties", {}).get(self.food_property_name, {})
            
            # 根据属性类型提取值
            property_type = food_property.get("type", "")
            
            if property_type == "rich_text":
                # 富文本类型
                rich_text = food_property.get("rich_text", [])
                if rich_text:
                    # 合并所有文本片段
                    full_text = "".join([text.get("plain_text", "") for text in rich_text])
                    # 按行分割
                    return [line.strip() for line in full_text.split("\n") if line.strip()]
            
            elif property_type == "title":
                # 标题类型
                title = food_property.get("title", [])
                if title:
                    # 合并所有文本片段
                    full_text = "".join([text.get("plain_text", "") for text in title])
                    # 按行分割
                    return [line.strip() for line in full_text.split("\n") if line.strip()]
            
            elif property_type == "multi_select":
                # 多选类型
                multi_select = food_property.get("multi_select", [])
                return [item.get("name", "") for item in multi_select if item.get("name")]
            
            # 如果无法识别类型或没有找到值，返回空列表
            return []
        
        except Exception as e:
            print(f"提取饮食信息失败: {e}")
            return []
    
    def create_diary_entry(self, date: datetime, food_items: List[str]) -> bool:
        """
        创建或更新日记条目
        
        Args:
            date: 日期
            food_items: 饮食项目列表
            
        Returns:
            bool: 是否成功
        """
        # 构建页面属性
        properties = {
            "Date": {  # 假设日期属性名为"Date"
                "date": {
                    "start": date.strftime("%Y-%m-%d")
                }
            },
            self.food_property_name: {  # 饮食属性
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "\n".join(food_items)
                        }
                    }
                ]
            }
        }
        
        # 检查是否已存在该日期的条目
        entries = self.get_diary_entries(date, date)
        
        try:
            if entries:
                # 更新现有条目
                page_id = entries[0].get("id")
                response = requests.patch(
                    f"{self.base_url}/pages/{page_id}",
                    headers=self.headers,
                    json={"properties": properties}
                )
            else:
                # 创建新条目
                response = requests.post(
                    f"{self.base_url}/pages",
                    headers=self.headers,
                    json={
                        "parent": {"database_id": self.database_id},
                        "properties": properties
                    }
                )
            
            # 检查响应
            if response.status_code in [200, 201]:
                return True
            else:
                print(f"创建/更新日记条目失败: HTTP {response.status_code}, {response.text}")
                return False
        
        except Exception as e:
            print(f"Notion API请求失败: {e}")
            return False
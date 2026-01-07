"""
KFit API客户端
用于与KFit后端API通信
"""

import requests
import json
from typing import Dict, Any, Optional

class KFitAPIClient:
    """KFit后端API客户端"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def _get(self, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """发送GET请求"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, timeout=10, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return {}

    def _post(self, endpoint: str, data: Dict[Any, Any] = None, **kwargs) -> Dict[Any, Any]:
        """发送POST请求"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.post(url, json=data, timeout=30, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return {}

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return self._get("/api/health")

    def get_fitness_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取健身数据"""
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        return self._get("/api/fitness", params=params)

    def get_nutrition_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取营养数据"""
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        return self._get("/api/nutrition", params=params)

    def get_summary(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取摘要数据"""
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        return self._get("/api/summary", params=params)

    def get_recent_activities(self, limit: int = 10) -> Dict[str, Any]:
        """获取最近活动"""
        params = {"limit": limit}
        return self._get("/api/activities/recent", params=params)

    def analyze_health(self, date: str, model_type: str = "openai", analysis_type: str = "daily") -> Dict[str, Any]:
        """分析健康数据"""
        data = {
            "date": date,
            "model_type": model_type,
            "type": analysis_type
        }
        return self._post("/api/analyze", data=data)

    def get_reports(self, date: str = None) -> Dict[str, Any]:
        """获取报告列表"""
        params = {}
        if date:
            params["date"] = date
        return self._get("/api/reports", params=params)

    def get_report_content(self, filename: str) -> Dict[str, Any]:
        """获取报告内容"""
        return self._get(f"/api/reports/{filename}")

    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        return self._get("/api/config")

    def update_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新配置"""
        return self._post("/api/config", data=config_data)

    def import_diary_data(self, file_path: str, date: str) -> Dict[str, Any]:
        """导入日记数据"""
        data = {
            "file_path": file_path,
            "date": date
        }
        return self._post("/api/import/diary", data=data)

    def test_garmin_connection(self) -> Dict[str, Any]:
        """测试Garmin连接"""
        return self._get("/api/test/garmin")

    def test_notion_connection(self) -> Dict[str, Any]:
        """测试Notion连接"""
        return self._get("/api/test/notion")
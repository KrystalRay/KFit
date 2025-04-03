from typing import Dict, Any, List, Optional
import json
import os
from ..utils import dict_utils
from ..utils.dict_utils import print_unique_keys
from datetime import datetime, timedelta
import time

# 导入garminconnect库
try:
    from garminconnect import (
        Garmin,
        GarminConnectConnectionError,
        GarminConnectTooManyRequestsError,
        GarminConnectAuthenticationError
    )
except ImportError:
    print("请安装python-garminconnect库: pip install garminconnect")

class GarminClient:
    """
    Garmin客户端类，负责与Garmin Connect API交互，获取用户的健身数据
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化Garmin客户端
        
        Args:
            config: Garmin配置字典
        """
        self.email = config.get('email')
        self.password = config.get('password')
        self.use_proxy = config.get('use_proxy', False)
        self.proxy = config.get('proxy', '')
        self.cache_ttl = config.get('cache_ttl', 3600)  # 缓存有效期，默认1小时
        self.is_cn = True
        # 缓存目录
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 初始化Garmin API客户端
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """
        初始化Garmin API客户端，包含重试逻辑
        """
        max_retries = 3
        retry_delay = 2  # 初始延迟2秒
        
        for attempt in range(1, max_retries + 1):
            try:
                # 设置代理
                if self.use_proxy and self.proxy:
                    proxies = {
                        "https": self.proxy
                    }
                    self.client = Garmin(self.email, self.password, True, proxies=proxies)
                else:
                    self.client = Garmin(self.email, self.password, True)
                    
                # 尝试登录
                print(f"尝试Garmin Connect登录 (尝试 {attempt}/{max_retries})...")
                self.client.login()
                print("Garmin Connect登录成功")
                return  # 登录成功，退出函数
                
            except GarminConnectTooManyRequestsError as e:
                # 请求过多，需要等待
                wait_time = retry_delay * attempt
                print(f"Garmin Connect请求过多，等待{wait_time}秒后重试: {e}")
                time.sleep(wait_time)
                
            except GarminConnectAuthenticationError as e:
                # 认证错误，检查凭据
                print(f"Garmin Connect认证失败，请检查用户名和密码: {e}")
                print("提示: 请确认config.yaml中的garmin.email和garmin.password是否正确")
                self.client = None
                return  # 认证错误，不再重试
                
            except GarminConnectConnectionError as e:
                # 连接错误，可能是网络问题
                print(f"Garmin Connect连接失败 (尝试 {attempt}/{max_retries}): {e}")
                if attempt < max_retries:
                    wait_time = retry_delay * attempt
                    print(f"等待{wait_time}秒后重试...")
                    time.sleep(wait_time)
                else:
                    print("已达到最大重试次数，放弃连接")
                    self.client = None
                    
            except Exception as e:
                # 其他未预期的错误
                print(f"Garmin Connect连接遇到未知错误: {e}")
                self.client = None
                return  # 未知错误，不再重试
        
        # 如果所有重试都失败
        if self.client is None:
            print("所有Garmin Connect连接尝试均失败")
            print("提示: 请检查网络连接和代理设置，或稍后再试")
    
    def _get_cache_path(self, cache_key: str) -> str:
        """
        获取缓存文件路径
        
        Args:
            cache_key: 缓存键名
            
        Returns:
            str: 缓存文件路径
        """
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        从缓存获取数据
        
        Args:
            cache_key: 缓存键名
            
        Returns:
            Optional[Dict[str, Any]]: 缓存数据，如果缓存不存在或已过期则返回None
        """
        cache_path = self._get_cache_path(cache_key)
        
        # 检查缓存文件是否存在
        if not os.path.exists(cache_path):
            return None
        
        # 检查缓存是否过期
        file_mtime = os.path.getmtime(cache_path)
        if time.time() - file_mtime > self.cache_ttl:
            return None
        
        # 读取缓存
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"读取缓存失败: {e}")
            return None
    
    def _save_to_cache(self, cache_key: str, data: Dict[str, Any]):
        """
        保存数据到缓存
        
        Args:
            cache_key: 缓存键名
            data: 要缓存的数据
        """
        cache_path = self._get_cache_path(cache_key)
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存缓存失败: {e}")
    
    def get_steps_data(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        # 设置默认日期为今天
        if date is None:
            date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        date_str = date.strftime("%Y-%m-%d")
        cache_key = f"steps_{date_str}"
        
        # 尝试从缓存获取
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        # 如果客户端未初始化或登录失败，返回空数据
        if not self.client:
            return {"date": date_str, "steps": 0}
        
        try:
            # 获取步数数据
            steps_data = self.client.get_steps_data(date.isoformat())
            
            
            # 提取总步数和活动级别统计
            total_steps = 0
            activity_stats = {
                "sedentary": 0,
                "lightlyActive": 0,
                "moderatelyActive": 0,
                "highlyActive": 0,
                "sleeping": 0
            }
            
            if isinstance(steps_data, list) and steps_data:
                for entry in steps_data:
                    total_steps += entry.get("steps", 0)
                    activity_level = entry.get("primaryActivityLevel", "")
                    if activity_level in activity_stats:
                        activity_stats[activity_level] += 1
            elif isinstance(steps_data, dict):
                total_steps = steps_data.get("totalSteps", 0)
            
            result = {
                "date": date_str, 
                "steps": total_steps,
                "activity_stats": activity_stats
            }
            
            # 保存到缓存
            self._save_to_cache(cache_key, result)
            
            return result
        
        except Exception as e:
            print(f"获取步数数据失败: {e}")
            return {"date": date_str, "steps": 0}
    
    def get_heart_rate(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        # 设置默认日期为今天
        if date is None:
            date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        date_str = date.strftime("%Y-%m-%d")
        cache_key = f"heart_rate_{date_str}"
        
        # 尝试从缓存获取
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        # 如果客户端未初始化或登录失败，返回空数据
        if not self.client:
            return {"date": date_str, "avg": 0, "min": 0, "max": 0}
        
        try:
            # 获取心率数据
            heart_rate_data = self.client.get_heart_rates(date.isoformat())
            
            # 初始化结果
            result = {
                "date": date_str,
                "avg": 0,
                "min": 0,
                "max": 0
            }
            
            if heart_rate_data:
                # 提取心率统计信息
                result["avg"] = heart_rate_data.get("restingHeartRate", 0) or 0
                
                # 如果有详细心率数据，计算最大和最小值
                heart_rate_values = []
                for item in heart_rate_data.get("heartRateValues", []):
                    if isinstance(item, (list, tuple)) and len(item) >= 2:
                        value = item[1]
                        if isinstance(value, (int, float)) and value > 0:
                            heart_rate_values.append(value)
                
                if heart_rate_values:
                    result["min"] = min(heart_rate_values)
                    result["max"] = max(heart_rate_values)
            
            # 保存到缓存
            self._save_to_cache(cache_key, result)
            
            return result
        
        except Exception as e:
            print(f"获取心率数据失败: {e}")
            return {"date": date_str, "avg": 0, "min": 0, "max": 0}
    
    def get_sleep_data(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        获取指定日期的睡眠数据
        
        Args:
            date: 日期，默认为今天
            
        Returns:
            Dict[str, Any]: 睡眠数据字典
        """
        # 设置默认日期为今天
        if date is None:
            date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        date_str = date.strftime("%Y-%m-%d")
        cache_key = f"sleep_{date_str}"
        
        # 尝试从缓存获取
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        # 如果客户端未初始化或登录失败，返回空数据
        if not self.client:
            return {"date": date_str, "duration": 0, "deep": 0, "light": 0, "rem": 0, "awake": 0}
        
        try:
            # 转换日期格式为YYYY-MM-DD
            api_date = date.strftime("%Y-%m-%d")
            print(api_date)
            sleep_data = self.client.get_sleep_data(api_date)
            print_unique_keys(sleep_data)
            result = {
                "date": date_str,
                "duration": 0,
                "deep": 0,
                "light": 0,
                "rem": 0,
                "awake": 0,
                "heart_rate": {"avg": 0, "min": 0, "max": 0},
                "stress": 0,
                "body_battery": {"start": 0, "end": 0, "change": 0},
                "resting_heart_rate": 0,
                "sleep_movement": [],
                "rem_sleep_data": [],
                "sleep_levels": [],
                "respiration_data": [],
                "respiration_averages": [],
                "respiration_version": 0,
                "skin_temp_exists": False,
                "body_battery_change": 0
            }
            
            # 处理睡眠数据
            if isinstance(sleep_data, dict):
                # 填充睡眠移动数据
                if "sleepMovement" in sleep_data:
                    result["sleep_movement"] = sleep_data["sleepMovement"]
                
                # 填充REM睡眠数据
                if "remSleepData" in sleep_data:
                    result["rem_sleep_data"] = sleep_data["remSleepData"]
                
                # 填充睡眠级别数据
                if "sleepLevels" in sleep_data:
                    result["sleep_levels"] = sleep_data["sleepLevels"]
                
                # 填充呼吸数据
                if "wellnessEpochRespirationDataDTOList" in sleep_data:
                    result["respiration_data"] = sleep_data["wellnessEpochRespirationDataDTOList"]
                
                # 填充呼吸平均值数据
                if "wellnessEpochRespirationAveragesList" in sleep_data:
                    result["respiration_averages"] = sleep_data["wellnessEpochRespirationAveragesList"]
                
                # 填充呼吸版本
                if "respirationVersion" in sleep_data:
                    result["respiration_version"] = sleep_data["respirationVersion"]
                
                # 填充皮肤温度数据存在标志
                if "skinTempDataExists" in sleep_data:
                    result["skin_temp_exists"] = sleep_data["skinTempDataExists"]
                
                # 填充身体电量变化
                if "bodyBatteryChange" in sleep_data:
                    result["body_battery_change"] = sleep_data["bodyBatteryChange"]
                
                # 填充静息心率
                if "restingHeartRate" in sleep_data:
                    result["resting_heart_rate"] = sleep_data["restingHeartRate"]
                

                # 填充睡眠压力
                if "sleepStress" in sleep_data:
                    result["stress"] = sleep_data["sleepStress"]
                

            # 保存到缓存
            self._save_to_cache(cache_key, result)
            
            return result
        
        except Exception as e:
            print(f"获取睡眠数据失败: {e}")

            # 返回默认睡眠数据结构
            return {"date": date_str, "duration": 0, "deep": 0, "light": 0, "rem": 0, "awake": 0}
    
    def get_activities(self, date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        获取指定日期的活动数据
        
        Args:
            date: 日期，默认为今天
            
        Returns:
            List[Dict[str, Any]]: 活动数据列表
        """
        # 设置默认日期为今天
        if date is None:
            date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        date_str = date.strftime("%Y-%m-%d")
        cache_key = f"activities_{date_str}"
        
        # 尝试从缓存获取
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        # 如果客户端未初始化或登录失败，返回空列表
        if not self.client:
            return []
        
        try:
            # 获取活动数据
            activities = self.client.get_activities_by_date(date.isoformat(), date.isoformat())
            
            # 提取活动信息
            result = []
            for activity in activities:
                # 提取活动类型、时长和消耗的卡路里
                activity_type = activity.get("activityType", {}).get("typeKey", "未知")
                duration_minutes = activity.get("duration", 0) / 60  # 转换为分钟
                calories = activity.get("calories", 0)
                distance = activity.get("distance", 0) / 1000  # 转换为公里
                
                result.append({
                    "type": activity_type,
                    "duration": round(duration_minutes, 1),
                    "calories": calories,
                    "distance": round(distance, 2)
                })
            
            # 保存到缓存
            self._save_to_cache(cache_key, result)
            
            return result
        
        except Exception as e:
            print(f"获取活动数据失败: {e}")
            return []
    
    def get_daily_fitness_data(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        获取指定日期的综合健身数据
        
        Args:
            date: 日期，默认为今天
            
        Returns:
            Dict[str, Any]: 综合健身数据字典
        """
        # 设置默认日期为今天
        if date is None:
            date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        date_str = date.strftime("%Y-%m-%d")
        
        # 获取各项数据
        steps_data = self.get_steps_data(date)
        heart_rate_data = self.get_heart_rate(date)
        sleep_data = self.get_sleep_data(date)
        activities = self.get_activities(date)
        
        # 获取总消耗卡路里
        total_calories = 0
        for activity in activities:
            total_calories += activity.get("calories", 0)
        
        # 整合数据
        return {
            "date": date_str,
            "steps": steps_data.get("steps", 0),
            "calories": total_calories,
            "heart_rate": {
                "avg": heart_rate_data.get("avg", 0),
                "min": heart_rate_data.get("min", 0),
                "max": heart_rate_data.get("max", 0)
            },
            "sleep": {
                "duration": sleep_data.get("duration", 0),
                "deep": sleep_data.get("deep", 0),
                "light": sleep_data.get("light", 0),
                "rem": sleep_data.get("rem", 0),
                "awake": sleep_data.get("awake", 0)
            },
            "activities": activities
        }
    
    def get_weekly_fitness_data(self, end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        获取一周的健身数据
        
        Args:
            end_date: 结束日期，默认为今天
            
        Returns:
            List[Dict[str, Any]]: 一周的健身数据列表
        """
        # 设置默认结束日期为今天
        if end_date is None:
            end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 计算开始日期（7天前）
        start_date = end_date - timedelta(days=6)
        
        # 获取每天的数据
        result = []
        current_date = start_date
        while current_date <= end_date:
            daily_data = self.get_daily_fitness_data(current_date)
            result.append(daily_data)
            current_date += timedelta(days=1)
        
        return result
"""
KFit API后端服务
提供REST API接口供前端调用
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
from datetime import datetime, date, timedelta
import pandas as pd
import os
import sys
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# 导入现有KFit代码
try:
    from main import analyze_daily_health, analyze_weekly_health, get_model
    from config.config import Config
    from modules.garmin.garmin_client import GarminClient
    from modules.notion.notion_client import NotionClient
    from modules.diary.diary_parser import DiaryParser
except ImportError as e:
    logger.error(f"导入KFit模块失败: {e}")
    # 提供模拟数据用于前端开发
    pass

# 创建FastAPI应用
app = FastAPI(
    title="KFit API",
    description="KFit健康分析系统API",
    version="1.0.0"
)

# CORS配置 - 开发环境允许所有来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局配置和客户端实例
config = None
garmin_client = None
notion_client = None
diary_parser = None

def init_clients():
    """初始化所有客户端"""
    global config, garmin_client, notion_client, diary_parser

    try:
        config = Config()
        logger.info("配置加载成功")

        # 初始化Garmin客户端
        garmin_config = config.get_garmin_config()
        garmin_client = GarminClient(garmin_config)
        logger.info("Garmin客户端初始化成功")

        # 初始化Notion客户端
        notion_config = config.get_notion_config()
        notion_client = NotionClient(notion_config)
        logger.info("Notion客户端初始化成功")

        # 初始化日记解析器
        diary_config = config.get_diary_config()
        diary_parser = DiaryParser(diary_config)
        logger.info("日记解析器初始化成功")

    except Exception as e:
        logger.error(f"客户端初始化失败: {e}")
        # 继续运行，前端可以使用模拟数据

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    init_clients()

@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "clients": {
            "garmin": garmin_client is not None,
            "notion": notion_client is not None,
            "diary": diary_parser is not None
        }
    }

@app.get("/api/config")
async def get_config():
    """获取配置"""
    try:
        if config:
            return {
                "model": config.get_model_config(),
                "garmin": config.get_garmin_config(),
                "notion": config.get_notion_config(),
                "diary": config.get_diary_config(),
                "analysis": config.get("analysis", {})
            }
        else:
            # 返回默认配置
            return {
                "model": {
                    "default": "openai",
                    "openai": {"api_key": "", "model": "gpt-3.5-turbo"},
                    "claude": {"api_key": "", "model": "claude-3-opus-20240229"}
                },
                "garmin": {"email": "", "password": ""},
                "notion": {"api_key": "", "page_id": ""},
                "diary": {"file_path": ""},
                "analysis": {"output_dir": "./output", "daily_report": True, "weekly_report": True}
            }
    except Exception as e:
        logger.error(f"获取配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/config")
async def update_config(config_data: Dict[str, Any]):
    """更新配置"""
    try:
        # 保存配置到config.yaml
        config_path = "../config/config.yaml"
        if os.path.exists(config_path):
            with open(config_path, "w") as f:
                import yaml
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)

            # 重新加载配置
            global config
            config = Config()
            init_clients()

            return {"status": "success", "message": "配置已更新"}
        else:
            raise HTTPException(status_code=404, detail="配置文件不存在")
    except Exception as e:
        logger.error(f"更新配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 模拟数据生成函数
def generate_mock_fitness_data(start_date: date, end_date: date) -> List[Dict[str, Any]]:
    """生成模拟健身数据用于前端开发"""
    data = []
    current_date = start_date
    while current_date <= end_date:
        # 生成一些随机但合理的数据
        import random
        steps = random.randint(3000, 15000)
        calories = int(steps * 0.05) + random.randint(100, 500)
        heart_rate_avg = random.randint(60, 85)
        heart_rate_min = random.randint(50, heart_rate_avg - 5)
        heart_rate_max = random.randint(heart_rate_avg + 5, 160)

        # 睡眠数据
        sleep_duration = round(random.uniform(6, 9), 1)
        sleep_deep = round(sleep_duration * random.uniform(0.2, 0.3), 1)
        sleep_light = round(sleep_duration * random.uniform(0.4, 0.5), 1)
        sleep_rem = round(sleep_duration * random.uniform(0.1, 0.2), 1)
        sleep_awake = round(sleep_duration * random.uniform(0.05, 0.1), 1)

        # 活动数据
        activities = []
        if random.random() > 0.3:  # 70%概率有活动
            activity_types = ["跑步", "步行", "游泳", "骑行", "健身"]
            activity_type = random.choice(activity_types)
            duration = random.randint(15, 120)
            activity_calories = random.randint(50, 800)
            activities.append({
                "type": activity_type,
                "duration": duration,
                "calories": activity_calories,
                "distance": round(random.uniform(0.5, 10), 1) if activity_type in ["跑步", "步行", "骑行"] else 0
            })

        data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "steps": steps,
            "calories": calories,
            "heart_rate": {
                "avg": heart_rate_avg,
                "min": heart_rate_min,
                "max": heart_rate_max
            },
            "sleep": {
                "duration": sleep_duration,
                "deep": sleep_deep,
                "light": sleep_light,
                "rem": sleep_rem,
                "awake": sleep_awake
            },
            "activities": activities,
            "duration": sum(act["duration"] for act in activities)
        })
        current_date += timedelta(days=1)

    return data

@app.get("/api/fitness")
async def get_fitness_data(start_date: str, end_date: str):
    """获取健身数据"""
    try:
        # 解析日期
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()

        # 如果客户端已初始化，尝试获取真实数据
        if garmin_client:
            try:
                data = []
                current_date = start_dt
                while current_date <= end_dt:
                    daily_data = garmin_client.get_daily_fitness_data(current_date)
                    daily_data["date"] = current_date.strftime("%Y-%m-%d")
                    data.append(daily_data)
                    current_date += timedelta(days=1)
                logger.info(f"成功获取{len(data)}天健身数据")
                return data
            except Exception as e:
                logger.warning(f"获取真实健身数据失败: {e}，使用模拟数据")

        # 使用模拟数据
        mock_data = generate_mock_fitness_data(start_dt, end_dt)
        logger.info(f"生成{len(mock_data)}天模拟健身数据")
        return mock_data

    except Exception as e:
        logger.error(f"获取健身数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def generate_mock_nutrition_data(start_date: date, end_date: date) -> List[Dict[str, Any]]:
    """生成模拟营养数据用于前端开发"""
    data = []
    current_date = start_date
    while current_date <= end_date:
        import random
        # 三餐数据
        meals = []
        meal_types = ["早餐", "午餐", "晚餐"]
        for meal_type in meal_types:
            if random.random() > 0.2:  # 80%概率有这餐
                calories = random.randint(300, 800)
                protein = round(random.uniform(10, 30), 1)
                carbs = round(random.uniform(30, 80), 1)
                fat = round(random.uniform(10, 30), 1)

                meals.append({
                    "meal": meal_type,
                    "content": f"{meal_type}内容示例",
                    "calories": calories,
                    "protein": protein,
                    "carbs": carbs,
                    "fat": fat
                })

        data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "meals": meals,
            "total_calories": sum(meal["calories"] for meal in meals),
            "total_protein": sum(meal["protein"] for meal in meals),
            "total_carbs": sum(meal["carbs"] for meal in meals),
            "total_fat": sum(meal["fat"] for meal in meals)
        })
        current_date += timedelta(days=1)

    return data

@app.get("/api/nutrition")
async def get_nutrition_data(start_date: str, end_date: str):
    """获取营养数据"""
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()

        # 如果客户端已初始化，尝试获取真实数据
        if notion_client:
            try:
                data = notion_client.get_food_data_range(start_dt, end_dt)
                # 转换为前端格式
                formatted_data = []
                for item in data:
                    formatted_item = {
                        "date": item.get("date", ""),
                        "meal": item.get("meal", ""),
                        "content": item.get("content", ""),
                        "calories": item.get("calories", 0),
                        "protein": item.get("protein", 0),
                        "carbs": item.get("carbs", 0),
                        "fat": item.get("fat", 0)
                    }
                    formatted_data.append(formatted_item)
                logger.info(f"成功获取{len(formatted_data)}天营养数据")
                return formatted_data
            except Exception as e:
                logger.warning(f"获取真实营养数据失败: {e}，使用模拟数据")

        # 使用模拟数据
        mock_data = generate_mock_nutrition_data(start_dt, end_dt)
        logger.info(f"生成{len(mock_data)}天模拟营养数据")
        return mock_data

    except Exception as e:
        logger.error(f"获取营养数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/summary")
async def get_summary(start_date: str, end_date: str):
    """获取数据摘要"""
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()

        # 获取健身数据
        fitness_data = await get_fitness_data(start_date, end_date)
        df_fitness = pd.DataFrame(fitness_data)

        # 获取营养数据
        nutrition_data = await get_nutrition_data(start_date, end_date)
        df_nutrition = pd.DataFrame(nutrition_data)

        # 计算摘要
        summary = {
            "steps": int(df_fitness["steps"].sum()),
            "calories": int(df_fitness["calories"].sum()),
            "activity_hours": round(df_fitness["duration"].sum() / 60, 1),
            "sleep_hours": round(df_fitness["sleep"].apply(lambda x: x.get("duration", 0)).mean(), 1),
            "avg_heart_rate": int(df_fitness["heart_rate"].apply(lambda x: x.get("avg", 0)).mean()),
            "activity_count": len(df_fitness[df_fitness["activities"].apply(lambda x: len(x) if isinstance(x, list) else 0) > 0]),
            "nutrition_days": len(df_nutrition),
            "avg_daily_calories": int(df_nutrition["total_calories"].mean()) if len(df_nutrition) > 0 else 0,
            "avg_daily_protein": round(df_nutrition["total_protein"].mean(), 1) if len(df_nutrition) > 0 else 0,
            "date_range": f"{start_date} 至 {end_date}"
        }

        return summary
    except Exception as e:
        logger.error(f"获取摘要数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/activities/recent")
async def get_recent_activities(limit: int = 10):
    """获取最近活动"""
    try:
        # 获取最近7天的数据
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)

        all_activities = []

        # 如果客户端已初始化，尝试获取真实数据
        if garmin_client:
            try:
                current_date = start_date
                while current_date <= end_date:
                    activities = garmin_client.get_activities(current_date)
                    for activity in activities:
                        activity["date"] = current_date.strftime("%Y-%m-%d")
                        all_activities.append(activity)
                    current_date += timedelta(days=1)
            except Exception as e:
                logger.warning(f"获取真实活动数据失败: {e}，使用模拟数据")

        # 如果没有真实数据，生成模拟数据
        if not all_activities:
            import random
            activity_types = ["跑步", "步行", "游泳", "骑行", "健身"]
            for i in range(min(limit * 2, 20)):  # 生成更多数据用于排序
                activity_type = random.choice(activity_types)
                duration = random.randint(15, 120)
                calories = random.randint(50, 800)

                all_activities.append({
                    "id": f"mock_{i}",
                    "type": activity_type,
                    "duration": duration,
                    "calories": calories,
                    "distance": round(random.uniform(0.5, 10), 1) if activity_type in ["跑步", "步行", "骑行"] else 0,
                    "start_time": (datetime.now() - timedelta(days=random.randint(0, 7),
                                                             hours=random.randint(0, 23),
                                                             minutes=random.randint(0, 59))).isoformat(),
                    "date": (datetime.now() - timedelta(days=random.randint(0, 7))).strftime("%Y-%m-%d")
                })

        # 按时间排序并限制数量
        sorted_activities = sorted(all_activities, key=lambda x: x.get("start_time", ""), reverse=True)
        return sorted_activities[:limit]
    except Exception as e:
        logger.error(f"获取最近活动失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def analyze_health(data: Dict[str, Any], background_tasks: BackgroundTasks):
    """分析健康数据"""
    try:
        date_str = data.get("date", "")
        model_type = data.get("model_type", "openai")
        analysis_type = data.get("type", "daily")  # daily, weekly

        # 设置模型类型
        if config:
            model_config = config.get_model_config()
            model_config["default"] = model_type
            config.set_model_config(model_config)

        # 执行分析
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

        if analysis_type == "weekly":
            # 计算周范围
            start_date = date_obj - timedelta(days=6)
            end_date = date_obj
            result = analyze_weekly_health(end_date, config_path="../config/config.yaml")
        else:
            result = analyze_daily_health(date_obj, config_path="../config/config.yaml")

        # 格式化结果
        formatted_result = {
            "date": date_str,
            "type": analysis_type,
            "summary": result.get("summary", "分析完成"),
            "food_analysis": result.get("food_analysis", ""),
            "fitness_analysis": result.get("fitness_analysis", ""),
            "recommendations": result.get("recommendations", ""),
            "model_used": model_type
        }

        return formatted_result
    except Exception as e:
        logger.error(f"健康分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports")
async def get_reports(date: str = None):
    """获取报告列表"""
    try:
        output_dir = "../output"
        if not os.path.exists(output_dir):
            return []

        reports = []
        for filename in os.listdir(output_dir):
            if filename.endswith(".txt") and "health_report" in filename:
                file_path = os.path.join(output_dir, filename)
                # 提取日期信息
                import re
                date_match = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
                report_date = date_match.group(1) if date_match else "未知"

                # 如果是特定日期，只返回该日期的报告
                if date and report_date != date:
                    continue

                # 读取报告内容摘要
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        # 提取前100个字符作为摘要
                        summary = content[:100] + "..." if len(content) > 100 else content
                except:
                    summary = "无法读取报告内容"

                reports.append({
                    "filename": filename,
                    "path": file_path,
                    "date": report_date,
                    "type": "weekly" if "weekly" in filename else "daily",
                    "summary": summary,
                    "created_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
                })

        # 按日期排序
        reports.sort(key=lambda x: x["created_at"], reverse=True)
        return reports
    except Exception as e:
        logger.error(f"获取报告失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/{filename}")
async def get_report_content(filename: str):
    """获取报告内容"""
    try:
        file_path = os.path.join("../output", filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="报告不存在")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return {
            "filename": filename,
            "content": content,
            "created_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
        }
    except Exception as e:
        logger.error(f"获取报告内容失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
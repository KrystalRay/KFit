import os
import sys
import argparse
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# 导入配置模块
from config.config import Config

# 导入Notion和Garmin客户端
from modules.notion.notion_client import NotionClient
from modules.garmin.garmin_client import GarminClient

# 导入模型工厂
from models.base_model import BaseModel
from models.openai_model import OpenAIModel
from models.claude_model import ClaudeModel
from models.local_model import LocalModel


def get_model(config: Config) -> BaseModel:
    """
    根据配置获取大模型实例
    
    Args:
        config: 配置对象
        
    Returns:
        BaseModel: 大模型实例
    """
    model_config = config.get_model_config()
    model_type = model_config.get('default', 'openai')
    
    if model_type == 'openai':
        return OpenAIModel(model_config.get('openai', {}))
    elif model_type == 'claude':
        return ClaudeModel(model_config.get('claude', {}))
    elif model_type == 'local':
        return LocalModel(model_config.get('local', {}))
    else:
        print(f"未知的模型类型: {model_type}，使用OpenAI模型作为默认值")
        return OpenAIModel(model_config.get('openai', {}))


def analyze_daily_health(date: Optional[datetime] = None, config_path: Optional[str] = None):
    """
    分析指定日期的健康数据
    
    Args:
        date: 日期，默认为今天
        config_path: 配置文件路径，默认为None
    """
    # 设置默认日期为今天
    if date is None:
        date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    date_str = date.strftime("%Y-%m-%d")
    print(f"\n===== 分析 {date_str} 的健康数据 =====")
    
    # 加载配置
    config = Config(config_path)
    
    # 初始化Notion客户端
    notion_config = config.get_notion_config()
    notion_client = NotionClient(notion_config)
    
    # 初始化Garmin客户端
    garmin_config = config.get_garmin_config()
    garmin_client = GarminClient(garmin_config)
    
    # 获取饮食数据
    print("\n获取Notion饮食数据...")
    food_data = notion_client.get_food_data(date)
    print(f"找到 {len(food_data.get('items', []))} 条饮食记录")
    
    # 获取健身数据
    print("\n获取Garmin健身数据...")
    fitness_data = garmin_client.get_daily_fitness_data(date)
    print(f"步数: {fitness_data.get('steps', 0)}")
    print(f"活动数量: {len(fitness_data.get('activities', []))}")
    
    # 如果没有数据，提示用户
    if not food_data.get('items') and not fitness_data.get('activities'):
        print("\n警告: 没有找到饮食和健身数据，无法进行分析")
        return
    
    # 初始化大模型
    print("\n初始化大模型...")
    model = get_model(config)
    model_info = model.get_model_info()
    print(f"使用模型: {model_info.get('provider')} - {model_info.get('model')}")
    
    # 分析健康数据
    print("\n分析健康数据...")
    analysis = model.analyze_health(food_data, fitness_data)
    
    # 输出分析结果
    print("\n===== 健康分析结果 =====")
    print(f"\n总体健康状况:\n{analysis.get('summary', '')}")
    
    if analysis.get('food_analysis'):
        print(f"\n饮食分析:\n{analysis.get('food_analysis')}")
    
    if analysis.get('fitness_analysis'):
        print(f"\n健身分析:\n{analysis.get('fitness_analysis')}")
    
    if analysis.get('recommendations'):
        print(f"\n改进建议:\n{analysis.get('recommendations')}")
    
    # 保存分析结果
    analysis_config = config.get('analysis', {})
    if analysis_config.get('daily_report', True):
        output_dir = analysis_config.get('output_dir', './output')
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"health_report_{date_str}.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"===== {date_str} 健康分析报告 =====\n\n")
            f.write(f"总体健康状况:\n{analysis.get('summary', '')}\n\n")
            f.write(f"饮食分析:\n{analysis.get('food_analysis', '')}\n\n")
            f.write(f"健身分析:\n{analysis.get('fitness_analysis', '')}\n\n")
            f.write(f"改进建议:\n{analysis.get('recommendations', '')}\n\n")
        
        print(f"\n分析报告已保存到: {output_file}")


def analyze_weekly_health(end_date: Optional[datetime] = None, config_path: Optional[str] = None):
    """
    分析一周的健康数据
    
    Args:
        end_date: 结束日期，默认为今天
        config_path: 配置文件路径，默认为None
    """
    # 设置默认结束日期为今天
    if end_date is None:
        end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 计算开始日期（7天前）
    start_date = end_date - timedelta(days=6)
    
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    print(f"\n===== 分析 {start_date_str} 至 {end_date_str} 的健康数据 =====")
    
    # 加载配置
    config = Config(config_path)
    
    # 初始化Notion客户端
    notion_config = config.get_notion_config()
    notion_client = NotionClient(notion_config)
    
    # 初始化Garmin客户端
    garmin_config = config.get_garmin_config()
    garmin_client = GarminClient(garmin_config)
    
    # 获取饮食数据
    print("\n获取Notion饮食数据...")
    food_data_list = notion_client.get_food_data_range(start_date, end_date)
    print(f"找到 {len(food_data_list)} 天的饮食记录")
    
    # 获取健身数据
    print("\n获取Garmin健身数据...")
    fitness_data_list = garmin_client.get_weekly_fitness_data(end_date)
    print(f"找到 {len(fitness_data_list)} 天的健身记录")
    
    # 合并数据
    print("\n整合周数据...")
    weekly_food_data = {
        "start_date": start_date_str,
        "end_date": end_date_str,
        "items": []
    }
    
    for food_data in food_data_list:
        weekly_food_data["items"].extend(food_data.get("items", []))
    
    weekly_fitness_data = {
        "start_date": start_date_str,
        "end_date": end_date_str,
        "steps": 0,
        "calories": 0,
        "activities": [],
        "heart_rate": {"avg": 0, "min": 0, "max": 0},
        "sleep": {"duration": 0, "deep": 0, "light": 0}
    }
    
    # 计算平均值和总和
    valid_days = len(fitness_data_list)
    if valid_days > 0:
        total_steps = 0
        total_calories = 0
        total_heart_rate_avg = 0
        total_heart_rate_min = 0
        total_heart_rate_max = 0
        total_sleep_duration = 0
        total_sleep_deep = 0
        total_sleep_light = 0
        
        for fitness_data in fitness_data_list:
            total_steps += fitness_data.get("steps", 0)
            total_calories += fitness_data.get("calories", 0)
            
            heart_rate = fitness_data.get("heart_rate", {})
            total_heart_rate_avg += heart_rate.get("avg", 0)
            
            if heart_rate.get("min", 0) > 0:
                if total_heart_rate_min == 0 or heart_rate.get("min") < total_heart_rate_min:
                    total_heart_rate_min = heart_rate.get("min")
            
            if heart_rate.get("max", 0) > total_heart_rate_max:
                total_heart_rate_max = heart_rate.get("max")
            
            sleep = fitness_data.get("sleep", {})
            total_sleep_duration += sleep.get("duration", 0)
            total_sleep_deep += sleep.get("deep", 0)
            total_sleep_light += sleep.get("light", 0)
            
            weekly_fitness_data["activities"].extend(fitness_data.get("activities", []))
        
        # 计算平均值
        weekly_fitness_data["steps"] = total_steps
        weekly_fitness_data["calories"] = total_calories
        weekly_fitness_data["heart_rate"]["avg"] = round(total_heart_rate_avg / valid_days, 1)
        weekly_fitness_data["heart_rate"]["min"] = total_heart_rate_min
        weekly_fitness_data["heart_rate"]["max"] = total_heart_rate_max
        weekly_fitness_data["sleep"]["duration"] = round(total_sleep_duration / valid_days, 1)
        weekly_fitness_data["sleep"]["deep"] = round(total_sleep_deep / valid_days, 1)
        weekly_fitness_data["sleep"]["light"] = round(total_sleep_light / valid_days, 1)
    
    # 如果没有数据，提示用户
    if not weekly_food_data.get('items') and not weekly_fitness_data.get('activities'):
        print("\n警告: 没有找到饮食和健身数据，无法进行分析")
        return
    
    # 初始化大模型
    print("\n初始化大模型...")
    model = get_model(config)
    model_info = model.get_model_info()
    print(f"使用模型: {model_info.get('provider')} - {model_info.get('model')}")
    
    # 分析健康数据
    print("\n分析健康数据...")
    analysis = model.analyze_health(weekly_food_data, weekly_fitness_data)
    
    # 输出分析结果
    print("\n===== 周健康分析结果 =====")
    print(f"\n总体健康状况:\n{analysis.get('summary', '')}")
    
    if analysis.get('food_analysis'):
        print(f"\n饮食分析:\n{analysis.get('food_analysis')}")
    
    if analysis.get('fitness_analysis'):
        print(f"\n健身分析:\n{analysis.get('fitness_analysis')}")
    
    if analysis.get('recommendations'):
        print(f"\n改进建议:\n{analysis.get('recommendations')}")
    
    # 保存分析结果
    analysis_config = config.get('analysis', {})
    if analysis_config.get('weekly_report', True):
        output_dir = analysis_config.get('output_dir', './output')
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"weekly_health_report_{start_date_str}_to_{end_date_str}.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"===== {start_date_str} 至 {end_date_str} 周健康分析报告 =====\n\n")
            f.write(f"总体健康状况:\n{analysis.get('summary', '')}\n\n")
            f.write(f"饮食分析:\n{analysis.get('food_analysis', '')}\n\n")
            f.write(f"健身分析:\n{analysis.get('fitness_analysis', '')}\n\n")
            f.write(f"改进建议:\n{analysis.get('recommendations', '')}\n\n")
        
        print(f"\n周分析报告已保存到: {output_file}")


def analyze_diary_health(date: Optional[datetime] = None, config_path: Optional[str] = None):
    """
    分析日记文件中指定日期的健康数据
    
    Args:
        date: 日期，默认为今天
        config_path: 配置文件路径，默认为None
    """
    # 设置默认日期为今天
    if date is None:
        date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    date_str = date.strftime("%Y-%m-%d")
    print(f"\n===== 分析日记文件中 {date_str} 的健康数据 =====")
    
    # 加载配置
    config = Config(config_path)
    
    # 获取日记配置
    diary_config = config.get_diary_config()
    diary_file_path = diary_config.get('file_path')
    
    if not diary_file_path:
        print("错误: 未配置日记文件路径，请在config.yaml中设置diary.file_path")
        return
    
    if not os.path.exists(diary_file_path):
        print(f"错误: 日记文件不存在: {diary_file_path}")
        return
    
    # 初始化日记解析器
    from modules.diary.diary_parser import DiaryParser
    diary_parser = DiaryParser(diary_config)
    
    # 获取饮食数据
    print("\n从日记文件获取饮食数据...")
    food_data = diary_parser.get_food_data(diary_file_path, date)
    print(f"找到 {len(food_data.get('items', []))} 条饮食记录")
    
    # 如果没有数据，提示用户
    if not food_data.get('items'):
        print("\n警告: 没有找到饮食数据，无法进行分析")
        return
    
    # 初始化大模型
    print("\n初始化大模型...")
    model = get_model(config)
    model_info = model.get_model_info()
    print(f"使用模型: {model_info.get('provider')} - {model_info.get('model')}")
    
    # 构建一个空的健身数据结构
    fitness_data = {
        "date": date_str,
        "steps": 0,
        "calories": 0,
        "activities": [],
        "heart_rate": {"avg": 0, "min": 0, "max": 0},
        "sleep": {"duration": 0, "deep": 0, "light": 0}
    }
    
    # 分析健康数据
    print("\n分析健康数据...")
    analysis = model.analyze_health(food_data, fitness_data)
    
    # 输出分析结果
    print("\n===== 健康分析结果 =====")
    print(f"\n总体健康状况:\n{analysis.get('summary', '')}")
    
    if analysis.get('food_analysis'):
        print(f"\n饮食分析:\n{analysis.get('food_analysis')}")
    
    if analysis.get('recommendations'):
        print(f"\n改进建议:\n{analysis.get('recommendations')}")
    
    # 保存分析结果
    analysis_config = config.get('analysis', {})
    if analysis_config.get('daily_report', True):
        output_dir = analysis_config.get('output_dir', './output')
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"diary_health_report_{date_str}.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"===== {date_str} 日记健康分析报告 =====\n\n")
            f.write(f"总体健康状况:\n{analysis.get('summary', '')}\n\n")
            f.write(f"饮食分析:\n{analysis.get('food_analysis', '')}\n\n")
            f.write(f"改进建议:\n{analysis.get('recommendations', '')}\n\n")
        
        print(f"\n分析报告已保存到: {output_file}")


def main():
    """
    主函数
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='KFit - 个人健康分析系统')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--date', type=str, help='分析日期，格式为YYYY-MM-DD，默认为今天')
    parser.add_argument('--weekly', action='store_true', help='生成周报告')
    parser.add_argument('--diary', action='store_true', help='使用日记文件进行分析')
    parser.add_argument('--test-garmin', action='store_true', help='测试Garmin API模块')
    
    args = parser.parse_args()
    
    # 解析日期
    date = None
    if args.date:
        try:
            date = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            print(f"错误: 日期格式不正确，应为YYYY-MM-DD，例如2023-01-01")
            return
    
    try:
        # 根据参数执行相应的分析
        if args.test_garmin:
            # 测试Garmin API模块
            test_garmin_api(args.config)
        elif args.weekly and args.diary:
            # 目前没有实现周度日记分析功能
            print("周度日记分析功能尚未实现")
            # analyze_weekly_diary_health(date, args.config)
        elif args.weekly:
            analyze_weekly_health(date, args.config)
        elif args.diary:
            analyze_diary_health(date, args.config)
        else:
            analyze_daily_health(date, args.config)
    except Exception as e:
        print(f"\n执行过程中发生错误: {e}")
        print("提示: 请检查配置文件中的账号信息是否正确，网络连接是否正常")

if __name__ == "__main__":
    main()
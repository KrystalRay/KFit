from main import *
import os
import shutil
from models.openai_model import OpenAIModel
from config.config import Config


def test_openai_api(config_path: Optional[str] = None):
    """
    测试OpenAI API模块的功能
    
    Args:
        config_path: 配置文件路径，默认为None
    """
    print("\n===== 测试OpenAI API模块 =====\n")
    
    # 加载配置
    config = Config(config_path)
    
    # 获取OpenAI配置
    openai_config = config.get_model_config().get('openai', {})
    
    # 检查配置是否有效
    if not openai_config.get('api_key') or openai_config.get('api_key') == "your_openai_api_key":
        print("错误: OpenAI API密钥未配置或使用了默认值")
        print("请在config.yaml文件中设置有效的OpenAI API密钥")
        return
    
    print(f"使用OpenAI模型: {openai_config.get('model', 'gpt-3.5-turbo')}")
    
    try:
        # 初始化OpenAI客户端
        print("正在初始化OpenAI客户端...")
        openai_client = OpenAIModel(openai_config)
        
        # 测试简单问答
        print("\n1. 测试简单问答功能:")
        test_prompt = "中国的首都是哪里？"
        print(f"测试问题: {test_prompt}")
        response = openai_client.generate(test_prompt)
        print(f"回答: {response}")
        
        # 测试长文本处理
        print("\n2. 测试长文本处理:")
        long_text = """请总结以下文本:\n\n""" + "\n".join([f"这是第{i}行测试文本。" for i in range(1, 21)])
        print(f"测试文本长度: {len(long_text)}")
        response = openai_client.generate(long_text)
        print(f"总结结果: {response}")
        
        
        print("\n===== OpenAI API模块测试完成 =====\n")
    except Exception as e:
        print(f"\nOpenAI API测试过程中发生错误: {e}")
        print("请检查网络连接和OpenAI API配置")
        import traceback
        traceback.print_exc()

def clear_cache():
    """
    清除cache目录中的所有文件
    """
    cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
    if os.path.exists(cache_dir):
        for filename in os.listdir(cache_dir):
            file_path = os.path.join(cache_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                    print(f"删除缓存文件{file_path}成功")
            except Exception as e:
                print(f"删除缓存文件{file_path}失败: {e}")


def test_garmin_api(config_path: Optional[str] = None, days: int = 1):
    """
    测试Garmin API模块的功能
    
    Args:
        config_path: 配置文件路径，默认为None
        days: 查询最近多少天的数据，0表示只查询当天
    """
    print("\n===== 测试Garmin API模块 =====\n")
    
    # 加载配置
    config = Config(config_path)
    
    # 获取Garmin配置
    garmin_config = config.get_garmin_config()
    
    # 检查配置是否有效
    if not garmin_config.get('email') or garmin_config.get('email') == "your_garmin_email@example.com":
        print("错误: Garmin账号未配置或使用了默认值")
        print("请在config.yaml文件中设置有效的Garmin账号和密码")
        return
    
    print(f"使用Garmin账号: {garmin_config.get('email')}")
    
    try:
        # 初始化Garmin客户端
        print("正在连接Garmin服务器...")
        garmin_client = GarminClient(garmin_config)
        
        # 检查客户端是否成功初始化
        if not hasattr(garmin_client, 'client') or not garmin_client.client:
            print("Garmin客户端初始化失败，无法继续测试")
            return
        
        print("Garmin客户端初始化成功，开始获取数据...")
        
        # 计算查询日期范围
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        dates = [today - timedelta(days=i) for i in range(days)] if days > 0 else [today]
        
        # 测试获取步数数据
        print(f"\n1. 测试获取{len(dates)}天的步数数据:")
        for date in dates:
            steps_data = garmin_client.get_steps_data(date)
            print(f"\n日期: {steps_data.get('date')}")
            print(f"步数: {steps_data.get('steps')}")
        
        # 测试获取心率数据
        print(f"\n2. 测试获取{len(dates)}天的心率数据:")
        for date in dates:
            heart_rate_data = garmin_client.get_heart_rate(date)
            print(f"\n日期: {heart_rate_data.get('date')}")
            print(f"平均心率: {heart_rate_data.get('avg')}")
            print(f"最低心率: {heart_rate_data.get('min')}")
            print(f"最高心率: {heart_rate_data.get('max')}")
        
        # 测试获取睡眠数据
        print(f"\n3. 测试获取{len(dates)}天的睡眠数据:")
        for date in dates:
            try:
                sleep_data = garmin_client.get_sleep_data(date)
                format_date = date.strftime("%Y-%m-%d")
                print(f"\n日期: {sleep_data.get('date')}")
                print(f"睡眠时长: {sleep_data.get('duration')}小时")
                print(f"深度睡眠: {sleep_data.get('deep')}小时")
                print(f"浅度睡眠: {sleep_data.get('light')}小时")
                print(f"REM睡眠: {sleep_data.get('rem')}小时")
                print(f"清醒时间: {sleep_data.get('awake')}小时")
                print(f"平均心率: {sleep_data.get('heart_rate', {}).get('avg', 0)}")
                print(f"最低心率: {sleep_data.get('heart_rate', {}).get('min', 0)}")
                print(f"最高心率: {sleep_data.get('heart_rate', {}).get('max', 0)}")
                print(f"静息心率: {sleep_data.get('resting_heart_rate', 0)}")
                print(f"压力指数: {garmin_client.get_stress_data(date)}")
                print(f"身体电量变化: {sleep_data.get('body_battery_change', 0)}")
                print(f"身体电量开始值: {sleep_data.get('body_battery', {}).get('start', 0)}")
                print(f"身体电量结束值: {sleep_data.get('body_battery', {}).get('end', 0)}")
                print(f"皮肤温度数据存在: {sleep_data.get('skin_temp_exists', False)}")
                print(f"呼吸数据版本: {sleep_data.get('respiration_version', 0)}")
            except Exception as e:
                print(f"获取睡眠数据失败: {e}")
        
        # 测试获取活动数据
        print(f"\n4. 测试获取{len(dates)}天的活动数据:")
        for date in dates:
            activities = garmin_client.get_activities(date)
            print(f"\n日期: {date.strftime('%Y-%m-%d')}")
            print(f"活动数量: {len(activities)}")
            for i, activity in enumerate(activities):
                print(f"  活动 {i+1}:")
                print(f"    类型: {activity.get('type')}")
                print(f"    时长: {activity.get('duration')}分钟")
                print(f"    消耗卡路里: {activity.get('calories')}")
                print(f"    距离: {activity.get('distance')}公里")
        
        # 测试获取综合健身数据
        print(f"\n5. 测试获取{len(dates)}天的综合健身数据:")
        for date in dates:
            fitness_data = garmin_client.get_daily_fitness_data(date)
            print(f"\n日期: {fitness_data.get('date')}")
            print(f"步数: {fitness_data.get('steps')}")
            print(f"消耗卡路里: {fitness_data.get('calories')}")
            print(f"活动数量: {len(fitness_data.get('activities', []))}")
        
        # 测试获取体重数据
        print("\n6. 测试获取体重数据:")
        for date in dates:
            weight_data = garmin_client.get_daily_weigh_ins(date,date)
            for measurement in weight_data:
                print(f"时间: {measurement['time']}, 体重: {measurement['weight']}kg")
                print(f"体脂率: {measurement['body_fat']}%")

        # 测试获取一周的健身数据
        # print("\n6. 测试获取一周的健身数据:")
        # weekly_data = garmin_client.get_weekly_fitness_data(today)
        # print(f"获取到 {len(weekly_data)} 天的数据")
        
        print("\n===== Garmin API模块测试完成 =====\n")
    except Exception as e:
        print(f"\nGarmin API测试过程中发生错误: {e}")
        print("请检查网络连接和Garmin账号配置")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='测试Garmin API')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--days', type=int, default=0, help='查询最近多少天的数据，0表示只查询当天')
    args = parser.parse_args()
    
    clear_cache()
    # test_openai_api()
    test_garmin_api(args.config, args.days)
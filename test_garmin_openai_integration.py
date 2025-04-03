from main import *
import os
import shutil
from models.openai_model import OpenAIModel
from config.config import Config
from modules.garmin.garmin_client import GarminClient
from datetime import datetime, timedelta


def test_garmin_openai_integration(config_path: Optional[str] = None, days: int = 0):
    """
    测试Garmin模块与OpenAI模块的集成功能
    
    Args:
        config_path: 配置文件路径，默认为None
        days: 查询最近多少天的数据，0表示只查询当天
    """
    print("\n===== 测试Garmin与OpenAI集成 =====\n")
    
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
        
        # 获取健身数据
        fitness_data = {
            'date': today.strftime('%Y-%m-%d'),
            'steps': 0,
            'calories': 0,
            'activities': [],
            'heart_rate': {},
            'sleep': {}
        }
        
        # 获取步数数据
        for date in dates:
            steps_data = garmin_client.get_steps_data(date)
            fitness_data['steps'] += steps_data.get('steps', 0)
            
        # 获取心率数据
        for date in dates:
            heart_rate_data = garmin_client.get_heart_rate(date)
            fitness_data['heart_rate'] = {
                'avg': heart_rate_data.get('avg', 0),
                'min': heart_rate_data.get('min', 0),
                'max': heart_rate_data.get('max', 0)
            }
        
        # 获取活动数据
        for date in dates:
            activities = garmin_client.get_activities(date)
            for activity in activities:
                fitness_data['activities'].append({
                    'type': activity.get('type', '未知'),
                    'duration': activity.get('duration', 0),
                    'calories': activity.get('calories', 0),
                    'distance': activity.get('distance', 0)
                })
                fitness_data['calories'] += activity.get('calories', 0)
        
        # 获取睡眠数据
        for date in dates:
            try:
                sleep_data = garmin_client.get_sleep_data(date)
                fitness_data['sleep'] = {
                    'duration': sleep_data.get('duration', 0),
                    'deep': sleep_data.get('deep', 0),
                    'light': sleep_data.get('light', 0),
                    'rem': sleep_data.get('rem', 0),
                    'awake': sleep_data.get('awake', 0)
                }
            except Exception as e:
                print(f"获取睡眠数据失败: {e}")
        
        # 初始化OpenAI模型
        print("\n正在初始化OpenAI模型...")
        openai_config = config.get_model_config().get('openai', {})
        openai_client = OpenAIModel(openai_config)
        
        # 构建提示词
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
        
        # 调用OpenAI进行分析
        print("\n正在调用OpenAI进行分析...")
        response = openai_client.generate(prompt)
        
        # 输出分析结果
        print("\n===== 健康分析结果 =====\n")
        print(response)
        
        print("\n===== Garmin与OpenAI集成测试完成 =====\n")
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='测试Garmin与OpenAI集成')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--days', type=int, default=0, help='查询最近多少天的数据，0表示只查询当天')
    args = parser.parse_args()
    
    test_garmin_openai_integration(args.config, args.days)
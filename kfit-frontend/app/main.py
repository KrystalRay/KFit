"""
KFit 健康分析系统前端主应用
基于Streamlit构建的现代化健康数据可视化界面
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import requests
import json
import os
from typing import Dict, Any, Optional, List

# 设置页面配置
st.set_page_config(
    page_title="KFit 健康分析系统",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/yourusername/kfit-frontend",
        "Report a bug": "https://github.com/yourusername/kfit-frontend/issues",
        "About": "KFit - 个人健康分析系统"
    }
)

# 自定义CSS样式
def load_css():
    """加载自定义CSS样式"""
    st.markdown("""
    <style>
    /* 全局样式 */
    .main {
        background-color: #f8f9fa;
    }

    /* 卡片样式 */
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 10px;
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }

    .metric-label {
        font-size: 1rem;
        color: #6c757d;
        margin-top: 5px;
    }

    .metric-unit {
        font-size: 0.8rem;
        color: #6c757d;
    }

    /* 标题样式 */
    .section-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #343a40;
        margin: 20px 0 10px 0;
        padding-bottom: 5px;
        border-bottom: 2px solid #1f77b4;
    }

    /* 按钮样式 */
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-weight: 500;
    }

    .stButton>button:hover {
        background-color: #145a8d;
    }

    /* 侧边栏样式 */
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }

    /* 警告样式 */
    .stAlert {
        border-radius: 10px;
    }

    /* 自定义标签页样式 */
    .stTabs [data-basemui-label] {
        font-size: 1rem;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

# API客户端
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
            st.warning(f"API请求失败: {e}")
            return {}

    def _post(self, endpoint: str, data: Dict[Any, Any] = None, **kwargs) -> Dict[Any, Any]:
        """发送POST请求"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.post(url, json=data, timeout=30, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.warning(f"API请求失败: {e}")
            return {}

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return self._get("/api/health")

    def get_fitness_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """获取健身数据"""
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        data = self._get("/api/fitness", params=params)
        return pd.DataFrame(data) if data else pd.DataFrame()

    def get_nutrition_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """获取营养数据"""
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        data = self._get("/api/nutrition", params=params)
        return pd.DataFrame(data) if data else pd.DataFrame()

    def get_summary(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取摘要数据"""
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        return self._get("/api/summary", params=params)

    def get_recent_activities(self, limit: int = 10) -> pd.DataFrame:
        """获取最近活动"""
        params = {"limit": limit}
        data = self._get("/api/activities/recent", params=params)
        return pd.DataFrame(data) if data else pd.DataFrame()

    def analyze_health(self, date: str, model_type: str = "openai", analysis_type: str = "daily") -> Dict[str, Any]:
        """分析健康数据"""
        data = {
            "date": date,
            "model_type": model_type,
            "type": analysis_type
        }
        return self._post("/api/analyze", data=data)

    def get_reports(self, date: str = None) -> List[Dict[str, Any]]:
        """获取报告列表"""
        params = {}
        if date:
            params["date"] = date
        return self._get("/api/reports", params=params)

    def get_report_content(self, filename: str) -> Dict[str, Any]:
        """获取报告内容"""
        return self._get(f"/api/reports/{filename}")

# 页面组件
def metric_card(title: str, value: str, unit: str = "", icon: str = ""):
    """指标卡片组件"""
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 2rem;">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{title}</div>
        <div class="metric-unit">{unit}</div>
    </div>
    """, unsafe_allow_html=True)

def show_dashboard(api_client: KFitAPIClient):
    """显示仪表盘页面"""
    st.title("健康仪表盘 🏃")

    # 日期范围选择
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("开始日期", datetime.now() - timedelta(days=7))
    with col2:
        end_date = st.date_input("结束日期", datetime.now())

    # 转换为字符串格式
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    # 创建加载状态
    with st.spinner("加载数据中..."):
        # 并行获取数据
        summary = api_client.get_summary(start_date_str, end_date_str)
        fitness_data = api_client.get_fitness_data(start_date_str, end_date_str)
        nutrition_data = api_client.get_nutrition_data(start_date_str, end_date_str)
        recent_activities = api_client.get_recent_activities(5)

    # 摘要卡片
    st.markdown('<div class="section-title">健康摘要</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("步数", f"{summary.get('steps', 0):,}", "步", "📊")
    with col2:
        metric_card("卡路里", f"{summary.get('calories', 0):,}", "卡", "🔥")
    with col3:
        metric_card("活动时长", f"{summary.get('activity_hours', 0):.1f}", "小时", "🏃")
    with col4:
        metric_card("睡眠时间", f"{summary.get('sleep_hours', 0):.1f}", "小时", "😴")

    # 健身数据图表
    st.markdown('<div class="section-title">健身数据</div>', unsafe_allow_html=True)

    if not fitness_data.empty:
        # 健身数据趋势图
        col1, col2 = st.columns(2)

        with col1:
            # 步数和卡路里趋势
            fig1 = st.empty()  # 占位符，稍后会用Plotly图表替换
            st.markdown("**步数和卡路里趋势**")
            # 使用简单的折线图作为占位符
            chart_data = pd.DataFrame({
                '日期': fitness_data['date'],
                '步数': fitness_data['steps'],
                '卡路里': fitness_data['calories']
            })
            st.line_chart(chart_data.set_index('日期'))

        with col2:
            # 心率趋势
            st.markdown("**心率趋势**")
            if 'heart_rate' in fitness_data.columns:
                # 提取心率数据
                heart_rate_data = []
                for idx, row in fitness_data.iterrows():
                    hr = row['heart_rate']
                    if isinstance(hr, dict):
                        heart_rate_data.append({
                            '日期': row['date'],
                            '平均心率': hr.get('avg', 0),
                            '最小心率': hr.get('min', 0),
                            '最大心率': hr.get('max', 0)
                        })

                if heart_rate_data:
                    hr_df = pd.DataFrame(heart_rate_data)
                    st.line_chart(hr_df.set_index('日期'))
                else:
                    st.info("无心率数据")
            else:
                st.info("无心率数据")

        # 活动类型分布
        if 'activities' in fitness_data.columns:
            st.markdown("**活动类型分布**")
            # 统计活动类型
            activity_types = []
            for activities in fitness_data['activities']:
                if isinstance(activities, list):
                    for activity in activities:
                        if isinstance(activity, dict):
                            activity_types.append(activity.get('type', '未知'))

            if activity_types:
                activity_counts = pd.Series(activity_types).value_counts()
                st.bar_chart(activity_counts)
            else:
                st.info("无活动数据")
    else:
        st.info("暂无健身数据，请检查Garmin账号配置")

    # 营养数据
    st.markdown('<div class="section-title">营养数据</div>', unsafe_allow_html=True)

    if not nutrition_data.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**每日卡路里摄入**")
            if 'total_calories' in nutrition_data.columns:
                st.line_chart(nutrition_data.set_index('date')['total_calories'])
            else:
                st.info("无卡路里数据")

        with col2:
            st.markdown("**营养元素分布**")
            if all(col in nutrition_data.columns for col in ['total_protein', 'total_carbs', 'total_fat']):
                # 计算平均值
                avg_nutrition = nutrition_data[['total_protein', 'total_carbs', 'total_fat']].mean()
                st.bar_chart(avg_nutrition)
            else:
                st.info("无营养元素数据")
    else:
        st.info("暂无营养数据，请检查Notion账号配置")

    # 最近活动
    st.markdown('<div class="section-title">最近活动</div>', unsafe_allow_html=True)

    if not recent_activities.empty:
        # 格式化活动数据
        display_activities = recent_activities.copy()
        if 'start_time' in display_activities.columns:
            display_activities['开始时间'] = pd.to_datetime(display_activities['start_time']).dt.strftime('%Y-%m-%d %H:%M')
            display_activities['活动类型'] = display_activities['type']
            display_activities['时长(分钟)'] = display_activities['duration']
            display_activities['消耗卡路里'] = display_activities['calories']
            display_activities['距离(km)'] = display_activities['distance'].fillna(0)

            # 显示表格
            st.dataframe(
                display_activities[['开始时间', '活动类型', '时长(分钟)', '消耗卡路里', '距离(km)']],
                use_container_width=True
            )
    else:
        st.info("暂无活动数据")

def show_health_data(api_client: KFitAPIClient):
    """显示健康数据页面"""
    st.title("健康数据 📊")

    # 数据筛选
    col1, col2, col3 = st.columns(3)
    with col1:
        data_type = st.selectbox("数据类型", ["健身数据", "营养数据", "活动数据"])
    with col2:
        start_date = st.date_input("开始日期", datetime.now() - timedelta(days=30))
    with col3:
        end_date = st.date_input("结束日期", datetime.now())

    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    # 获取数据
    with st.spinner("加载数据中..."):
        if data_type == "健身数据":
            data = api_client.get_fitness_data(start_date_str, end_date_str)
            if not data.empty:
                # 数据表格
                st.markdown("### 详细数据")
                st.dataframe(data, use_container_width=True)

                # 数据统计
                st.markdown("### 数据统计")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("总步数", f"{data['steps'].sum():,}")
                with col2:
                    st.metric("总卡路里", f"{data['calories'].sum():,}")
                with col3:
                    st.metric("平均步数", f"{data['steps'].mean():.0f}")
                with col4:
                    st.metric("平均卡路里", f"{data['calories'].mean():.0f}")
            else:
                st.info("暂无健身数据")

        elif data_type == "营养数据":
            data = api_client.get_nutrition_data(start_date_str, end_date_str)
            if not data.empty:
                st.markdown("### 详细数据")
                st.dataframe(data, use_container_width=True)

                st.markdown("### 数据统计")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("总卡路里", f"{data['total_calories'].sum():,}")
                with col2:
                    st.metric("平均每日卡路里", f"{data['total_calories'].mean():.0f}")
                with col3:
                    st.metric("平均蛋白质", f"{data['total_protein'].mean():.1f}g")
                with col4:
                    st.metric("平均碳水化合物", f"{data['total_carbs'].mean():.1f}g")
            else:
                st.info("暂无营养数据")

        elif data_type == "活动数据":
            data = api_client.get_recent_activities(limit=100)
            if not data.empty:
                # 按日期筛选
                data['date'] = pd.to_datetime(data['start_time']).dt.date
                mask = (data['date'] >= start_date) & (data['date'] <= end_date)
                filtered_data = data[mask]

                st.markdown("### 详细数据")
                st.dataframe(filtered_data, use_container_width=True)

                st.markdown("### 活动统计")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("活动次数", len(filtered_data))
                with col2:
                    st.metric("总时长", f"{filtered_data['duration'].sum():.0f}分钟")
                with col3:
                    st.metric("总卡路里", f"{filtered_data['calories'].sum():,}")
                with col4:
                    if 'distance' in filtered_data.columns:
                        st.metric("总距离", f"{filtered_data['distance'].sum():.1f}km")
            else:
                st.info("暂无活动数据")

def show_analysis_reports(api_client: KFitAPIClient):
    """显示分析报告页面"""
    st.title("健康分析报告 📝")

    # 报告类型选择
    report_type = st.radio("报告类型", ["每日报告", "周报告", "自定义分析"])

    if report_type == "每日报告":
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("选择日期", datetime.now())
        with col2:
            model_type = st.selectbox("模型选择", ["openai", "claude"], format_func=lambda x: "OpenAI" if x == "openai" else "Claude")

        date_str = date.strftime("%Y-%m-%d")

        # 检查是否已有报告
        reports = api_client.get_reports(date=date_str)
        if reports:
            st.success(f"找到 {len(reports)} 份报告")
            for report in reports:
                with st.expander(f"📄 {report['filename']}"):
                    content = api_client.get_report_content(report['filename'])
                    st.markdown(content.get('content', ''))
        else:
            st.info("该日期暂无报告")

        # 生成新报告
        if st.button("生成分析报告"):
            with st.spinner("正在分析健康数据..."):
                result = api_client.analyze_health(date_str, model_type, "daily")

                if result:
                    st.success("分析完成！")
                    st.markdown("### 分析结果")
                    st.markdown(f"**总体健康状况:**\n{result.get('summary', '')}")

                    if result.get('food_analysis'):
                        st.markdown(f"**饮食分析:**\n{result.get('food_analysis')}")

                    if result.get('fitness_analysis'):
                        st.markdown(f"**健身分析:**\n{result.get('fitness_analysis')}")

                    if result.get('recommendations'):
                        st.markdown(f"**改进建议:**\n{result.get('recommendations')}")
                else:
                    st.error("分析失败，请检查API服务是否正常")

    elif report_type == "周报告":
        col1, col2 = st.columns(2)
        with col1:
            end_date = st.date_input("选择结束日期", datetime.now())
        with col2:
            model_type = st.selectbox("模型选择", ["openai", "claude"], format_func=lambda x: "OpenAI" if x == "openai" else "Claude", key="weekly_model")

        end_date_str = end_date.strftime("%Y-%m-%d")

        # 检查是否已有报告
        reports = api_client.get_reports()
        weekly_reports = [r for r in reports if "weekly" in r.get('filename', '')]
        if weekly_reports:
            st.success(f"找到 {len(weekly_reports)} 份周报告")
            for report in weekly_reports:
                with st.expander(f"📄 {report['filename']}"):
                    content = api_client.get_report_content(report['filename'])
                    st.markdown(content.get('content', ''))
        else:
            st.info("暂无周报告")

        # 生成新报告
        if st.button("生成周度分析报告"):
            with st.spinner("正在分析健康数据..."):
                result = api_client.analyze_health(end_date_str, model_type, "weekly")

                if result:
                    st.success("分析完成！")
                    st.markdown("### 周度分析结果")
                    st.markdown(f"**总体健康状况:**\n{result.get('summary', '')}")

                    if result.get('food_analysis'):
                        st.markdown(f"**饮食分析:**\n{result.get('food_analysis')}")

                    if result.get('fitness_analysis'):
                        st.markdown(f"**健身分析:**\n{result.get('fitness_analysis')}")

                    if result.get('recommendations'):
                        st.markdown(f"**改进建议:**\n{result.get('recommendations')}")
                else:
                    st.error("分析失败，请检查API服务是否正常")

    elif report_type == "自定义分析":
        st.info("此功能正在开发中...")

def show_config_management(api_client: KFitAPIClient):
    """显示配置管理页面"""
    st.title("配置管理 ⚙️")

    try:
        # 获取当前配置
        config = api_client._get("/api/config")
        if not config:
            st.error("无法获取配置信息")
            return

        # 创建表单
        with st.form("config_form", clear_on_submit=False):
            st.markdown("### 大模型配置")

            # 模型选择
            model_type = st.selectbox(
                "默认模型",
                ["openai", "claude"],
                index=["openai", "claude"].index(config.get("model", {}).get("default", "openai"))
            )

            # OpenAI配置
            st.markdown("#### OpenAI 配置")
            openai_api_key = st.text_input(
                "API密钥",
                value=config.get("model", {}).get("openai", {}).get("api_key", ""),
                type="password"
            )
            openai_model = st.selectbox(
                "模型",
                ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
                index=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"].index(
                    config.get("model", {}).get("openai", {}).get("model", "gpt-3.5-turbo")
                )
            )

            # Claude配置
            st.markdown("#### Claude 配置")
            claude_api_key = st.text_input(
                "API密钥",
                value=config.get("model", {}).get("claude", {}).get("api_key", ""),
                type="password"
            )
            claude_model = st.selectbox(
                "模型",
                ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
                index=["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"].index(
                    config.get("model", {}).get("claude", {}).get("model", "claude-3-opus-20240229")
                )
            )

            # Garmin配置
            st.markdown("### Garmin 配置")
            garmin_email = st.text_input(
                "邮箱",
                value=config.get("garmin", {}).get("email", "")
            )
            garmin_password = st.text_input(
                "密码",
                value=config.get("garmin", {}).get("password", ""),
                type="password"
            )

            # Notion配置
            st.markdown("### Notion 配置")
            notion_api_key = st.text_input(
                "API密钥",
                value=config.get("notion", {}).get("api_key", ""),
                type="password"
            )
            notion_page_id = st.text_input(
                "页面ID",
                value=config.get("notion", {}).get("page_id", "")
            )

            # 日记配置
            st.markdown("### 日记配置")
            diary_file_path = st.text_input(
                "日记文件路径",
                value=config.get("diary", {}).get("file_path", "")
            )

            # 分析配置
            st.markdown("### 分析配置")
            output_dir = st.text_input(
                "输出目录",
                value=config.get("analysis", {}).get("output_dir", "./output")
            )
            daily_report = st.checkbox(
                "生成每日报告",
                value=config.get("analysis", {}).get("daily_report", True)
            )
            weekly_report = st.checkbox(
                "生成周报",
                value=config.get("analysis", {}).get("weekly_report", True)
            )

            # 提交按钮
            submitted = st.form_submit_button("保存配置")

            if submitted:
                # 构建配置数据
                new_config = {
                    "model": {
                        "default": model_type,
                        "openai": {
                            "api_key": openai_api_key,
                            "model": openai_model
                        },
                        "claude": {
                            "api_key": claude_api_key,
                            "model": claude_model
                        }
                    },
                    "garmin": {
                        "email": garmin_email,
                        "password": garmin_password
                    },
                    "notion": {
                        "api_key": notion_api_key,
                        "page_id": notion_page_id
                    },
                    "diary": {
                        "file_path": diary_file_path
                    },
                    "analysis": {
                        "output_dir": output_dir,
                        "daily_report": daily_report,
                        "weekly_report": weekly_report
                    }
                }

                # 保存配置
                result = api_client._post("/api/config", data=new_config)
                if result.get("status") == "success":
                    st.success("配置保存成功！")
                else:
                    st.error(f"保存配置失败: {result.get('message', '未知错误')}")

    except Exception as e:
        st.error(f"配置管理出错: {e}")

def show_data_import(api_client: KFitAPIClient):
    """显示数据导入页面"""
    st.title("数据导入 📤")

    st.info("此功能正在开发中...")

    # 导入类型选择
    import_type = st.selectbox("导入类型", ["日记文件", "Garmin数据", "Notion数据"])

    if import_type == "日记文件":
        uploaded_file = st.file_uploader("选择日记文件", type=["txt", "md", "pdf"])
        if uploaded_file is not None:
            st.write(f"已选择文件: {uploaded_file.name}")
            # 这里可以添加文件处理逻辑
            st.info("文件处理功能正在开发中...")

    elif import_type == "Garmin数据":
        st.info("Garmin数据通过API自动同步")

    elif import_type == "Notion数据":
        st.info("Notion数据通过API自动同步")

def main():
    """主函数"""
    # 加载CSS样式
    load_css()

    # 初始化API客户端
    api_client = KFitAPIClient()

    # 健康检查
    try:
        health = api_client.health_check()
        if health.get("status") == "healthy":
            st.sidebar.success("✅ API服务正常")
        else:
            st.sidebar.warning("⚠️ API服务异常")
    except:
        st.sidebar.error("❌ API服务未连接")

    # 侧边栏导航
    st.sidebar.title("KFit 健康分析")
    st.sidebar.markdown("---")

    # 版本信息
    st.sidebar.markdown(f"**版本**: 1.0.0")
    st.sidebar.markdown(f"**日期**: {datetime.now().strftime('%Y-%m-%d')}")

    st.sidebar.markdown("---")

    # 导航菜单
    page = st.sidebar.radio(
        "导航",
        ["仪表盘", "健康数据", "分析报告", "配置管理", "导入数据"],
        index=0
    )

    st.sidebar.markdown("---")

    # 帮助信息
    with st.sidebar.expander("帮助信息"):
        st.markdown("""
        **KFit 使用指南**

        1. **配置API密钥**: 在"配置管理"页面设置你的API密钥和账号信息
        2. **查看仪表盘**: 主仪表盘展示健康数据概览
        3. **查看详细数据**: 在"健康数据"页面查看详细数据
        4. **生成分析报告**: 在"分析报告"页面生成健康分析报告
        5. **导入数据**: 在"导入数据"页面上传本地数据文件

        **联系方式**
        - 邮箱: support@kfit.com
        - GitHub: https://github.com/yourusername/kfit-frontend
        """)

    # 页面路由
    if page == "仪表盘":
        show_dashboard(api_client)
    elif page == "健康数据":
        show_health_data(api_client)
    elif page == "分析报告":
        show_analysis_reports(api_client)
    elif page == "配置管理":
        show_config_management(api_client)
    elif page == "导入数据":
        show_data_import(api_client)

    # 页脚
    st.markdown("---")
    st.markdown(f"© {datetime.now().year} KFit 健康分析系统 | 基于Streamlit和FastAPI构建")

if __name__ == "__main__":
    main()
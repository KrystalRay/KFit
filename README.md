# KFit - 个人健康分析系统 | Personal Health Analysis System(Health Analysis for Garmin Users with LLMs)

> **注意：此项目仍在积极开发中，部分功能可能尚未完全实现或可能发生变更。**
>
> **Note: This project is still under active development. Some features may not be fully implemented or may change.**

这个项目旨在创建一个综合性的健康分析系统，通过整合多个数据源（Notion日记中的饮食信息和Garmin的健身数据）并利用大模型API进行智能分析，为用户提供每日健康状况的深入洞察。

This project aims to create a comprehensive health analysis system that integrates multiple data sources (dietary information from Notion diaries and fitness data from Garmin) and uses LLMs for intelligent analysis.

## 项目结构 | Project Structure
Fit/
├── config/                  # 配置文件目录 | Configuration directory
│   ├── config.py           # 配置加载模块 | Configuration loading module
│   └── config.yaml         # 配置文件 | Configuration file
├── modules/                 # 核心功能模块 | Core functional modules
│   ├── notion/             # Notion API交互模块 | Notion API interaction module
│   │   ├── init .py
│   │   └── notion_client.py # Notion客户端 | Notion client
│   ├── garmin/             # Garmin数据获取模块 | Garmin data retrieval module
│   │   ├── init .py
│   │   └── garmin_client.py # Garmin客户端 | Garmin client
│   ├── diary/              # 日记文件处理模块 | Diary file processing module
│   │   ├── init .py
│   │   ├── diary_parser.py # 日记解析器 | Diary parser
│   │   └── diary_weekly_analyzer.py # 周分析器 | Weekly analyzer
│   └── analysis/           # 数据分析模块 | Data analysis module
│       ├── init .py
│       └── analyzer.py     # 健康数据分析器 | Health data analyzer
├── models/                  # 大模型接口层 | LLM interface layer
│   ├── init .py
│   ├── base_model.py       # 模型基类 | Model base class
│   ├── openai_model.py     # OpenAI模型实现 | OpenAI model implementation
│   ├── claude_model.py     # Claude模型实现 | Claude model implementation
│   └── local_model.py      # 本地模型实现 | Local model implementation
├── utils/                   # 工具函数 | Utility functions
│   ├── init .py
│   └── helpers.py          # 辅助函数 | Helper functions
├── cache/                   # 缓存目录 | Cache directory
├── output/                  # 输出报告目录 | Output reports directory
├── main.py                  # 主程序入口 | Main program entry
├── UnitTest.py              # 单元测试 | Unit tests
├── test_garmin_openai_integration.py # Garmin和OpenAI集成测试 | Integration test
├── requirements.txt         # 项目依赖 | Project dependencies
└── README.md               # 项目说明 | Project documentation
## 功能模块 | Functional Modules

1. **Notion模块 | Notion Module**：负责从Notion API获取用户的日记内容，并提取其中的饮食信息。
   _Responsible for retrieving diary content from the Notion API and extracting dietary information._

2. **Garmin模块 | Garmin Module**：使用python-garminconnect库获取用户的健身数据，包括活动、步数、心率等信息。
   _Uses the python-garminconnect library to obtain user fitness data, including activities, steps, heart rate, and more._

3. **日记文件模块 | Diary File Module**：直接读取和解析本地日记文件，提取特定日期的饮食信息。
   _Directly reads and parses local diary files to extract dietary information for specific dates._

4. **分析模块 | Analysis Module**：整合来自Notion、Garmin或日记文件的数据，并调用大模型API进行综合分析。
   _Integrates data from Notion, Garmin, or diary files and calls large language model APIs for comprehensive analysis._

5. **大模型接口层 | LLM Interface Layer**：提供统一的接口来支持多种大模型（如OpenAI、Claude、本地模型等）。
   _Provides a unified interface to support various large language models (such as OpenAI, Claude, local models, etc.)._

## 当前开发状态 | Current Development Status

- ✅ 基础项目结构搭建 | Basic project structure setup
- ✅ Garmin Connect数据获取 | Garmin Connect data retrieval
- ✅ 本地日记文件解析 | Local diary file parsing
- ✅ OpenAI模型接口 | OpenAI model interface
- ✅ Claude模型接口 | Claude model interface
- ⚠️ 本地模型接口（部分实现） | Local model interface (partially implemented)
- ⚠️ 健康数据分析器（开发中） | Health data analyzer (in development)
- ⚠️ 周报告生成（开发中） | Weekly report generation (in development)
- ⚠️ Notion API客户端实现 （开发中）| Notion API client implementation
- ❌ 用户界面（计划中） | User interface (planned)

## 使用方法 | Usage Instructions

1. 安装依赖 | Install dependencies：`pip install -r requirements.txt`
2. 配置`config/config.yaml`文件，填入必要的API密钥和配置信息 | Configure the `config/config.yaml` file with necessary API keys and settings
3. 运行主程序 | Run the main program：
   - 使用Notion和Garmin数据分析 | Using Notion and Garmin data analysis：`python main.py`
   - 使用日记文件分析 | Using diary file analysis：`python main.py --diary`
   - 指定分析日期 | Specify analysis date：`python main.py --date 2023-01-01`
   - 生成周报告 | Generate weekly report：`python main.py --weekly`

## 配置说明 | Configuration Guide

在`config/config.yaml`中，你需要配置以下信息 | In `config/config.yaml`, you need to configure the following information：

- Notion API密钥和数据库ID | Notion API key and database ID
- Garmin账号信息 | Garmin account information
- 选择使用的大模型及其API密钥 | Choose which large language model to use and its API key
- 其他自定义配置 | Other custom configurations

## 依赖项 | Dependencies

- Python 3.8+
- notion-client
- python-garminconnect
- 各大模型的Python SDK（如openai、anthropic等） | Python SDKs for various models (such as openai, anthropic, etc.)
- PyYAML
- 其他依赖见requirements.txt | See requirements.txt for other dependencies

## 测试 | Testing

项目包含单元测试和集成测试，可以通过以下命令运行 | The project includes unit tests and integration tests that can be run with the following commands：

```bash
# 运行单元测试 | Run unit tests
python UnitTest.py

# 运行Garmin和OpenAI集成测试 | Run Garmin and OpenAI integration test
python test_garmin_openai_integration.py
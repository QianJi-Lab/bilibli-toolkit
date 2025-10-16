# Bilibili 工具包

> 在此感谢所有 b 站开发者前辈们, 还有基于各种库研发并开源自己的 b 站工具的前辈们, 没有大家提供的 API 以及思路, 无法完成我的工具开发🫡

## ✨ 核心功能

1. 📝 **缓存视频整理->列表**: 遍历 Bilibili 缓存目录，提取视频信息, 生成 `.md` 格式 list
    - 📊 **数据聚合**: 按合集自动聚合视频，统计集数和总时长  

2. 🤖 **缓存视频分类**: 使用智谱AI大语言模型(欢迎提PR帮助我提供其他LLM接口🫡)对视频标题进行分类  

3. 🎬 **b站缓存格式2MP4转换**: 将 B站缓存(.m4s)转换为标准 MP4 格式  

4. 📥 **"稍后再看"批量自动下载(MP4格式)**: 一键下载"稍后再看"列表中的所有视频, 结果为 MP4 格式

## 🚀 快速开始

### 前置要求

- Python 3.8+
- FFmpeg (用于视频转换功能)
- yt-dlp (用于视频下载功能)

### 安装步骤
> 默认基于 uv 进行环境管理, 其他环境管理工具类似思路即可

```powershell
# 1. 克隆或下载项目

# 2. 创建并激活虚拟环境
uv venv
# 假设环境为 Windows(其他平台激活环境脚本在类似位置)
.\.venv\Scripts\Activate.ps1

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
# bilibliToolkit\src\utils\.env.example 改名为 .env 即可 
```

### 基础使用

```powershell
# 1. 扫描视频缓存
python scripts/scan.py

# 2. 智能分类
# 会受到 token 上限影响, 我这边实测是大概可以给七百个视频进行分类
python scripts/categorize.py

# 3. 转换视频格式 (可选)
# 这里加入了检测机制, 合并过的视频不会重复合并
# 对1421个视频进行了测试, 包含了标题特殊, 子标题特殊, 不包含子标题等情况
# 如果遇到无法处理情况欢迎提issue, 或者帮助一起提PR解决
python scripts/convert.py

# 4. 下载稍后再看 (可选)
python scripts/download_watchlater.py
```

## 📁 项目结构

```
bilibliToolkit/
├── src/                        # 源代码目录
│   ├── core/                   # 核心功能模块
│   │   ├── scanner.py          # 视频扫描
│   │   ├── categorizer.py      # 智能分类
│   │   └── converter.py        # 视频转换
│   ├── downloaders/            # 下载器模块
│   │   └── watchlater.py       # 稍后再看下载器
│   └── utils/                  # 工具模块
│       └── config.py           # 配置管理
├── scripts/                    # 可执行脚本
│   ├── scan.py                 # 扫描入口
│   ├── categorize.py           # 分类入口
│   ├── convert.py              # 转换入口
│   └── download_watchlater.py  # 下载入口
└── README.md                   # 项目说明
```


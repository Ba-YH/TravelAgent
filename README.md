# 🌏 智能旅游规划系统

![Python](https://img.shields.io/badge/Python-3.9%2B-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-ff4b4b) ![DeepSeek](https://img.shields.io/badge/AI-DeepSeek_V3-success)

## 📖 项目简介

本项目是一个基于大语言模型（LLM）的智能旅游攻略生成系统。旨在解决传统旅游规划中信息碎片化、路线规划繁琐的问题。用户只需输入模糊的自然语言需求，系统即可自动通过多阶段推理，生成包含**每日详细行程**、**可视化轨迹地图**、**智能后勤清单**及**可下载 PDF 路书**的完整方案。

## ✨ 项目亮点

1.  **🧠 深度意图理解**：
    * 利用 LLM 分析用户画像（如“特种兵”、“带父母”），自动设定旅行主题，而非简单的关键词匹配。
2.  **🗺️ 交互式轨迹地图**：
    * 利用 LLM 输出结构化 JSON 数据（经纬度），结合 `Folium` 在地图上绘制每日游玩轨迹与连线，直观展示行程合理性。
3.  **📝 专业级 PDF 导出**：
    * 内置二进制流处理引擎，支持中文字体渲染，一键导出排版工整的 `.pdf` 电子路书，方便离线使用。
4.  **🧳 上下文感知后勤**：
    * 具备逻辑判断能力，根据目的地自动识别“境内/境外”，动态切换推荐的高频 APP 及证件提醒。
5.  **⚙️ 模块化工程架构**：
    * 采用 MVC 分层设计，将前端界面、业务逻辑、资源文件解耦，代码结构清晰，易于维护。

---

## 📂 目录结构

```text
TravelAgent/
├── assets/                 # [资源目录]
│   └── font.ttf            # ⚠️ 必须包含的中文字体文件 (用于PDF生成)
├── utils/                  # [核心逻辑包]
│   ├── __init__.py         # 包标识文件
│   ├── chains.py           # LLM 交互链 (意图分析/骨架规划/详情生成)
│   └── pdf_gen.py          # PDF 生成引擎
├── config.py               # [配置文件] API Key 与模型配置
├── main.py                 # [入口文件] Streamlit 前端交互界面
├── requirements.txt        # [依赖文件] 项目依赖库列表
└── README.md               # 项目说明文档
```

---

## 🚀 快速开始 (使用说明)

### 1. 环境准备 

本项目基于 Python 开发，建议使用 Anaconda 或 Python 虚拟环境运行。

#### 第一步：下载项目
将项目文件下载到本地，并进入项目目录：
```bash
cd TravelAgent
```

#### 第二步：创建虚拟环境 (推荐)
为了避免依赖冲突，建议创建独立的虚拟环境。

* **使用 Conda (推荐):**
    ```bash
    conda create -n travel_ai python=3.10
    conda activate travel_ai
    ```
* **或者使用 venv:**
    ```bash
    python -m venv venv
    # Windows 激活:
    .\venv\Scripts\activate
    # Mac/Linux 激活:
    source venv/bin/activate
    ```

#### 第三步：安装依赖库
```bash
pip install -r requirements.txt
```

#### ⚠️ 第四步：配置字体文件 (关键！)
由于 `fpdf` 库默认不支持中文，**您必须手动添加一个中文字体文件**，否则导出的 PDF 将全是乱码。

1.  找到一个 `.ttf` 格式的中文字体（如微软雅黑、黑体、思源黑体）。
    * *注意：不支持 `.ttc` 格式，必须是 `.ttf`。*
2.  将文件重命名为 **`font.ttf`**。
3.  将文件放入 **`assets/`** 文件夹中。
    * 正确路径应为：`TravelAgent/assets/font.ttf`

---

### 2. 配置 API Key

打开根目录下的 `config.py` 文件，填入您的 DeepSeek API Key：

```python
# config.py

# 在此处填入您的 API Key
API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" 

# 模型配置 (默认无需修改)
BASE_URL = "[https://api.deepseek.com](https://api.deepseek.com)"
MODEL_NAME = "deepseek-chat"
```

> 💡 **提示**：如果没有 API Key，请前往 [DeepSeek 开放平台](https://platform.deepseek.com/) 申请。

---

### 3. 运行项目

在终端中确保处于虚拟环境内，执行以下命令启动系统：

```bash
streamlit run main.py
```

启动成功后，终端会显示访问地址（通常为 `http://localhost:8501`），浏览器会自动打开该页面。

---

## 🛠️ 常见问题 (Troubleshooting)

**Q1: PDF 导出的中文全是乱码？**
* **A:** 请检查 `assets/` 目录下是否存在 `font.ttf` 文件，且该文件必须是真实有效的中文 `.ttf` 字体。

**Q2: 地图无法显示或报错？**
* **A:** 这通常是因为网络问题导致无法连接 OpenStreetMap 服务器，或者模型偶尔生成的经纬度格式有误。系统已内置容错机制，若地图加载失败，不影响文字攻略的显示。

**Q3: 生成速度较慢？**
* **A:** 这是一个多步推理系统（Chain of Thought），需要连续调用多次大模型 API。生成一份 3-5 天的完整攻略通常需要 30-60 秒，请耐心等待进度条走完。

---

## 📜 许可证

本项目仅供课程学习与交流使用。
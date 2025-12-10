# 🌏 智能旅行规划师

## 项目简介
这是一个基于 DeepSeek LLM 的智能旅游攻略生成系统。采用 Python Streamlit 开发，具备多模态意图识别、地图轨迹绘制及 PDF 报告导出功能。

## 核心功能
1.  **AI 意图分析**：自动解析模糊需求。
2.  **可视化地图**：使用 Folium 绘制每日游玩轨迹。
3.  **智能后勤逻辑**：根据境内/境外自动切换 APP 推荐策略。
4.  **PDF 导出**：支持生成排版精美的中文路书。

## 项目结构
- `main.py`: 前端交互入口
- `utils/`: 核心业务逻辑 (AI Chains & PDF Engine)
- `assets/`: 静态资源文件

## 如何运行
1. 安装依赖: `pip install -r requirements.txt`
2. 配置 API: 修改 `config.py`
3. 启动: `streamlit run main.py`
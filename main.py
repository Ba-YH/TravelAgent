import datetime
import os
import streamlit as st
import folium
from streamlit_folium import st_folium

# 假设这些模块/函数存在且功能正常
from utils import chains
from utils.pdf_gen import create_pdf

# --- 常量与配置 ---
APP_TITLE = "🌏 智能旅行规划师"
PAGE_ICON = "🌏"
LAYOUT = "wide"
MAP_ZOOM_START = 11
DAY_COLORS = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'cadetblue']

st.set_page_config(page_title="智能旅行规划师", layout=LAYOUT, page_icon=PAGE_ICON)

# --- 会话状态初始化 ---
if "travel_data" not in st.session_state:
    st.session_state.travel_data = None
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

# --- 自定义 CSS 样式 ---
st.markdown("""
<style>
    .stButton>button {height: 3em; border-radius: 10px; font-weight: bold;}
    .report-view {background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);}
</style>
""", unsafe_allow_html=True)

st.title(APP_TITLE)
st.caption("上下文感知推理 | 透明式思维链 | 多点地图轨迹 ")

# --- 侧边栏：用户输入 ---
with st.sidebar:
    st.header("1. 填写需求")

    destination = st.text_input("📍 目的地", "北京")
    num_days = st.slider("📅 游玩天数", 1, 10, 3)
    start_date = st.date_input("出发日期", datetime.date.today())

    st.header("2. 个性化")
    companion_type = st.selectbox("同行人", ["独自一人", "情侣", "带父母", "带孩子", "朋友结伴"])
    travel_budget = st.select_slider("预算", options=["穷游", "经济", "舒适", "豪华"])
    user_interests = st.multiselect(
        "偏好",
        ["历史人文", "自然风光", "地道美食", "网红打卡", "博物馆"],
        default=["历史人文"]
    )

    st.divider()

    # 切换生成状态
    if st.button("🚀 生成详细攻略", type="primary"):
        st.session_state.is_generating = True
    else:
        st.session_state.is_generating = False


# --- 核心逻辑执行 ---
if st.session_state.is_generating:
    # 清空旧数据并初始化存储字典
    st.session_state.travel_data = {}

    input_params = {
        "dest": destination,
        "dates": str(start_date),
        "people": companion_type,
        "budget": travel_budget,
        "interests": user_interests
    }

    try:
        # 1. 意图分析与摘要生成
        with st.status("🔍 正在分析目的地环境...", expanded=True) as status:
            travel_summary = chains.step_analyze_intent(input_params)
            st.session_state.travel_data['summary'] = travel_summary
            st.write(f"定位：{travel_summary}")

            # 2. 骨架规划（含坐标）
            st.write("🗺️ 正在检索景点坐标并规划路线...")
            travel_skeleton = chains.step_create_skeleton(travel_summary, num_days, destination)
            st.session_state.travel_data['skeleton'] = travel_skeleton

            status.update(label="✅ 路线骨架生成完毕", state="complete", expanded=False)

        # 3. 每日详细内容生成（带进度条）
        progress_bar = st.progress(0)
        full_markdown_report = ""
        travel_skeleton = st.session_state.travel_data['skeleton'] # 获取更新后的骨架

        status_text = st.empty()

        # 遍历每一天以生成详细内容
        for idx, day_plan in enumerate(travel_skeleton):
            day_num = day_plan['day']
            day_title = day_plan['title']

            status_text.text(f"正在撰写 Day {day_num}: {day_title}...")

            # 生成内容详情，传入用户上下文
            user_context = f"{companion_type}, {travel_budget}"
            day_content = chains.step_detail_day(day_plan, user_context)

            travel_skeleton[idx]['content'] = day_content # 存储生成的内容
            full_markdown_report += f"# Day {day_num}：{day_title}\n{day_content}\n\n"

            progress_bar.progress((idx + 1) / len(travel_skeleton))

        st.session_state.travel_data['skeleton'] = travel_skeleton
        st.session_state.travel_data['full_markdown_report'] = full_markdown_report
        status_text.empty()

        # 4. 后勤生成
        with st.spinner("🧳 正在根据目的地生成专属行前清单..."):
            logistics_content = chains.step_logistics(destination, full_markdown_report)
            st.session_state.travel_data['logistics'] = logistics_content

    except Exception as e:
        st.error(f"生成过程中出现错误: {e}")
        st.stop()

    # 重新运行以从生成状态切换到显示状态
    st.rerun()

# --- 结果显示界面 ---
if st.session_state.travel_data:
    data = st.session_state.travel_data
    travel_skeleton = data['skeleton']

    # 顶层概览
    st.info(f"🎯 **旅行基调**：{data['summary']}")

    # 使用标签页布局
    tab_map_detail, tab_logistics, tab_export = st.tabs(["🗺️ 行程地图 & 详情", "🎒 行前准备 & 贴士", "📥 导出报告"])

    with tab_map_detail:
        # --- 地图绘制 ---
        try:
            # 确定地图中心（第一天的第一个景点）
            first_spot = travel_skeleton[0]['spots'][0]
            start_location = [first_spot['lat'], first_spot['lon']]
            map_instance = folium.Map(location=start_location, zoom_start=MAP_ZOOM_START)

            # 绘制每一天的轨迹和标记
            for i, day_plan in enumerate(travel_skeleton):
                day_color = DAY_COLORS[i % len(DAY_COLORS)]
                day_coordinates = []

                # 绘制当天的景点
                for spot in day_plan['spots']:
                    location = [spot['lat'], spot['lon']]
                    day_coordinates.append(location)

                    # 创建自定义弹窗，增加宽度以适应中文字符
                    popup_content = f"第{day_plan['day']}天: {spot['name']}"
                    custom_popup = folium.Popup(popup_content, max_width=300)

                    folium.Marker(
                        location,
                        popup=custom_popup,
                        icon=folium.Icon(color=day_color, icon="info-sign"),
                        tooltip=popup_content # 悬停提示以快速查看信息
                    ).add_to(map_instance)

                # 绘制当天的路线
                if len(day_coordinates) > 1:
                    folium.PolyLine(
                        day_coordinates,
                        color=day_color,
                        weight=3,
                        opacity=0.8,
                        tooltip=f"Day {day_plan['day']} 路线"
                    ).add_to(map_instance)

            # 在 Streamlit 中显示地图
            st_folium(map_instance, width="100%", height=400)

        except Exception as e:
            # 处理地图数据可能缺失或损坏的情况
            st.warning(f"地图数据解析不完整，可能缺少经纬度信息。仅展示文字攻略。错误详情: {e}")

        st.divider()

        # --- 每日文字详情 ---
        for day_plan in travel_skeleton:
            expander_title = f"📅 Day {day_plan['day']}：{day_plan['title']}"
            with st.expander(expander_title, expanded=True):
                st.markdown(day_plan['content'])

    with tab_logistics:
        st.header("行前准备与智能后勤")
        st.markdown(data['logistics'])

    with tab_export:
        st.success("✅ 您的攻略已准备就绪")

        # 按需生成 PDF 字节流
        if st.button("生成 PDF 文件"):
            pdf_bytes = create_pdf(
                destination,
                data['summary'],
                data['full_markdown_report'],
                data['logistics']
            )

            st.download_button(
                label="⬇️ 点击下载完整攻略 (.pdf)",
                data=pdf_bytes,
                file_name=f"{destination}_旅游攻略.pdf",
                mime="application/pdf"
            )
            st.success("PDF 生成成功，请点击下载按钮。")
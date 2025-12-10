import streamlit as st
import datetime
import chains
import folium
from streamlit_folium import st_folium
from pdf_gen import create_pdf

st.set_page_config(page_title="深度游", layout="wide", page_icon="🌏")

# 初始化 Session State
if "data" not in st.session_state:
    st.session_state.data = None
if "generating" not in st.session_state:
    st.session_state.generating = False

# --- CSS ---
st.markdown("""
<style>
    .stButton>button {height: 3em; border-radius: 10px; font-weight: bold;}
    .report-view {background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);}
</style>
""", unsafe_allow_html=True)

st.title("🌏 智能旅行规划师")
st.caption("Context-Aware Reasoning | Multi-Point Mapping | Domestic/Intl Logic")

# --- 侧边栏：输入 ---
with st.sidebar:
    st.header("1. 填写需求")
    dest = st.text_input("📍 目的地", "北京")
    days = st.slider("📅 游玩天数", 1, 10, 3)
    start_date = st.date_input("出发日期", datetime.date.today())

    st.header("2. 个性化")
    who = st.selectbox("同行人", ["独自一人", "情侣", "带父母", "带孩子", "朋友结伴"])
    budget = st.select_slider("预算", options=["穷游", "经济", "舒适", "豪华"])
    interests = st.multiselect("偏好", ["历史人文", "自然风光", "地道美食", "网红打卡", "博物馆"], default=["历史人文"])

    st.divider()
    if st.button("🚀 生成详细路书", type="primary"):
        st.session_state.generating = True
    else:
        st.session_state.generating = False

# --- 核心逻辑执行 ---
if st.session_state.generating:
    st.session_state.data = {} # 清空旧数据
    inputs = {"dest": dest, "dates": str(start_date), "people": who, "budget": budget, "interests": interests}

    try:
        # 1. 意图分析
        with st.status("🔍 正在分析目的地环境...", expanded=True) as status:
            summary = chains.step_analyze_intent(inputs)
            st.session_state.data['summary'] = summary
            st.write(f"定位：{summary}")

            # 2. 规划具体景点骨架 (含坐标)
            st.write("🗺️ 正在检索景点坐标并规划路线...")
            skeleton = chains.step_create_skeleton(summary, days, dest)
            st.session_state.data['skeleton'] = skeleton

            status.update(label="✅ 路线骨架生成完毕", state="complete", expanded=False)

        # 3. 撰写每日详情 (带进度条)
        progress_bar = st.progress(0)
        full_md = ""
        skeleton = st.session_state.data['skeleton']

        status_text = st.empty()
        for i, day in enumerate(skeleton):
            status_text.text(f"正在撰写 Day {day['day']}: {day['title']}...")
            # 传入用户画像
            content = chains.step_detail_day(day, f"{who}, {budget}")
            skeleton[i]['content'] = content # 存入结构中
            full_md += f"# Day {day['day']}：{day['title']}\n{content}\n\n"
            progress_bar.progress((i + 1) / len(skeleton))

        st.session_state.data['skeleton'] = skeleton
        st.session_state.data['full_md'] = full_md
        status_text.empty()

        # 4. 生成行前准备 (智能判断境内外)
        with st.spinner("🧳 正在根据目的地生成专属行前清单..."):
            logistics = chains.step_logistics(dest, full_md)
            st.session_state.data['logistics'] = logistics

    except Exception as e:
        st.error(f"生成过程中出现错误: {e}")
        st.stop()

    st.rerun() # 强制刷新显示结果

# --- 结果展示界面 ---
if st.session_state.data:
    data = st.session_state.data

    # 顶部概览
    st.info(f"🎯 **旅行基调**：{data['summary']}")

    # 使用 Tabs 布局
    tab1, tab2, tab3 = st.tabs(["🗺️ 行程地图 & 详情", "🎒 行前准备 & 贴士", "📥 导出报告"])

    with tab1:
        # --- A. 地图绘制 (支持多点轨迹) ---
        skeleton = data['skeleton']
        try:
            # 寻找地图中心点 (取第一天的第一个景点)
            start_loc = [skeleton[0]['spots'][0]['lat'], skeleton[0]['spots'][0]['lon']]
            m = folium.Map(location=start_loc, zoom_start=11)

            colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'cadetblue']

            for i, day in enumerate(skeleton):
                day_color = colors[i % len(colors)]
                day_coords = []

                # 绘制该天内的所有景点
                for spot in day['spots']:
                    loc = [spot['lat'], spot['lon']]
                    day_coords.append(loc)
                    folium.Marker(
                        loc,
                        popup=f"Day {day['day']}: {spot['name']}",
                        icon=folium.Icon(color=day_color, icon="info-sign")
                    ).add_to(m)

                # 画出当天的游玩连线
                if len(day_coords) > 1:
                    folium.PolyLine(
                        day_coords,
                        color=day_color,
                        weight=3,
                        opacity=0.8,
                        tooltip=f"Day {day['day']} 路线"
                    ).add_to(m)

            st_folium(m, width=None, height=400)

        except Exception as e:
            st.warning("地图数据解析不完整，仅展示文字攻略。")

        st.divider()

        # --- B. 每日文字详情 ---
        for day in skeleton:
            with st.expander(f"📅 Day {day['day']}：{day['title']}", expanded=True):
                st.markdown(day['content'])

    with tab2:
        st.markdown(data['logistics'])

    with tab3:
        st.success("✅ 您的路书已准备就绪")

        # 生成 PDF
        if st.button("生成 PDF 文件"):
            pdf_bytes = create_pdf(
                dest,
                data['summary'],
                data['full_md'],
                data['logistics']
            )
            st.download_button(
                label="⬇️ 点击下载完整路书 (.pdf)",
                data=pdf_bytes,
                file_name=f"{dest}_Travel_Guide.pdf",
                mime="application/pdf"
            )
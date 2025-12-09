import streamlit as st
import datetime
import chains
import time

st.set_page_config(page_title="全球旅游规划师", layout="wide", page_icon="🌍")

# CSS 美化
st.markdown("""
<style>
    .step-title {font-weight: bold; color: #1E88E5; margin-top: 20px;}
    .success-box {padding: 15px; background-color: #e8f5e9; border-radius: 5px; border-left: 5px solid #4caf50;}
</style>
""", unsafe_allow_html=True)

st.title("🌏全球旅行规划师")
st.caption("Powered by DeepSeek V3 | Multi-Step Reasoning Workflow")

# --- 左侧：详细设置区 ---
with st.sidebar:
    st.header("📝 旅行档案")

    # 1. 基础信息
    dest = st.text_input("目的地", "日本·关西地区")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        start_date = st.date_input("出发日期", datetime.date.today())
    with col_d2:
        days = st.number_input("游玩天数", min_value=1, max_value=15, value=5)

    st.divider()

    # 2. 个性化参数
    st.subheader("🎨 偏好设置")
    who = st.selectbox("同行人员", ["独自一人", "情侣/夫妻", "带娃家庭", "带父母", "特种兵学生党"])
    budget = st.select_slider("预算等级", options=["穷游", "经济", "舒适", "豪华", "不差钱"], value="舒适")
    pace = st.radio("行程节奏", ["特种兵 (早起晚睡)", "适中 (劳逸结合)", "松弛 (睡到自然醒)"], index=1)

    interests = st.multiselect(
        "兴趣标签 (多选)",
        ["地道美食", "历史古迹", "自然风光", "博物馆/艺术", "二次元/动漫", "疯狂购物", "夜生活"],
        default=["地道美食", "历史古迹"]
    )

    st.divider()
    generate_btn = st.button("🚀 启动规划引擎", type="primary", use_container_width=True)

# --- 右侧：生成展示区 ---
if generate_btn:
    # 组装输入数据
    user_inputs = {
        "dest": dest,
        "dates": f"{start_date} 出发，共 {days} 天",
        "people": who,
        "budget": budget,
        "pace": pace,
        "interests": interests
    }

    # === 阶段 1：意图理解 ===
    with st.status("🤔 阶段 1/4：正在分析您的旅行画像...", expanded=True) as status:
        st.write("正在读取用户输入...")
        time.sleep(0.5) # 模拟一点延迟感

        # 调用 Chain
        travel_summary = chains.step_analyze_intent(user_inputs)

        st.markdown(f"**分析结果：** `{travel_summary}`")
        status.update(label="✅ 需求分析完成", state="complete", expanded=False)

    # === 阶段 2：骨架生成 ===
    with st.status("🗺️ 阶段 2/4：正在规划全局路线骨架...", expanded=True) as status:
        st.write("正在根据地理位置和时间分配行程...")

        skeleton = chains.step_create_skeleton(travel_summary, days)

        # 可视化展示骨架
        st.table(skeleton)
        status.update(label="✅ 路线骨架已生成", state="complete", expanded=False)

    # === 阶段 3：细节填充 (最耗时) ===
    full_content = ""
    result_container = st.container() # 占位符，用于最后渲染

    with st.status("✍️ 阶段 3/4：正在撰写每日详细攻略...", expanded=True) as status:
        progress_bar = st.progress(0)

        detailed_md = ""
        for i, day in enumerate(skeleton):
            st.write(f"正在编写第 {day['day']} 天：{day['city']} - {day['theme']}...")

            # 调用 Chain
            day_content = chains.step_detail_day(day, f"{who}, {budget}, {pace}")

            detailed_md += f"## Day {day['day']}：{day['theme']}\n{day_content}\n\n---\n\n"
            progress_bar.progress((i + 1) / days)

        status.update(label="✅ 详细攻略撰写完毕", state="complete", expanded=False)

    # === 阶段 4：后勤汇总 ===
    with st.status("🧳 阶段 4/4：正在生成行前清单与预算...", expanded=True) as status:
        logistics_content = chains.step_logistics(detailed_md)
        status.update(label="✅ 后勤信息已生成", state="complete", expanded=False)

    # === 最终展示 ===
    st.balloons()
    st.markdown("## 📖 您的专属旅行路书")

    tab1, tab2, tab3 = st.tabs(["🗓️ 每日详情", "🎒 行前准备", "🛠️ 调试信息"])

    with tab1:
        st.markdown(detailed_md)

    with tab2:
        st.info(f"旅行基调：{travel_summary}")
        st.markdown(logistics_content)

    with tab3:
        st.json(skeleton)
        st.warning("此页面用于展示结构化数据，供开发调试使用。")

    # 下载按钮
    final_text = f"# {dest} {days}日游深度攻略\n\n> {travel_summary}\n\n{detailed_md}\n\n# 行前准备\n{logistics_content}"
    st.download_button("📥 下载完整攻略 (.md)", final_text, file_name="travel_plan.md")
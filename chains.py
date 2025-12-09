import json
from openai import OpenAI
import streamlit as st
import config

client = OpenAI(api_key=config.API_KEY, base_url=config.BASE_URL)

def call_llm(prompt, system_role="You are a helpful assistant."):
    """封装 LLM 调用，包含流式输出处理（为了简单这里先用非流式，方便 JSON 解析）"""

    # 演示功能：如果开启调试，在界面展示 Prompt
    if config.DEBUG_SHOW_PROMPTS:
        with st.expander(f"🔍 查看发送给 [{system_role[:10]}...] 的 Prompt", expanded=False):
            st.code(prompt, language="markdown")

    response = client.chat.completions.create(
        model=config.MODEL_NAME,
        messages=[
            {"role": "system", "content": system_role},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

# --- 节点 1: 需求分析 ---
def step_analyze_intent(inputs):
    prompt = f"""
    用户提交了复杂的旅游需求，请将其转化为结构化的标签。
    用户输入：
    - 目的地：{inputs['dest']}
    - 往返日期：{inputs['dates']}
    - 人员构成：{inputs['people']}
    - 节奏偏好：{inputs['pace']}
    - 预算等级：{inputs['budget']}
    - 特殊兴趣：{', '.join(inputs['interests'])}
    
    请分析并返回一段简短的「旅行基调」描述（50字以内），例如：“这是一趟针对年轻情侣的京都赏樱之旅，主打高性价比美食，节奏适中。”
    """
    return call_llm(prompt, system_role="你是一位资深旅行需求分析师")

# --- 节点 2: 骨架规划 ---
def step_create_skeleton(summary, days):
    prompt = f"""
    基于旅行基调：“{summary}”
    请规划一个 {days} 天的行程骨架。
    
    必须严格返回 JSON 列表格式，不要包含 Markdown 标记。
    格式示例：
    [
        {{"day": 1, "city": "大阪", "theme": "到达与道顿堀美食", "main_spots": "心斋桥, 道顿堀"}},
        {{"day": 2, "city": "京都", "theme": "古寺巡礼", "main_spots": "清水寺, 二年坂"}}
    ]
    """
    response = call_llm(prompt, system_role="你是一位逻辑严密的行程规划师，只输出 JSON")
    # 简单的清洗逻辑
    cleaned = response.replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned)

# --- 节点 3: 每日详情 (循环节点) ---
def step_detail_day(day_data, specific_reqs):
    prompt = f"""
    请为第 {day_data['day']} 天撰写超详细攻略。
    
    当前信息：
    - 城市：{day_data['city']}
    - 主题：{day_data['theme']}
    - 核心景点：{day_data['main_spots']}
    - 用户偏好：{specific_reqs}
    
    输出要求：
    1. 「上午/下午/晚上」的时间节点安排。
    2. 推荐 1 个具体的午餐地点和 1 个晚餐地点（带菜名）。
    3. 这一天内的交通连接方式。
    4. 避坑指南。
    5. 使用 Markdown 格式，层级清晰。
    """
    return call_llm(prompt, system_role="你是一位本地通导游，熟悉大街小巷")

# --- 节点 4: 后勤与预算 ---
def step_logistics(full_plan):
    prompt = f"""
    基于以上生成的完整行程，生成一份「行前准备清单」。
    包含：
    1. 预估人均总花费（根据之前的预算等级估算）。
    2. 必备物品清单（根据目的地天气和活动）。
    3. 当地常用 APP 推荐。
    4. 签证与网络提示。
    """
    return call_llm(prompt, system_role="你是一位细心的旅行管家")
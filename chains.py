import json
from openai import OpenAI
import config

client = OpenAI(api_key=config.API_KEY, base_url=config.BASE_URL)

def call_llm(prompt, system_role="You are a helpful assistant."):
    """通用 LLM 调用函数"""
    try:
        response = client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"} # 强制 JSON 模式，DeepSeek 支持
        )
        return response.choices[0].message.content
    except Exception as e:
        return str(e)

def call_llm_text(prompt, system_role):
    """用于生成长文本（非 JSON）的调用"""
    response = client.chat.completions.create(
        model=config.MODEL_NAME,
        messages=[{"role": "system", "content": system_role}, {"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

# --- 节点 1: 意图分析 ---
def step_analyze_intent(inputs):
    prompt = f"""
    用户输入：
    - 目的地：{inputs['dest']}
    - 时间：{inputs['dates']}
    - 人员：{inputs['people']}
    - 预算：{inputs['budget']}
    - 偏好：{', '.join(inputs['interests'])}
    
    任务：分析并返回一个 JSON 对象，包含字段 'summary' (一段简短的旅行基调描述，50字以内)。
    """
    res = call_llm(prompt, system_role="资深旅行顾问")
    return json.loads(res)['summary']

# --- 节点 2: 骨架与地图规划 (核心升级) ---
def step_create_skeleton(summary, days, dest):
    prompt = f"""
    目的地：{dest}
    基调：{summary}
    天数：{days}天
    
    任务：规划每天的行程骨架，重点是地理位置。
    要求：
    1. 返回 JSON 格式。
    2. 包含一个列表 'itinerary'。
    3. 每一天包含：'day'(数字), 'title'(标题), 'spots'(景点列表)。
    4. **关键**：'spots' 列表中的每个景点，必须包含 'name'(名称), 'lat'(纬度), 'lon'(经度)。
    5. 经纬度请根据景点实际位置尽可能准确（例如：如果是北京，故宫和颐和园的坐标必须不同）。
    
    JSON 结构示例：
    {{
        "itinerary": [
            {{
                "day": 1,
                "title": "皇城根下",
                "spots": [
                    {{"name": "故宫博物院", "lat": 39.9163, "lon": 116.3971}},
                    {{"name": "景山公园", "lat": 39.9220, "lon": 116.3956}}
                ]
            }}
        ]
    }}
    """
    res = call_llm(prompt, system_role="精通地理信息的规划师")
    return json.loads(res)['itinerary']

# --- 节点 3: 每日详情 ---
def step_detail_day(day_data, user_profile):
    spot_names = ", ".join([s['name'] for s in day_data['spots']])
    prompt = f"""
    为第 {day_data['day']} 天生成详细攻略。
    
    核心景点路线：{spot_names}
    当日主题：{day_data['title']}
    用户画像：{user_profile}
    
    要求：
    1. 输出 Markdown 格式。
    2. 按「上午」「午餐」「下午」「晚餐」「晚上」的时间轴撰写。
    3. 详细描写景点玩法、餐厅推荐（具体店名）。
    4. 给出景点之间的具体交通建议。
    """
    return call_llm_text(prompt, system_role="金牌导游")

# --- 节点 4: 后勤 (智能判断境内外) ---
def step_logistics(dest, full_plan):
    prompt = f"""
    使用者是中国人。目的地是：{dest}。
    基于生成的行程：{full_plan}
    
    请生成「行前准备清单」(Markdown格式)。
    
    **重要逻辑判断**：
    1. 首先判断目的地是在「中国大陆境内」还是「境外/港澳台」。
    2. **如果是境内**：
       - 证件：提醒身份证。
       - APP推荐：高德/百度地图、大众点评、美团、支付宝/微信。**绝对不要**推荐Google Maps。
    3. **如果是境外**：
       - 证件：护照、签证政策提醒。
       - APP推荐：Google Maps, Uber/Grab, 当地特色App。
       
    输出包含：证件/签证、必备衣物、APP推荐、预估花费提示。
    """
    return call_llm_text(prompt, system_role="贴心的旅行管家")
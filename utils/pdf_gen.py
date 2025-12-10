from fpdf import FPDF
import os

# ================= 配置区域 =================
# 确保你的 assets 文件夹里真的有 SimHei.ttf 这个文件
FONT_PATH = os.path.join("assets", "MicrosoftYaHei.ttf")
FONT_NAME = "MicrosoftYaHei"
# ===========================================

class PDF(FPDF):
    def header(self):
        # 只有当已经注册了字体后，才能在 header 里使用中文
        # 为了防止第一页初始化报错，这里加个判断或使用 try-except
        try:
            self.set_font(FONT_NAME, size=10)
            self.cell(0, 10, "AI Travel Agent - 智能行程单", ln=True, align='R')
            self.ln(5)
        except:
            pass # 如果字体还没注册，跳过 header 渲染

    def footer(self):
        self.set_y(-15)
        try:
            self.set_font(FONT_NAME, size=8)
            self.cell(0, 10, f'Page {self.page_no()}', align='C')
        except:
            pass

def create_pdf(destination, travel_summary, daily_plan, logistics):
    """
    生成 PDF 二进制流
    :param destination: 目的地 (str)
    :param travel_summary: 旅行基调 (str)
    :param daily_plan: 每日行程详情 (str/markdown)
    :param logistics: 后勤信息 (str)
    """

    # 1. 检查字体文件是否存在 (非常重要，否则会报错)
    if not os.path.exists(FONT_PATH):
        # 如果找不到字体，返回一个包含错误信息的 PDF 字节流
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        pdf.cell(0, 10, f"Error: Font file not found at {FONT_PATH}", ln=True)
        pdf.cell(0, 10, "Please put 'SimHei.ttf' in the 'assets' folder.", ln=True)
        return pdf.output()

    # 2. 初始化 PDF
    pdf = PDF()

    # [关键] 注册字体：必须在 add_page 之前或写字之前完成
    # fname 是文件路径，family 是后续引用的名字
    pdf.add_font(family=FONT_NAME, fname=FONT_PATH)

    pdf.add_page()

    # [关键] 设置字体：注册完必须 set_font 才能生效
    pdf.set_font(FONT_NAME, size=24)

    # 3. 写入标题
    pdf.cell(0, 20, f"{destination} 专属旅行路书", ln=True, align='C')

    # 4. 写入旅行基调
    pdf.set_font(FONT_NAME, size=14)
    pdf.cell(0, 10, "「旅行基调」", ln=True)
    pdf.set_font(FONT_NAME, size=11)
    pdf.multi_cell(0, 7, travel_summary)
    pdf.ln(5)

    # 5. 写入每日详细行程
    pdf.set_font(FONT_NAME, size=14)
    pdf.cell(0, 10, "「详细行程」", ln=True)
    pdf.set_font(FONT_NAME, size=11)

    # 简单清洗 Markdown 的加粗符号，fpdf2 默认不支持 markdown 语法渲染
    # 如果想完美渲染 Markdown 需要额外库，这里做简单清洗防止难看
    clean_plan = daily_plan.replace("**", "").replace("##", "").replace("###", "")
    pdf.multi_cell(0, 7, clean_plan)
    pdf.ln(5)

    # 6. 写入行前准备
    pdf.set_font(FONT_NAME, size=14)
    pdf.cell(0, 10, "「行前准备与后勤」", ln=True)
    pdf.set_font(FONT_NAME, size=11)
    clean_logistics = logistics.replace("**", "").replace("##", "")
    pdf.multi_cell(0, 7, clean_logistics)

    # 7. 输出
    # fpdf2 的 output() 默认返回 bytes，适合 Streamlit 直接下载
    return pdf.output()
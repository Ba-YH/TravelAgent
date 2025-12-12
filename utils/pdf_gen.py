from fpdf import FPDF
import os

# --- 配置区域 ---
FONT_PATH = os.path.join("assets", "MicrosoftYaHei.ttf")
FONT_NAME = "MicrosoftYaHei"

class PDF(FPDF):
    def header(self):
        try:
            self.set_font(FONT_NAME, size=10)
            self.cell(0, 10, "智能旅游规划", ln=True, align='R')
            self.ln(5)
        except:
            pass

    def footer(self):
        self.set_y(-15)
        try:
            self.set_font(FONT_NAME, size=8)
            self.cell(0, 10, f'{self.page_no()}', align='C')
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

    # 1. 检查字体文件是否存在
    if not os.path.exists(FONT_PATH):
        # 如果找不到字体，返回一个包含错误信息的 PDF 字节流
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        pdf.cell(0, 10, f"错误: 在 {FONT_PATH} 没有找到字体文件", ln=True)
        return pdf.output()

    # 2. 初始化 PDF
    pdf = PDF()

    # [关键] 注册字体：必须在 add_page 之前或写字之前完成
    # fname 是文件路径，family 是后续引用的名字
    # [关键] 设置字体：注册完必须 set_font 才能生效

    pdf.add_font(family=FONT_NAME, fname=FONT_PATH)
    pdf.add_page()
    pdf.set_font(FONT_NAME, size=24)

    # 3. 写入标题
    pdf.cell(0, 20, f"{destination} 专属旅行攻略", ln=True, align='C')

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
    return bytes(pdf.output())
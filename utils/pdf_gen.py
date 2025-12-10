from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        try:
            # 必须要有 font.ttf 才能显示中文
            self.add_font('CustomFont', '', 'font.ttf', uni=True)
            self.set_font('CustomFont', '', 10)
        except:
            pass

def create_pdf(dest, summary, detailed_md, logistics):
    pdf = PDF()
    pdf.add_page()

    font_path = '../assets/font.ttf'
    if os.path.exists(font_path):
        pdf.add_font('CustomFont', '', font_path, uni=True)
        pdf.set_font('CustomFont', '', 12)
    else:
        pdf.set_font("Arial", size=12) # 无字体回退模式

    # 封面区
    pdf.set_font_size(24)
    pdf.cell(0, 20, f"{dest} 专属旅行路书", ln=True, align='C')

    pdf.set_font_size(12)
    pdf.multi_cell(0, 8, f"旅行基调：{summary}")
    pdf.ln(10)

    # 每日详情
    pdf.set_font_size(16)
    pdf.cell(0, 10, "一、详细行程", ln=True)
    pdf.set_font_size(11)
    # 简单清理 Markdown 符号，防止 PDF 排版混乱
    clean_detail = detailed_md.replace("##", "").replace("**", "")
    pdf.multi_cell(0, 7, clean_detail)
    pdf.ln(10)

    # 行前准备
    pdf.set_font_size(16)
    pdf.cell(0, 10, "二、行前准备", ln=True)
    pdf.set_font_size(11)
    clean_logistics = logistics.replace("##", "").replace("**", "")
    pdf.multi_cell(0, 7, clean_logistics)

    return pdf.output(dest="S").encode("latin1")
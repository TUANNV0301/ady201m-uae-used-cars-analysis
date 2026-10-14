"""Create a concise Vietnamese project presentation draft."""
from pathlib import Path
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "ADY201m_Project_Presentation.pptx"
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
NAVY = RGBColor(20, 38, 72)
BLUE = RGBColor(39, 108, 178)
TEAL = RGBColor(40, 163, 135)
PALE = RGBColor(239, 245, 250)
TEXT = RGBColor(42, 52, 66)
MUTED = RGBColor(95, 109, 126)
WHITE = RGBColor(255, 255, 255)


def textbox(slide, x, y, w, h, text, size=20, color=TEXT, bold=False, font="Aptos", align=None):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = Inches(.04); tf.margin_right = Inches(.04)
    tf.margin_top = Inches(.02); tf.margin_bottom = Inches(.02)
    p = tf.paragraphs[0]
    p.text = text
    p.font.name = font; p.font.size = Pt(size); p.font.bold = bold; p.font.color.rgb = color
    if align is not None: p.alignment = align
    return box


def base(title, kicker="ADY201m · DATA SCIENCE WITH PYTHON & SQL"):
    slide = prs.slides.add_slide(BLANK)
    slide.background.fill.solid(); slide.background.fill.fore_color.rgb = WHITE
    textbox(slide, .65, .25, 12, .3, kicker, 10, TEAL, True)
    textbox(slide, .65, .65, 12, .7, title, 28, NAVY, True)
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(.65), Inches(1.42), Inches(1.15), Inches(.06))
    line.fill.solid(); line.fill.fore_color.rgb = TEAL; line.line.fill.background()
    textbox(slide, .65, 7.1, 12, .2, "Nguồn dữ liệu: Kaggle · UAE Used Car Prices & Features (10K+ Listings) · CC BY-SA 4.0", 9, MUTED)
    return slide


def card(slide, x, y, w, h, heading, body, accent=BLUE):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = PALE; sh.line.color.rgb = PALE
    textbox(slide, x+.2, y+.18, w-.4, .36, heading, 17, accent, True)
    textbox(slide, x+.2, y+.65, w-.4, h-.8, body, 14, TEXT)


# 1 — Title
s = prs.slides.add_slide(BLANK)
s.background.fill.solid(); s.background.fill.fore_color.rgb = NAVY
for x, y, w, h, c in [(9.4, .8, 2.9, 2.9, BLUE), (10.7, 2.4, 1.8, 1.8, TEAL), (8.5, 3.4, 1.5, 1.5, RGBColor(72, 130, 190))]:
    sh=s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(w), Inches(h)); sh.fill.solid(); sh.fill.fore_color.rgb=c; sh.line.fill.background()
textbox(s,.85,.65,7.5,.35,"ADY201m · PROJECT PHÂN TÍCH DỮ LIỆU",13,RGBColor(115,220,195),True)
textbox(s,.85,1.65,7.8,1.8,"Giá niêm yết xe cũ\ntại UAE",34,WHITE,True)
textbox(s,.9,4.05,7.2,.85,"Khám phá liên hệ giữa giá, năm sản xuất, số km và đặc điểm xe",19,RGBColor(218,228,242))
textbox(s,.9,6.35,7.5,.35,"Nguồn: Kaggle · 10.000 tin đăng · CC BY-SA 4.0",12,RGBColor(185,198,218))

# 2 — Questions
s=base("Bài toán thực tế và câu hỏi nghiên cứu")
textbox(s,.75,1.72,11.6,.6,"Người mua/bán cần hiểu mức giá rao bán khác nhau giữa các dòng xe.",20,NAVY,True)
card(s,.75,2.55,3.8,2.4,"RQ1 · Mô tả","Giá thay đổi thế nào theo năm, số km, hãng, kiểu thân xe và địa điểm?")
card(s,4.8,2.55,3.8,2.4,"RQ2 · So sánh","Phân phối giá SUV và Sedan có khác nhau trong mẫu không?",TEAL)
card(s,8.85,2.55,3.7,2.4,"RQ3 · Đánh giá","Year + Mileage dự đoán giá tốt đến đâu so với baseline trung vị?",BLUE)
textbox(s,.8,5.45,11.5,.65,"Biến đích: Price (AED) trong tin đăng. Đây không phải giá giao dịch đã xác nhận.",16,MUTED)

# 3 — Dataset
s=base("Dữ liệu và bước chuẩn bị")
card(s,.75,1.85,2.8,1.65,"Quy mô","10.000 tin đăng\n12 trường",BLUE)
card(s,3.7,1.85,2.8,1.65,"Đặc trưng","Hãng, mẫu, năm, km, kiểu xe, nhiên liệu, hộp số, địa điểm…",TEAL)
card(s,6.65,1.85,2.8,1.65,"Thiếu","155 giá trị Cylinders chưa biết",BLUE)
card(s,9.6,1.85,2.8,1.65,"Chuẩn hóa","9.869 Location có khoảng trắng đầu/cuối",TEAL)
textbox(s,.85,4.15,11.4,.5,"Không có dòng trùng hoàn toàn. CSV gốc được giữ nguyên; làm sạch và lưu riêng.",17,NAVY,True)
textbox(s,.85,4.9,11.5,1.0,"Giá rất lệch phải: median 102.766 AED, mean 245.235 AED; cực đại 14.686.975 AED. Cần kiểm tra bản ghi đắt trước khi quyết định xử lý ngoại lệ.",16,TEXT)

# 4 — Method and SQL
s=base("Quy trình: từ CSV đến SQL và thống kê")
steps=[("01","Câu hỏi"),("02","Profile & clean"),("03","SQLite + SQL"),("04","Thống kê & test"),("05","Hồi quy & kết luận")]
for i,(n,label) in enumerate(steps):
    x=.75+i*2.52
    sh=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(2.25), Inches(2.15), Inches(1.25))
    sh.fill.solid(); sh.fill.fore_color.rgb=PALE; sh.line.color.rgb=PALE
    textbox(s,x+.12,2.42,.55,.35,n,17,TEAL,True)
    textbox(s,x+.12,2.83,1.95,.48,label,15,NAVY,True)
    if i<4:
        textbox(s,x+2.18,2.63,.32,.3,"→",20,BLUE,True)
textbox(s,.85,4.35,11.4,.85,"SQLite chuẩn hóa: car_listing liên kết make, body_type, emirate. Truy vấn dùng JOIN, GROUP BY, HAVING; Python kết nối qua sqlite3 và pandas.read_sql_query.",16,TEXT)
textbox(s,.85,5.55,11.2,.45,"Code và database có thể chạy lại từ README.md.",15,MUTED)

# 5 — Distribution
s=base("Kết quả 1 · Giá niêm yết có đuôi phải dài")
textbox(s,.85,1.8,4.5,.45,"Trung vị so với trung bình (AED)",17,NAVY,True)
for label,val,color,y in [("Median",102766,TEAL,2.55),("Mean",245235,BLUE,3.55)]:
    textbox(s,.9,y,1.25,.35,label,15,TEXT,True)
    bg=s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(2.3), Inches(y+.02), Inches(4.25), Inches(.32)); bg.fill.solid(); bg.fill.fore_color.rgb=PALE; bg.line.fill.background()
    bar=s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(2.3), Inches(y+.02), Inches(4.25*val/260000), Inches(.32)); bar.fill.solid(); bar.fill.fore_color.rgb=color; bar.line.fill.background()
    textbox(s,6.7,y-.03,1.6,.38,f"{val:,.0f}",15,NAVY,True)
card(s,8.5,2.05,3.8,2.35,"Khoảng giá","7.183 AED đến 14,69 triệu AED\nQ1: 50.353 · Q3: 231.248",TEAL)
textbox(s,.9,5.05,11.4,.8,"Diễn giải: một số xe rất đắt kéo trung bình lên. Dùng median/quantile để tóm tắt trung tâm; chưa xóa ngoại lệ.",16,TEXT)

# 6 — group comparison
s=base("Kết quả 2 · SUV và Sedan khác nhau trong mẫu")
vals=[("SUV",118414,4607,TEAL),("Sedan",70287.5,2790,BLUE)]
for label,val,n,color,y in [(a,b,c,d,2.2+i*1.5) for i,(a,b,c,d) in enumerate(vals)]:
    textbox(s,.9,y,1.25,.4,label,17,NAVY,True)
    bg=s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(2.25), Inches(y+.02), Inches(5.25), Inches(.36)); bg.fill.solid(); bg.fill.fore_color.rgb=PALE; bg.line.fill.background()
    bar=s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(2.25), Inches(y+.02), Inches(5.25*val/130000), Inches(.36)); bar.fill.solid(); bar.fill.fore_color.rgb=color; bar.line.fill.background()
    textbox(s,7.7,y-.02,2.0,.42,f"{val:,.0f} AED",16,NAVY,True)
    textbox(s,9.9,y,1.4,.35,f"n={n:,}",14,MUTED)
card(s,.9,5.05,11.1,1.45,"Mann–Whitney U, hai phía","p xấp xỉ 1,44×10⁻⁷²; phân phối khác nhau trong mẫu. Không suy ra quan hệ nhân quả hoặc áp dụng trực tiếp cho cả thị trường.",TEAL)

# 7 — model
s=base("Kết quả 3 · Baseline hồi quy dự đoán yếu")
headers=[("Mô hình",.9,3.5),("MAE AED",4.6,2.2),("RMSE AED",7.0,2.3),("R² AED",9.8,1.6)]
for t,x,w in headers: textbox(s,x,1.95,w,.4,t,14,MUTED,True)
rows=[("Median train",193478,488599,-.096), ("Log-price: Year + Mileage",193896,484788,-.079)]
for i,(name,mae,rmse,r2) in enumerate(rows):
    y=2.55+i*1.0
    textbox(s,.9,y,3.55,.55,name,16,NAVY,True)
    textbox(s,4.6,y,2.2,.55,f"{mae:,.0f}",16,TEXT)
    textbox(s,7.0,y,2.3,.55,f"{rmse:,.0f}",16,TEXT)
    textbox(s,9.8,y,1.6,.55,f"{r2:.3f}",16,TEXT)
textbox(s,.9,4.85,11.4,.9,"Train/test = 8.000/2.000, seed cố định. Hồi quy giảm RMSE nhẹ nhưng MAE cao hơn baseline; cả hai R² đều âm. Không dùng mô hình này để định giá.",17,RGBColor(155,74,45),True)

# 8 — conclusion/limits
s=base("Kết luận và bước tiếp theo")
card(s,.85,1.9,5.55,2.25,"Kết luận","Kiểu xe và giá có khác biệt mô tả. Year/Mileage đơn lẻ gần như không tương quan tuyến tính với Price trong toàn bộ mẫu.",TEAL)
card(s,6.75,1.9,5.55,2.25,"Hạn chế","Giá đăng, không phải giá bán; Dubai chiếm đa số; giá cực trị; mô tả tình trạng là văn bản tự do; baseline thiếu nhiều đặc trưng.",BLUE)
textbox(s,.9,4.75,11.4,.65,"Tiếp theo: bổ sung hãng/mẫu/địa điểm và thông tin mô tả có kiểm soát, kiểm tra ngoại lệ, cross-validation, phân tích phần dư.",16,NAVY,True)
textbox(s,.9,5.7,11.2,.4,"Nguồn và giấy phép được ghi trong báo cáo. Đối chiếu slide với rubric chính thức trước khi nộp.",13,MUTED)

prs.save(OUT)
print(f"Created {OUT} ({len(prs.slides)} slides)")

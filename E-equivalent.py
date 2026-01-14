import streamlit as st
import pandas as pd
from docx import Document

# =============================
# ค่าคงที่
# =============================
CM_TO_INCH = 1 / 2.54
MPA_TO_PSI = 145.038

E_LIMITS = {
    "แอสฟัลต์คอนกรีต (AC)": (1500, 5000),
    "ชั้นปรับปรุงด้วยซีเมนต์ (CTB)": (500, 5000),
    "ชั้นหินคลุก / วัสดุเม็ด": (100, 400),
    "ชั้นดินเดิม (Subgrade)": (20, 150),
    "อื่น ๆ": (0, 10000)
}

# =============================
# หน้าเว็บ
# =============================
st.set_page_config(page_title="โมดูลัสเทียบเท่า", layout="centered")
st.title("การคำนวณโมดูลัสเทียบเท่าของโครงสร้างทาง")
st.subheader("วิธี Odemark (1974)")
st.markdown("กรอกความหนาเป็น **เซนติเมตร** และโมดูลัสเป็น **MPa**")

# =============================
# จำนวนชั้น
# =============================
n_layers = st.slider("จำนวนชั้นโครงสร้างทาง", 1, 5, 3)
layers = []

# =============================
# กรอกข้อมูล
# =============================
st.markdown("### ข้อมูลโครงสร้างทาง")

for i in range(n_layers):
    with st.expander(f"ชั้นที่ {i+1}", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            material = st.selectbox(
                "ชนิดวัสดุ", list(E_LIMITS.keys()), key=f"mat{i}"
            )
        with col2:
            h_cm = st.number_input(
                "ความหนา (ซม.)", 0.1, value=10.0, step=0.5, key=f"h{i}"
            )
        with col3:
            E = st.number_input(
                "โมดูลัส E (MPa)", 1.0, value=300.0, step=50.0, key=f"E{i}"
            )

        Emin, Emax = E_LIMITS[material]
        if not (Emin <= E <= Emax):
            st.warning(
                f"ค่า E = {E:.0f} MPa อยู่นอกช่วงที่พบบ่อย "
                f"({Emin}–{Emax} MPa)"
            )

        layers.append({
            "ชั้น": f"ชั้นที่ {i+1}",
            "ชนิดวัสดุ": material,
            "ความหนา (ซม.)": h_cm,
            "ความหนา (นิ้ว)": h_cm * CM_TO_INCH,
            "E (MPa)": E
        })

# =============================
# คำนวณ
# =============================
if st.button("คำนวณโมดูลัสเทียบเท่า"):

    sum_h = sum(l["ความหนา (ซม.)"] for l in layers)
    sum_h_E13 = sum(
        l["ความหนา (ซม.)"] * (l["E (MPa)"] ** (1/3)) for l in layers
    )

    Eeq_MPa = (sum_h_E13 / sum_h) ** 3
    Eeq_psi = Eeq_MPa * MPA_TO_PSI

    df = pd.DataFrame(layers)

    st.markdown("### สรุปข้อมูลที่กรอก")
    st.dataframe(df, use_container_width=True)

    st.success(
        f"โมดูลัสเทียบเท่า = {Eeq_psi:,.0f} psi ({Eeq_MPa:.1f} MPa)"
    )

    # =============================
    # Toggle แสดงวิธีคำนวณ
    # =============================
    show_method = st.checkbox("แสดงวิธีการคำนวณ")

    if show_method:
        st.markdown("### วิธีการคำนวณ (Odemark, 1974)")
        st.latex(
            r"E_{eq} = \left( \frac{\sum h_i E_i^{1/3}}{\sum h_i} \right)^3"
        )

        st.markdown("**ขั้นตอนการคำนวณ**")
        for l in layers:
            st.write(
                f"- {l['ชั้น']} : "
                f"h = {l['ความหนา (ซม.)']:.2f} cm, "
                f"E = {l['E (MPa)']:.1f} MPa, "
                f"E^(1/3) = {(l['E (MPa)']**(1/3)):.3f}"
            )

        st.write(f"Σh = {sum_h:.2f} cm")
        st.write(f"Σ(h·E¹ᐟ³) = {sum_h_E13:.2f}")
        st.write(
            f"E_equivalent = {Eeq_psi:,.0f} psi ({Eeq_MPa:.1f} MPa)"
        )

    # =============================
    # สร้างไฟล์ Word
    # =============================
    doc = Document()
    doc.add_heading("การคำนวณโมดูลัสเทียบเท่าของโครงสร้างทาง", level=1)
    doc.add_paragraph("วิธี Odemark (1974)\n")

    doc.add_heading("ข้อมูลโครงสร้างทาง", level=2)
    for l in layers:
        doc.add_paragraph(
            f"{l['ชั้น']} : {l['ชนิดวัสดุ']}, "
            f"h = {l['ความหนา (ซม.)']:.2f} cm "
            f"({l['ความหนา (นิ้ว)']:.2f} in), "
            f"E = {l['E (MPa)']:.1f} MPa"
        )

    doc.add_heading("วิธีการคำนวณ", level=2)
    doc.add_paragraph(
        "E_eq = ( Σ(h·E^(1/3)) / Σh )^3"
    )
    doc.add_paragraph(f"Σh = {sum_h:.2f} cm")
    doc.add_paragraph(f"Σ(h·E^(1/3)) = {sum_h_E13:.2f}")

    doc.add_heading("ผลการคำนวณ", level=2)
    doc.add_paragraph(
        f"E_equivalent = {Eeq_psi:,.0f} psi ({Eeq_MPa:.1f} MPa)"
    )

    # บันทึกไฟล์
    file_name = "Equivalent_Modulus_Odemark.docx"
    doc.save(file_name)

    with open(file_name, "rb") as f:
        st.download_button(
            label="ดาวน์โหลดรายงาน (Word)",
            data=f,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

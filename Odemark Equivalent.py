import streamlit as st
import numpy as np
import pandas as pd

# ======================================================
# Page config
# ======================================================
st.set_page_config(
    page_title="Equivalent Thickness (Odemark)",
    page_icon="🧱",
    layout="wide"
)

st.title("🧱 โปรแกรมคำนวณความหนาเทียบเท่า (Equivalent Thickness)")
st.markdown(
"""
สำหรับการเรียนการสอนและงานวิเคราะห์โครงสร้างผิวทาง  
**Odemark Transformation Method**
"""
)

# ======================================================
# Sidebar settings
# ======================================================
st.sidebar.header("⚙️ การตั้งค่า")

n_layer = st.sidebar.slider(
    "จำนวนชั้นวัสดุ",
    min_value=2,          # ✅ ปรับจาก 3 → 2
    max_value=5,
    value=3,
    key="n_layer"
)

n_exp = st.sidebar.number_input(
    "ค่า n (Odemark exponent)",
    min_value=1.0,
    max_value=5.0,
    value=3.0,
    step=0.1,
    key="n_exp"
)

st.sidebar.info("งานผิวทางยืดหยุ่นมักใช้ n ≈ 3")

# ======================================================
# Default layer names (รองรับ 2–5 ชั้น)
# ======================================================
default_layers = [
    "Base ",
    "Subbase ",
    "Subgrade",
    "Improved Subgrade 1",
    "Improved Subgrade 2"
]

layer_names_default = default_layers[:n_layer]

# ======================================================
# Input section
# ======================================================
st.subheader("📥 ป้อนข้อมูลชั้นวัสดุ")

cols = st.columns(n_layer)

h = []
E = []
names = []

for i in range(n_layer):
    with cols[i]:
        st.markdown(f"### ชั้นที่ {i+1}")

        name = st.text_input(
            "ชื่อชั้นวัสดุ",
            value=layer_names_default[i],
            key=f"name_{i}"
        )

        h_i = st.number_input(
            "ความหนา h (cm)",
            min_value=1.0,
            value=10.0,
            step=1.0,
            key=f"h_{i}"
        )

        E_i = st.number_input(
            "Modulus E (MPa)",
            min_value=10.0,
            value=3000.0 if i == 0 else 300.0,
            step=50.0,
            key=f"E_{i}"
        )

        names.append(name)
        h.append(h_i)
        E.append(E_i)

h = np.array(h)
E = np.array(E)

# ======================================================
# Reference layer selection
# ======================================================
st.divider()
st.subheader("📌 เลือกชั้นอ้างอิง (E_ref)")

ref_layer = st.selectbox(
    "เลือกชั้นที่ใช้เป็นชั้นอ้างอิง",
    options=names,
    key="ref_layer"
)

ref_index = names.index(ref_layer)
E_ref = E[ref_index]

st.info(f"ใช้ **{ref_layer}** เป็นชั้นอ้างอิง (E_ref = {E_ref:.0f} MPa)")

# ======================================================
# Equivalent Thickness calculation
# ======================================================
odemark_factor = (E / E_ref) ** (1 / n_exp)
h_eq = np.sum(h * odemark_factor)

st.divider()
st.subheader("📐 ผลการคำนวณ")

st.metric(
    "ความหนาเทียบเท่า (hₑq)",
    f"{h_eq:.2f} cm"
)

# ======================================================
# Summary table
# ======================================================
df = pd.DataFrame({
    "ชั้นที่": np.arange(1, n_layer + 1),
    "ชื่อชั้นวัสดุ": names,
    "ความหนา h (cm)": h,
    "Modulus E (MPa)": E,
    "ตัวคูณ Odemark": odemark_factor
})

st.subheader("📋 ตารางสรุปชั้นวัสดุ")
st.dataframe(df, use_container_width=True)

# ======================================================
# Sensitivity Analysis
# ======================================================
st.divider()
st.subheader("📊 Sensitivity Analysis")

delta = 0.10
h_eq_base = h_eq
sensitivity = []

for i in range(n_layer):
    E_new = E.copy()
    E_new[i] *= (1 + delta)

    h_eq_new = np.sum(
        h * (E_new / E_ref) ** (1 / n_exp)
    )

    S_i = ((h_eq_new - h_eq_base) / h_eq_base) / delta
    sensitivity.append(S_i)

df_sens = pd.DataFrame({
    "ชั้นวัสดุ": names,
    "Sensitivity": sensitivity
})

st.dataframe(df_sens, use_container_width=True)

# ======================================================
# Chart (Cloud-safe)
# ======================================================
st.subheader("📈 กราฟ Sensitivity")

st.bar_chart(
    df_sens.set_index("ชั้นวัสดุ"),
    use_container_width=True
)

# ======================================================
# Engineering conclusion
# ======================================================
critical_idx = df_sens["Sensitivity"].idxmax()

st.success(
    f"📌 ชั้นที่มีอิทธิพลต่อ hₑq มากที่สุดคือ "
    f"**{df_sens.loc[critical_idx, 'ชั้นวัสดุ']}** "
    f"(Sensitivity = {df_sens.loc[critical_idx, 'Sensitivity']:.2f})"
)

st.markdown(
"""
### 🧠 ค่า Modulus ของวัสดุ
- วัสดุ AC........................2500 Mpa
- วัสดุปรับคุณภาพด้วยซีเมนต์ CTB......1200 Mpa
- หินคลุกผสมซีเมนต์ (2.45 MPa)......850 Mpa
- หินคลุกรองใต้ผิวทางคอนกรีต.........350 Mpa
- ดินซีเมนต์ (1.75 MPa)............300 Mpa
- ดินซีเมนต์ (2.1 MPa).............500 Mpa
- วัสดุมวลรวม......................150 Mpa

- *** การเลือก E_ref ส่งผลต่อ hₑq โดยตรง

"""
)

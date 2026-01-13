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
ด้วยสมการของ  
**Odemark's Method**
"""
)

# ======================================================
# Material Library (Default Modulus)
# ======================================================
material_library = {
    "วัสดุ AC": 2500,
    "ปรับคุณภาพด้วยซีเมนต์ CTB": 1200,
    "หินคลุกผสมซีเมนต์ (2.45 MPa)": 850,
    "หินคลุกรองใต้ผิวทางคอนกรีต": 350,
    "ดินซีเมนต์ (1.75 MPa)": 300,
    "ดินซีเมนต์ (2.1 MPa)": 500,
    "วัสดุมวลรวม": 150
}

material_list = list(material_library.keys())

# ======================================================
# Sidebar settings
# ======================================================
st.sidebar.header("⚙️ การตั้งค่า")

n_layer = st.sidebar.slider(
    "จำนวนชั้นวัสดุ",
    min_value=2,
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
# Input section
# ======================================================
st.subheader("📥 ป้อนข้อมูลชั้นวัสดุ")

cols = st.columns(n_layer)

h = []
E = []
materials = []

for i in range(n_layer):
    with cols[i]:
        st.markdown(f"### ชั้นที่ {i+1}")

        mat = st.selectbox(
            "เลือกชนิดวัสดุ",
            options=material_list,
            index=0 if i == 0 else min(i, len(material_list)-1),
            key=f"mat_{i}"
        )

        E_default = material_library[mat]

        E_i = st.number_input(
            "Modulus E (MPa)",
            min_value=50.0,
            value=float(E_default),
            step=50.0,
            key=f"E_{i}"
        )

        h_i = st.number_input(
            "ความหนา h (cm)",
            min_value=1.0,
            value=10.0,
            step=1.0,
            key=f"h_{i}"
        )

        materials.append(mat)
        E.append(E_i)
        h.append(h_i)

h = np.array(h)
E = np.array(E)

# ======================================================
# Reference layer selection
# ======================================================
st.divider()
st.subheader("📌 เลือกชั้นอ้างอิง (E_ref)")

ref_layer = st.selectbox(
    "เลือกชั้นที่ใช้เป็นชั้นอ้างอิง",
    options=[f"ชั้นที่ {i+1}: {materials[i]}" for i in range(n_layer)],
    key="ref_layer"
)

ref_index = int(ref_layer.split(":")[0].replace("ชั้นที่", "")) - 1
E_ref = E[ref_index]

st.info(
    f"ใช้ **{materials[ref_index]}** เป็นชั้นอ้างอิง "
    f"(E_ref = {E_ref:.0f} MPa)"
)

# ======================================================
# Equivalent Thickness calculation
# ======================================================
odemark_factor = (E / E_ref) ** (1 / n_exp)
h_eq = np.sum(h * odemark_factor)
h_eq_inch = h_eq / 2.54
st.divider()
st.subheader("📐 ผลการคำนวณ")

st.metric(
    label="ความหนาเทียบเท่า (hₑq)",
    value=f"{h_eq:.2f} cm",
    delta=f"{h_eq_inch:.2f} in"
)

# ======================================================
# Summary table
# ======================================================
df = pd.DataFrame({
    "ชั้นที่": np.arange(1, n_layer + 1),
    "วัสดุ": materials,
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
    "วัสดุ": materials,
    "Sensitivity": sensitivity
})

st.dataframe(df_sens, use_container_width=True)

# ======================================================
# Chart (Cloud-safe)
# ======================================================
st.subheader("📈 กราฟ Sensitivity")

st.bar_chart(
    df_sens.set_index("วัสดุ"),
    use_container_width=True
)
# ======================================================
# แสดงวิธีการคำนวณ (เปิด / ปิด ได้)
# ======================================================
with st.expander("🧮 แสดงวิธีการคำนวณ (Odemark Method)", expanded=False):

    st.markdown("### 1️⃣ สมการที่ใช้")
    st.latex(
        r"h_{eq} = \sum_{i=1}^{n} h_i \left(\frac{E_i}{E_{ref}}\right)^{1/n}"
    )

    st.markdown("### 2️⃣ ค่าที่ใช้ในการคำนวณ")
    st.markdown(
        f"""
- จำนวนชั้นวัสดุ = **{n_layer} ชั้น**  
- ค่า Odemark exponent, n = **{n_exp}**  
- ชั้นอ้างอิง (E_ref) = **{materials[ref_index]}**  
- ค่า E_ref = **{E_ref:.0f} MPa**
"""
    )

    st.markdown("### 3️⃣ การคำนวณรายชั้น")

    calc_rows = []
    for i in range(n_layer):
        factor_i = (E[i] / E_ref) ** (1 / n_exp)
        h_eq_i = h[i] * factor_i

        calc_rows.append({
            "ชั้นที่": i + 1,
            "วัสดุ": materials[i],
            "hᵢ (cm)": f"{h[i]:.2f}",
            "Eᵢ (MPa)": f"{E[i]:.0f}",
            "(Eᵢ / E_ref)^(1/n)": f"{factor_i:.3f}",
            "hᵢ × factor (cm)": f"{h_eq_i:.2f}"
        })

    df_calc = pd.DataFrame(calc_rows)
    st.dataframe(df_calc, use_container_width=True)

    st.markdown("### 4️⃣ ผลรวมความหนาเทียบเท่า")

    st.markdown(
        f"""
\[
h_{{eq}} = {h_eq:.2f}\ \text{{cm}} = {h_eq_inch:.2f}\ \text{{inch}}
\]

โดย  
\[
1\ \text{{inch}} = 2.54\ \text{{cm}}
\]
"""
    )

# ======================================================
# Engineering conclusion
# ======================================================
critical_idx = df_sens["Sensitivity"].idxmax()

st.success(
    f"📌 ชั้นที่มีอิทธิพลต่อ hₑq มากที่สุดคือ "
    f"**{df_sens.loc[critical_idx, 'วัสดุ']}** "
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

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# ตั้งค่าหน้าเว็บ
# -----------------------------
st.set_page_config(
    page_title="Equivalent Thickness & Sensitivity Analysis",
    page_icon="🧱",
    layout="wide"
)

st.title("🧱 โปรแกรมคำนวณความหนาเทียบเท่า (Equivalent Thickness)")
st.markdown(
"""
พัฒนาเพื่อการเรียนการสอนและงานวิจัยด้าน **โครงสร้างผิวทางหลายชั้น**  
ใช้แนวคิด **Odemark Transformation Method**
"""
)

# -----------------------------
# เลือกจำนวนชั้น
# -----------------------------
st.sidebar.header("⚙️ การตั้งค่าโครงสร้าง")
n_layer = st.sidebar.slider(
    "เลือกจำนวนชั้นวัสดุ",
    min_value=3,
    max_value=5,
    value=3
)

n_exp = st.sidebar.number_input(
    "ค่าดัชนี n (Odemark exponent)",
    min_value=1.0,
    max_value=5.0,
    value=3.0,
    step=0.1
)

st.sidebar.info("โดยทั่วไปงานผิวทางยืดหยุ่นใช้ n ≈ 3")

# -----------------------------
# รับข้อมูล h และ E
# -----------------------------
st.subheader("📥 ป้อนข้อมูลชั้นวัสดุ")

cols = st.columns(n_layer)

h = []
E = []

for i in range(n_layer):
    with cols[i]:
        st.markdown(f"### ชั้นที่ {i+1}")
        h_i = st.number_input(
            f"ความหนา h{i+1} (cm)",
            min_value=1.0,
            value=10.0,
            step=1.0
        )
        E_i = st.number_input(
            f"Modulus E{i+1} (MPa)",
            min_value=10.0,
            value=1000.0/(i+1),
            step=50.0
        )
        h.append(h_i)
        E.append(E_i)

h = np.array(h)
E = np.array(E)

E_ref = E[0]

# -----------------------------
# คำนวณ Equivalent Thickness
# -----------------------------
h_eq = np.sum(h * (E / E_ref) ** (1 / n_exp))

st.markdown("---")
st.subheader("📐 ผลการคำนวณ Equivalent Thickness")

st.metric(
    label="ความหนาเทียบเท่า (h_eq)",
    value=f"{h_eq:.2f} cm"
)

st.caption("เทียบเท่าชั้นอ้างอิง (Layer 1)")

# -----------------------------
# ตารางสรุป
# -----------------------------
df = pd.DataFrame({
    "ชั้นที่": np.arange(1, n_layer + 1),
    "ความหนา h (cm)": h,
    "Modulus E (MPa)": E,
    "ตัวคูณ Odemark": (E / E_ref) ** (1 / n_exp)
})

st.dataframe(df, use_container_width=True)

# -----------------------------
# Sensitivity Analysis
# -----------------------------
st.markdown("---")
st.subheader("📊 Sensitivity Analysis")

delta = 0.10  # เพิ่ม E ทีละ 10%
h_eq_base = h_eq
sensitivity = []

for i in range(n_layer):
    E_perturbed = E.copy()
    E_perturbed[i] *= (1 + delta)

    h_eq_new = np.sum(h * (E_perturbed / E_ref) ** (1 / n_exp))

    S_i = ((h_eq_new - h_eq_base) / h_eq_base) / delta
    sensitivity.append(S_i)

df_sens = pd.DataFrame({
    "ชั้นที่": np.arange(1, n_layer + 1),
    "Sensitivity (∂h_eq/∂E)": sensitivity
})

st.dataframe(df_sens, use_container_width=True)

# -----------------------------
# กราฟ
# -----------------------------
st.subheader("📈 กราฟ Sensitivity ของแต่ละชั้น")

fig, ax = plt.subplots()
ax.bar(df_sens["ชั้นที่"], df_sens["Sensitivity (∂h_eq/∂E)"])
ax.set_xlabel("ชั้นวัสดุ")
ax.set_ylabel("Sensitivity")
ax.set_title("ผลกระทบของ Modulus ต่อ h_eq")
ax.grid(True, linestyle="--", alpha=0.5)

st.pyplot(fig)

# -----------------------------
# สรุปเชิงวิศวกรรม
# -----------------------------
max_layer = np.argmax(sensitivity) + 1

st.success(
    f"📌 **ชั้นที่ {max_layer} มีผลต่อ h_eq มากที่สุด** "
    f"(Sensitivity = {sensitivity[max_layer-1]:.2f})"
)

st.markdown(
"""
### 🧠 ข้อสังเกตเชิงวิศวกรรม
- ชั้นบน (Modulus สูง) มักส่งผลต่อความหนาเทียบเท่ามากที่สุด  
- ชั้นล่างแม้หนา แต่ถ้า E ต่ำ → อิทธิพลต่อ h_eq จำกัด  
- ใช้ผลนี้ในการ:
  - ปรับปรุงโครงสร้างอย่างคุ้มค่า
  - อธิบายแนวคิด SN และ Layer Coefficient ใน AASHTO
"""
)

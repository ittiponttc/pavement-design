import streamlit as st
st.write("สำหรับการออกแบบโครงสร้างชั้นทาง (Pavement Design)")
st.subheader("Odemark's Method of Equivalent Thickness Calculator")

# Sidebar สำหรับตั้งค่า
st.sidebar.header("⚙️ ตั้งค่าพารามิเตอร์")

# เลือกจำนวนชั้น
num_layers = st.sidebar.slider(
    "จำนวนชั้นวัสดุ (ไม่รวม Subgrade)",
    min_value=1,
    max_value=6,
    value=3,
    help="เลือกจำนวนชั้นวัสดุที่อยู่เหนือชั้น Subgrade"
)

# Correction Factor
correction_factor = st.sidebar.slider(
    "Correction Factor (f)",
    min_value=0.7,
    max_value=1.0,
    value=0.9,
    step=0.05,
    help="ค่าปรับแก้ตาม Odemark (แนะนำ 0.8-0.9)"
)

# ข้อมูล Subgrade
st.sidebar.markdown("---")
st.sidebar.subheader("🏔️ ชั้น Subgrade")
E_subgrade = st.sidebar.number_input(
    "Modulus ของ Subgrade (MPa)",
    min_value=5.0,
    max_value=500.0,
    value=40.0,
    step=5.0,
    help="ค่า Resilient Modulus ของดินคันทาง"
)

CBR_subgrade = E_subgrade / 10.34
st.sidebar.info(f"📊 CBR โดยประมาณ: {CBR_subgrade:.1f}%")

# ค่า Default สำหรับแต่ละชั้น
default_names = [
    "Surface Course",
    "Binder Course", 
    "Base Course",
    "Subbase Course",
    "Selected Material",
    "Capping Layer"
]

default_thickness = [5, 7, 20, 25, 30, 20]
default_modulus = [3000, 2500, 400, 200, 100, 80]



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



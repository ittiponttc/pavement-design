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

# ส่วนกรอกข้อมูล
st.header("📝 ข้อมูลชั้นวัสดุ")

# สร้าง columns สำหรับ header
col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1])
with col1:
    st.markdown("**ชื่อชั้นวัสดุ**")
with col2:
    st.markdown("**ความหนา (cm)**")
with col3:
    st.markdown("**Modulus E (MPa)**")
with col4:
    st.markdown("**CBR ≈ (%)**")

# เก็บข้อมูลแต่ละชั้น
layer_data = []

for i in range(num_layers):
    col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1])
    
    with col1:
        name = st.text_input(
            f"ชื่อชั้น {i+1}",
            value=default_names[i] if i < len(default_names) else f"Layer {i+1}",
            key=f"name_{i}",
            label_visibility="collapsed"
        )
    
    with col2:
        thickness = st.number_input(
            f"ความหนา {i+1}",
            min_value=1.0,
            max_value=100.0,
            value=float(default_thickness[i]) if i < len(default_thickness) else 20.0,
            step=1.0,
            key=f"thickness_{i}",
            label_visibility="collapsed"
        )
    
    with col3:
        modulus = st.number_input(
            f"Modulus {i+1}",
            min_value=10.0,
            max_value=10000.0,
            value=float(default_modulus[i]) if i < len(default_modulus) else 200.0,
            step=10.0,
            key=f"modulus_{i}",
            label_visibility="collapsed"
        )
    
    with col4:
        cbr_approx = modulus / 10.34
        st.markdown(f"**{cbr_approx:.1f}**")
    
    layer_data.append({
        "name": name,
        "thickness": thickness,
        "modulus": modulus,
        "cbr": cbr_approx
    })

# แสดงชั้น Subgrade
st.markdown("---")
col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1])
with col1:
    st.markdown("**🏔️ Subgrade (ดินคันทาง)**")
with col2:
    st.markdown("**∞**")
with col3:
    st.markdown(f"**{E_subgrade:.1f}**")
with col4:
    st.markdown(f"**{CBR_subgrade:.1f}**")

# ปุ่มคำนวณ
st.markdown("---")

if st.button("🔢 คำนวณ Equivalent Thickness", type="primary"):
    
    st.header("📊 ผลการคำนวณ")
    
    # แสดงสูตร
    st.markdown("### สูตร Odemark's Method")
    st.latex(r"h_e = f \times h \times \sqrt[3]{\frac{E}{E_{subgrade}}}")
    
    # คำนวณ Equivalent Thickness
    st.markdown("### ตารางผลการคำนวณ")
    
    results = []
    total_he = 0
    total_h = 0
    
    for i, layer in enumerate(layer_data):
        h = layer["thickness"]
        E = layer["modulus"]
        
        modular_ratio = E / E_subgrade
        cube_root = modular_ratio ** (1/3)
        he = correction_factor * h * cube_root
        
        total_he += he
        total_h += h
        
        results.append({
            "ลำดับ": i + 1,
            "ชื่อชั้น": layer["name"],
            "h (cm)": h,
            "E (MPa)": E,
            "E/E_sub": round(modular_ratio, 3),
            "∛(E/E_sub)": round(cube_root, 3),
            "h_e (cm)": round(he, 2)
        })
    
    # แสดงตารางผลลัพธ์
    df_results = pd.DataFrame(results)
    st.dataframe(df_results, use_container_width=True, hide_index=True)
    
    # แสดงรายละเอียดการคำนวณ
    st.markdown("### รายละเอียดการคำนวณแต่ละชั้น")
    
    for i, layer in enumerate(layer_data):
        h = layer["thickness"]
        E = layer["modulus"]
        modular_ratio = E / E_subgrade
        cube_root = modular_ratio ** (1/3)
        he = correction_factor * h * cube_root
        
        with st.expander(f"📐 ชั้นที่ {i+1}: {layer['name']}", expanded=False):
            st.write(f"**ข้อมูล:** h = {h} cm, E = {E} MPa")
            st.write(f"**E/E_sub** = {E}/{E_subgrade} = {modular_ratio:.4f}")
            st.write(f"**∛(E/E_sub)** = ∛{modular_ratio:.4f} = {cube_root:.4f}")
            st.write(f"**h_e** = {correction_factor} × {h} × {cube_root:.4f} = **{he:.2f} cm**")
    
    # สรุปผล
    st.markdown("---")
    st.markdown("### 🎯 สรุปผลการคำนวณ")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="ความหนารวมจริง (Σh)",
            value=f"{total_h:.1f} cm"
        )
    
    with col2:
        st.metric(
            label="ความหนาเทียบเท่ารวม (Σh_e)",
            value=f"{total_he:.2f} cm"
        )
    
    with col3:
        E_eff = E_subgrade * (total_he / total_h) ** 3 if total_h > 0 else E_subgrade
        CBR_eff = E_eff / 10.34
        
        st.metric(
            label="Effective CBR",
            value=f"{CBR_eff:.1f}%"
        )
    
    # แสดงการคำนวณ Effective Modulus
    st.markdown("### การคำนวณ Effective Modulus")
    
    st.latex(r"E_{eff} = E_{sub} \times \left(\frac{h_{e,total}}{h_{total}}\right)^3")
    
    ratio = total_he / total_h
    st.write(f"**E_eff** = {E_subgrade} × ({total_he:.2f}/{total_h:.1f})³")
    st.write(f"**E_eff** = {E_subgrade} × ({ratio:.4f})³")
    st.write(f"**E_eff** = {E_subgrade} × {ratio**3:.4f}")
    st.write(f"**E_eff** = **{E_eff:.2f} MPa**")
    
    st.markdown("### การแปลงเป็น CBR")
    st.latex(r"CBR_{eff} = \frac{E_{eff}}{10.34}")
    st.write(f"**CBR_eff** = {E_eff:.2f} / 10.34 = **{CBR_eff:.1f}%**")
    
    # ตารางสรุป
    st.markdown("---")
    st.markdown("### 📋 ตารางสรุปสำหรับรายงาน")
    
    summary_data = {
        "รายการ": [
            "จำนวนชั้นวัสดุ",
            "Correction Factor (f)",
            "ความหนารวมจริง (Σh)",
            "ความหนาเทียบเท่ารวม (Σh_e)",
            "Modulus ของ Subgrade (E_sub)",
            "CBR ของ Subgrade",
            "Effective Modulus (E_eff)",
            "Effective CBR"
        ],
        "ค่า": [
            f"{num_layers} ชั้น",
            f"{correction_factor}",
            f"{total_h:.1f} cm",
            f"{total_he:.2f} cm",
            f"{E_subgrade:.1f} MPa",
            f"{CBR_subgrade:.1f}%",
            f"{E_eff:.2f} MPa",
            f"{CBR_eff:.1f}%"
        ]
    }
    
    df_summary = pd.DataFrame(summary_data)
    st.dataframe(df_summary, use_container_width=True, hide_index=True)
    
    # ปุ่ม Download
    csv_results = df_results.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Download ผลลัพธ์ (CSV)",
        data=csv_results,
        file_name="odemark_results.csv",
        mime="text/csv"
    )

# ส่วนทฤษฎี
st.markdown("---")
with st.expander("📖 ทฤษฎี Odemark's Method"):
    st.markdown("""
    ### หลักการ
    
    **Odemark's Method of Equivalent Thickness** เป็นวิธีการแปลงโครงสร้างชั้นทางหลายชั้น 
    ให้เป็นชั้นเดียวที่มีความหนาเทียบเท่า โดยอ้างอิงกับ Modulus ของชั้น Subgrade
    
    ### สูตรหลัก
    """)
    
    st.latex(r"h_e = f \times h \times \sqrt[3]{\frac{E}{E_{subgrade}}}")
    
    st.markdown("""
    ### ความหมายของตัวแปร
    
    | ตัวแปร | ความหมาย | หน่วย |
    |--------|---------|-------|
    | h_e | ความหนาเทียบเท่า (Equivalent Thickness) | cm |
    | h | ความหนาจริงของชั้นวัสดุ | cm |
    | E | Elastic Modulus ของชั้นวัสดุ | MPa |
    | E_subgrade | Elastic Modulus ของชั้น Subgrade | MPa |
    | f | Correction Factor (0.8 - 0.9) | - |
    
    ### เอกสารอ้างอิง
    
    - Odemark, N. (1949)
    - AASHTO Guide for Design of Pavement Structures (1993)
    - Huang, Y.H. (2004). "Pavement Analysis and Design"
    """)

# Footer
st.markdown("---")
st.caption("🛣️ Odemark's Method Calculator | Developed for Pavement Engineering Education")

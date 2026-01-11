"""
Odemark's Method of Equivalent Thickness Calculator
สำหรับการออกแบบโครงสร้างชั้นทาง (Pavement Design)
พัฒนาสำหรับงานวิศวกรรมโยธา

Developed by: รศ.ดร.อิทธิพลมีผล
Reference: AASHTO 1993, Layered Elastic Theory
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="Odemark's Method Calculator",
    page_icon="🛣️",
    layout="wide"
)

# CSS สำหรับตกแต่ง
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #475569;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        background-color: #F0F9FF;
        border: 2px solid #0EA5E9;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .formula-box {
        background-color: #FEF3C7;
        border: 1px solid #F59E0B;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
        font-family: 'Courier New', monospace;
    }
    .layer-input {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# หัวข้อหลัก
st.markdown('<h1 class="main-header">🛣️ Odemark\'s Method Calculator</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">การคำนวณความหนาเทียบเท่า (Equivalent Thickness) สำหรับโครงสร้างชั้นทาง</p>', unsafe_allow_html=True)

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

CBR_subgrade = E_subgrade / 10.34  # แปลงเป็น CBR โดยประมาณ
st.sidebar.info(f"📊 CBR โดยประมาณ: {CBR_subgrade:.1f}%")

# ค่า Default สำหรับแต่ละชั้น
default_names = [
    "Surface Course (ผิวทาง)",
    "Binder Course",
    "Base Course (ชั้นพื้นทาง)",
    "Subbase Course (ชั้นรองพื้นทาง)",
    "Selected Material",
    "Capping Layer"
]

default_thickness = [5, 7, 20, 25, 30, 20]  # cm
default_modulus = [3000, 2500, 400, 200, 100, 80]  # MPa

# สร้าง Tabs
tab1, tab2, tab3 = st.tabs(["📝 ข้อมูลนำเข้า", "📊 ผลการคำนวณ", "📖 ทฤษฎี"])

with tab1:
    st.subheader("กรอกข้อมูลชั้นวัสดุ")
    
    # สร้าง columns สำหรับ input
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
                f"ชั้นที่ {i+1}",
                value=default_names[i] if i < len(default_names) else f"Layer {i+1}",
                key=f"name_{i}",
                label_visibility="collapsed"
            )
        
        with col2:
            thickness = st.number_input(
                f"h{i+1}",
                min_value=1.0,
                max_value=100.0,
                value=float(default_thickness[i]) if i < len(default_thickness) else 20.0,
                step=1.0,
                key=f"thickness_{i}",
                label_visibility="collapsed"
            )
        
        with col3:
            modulus = st.number_input(
                f"E{i+1}",
                min_value=10.0,
                max_value=10000.0,
                value=float(default_modulus[i]) if i < len(default_modulus) else 200.0,
                step=10.0,
                key=f"modulus_{i}",
                label_visibility="collapsed"
            )
        
        with col4:
            cbr_approx = modulus / 10.34
            st.markdown(f"<br>**{cbr_approx:.1f}**", unsafe_allow_html=True)
        
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

with tab2:
    st.subheader("📊 ผลการคำนวณตาม Odemark's Method")
    
    # คำนวณ Equivalent Thickness
    st.markdown("### 1. การคำนวณ Equivalent Thickness แต่ละชั้น")
    
    results = []
    total_he = 0
    total_h = 0
    
    for i, layer in enumerate(layer_data):
        h = layer["thickness"]
        E = layer["modulus"]
        
        # สูตร Odemark: he = f × h × (E/E_subgrade)^(1/3)
        modular_ratio = E / E_subgrade
        cube_root = modular_ratio ** (1/3)
        he = correction_factor * h * cube_root
        
        total_he += he
        total_h += h
        
        results.append({
            "ชั้น": layer["name"],
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
    st.markdown("### 2. รายละเอียดการคำนวณ")
    
    for i, layer in enumerate(layer_data):
        h = layer["thickness"]
        E = layer["modulus"]
        modular_ratio = E / E_subgrade
        cube_root = modular_ratio ** (1/3)
        he = correction_factor * h * cube_root
        
        with st.expander(f"📐 {layer['name']}", expanded=(i==0)):
            st.latex(rf"h_{{e,{i+1}}} = f \times h_{i+1} \times \sqrt[3]{{\frac{{E_{i+1}}}{{E_{{sub}}}}}}")
            st.latex(rf"h_{{e,{i+1}}} = {correction_factor} \times {h} \times \sqrt[3]{{\frac{{{E}}}{{{E_subgrade}}}}}")
            st.latex(rf"h_{{e,{i+1}}} = {correction_factor} \times {h} \times \sqrt[3]{{{modular_ratio:.3f}}}")
            st.latex(rf"h_{{e,{i+1}}} = {correction_factor} \times {h} \times {cube_root:.3f}")
            st.latex(rf"h_{{e,{i+1}}} = {he:.2f} \text{{ cm}}")
    
    # สรุปผล
    st.markdown("---")
    st.markdown("### 3. สรุปผลการคำนวณ")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="🔢 ความหนารวมจริง (Σh)",
            value=f"{total_h:.1f} cm",
            delta=None
        )
    
    with col2:
        st.metric(
            label="📐 ความหนาเทียบเท่ารวม (Σh_e)",
            value=f"{total_he:.1f} cm",
            delta=f"{((total_he/total_h)-1)*100:.1f}%" if total_h > 0 else None
        )
    
    with col3:
        # คำนวณ Effective Modulus
        E_eff = E_subgrade * (total_he / total_h) ** 3 if total_h > 0 else E_subgrade
        CBR_eff = E_eff / 10.34
        
        st.metric(
            label="📊 Effective CBR",
            value=f"{CBR_eff:.1f}%",
            delta=f"{CBR_eff - CBR_subgrade:.1f}%" if CBR_eff > CBR_subgrade else f"{CBR_eff - CBR_subgrade:.1f}%"
        )
    
    # แสดงสูตรสรุป
    st.markdown("### 4. สูตรการคำนวณ")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Total Equivalent Thickness:**")
        st.latex(rf"h_{{e,total}} = \sum_{{i=1}}^{{n}} h_{{e,i}} = {total_he:.2f} \text{{ cm}}")
    
    with col2:
        st.markdown("**Effective Modulus:**")
        st.latex(rf"E_{{eff}} = E_{{sub}} \times \left(\frac{{h_{{e,total}}}}{{h_{{total}}}}\right)^3")
        st.latex(rf"E_{{eff}} = {E_subgrade} \times \left(\frac{{{total_he:.2f}}}{{{total_h:.1f}}}\right)^3 = {E_eff:.1f} \text{{ MPa}}")
    
    # แผนภาพโครงสร้างชั้นทาง
    st.markdown("---")
    st.markdown("### 5. แผนภาพโครงสร้างชั้นทาง")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**โครงสร้างจริง**")
        
        # สร้างแผนภาพด้วย Plotly
        fig1 = go.Figure()
        
        colors = ['#1E40AF', '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE', '#DBEAFE']
        y_pos = 0
        
        for i, layer in enumerate(layer_data):
            fig1.add_trace(go.Bar(
                x=[100],
                y=[layer["thickness"]],
                base=y_pos,
                orientation='v',
                name=layer["name"],
                marker_color=colors[i % len(colors)],
                text=f"{layer['name']}<br>h={layer['thickness']} cm<br>E={layer['modulus']} MPa",
                textposition='inside',
                hoverinfo='text'
            ))
            y_pos += layer["thickness"]
        
        # เพิ่ม Subgrade
        fig1.add_trace(go.Bar(
            x=[100],
            y=[30],
            base=y_pos,
            orientation='v',
            name="Subgrade",
            marker_color='#A3A3A3',
            text=f"Subgrade<br>E={E_subgrade} MPa",
            textposition='inside'
        ))
        
        fig1.update_layout(
            showlegend=False,
            height=500,
            yaxis_title="ความลึก (cm)",
            xaxis_visible=False,
            yaxis=dict(autorange="reversed"),
            margin=dict(l=50, r=20, t=20, b=20)
        )
        
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.markdown("**เปรียบเทียบ h จริง vs h_e**")
        
        # สร้างกราฟเปรียบเทียบ
        fig2 = go.Figure()
        
        layer_names = [layer["name"][:15] for layer in layer_data]
        h_actual = [layer["thickness"] for layer in layer_data]
        h_equiv = [r["h_e (cm)"] for r in results]
        
        fig2.add_trace(go.Bar(
            name='h จริง (cm)',
            x=layer_names,
            y=h_actual,
            marker_color='#3B82F6'
        ))
        
        fig2.add_trace(go.Bar(
            name='h_e เทียบเท่า (cm)',
            x=layer_names,
            y=h_equiv,
            marker_color='#10B981'
        ))
        
        fig2.update_layout(
            barmode='group',
            height=500,
            yaxis_title="ความหนา (cm)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=50, r=20, t=50, b=20)
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    
    # ตารางสรุปสำหรับ Export
    st.markdown("---")
    st.markdown("### 6. ตารางสรุปสำหรับรายงาน")
    
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
            num_layers,
            correction_factor,
            f"{total_h:.1f} cm",
            f"{total_he:.2f} cm",
            f"{E_subgrade:.1f} MPa",
            f"{CBR_subgrade:.1f}%",
            f"{E_eff:.1f} MPa",
            f"{CBR_eff:.1f}%"
        ]
    }
    
    df_summary = pd.DataFrame(summary_data)
    st.dataframe(df_summary, use_container_width=True, hide_index=True)
    
    # ปุ่ม Download CSV
    csv_results = df_results.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Download ผลลัพธ์ (CSV)",
        data=csv_results,
        file_name="odemark_results.csv",
        mime="text/csv"
    )

with tab3:
    st.subheader("📖 ทฤษฎี Odemark's Method")
    
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
    | $h_e$ | ความหนาเทียบเท่า (Equivalent Thickness) | cm |
    | $h$ | ความหนาจริงของชั้นวัสดุ | cm |
    | $E$ | Elastic Modulus ของชั้นวัสดุ | MPa |
    | $E_{subgrade}$ | Elastic Modulus ของชั้น Subgrade | MPa |
    | $f$ | Correction Factor (0.8 - 0.9) | - |
    
    ### สำหรับหลายชั้น
    """)
    
    st.latex(r"h_{e,total} = f \times \sum_{i=1}^{n} h_i \times \sqrt[3]{\frac{E_i}{E_{subgrade}}}")
    
    st.markdown("""
    ### การหา Effective Modulus
    
    เมื่อต้องการหาค่า Modulus รวมของโครงสร้างทั้งหมด:
    """)
    
    st.latex(r"E_{eff} = E_{subgrade} \times \left(\frac{h_{e,total}}{h_{total}}\right)^3")
    
    st.markdown("""
    ### การแปลงเป็น CBR
    
    ใช้สูตรความสัมพันธ์ AASHTO:
    """)
    
    st.latex(r"CBR \approx \frac{E_{(MPa)}}{10.34}")
    
    st.markdown("""
    หรือ
    """)
    
    st.latex(r"M_R (psi) = 1,500 \times CBR")
    
    st.markdown("""
    ### ข้อจำกัดของวิธี Odemark
    
    1. สมมติว่าวัสดุเป็น **Linear Elastic** และ **Isotropic**
    2. ไม่พิจารณาผลของ **Interface Bonding** ระหว่างชั้น
    3. ค่า Correction Factor ควรอยู่ระหว่าง **0.8 - 0.9**
    4. เหมาะสำหรับการประมาณเบื้องต้น ควรใช้ร่วมกับ Software เช่น KENLAYER, BISAR
    
    ### เอกสารอ้างอิง
    
    - Odemark, N. (1949). "Investigations as to the Elastic Properties of Soils and Design of Pavements According to the Theory of Elasticity"
    - AASHTO Guide for Design of Pavement Structures (1993)
    - Huang, Y.H. (2004). "Pavement Analysis and Design", 2nd Edition
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748B; font-size: 0.9rem;'>
    🛣️ Odemark's Method Calculator | Developed for Pavement Engineering Education<br>
    Reference: AASHTO 1993, Layered Elastic Theory
</div>
""", unsafe_allow_html=True)

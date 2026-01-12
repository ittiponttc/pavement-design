import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from io import BytesIO
import base64

# ═══════════════════════════════════════════════════════════════
# การตั้งค่าหน้าเว็บ
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AASHTO 1993 เครื่องคำนวณ",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com',
        'Report a bug': "https://github.com"
    }
)

# CSS ที่ปรับปรุง
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Prompt', sans-serif;
    }
    
    /* Header Section */
    .header-main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px 20px;
        border-radius: 15px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .header-main h1 {
        margin: 0;
        font-weight: 700;
        font-size: 2.5em;
    }
    
    .header-main p {
        margin: 10px 0 0 0;
        font-weight: 300;
        font-size: 1.1em;
        opacity: 0.9;
    }
    
    /* Box Styles */
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 5px solid #28a745;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(40, 167, 69, 0.1);
    }
    
    .info-box {
        background: linear-gradient(135deg, #cfe2ff 0%, #b6d4fe 100%);
        border-left: 5px solid #0d6efd;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(13, 110, 253, 0.1);
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffe69c 100%);
        border-left: 5px solid #ffc107;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(255, 193, 7, 0.1);
    }
    
    .concept-box {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-left: 5px solid #6c757d;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(108, 117, 125, 0.1);
    }
    
    /* Metric Cards */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
        text-align: center;
        border-top: 3px solid #667eea;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        font-weight: 600 !important;
    }
    
    /* Table */
    table {
        border-collapse: collapse !important;
        width: 100%;
    }
    
    th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 12px !important;
    }
    
    /* Divider */
    .divider-line {
        border: 1px solid #e0e0e0;
        margin: 20px 0;
    }
    
    /* Button Hover */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 12px 30px !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Select Box */
    .stSelectbox, .stNumberInput {
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# ส่วนหัว
# ═══════════════════════════════════════════════════════════════
st.markdown("""
    <div class="header-main">
        <h1>🛣️ เครื่องคำนวณ AASHTO 1993</h1>
        <p>วิธี Odemark สำหรับออกแบบผิวทางคอนกรีต (JPCP)</p>
    </div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📚 ฐานข้อมูลวัสดุ")
    
    material_db = {
        "คอนกรีตแอสฟัลต์ (AC)": 2500,
        "ชั้นฐานที่เสริมซีเมนต์ (CTB)": 1200,
        "หินผ่าปรุงแต่งด้วยซีเมนต์": 800,
        "ดินเสริมปูนขาว": 400,
        "มวลรวมทุบหรือสกัด (Granular)": 300,
        "ดินสกัดหรือมวลรวม": 150,
        "ดินแลตไรต์": 200
    }
    
    st.markdown("### 📊 ค่า E (Elastic Modulus)")
    for material, e_value in material_db.items():
        st.caption(f"**{material}**  \n{e_value} MPa")
    
    st.divider()
    
    st.markdown("### 💡 แนวคิดหลัก AASHTO 1993")
    st.info("""
    ✅ **วิธีถูกต้อง:**
    - เก็บค่า E จริงของวัสดุ
    - เก็บความหนา h จริง
    - **แปลงเป็น:** ความหนาเทียบเท่า
    
    ❌ **วิธีผิด:**
    - ลดค่า E ของวัสดุ
    
    **คำถาม:** ระบบนี้เทียบเท่า Reference Material หนาเท่าไร?
    """)

# ═══════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 ขั้นตอนที่ 1: ดินฐาน", 
    "🏗️ ขั้นตอนที่ 2: ความหนาเทียบเท่า",
    "🔧 ขั้นตอนที่ 3: k ที่มีประสิทธิผล",
    "📖 วิธีใช้ & ทฤษฎี"
])

# ═══════════════════════════════════════════════════════════════
# TAB 1: ดินฐาน
# ═══════════════════════════════════════════════════════════════
with tab1:
    st.markdown("## 🔹 คุณสมบัติดินฐาน (พื้นฐานอ้างอิง)")
    
    st.markdown("""
    <div class="concept-box">
    <b>📌 ขั้นตอนที่ 1:</b> กำหนดคุณสมบัติดินฐานจากการทดสอบ CBR
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        cbr_sg = st.number_input(
            "💧 CBR ของดินฐาน (%)",
            min_value=1.0,
            max_value=30.0,
            value=5.0,
            step=0.5,
            key="cbr_sg_main",
            help="ค่า California Bearing Ratio จากการทดสอบในห้องแล็บ"
        )
    
    # คำนวณค่า
    e_sg = 17.6 * (cbr_sg ** 0.64)
    mr_sg_psi = e_sg * 145.038
    k1 = mr_sg_psi / 19.4
    
    with col2:
        st.metric(
            label="🔹 E (โมดูลัส)",
            value=f"{e_sg:.1f} MPa",
            delta=f"{mr_sg_psi:.0f} psi"
        )
    
    with col3:
        st.metric(
            label="🔹 k₁ (ดินฐาน)",
            value=f"{k1:.1f} pci",
            delta="ไม่มีการสูญเสีย"
        )
    
    st.divider()
    
    st.markdown("### 📊 รายละเอียดการคำนวณ")
    
    col_calc1, col_calc2 = st.columns(2)
    
    with col_calc1:
        st.markdown("""
        **สูตร: E จาก CBR**
        ```
        E = 17.6 × CBR^0.64
        ```
        """)
        st.markdown(f"""
        ```
        E = 17.6 × {cbr_sg}^0.64
        E = {e_sg:.2f} MPa
        ```
        """)
    
    with col_calc2:
        st.markdown("""
        **สูตร: k จาก M_R**
        ```
        M_R (psi) = E (MPa) × 145.038
        k = M_R / 19.4
        ```
        """)
        st.markdown(f"""
        ```
        M_R = {e_sg:.2f} × 145.038
        M_R = {mr_sg_psi:.0f} psi
        k₁ = {mr_sg_psi:.0f} / 19.4
        k₁ = {k1:.1f} pci
        ```
        """)
    
    # สร้าง visualization
    st.markdown("### 📈 กราฟแสดงความสัมพันธ์ CBR - E")
    
    cbr_range = np.linspace(1, 20, 50)
    e_range = 17.6 * (cbr_range ** 0.64)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=cbr_range,
        y=e_range,
        mode='lines',
        name='E = 17.6 × CBR^0.64',
        line=dict(color='#667eea', width=3),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.2)'
    ))
    
    fig.add_scatter(
        x=[cbr_sg],
        y=[e_sg],
        mode='markers',
        marker=dict(size=15, color='#764ba2'),
        name=f'CBR = {cbr_sg}%'
    )
    
    fig.update_layout(
        title="ความสัมพันธ์ระหว่าง CBR และ Elastic Modulus",
        xaxis_title="CBR (%)",
        yaxis_title="E (MPa)",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.success(f"✅ ดินฐานของอาจารย์มี CBR = {cbr_sg}% → E = {e_sg:.1f} MPa → k₁ = {k1:.1f} pci")
    
    # เก็บค่าในหน่วยความจำ
    st.session_state.cbr_sg = cbr_sg
    st.session_state.e_sg = e_sg
    st.session_state.mr_sg_psi = mr_sg_psi
    st.session_state.k1 = k1

# ═══════════════════════════════════════════════════════════════
# TAB 2: ความหนาเทียบเท่า
# ═══════════════════════════════════════════════════════════════
with tab2:
    st.markdown("## 🔹 ความหนาเทียบเท่า (Equivalent Thickness)")
    
    st.markdown("""
    <div class="concept-box">
    <b>📌 ขั้นตอนที่ 2:</b> กำหนดชั้นทางจริง + เลือกวัสดุอ้างอิง
    <br><br>
    <b>⭐ ประเด็นสำคัญ:</b> เราไม่ลดค่า E ของชั้นใดเลย!
    <br>
    เราแปลง "ระบบหลายชั้น" เป็น "ความหนาเทียบเท่า" ของวัสดุอ้างอิง
    </div>
    """, unsafe_allow_html=True)
    
    # ดึงค่า E ของดินฐาน
    if 'e_sg' in st.session_state:
        e_sg_ref = st.session_state.e_sg
        cbr_sg_ref = st.session_state.cbr_sg
    else:
        cbr_sg_ref = 5
        e_sg_ref = 17.6 * (5 ** 0.64)
    
    st.divider()
    
    st.markdown("### 🔸 ขั้นตอนที่ 2ก: เลือกวัสดุอ้างอิง")
    
    material_db = {
        "คอนกรีตแอสฟัลต์ (AC)": 2500,
        "ชั้นฐานที่เสริมซีเมนต์ (CTB)": 1200,
        "หินผ่าปรุงแต่งด้วยซีเมนต์": 800,
        "ดินเสริมปูนขาว": 400,
        "มวลรวมทุบหรือสกัด (Granular) ✓ แนะนำ": 300,
        "ดินสกัดหรือมวลรวม": 150,
        "ดินแลตไรต์": 200
    }
    
    ref_material = st.selectbox(
        "🎯 เลือกวัสดุอ้างอิง (Reference Material)",
        list(material_db.keys()),
        index=4,
        help="นี่คือวัสดุที่เราจะเปรียบเทียบชั้นทางอื่นๆ"
    )
    
    e_ref = material_db[ref_material]
    
    col_ref1, col_ref2, col_ref3 = st.columns(3)
    with col_ref1:
        st.info(f"**วัสดุ:** {ref_material.split('✓')[0].strip()}")
    with col_ref2:
        st.info(f"**E_ref:** {e_ref} MPa")
    with col_ref3:
        st.info(f"**CBR ของดินฐาน:** {cbr_sg_ref}%")
    
    st.divider()
    
    st.markdown("### 🔸 ขั้นตอนที่ 2ข: กำหนดชั้นทางจริง")
    
    num_layers = st.selectbox(
        "📊 จำนวนชั้นทางเหนือดินฐาน",
        [1, 2, 3, 4, 5],
        index=2,
        key="num_layers_tab2"
    )
    
    layers = []
    
    layer_container = st.container()
    
    for i in range(num_layers):
        with st.expander(f"🟦 ชั้นที่ {i+1}", expanded=(i==0)):
            col_mat, col_h, col_e = st.columns([2, 1, 1])
            
            with col_mat:
                mat = st.selectbox(
                    f"วัสดุ",
                    list(material_db.keys()),
                    index=0 if i==0 else (1 if i==1 else 4),
                    key=f"mat_tab2_{i}",
                    label_visibility="collapsed"
                )
            
            with col_h:
                h = st.number_input(
                    f"หนา (cm)",
                    min_value=1.0,
                    value=10.0 if i < 2 else 15.0,
                    step=0.5,
                    key=f"h_tab2_{i}",
                    label_visibility="collapsed"
                )
            
            with col_e:
                e_default = material_db[mat]
                e = st.number_input(
                    f"E (MPa)",
                    min_value=10.0,
                    value=float(e_default),
                    step=10.0,
                    key=f"E_tab2_{i}",
                    label_visibility="collapsed"
                )
            
            st.caption(f"**ชั้นที่ {i+1}:** {h} cm • {mat.split('✓')[0].strip()} @ {e} MPa")
            
            layers.append({
                "Layer": i + 1,
                "Material": mat.split('✓')[0].strip(),
                "h_actual (cm)": h,
                "E_actual (MPa)": e
            })
    
    st.divider()
    
    # ปุ่มคำนวณ
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
    
    with col_btn1:
        calculate_heq = st.button(
            "🧮 คำนวณความหนาเทียบเท่า",
            use_container_width=True,
            key="calc_heq",
            type="primary"
        )
    
    # ผลลัพธ์
    if calculate_heq:
        st.session_state.calculate_heq = True
    
    if 'calculate_heq' in st.session_state and st.session_state.calculate_heq:
        st.markdown("---")
        st.markdown("## 📊 ผลลัพธ์: ความหนาเทียบเท่า")
        
        results = []
        total_h_actual = 0
        total_h_eq = 0
        
        for layer in layers:
            h = layer["h_actual (cm)"]
            e = layer["E_actual (MPa)"]
            
            # Odemark formula
            h_eq = h * ((e / e_ref) ** (1/3))
            
            total_h_actual += h
            total_h_eq += h_eq
            
            results.append({
                "ชั้น": layer["Layer"],
                "วัสดุ": layer["Material"],
                "h จริง (cm)": round(h, 2),
                "E จริง (MPa)": round(e, 0),
                "E/E_ref": round(e/e_ref, 3),
                "(E/E_ref)^(1/3)": round((e/e_ref)**(1/3), 3),
                "h_eq (cm)": round(h_eq, 2)
            })
        
        df_results = pd.DataFrame(results)
        
        st.markdown("### 📋 การคำนวณรายละเอียดของแต่ละชั้น")
        st.dataframe(df_results, use_container_width=True, hide_index=True)
        
        st.markdown("### 🎯 สรุปผลลัพธ์")
        
        summary_col1, summary_col2, summary_col3 = st.columns(3)
        
        with summary_col1:
            st.metric(
                label="💪 ความหนาจริงรวม",
                value=f"{total_h_actual:.1f} cm",
                delta=f"{total_h_actual/2.54:.2f} นิ้ว"
            )
        
        with summary_col2:
            st.metric(
                label="🎯 วัสดุอ้างอิง",
                value=f"E = {e_ref} MPa",
                delta=ref_material.split('✓')[0].strip()
            )
        
        with summary_col3:
            st.metric(
                label="📏 ความหนาเทียบเท่า",
                value=f"{total_h_eq:.1f} cm",
                delta=f"{total_h_eq/2.54:.2f} นิ้ว"
            )
        
        st.divider()
        
        # Visualization
        st.markdown("### 📈 กราฟเปรียบเทียบ")
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            fig_bar = go.Figure()
            
            fig_bar.add_trace(go.Bar(
                y=[r["วัสดุ"] for r in results],
                x=[r["h จริง (cm)"] for r in results],
                orientation='h',
                name='h จริง',
                marker=dict(color='#667eea')
            ))
            
            fig_bar.update_layout(
                title="ความหนาจริงของแต่ละชั้น",
                xaxis_title="ความหนา (cm)",
                yaxis_title="ชั้น",
                height=400,
                template='plotly_white'
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col_chart2:
            fig_eq = go.Figure()
            
            fig_eq.add_trace(go.Bar(
                y=[r["วัสดุ"] for r in results],
                x=[r["h_eq (cm)"] for r in results],
                orientation='h',
                name='h เทียบเท่า',
                marker=dict(color='#764ba2')
            ))
            
            fig_eq.update_layout(
                title="ความหนาเทียบเท่า (Granular)",
                xaxis_title="ความหนา (cm)",
                yaxis_title="ชั้น",
                height=400,
                template='plotly_white'
            )
            
            st.plotly_chart(fig_eq, use_container_width=True)
        
        st.markdown(f"""
        <div class="success-box">
        <h4>✅ การแปลความหมาย (แนวคิดที่ถูกต้อง):</h4>
        <p>ระบบชั้นทางของอาจารย์ที่มี <b>ความหนาจริง {total_h_actual:.1f} cm</b> 
        (ประกอบด้วยวัสดุหลายชนิดที่มี E ต่างกัน) 
        มีความแข็งแรงเทียบเท่ากับชั้นเดียวของ <b>{ref_material.split('✓')[0].strip()}</b> 
        ที่มี <b>ความหนา {total_h_eq:.1f} cm</b></p>
        
        <p><b>สิ่งที่ไม่ได้เกิดขึ้น:</b></p>
        <ul>
        <li>❌ ไม่ได้ลดค่า E ของ AC จาก 2500 MPa ลงมา</li>
        <li>❌ ไม่ได้เปลี่ยนความหนาจริงของชั้นใด</li>
        <li>✅ ทำการแปลง: "ระบบ 3 ชั้น" → "ความหนาเทียบเท่า Reference Material"</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.session_state.total_h_eq = total_h_eq
        st.session_state.layers_data = layers
        st.session_state.e_ref = e_ref
        st.session_state.ref_material_name = ref_material.split('✓')[0].strip()

# ═══════════════════════════════════════════════════════════════
# TAB 3: k ที่มีประสิทธิผล
# ═══════════════════════════════════════════════════════════════
with tab3:
    st.markdown("## 🔹 โมดูลัสของปฏิกิริยาดินฐานที่มีประสิทธิผล (k_eff)")
    
    st.markdown("""
    <div class="concept-box">
    <b>📌 ขั้นตอนที่ 3:</b> คำนวณค่า k ที่มีประสิทธิผล สำหรับใช้ในการออกแบบ
    <br>
    k_eff คำนึงถึงการรองรับจากชั้นรองพื้น
    </div>
    """, unsafe_allow_html=True)
    
    if 'k1' in st.session_state:
        k1_val = st.session_state.k1
        e_sg_val = st.session_state.e_sg
        cbr_sg_val = st.session_state.cbr_sg
    else:
        cbr_sg_val = st.number_input(
            "💧 CBR ของดินฐาน (%)",
            min_value=1.0,
            max_value=30.0,
            value=5.0,
            step=0.5,
            key="cbr_for_k"
        )
        e_sg_val = 17.6 * (cbr_sg_val ** 0.64)
        k1_val = (e_sg_val * 145.038) / 19.4
    
    col_k1a, col_k1b = st.columns(2)
    
    with col_k1a:
        st.metric(
            label="📊 k₁ (ดินฐานเพียงอย่างเดียว)",
            value=f"{k1_val:.1f} pci",
            delta=f"CBR = {cbr_sg_val}%, E = {e_sg_val:.1f} MPa"
        )
    
    with col_k1b:
        st.info("""
        **k₁** = ค่า k ของดินฐาน **ไม่มี** การรองรับจากชั้นรองพื้น
        """)
    
    st.divider()
    
    st.markdown("### 🔸 ขั้นตอนที่ 3ก: ตัวประกอบการสูญเสียการรองรับ (f_LS)")
    
    st.markdown("""
    **ตัวประกอบการสูญเสียการรองรับ (f_LS)** คำนึงถึง:
    - ความหนาและคุณภาพของชั้นรองพื้น
    - เงื่อนไขการระบายน้ำ
    - การพังทลายหรือสูบน้ำ
    
    **สูตร:**
    ```
    k_eff = k₁ / f_LS
    ```
    """)
    
    ls_options = {
        "ไม่มีการสูญเสีย (รองรับดีเยี่ยม)": 1.0,
        "LS = 1 (Granular ดี + ระบายน้ำดี)": 0.9,
        "LS = 2 (ชั้นรองพื้นปานกลาง หรือระบายน้ำปานกลาง)": 0.8,
        "LS = 3 (ชั้นรองพื้นไม่ดี หรือระบายน้ำไม่ดี)": 0.6
    }
    
    ls_description = st.selectbox(
        "🎯 เลือกสภาวะการสูญเสีย",
        list(ls_options.keys()),
        help="เลือกตามประเภทชั้นรองพื้นและการระบายน้ำ"
    )
    
    f_ls = ls_options[ls_description]
    
    col_fls1, col_fls2 = st.columns(2)
    
    with col_fls1:
        st.metric(
            label="🔹 ตัวประกอบ f_LS",
            value=f"{f_ls}",
            delta=ls_description.split("(")[0]
        )
    
    with col_fls2:
        st.info(f"""
        **สภาวะที่เลือก:**
        
        {ls_description}
        """)
    
    # Custom input
    st.markdown("---")
    st.markdown("**หรือปรับปรุงค่าด้วยตัวเอง:**")
    f_ls_custom = st.slider(
        "🎚️ ค่า f_LS แบบกำหนดเอง",
        min_value=0.5,
        max_value=2.0,
        value=f_ls,
        step=0.05,
        help="0.5-1.0 = ดี, 1.0-1.5 = ปานกลาง, >1.5 = ไม่ดี"
    )
    
    f_ls = f_ls_custom
    
    st.divider()
    
    st.markdown("### 🔸 ขั้นตอนที่ 3ข: คำนวณ k_eff")
    
    if st.button("🧮 คำนวณค่า k ที่มีประสิทธิผล", use_container_width=True, key="calc_keff", type="primary"):
        st.session_state.calculate_keff = True
    
    if 'calculate_keff' in st.session_state and st.session_state.calculate_keff:
        k_eff = k1_val / f_ls
        
        st.markdown("---")
        st.markdown("## 📊 ผลลัพธ์: ค่า k ที่มีประสิทธิผล")
        
        calc_col1, calc_col2, calc_col3 = st.columns(3)
        
        with calc_col1:
            st.markdown(f"""
            <div class="metric-card">
            <h4 style="margin: 0;">k₁ (พื้นฐาน)</h4>
            <h2 style="margin: 10px 0 0 0; color: #667eea;"><b>{k1_val:.1f} pci</b></h2>
            <small>ดินฐานเพียงอย่างเดียว</small>
            </div>
            """, unsafe_allow_html=True)
        
        with calc_col2:
            st.markdown(f"""
            <div class="metric-card">
            <h4 style="margin: 0;">f_LS (การสูญเสีย)</h4>
            <h2 style="margin: 10px 0 0 0; color: #ffc107;"><b>{f_ls:.2f}</b></h2>
            <small>ตัวประกอบการสูญเสีย</small>
            </div>
            """, unsafe_allow_html=True)
        
        with calc_col3:
            st.markdown(f"""
            <div class="metric-card">
            <h4 style="margin: 0;">k_eff (ออกแบบ)</h4>
            <h2 style="margin: 10px 0 0 0; color: #28a745;"><b>{k_eff:.1f} pci</b></h2>
            <small>ใช้ในการออกแบบ JPCP</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown(f"""
        <div class="info-box">
        <h4>📝 รายละเอียดการคำนวณ:</h4>
        <p style="font-size: 1.1em;">
        <b>k_eff = k₁ / f_LS</b><br>
        k_eff = {k1_val:.1f} / {f_ls:.2f} = <b style="color: #28a745;">{k_eff:.1f} pci</b>
        </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### 📋 สรุปผลออกแบบ")
        
        summary_table = {
            "รายการ": [
                "CBR ของดินฐาน",
                "โมดูลัส E ของดินฐาน",
                "ค่า M_R ของดินฐาน",
                "k₁ (ดินฐานเพียงอย่างเดียว)",
                "ตัวประกอบการสูญเสีย (f_LS)",
                "k_eff (ใช้ในการออกแบบ JPCP)"
            ],
            "ค่า": [
                f"{cbr_sg_val} %",
                f"{e_sg_val:.1f} MPa",
                f"{e_sg_val * 145.038:.0f} psi",
                f"{k1_val:.1f} pci",
                f"{f_ls}",
                f"{k_eff:.1f} pci"
            ]
        }
        
        df_summary = pd.DataFrame(summary_table)
        st.dataframe(df_summary, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Visualization
        st.markdown("### 📈 การเปรียบเทียบค่า k")
        
        fig_k = go.Figure()
        
        fig_k.add_trace(go.Bar(
            x=['k₁ (ดินฐาน)', 'k_eff (มีชั้นรองพื้น)'],
            y=[k1_val, k_eff],
            marker=dict(color=['#667eea', '#28a745']),
            text=[f'{k1_val:.1f}', f'{k_eff:.1f}'],
            textposition='auto'
        ))
        
        fig_k.update_layout(
            title="การเปรียบเทียบค่า k ก่อนและหลังรองรับ",
            yaxis_title="ค่า k (pci)",
            height=400,
            template='plotly_white',
            showlegend=False
        )
        
        st.plotly_chart(fig_k, use_container_width=True)
        
        st.markdown(f"""
        <div class="success-box">
        <h4>✅ ค่า k ที่ใช้ในการออกแบบ JPCP:</h4>
        <h2 style="color: #28a745; margin: 10px 0;"><b>k_eff = {k_eff:.1f} pci</b></h2>
        <p>ค่า k นี้คำนึงถึง:</p>
        <ul>
        <li>✓ คุณสมบัติของดินฐาน (CBR = {cbr_sg_val}%)</li>
        <li>✓ การรองรับจากชั้นรองพื้น (f_LS = {f_ls})</li>
        </ul>
        <p><b>ใช้ค่านี้ในสมการออกแบบ AASHTO 1993 เพื่อหาความหนาผิวทางคอนกรีต</b></p>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TAB 4: วิธีใช้ & ทฤษฎี
# ═══════════════════════════════════════════════════════════════
with tab4:
    st.markdown("## 📚 คู่มือใช้งานและทฤษฎี")
    
    st.markdown("""
    ### 🎯 แนวคิดหลัก (THE KEY POINT)
    
    #### ❌ ความเข้าใจที่ผิด:
    - "AASHTO 1993 ต้องการให้เราลดค่า E"
    - "เราควรลดค่า E ของ AC จาก 2500 ลงมาเป็นค่าที่น้อยกว่า"
    - "เราเปลี่ยนแปลงคุณสมบัติของวัสดุเพื่อให้เข้ากับการออกแบบ"
    
    #### ✅ ความเข้าใจที่ถูกต้อง:
    - **AASHTO 1993 ไม่ได้ใช้การวิเคราะห์ elastic layer-by-layer**
    - **AASHTO 1993 ถาม:** "ระบบหลายชั้นนี้ เทียบเท่า reference material หนาเท่าไร?"
    - **เราแปลง** ระบบหลายชั้น → ความหนาเทียบเท่า (equivalent thickness)
    - **เราไม่เปลี่ยน** E หรือ h ของวัสดุจริงเลย
    """)
    
    st.divider()
    
    st.markdown("""
    ### 📐 สูตรวิธี Odemark (ถูกต้อง)
    
    #### สูตรคณิตศาสตร์:
    $$h_e = \\sum_{i=1}^{n} h_i \\sqrt[3]{\\frac{E_i}{E_{ref}}}$$
    
    #### ตัวแปร:
    - **h_i** = ความหนาจริงของชั้น i (เก็บเป็นค่าจริง!)
    - **E_i** = โมดูลัส elastic จริงของชั้น i (เก็บเป็นค่าจริง!)
    - **E_ref** = โมดูลัสของวัสดุอ้างอิง
    - **h_e** = ความหนาเทียบเท่า (สิ่งที่เราคำนวณ)
    
    #### ความหมาย:
    ✅ เราเก็บค่า E_i จริงไว้  
    ✅ เราเก็บค่า h_i จริงไว้  
    ✅ เราคำนวณ h_e = "reference material ควรหนาเท่าไร?"  
    
    ❌ เราไม่ลดค่า E_i  
    ❌ เราไม่เปลี่ยน h_i  
    """)
    
    st.divider()
    
    st.markdown("### 📊 ตัวอย่างการคำนวณ")
    
    example_data = {
        "ชั้น": ["AC", "CTB", "Granular Subbase"],
        "h จริง (cm)": [5, 20, 15],
        "E จริง (MPa)": [2500, 1200, 300],
        "E_ref (MPa)": [300, 300, 300],
        "E/E_ref": [8.33, 4.00, 1.00],
        "(E/E_ref)^(1/3)": [2.03, 1.59, 1.00],
        "h_eq (cm)": [10.2, 31.8, 15.0]
    }
    
    df_example = pd.DataFrame(example_data)
    st.dataframe(df_example, use_container_width=True, hide_index=True)
    
    st.markdown(f"""
    **รวม h จริง = 40 cm**
    
    **รวม h_eq = 57.0 cm** (ความหนาเทียบเท่า Granular)
    
    #### การแปลความหมาย:
    ระบบ 40 cm (AC + CTB + Granular) ของอาจารย์ 
    มีความแข็งแรงเทียบเท่ากับ **Granular ที่หนา 57 cm**
    
    ค่า h_eq นี้จะนำไปใช้เพื่อหาค่า k โดยใช้ตารางหรือกราฟ AASHTO
    """)
    
    st.divider()
    
    st.markdown("""
    ### 🔄 ขั้นตอนออกแบบแบบเต็มรูปแบบ (AASHTO 1993)
    
    1. **กำหนด Subgrade CBR** → คำนวณ E_SG
    2. **คำนวณ k₁** จาก E_SG (ดินฐาน ไม่มีการรองรับ)
    3. **กำหนดชั้นทางจริง** (h จริง และ E จริง)
    4. **เลือกวัสดุอ้างอิง** (E_ref)
    5. **คำนวณ h_eq** ด้วยสูตร Odemark
    6. **กำหนดตัวประกอบการสูญเสีย** (f_LS)
    7. **คำนวณ k_eff** = k₁ / f_LS
    8. **ใช้ k_eff ในสมการออกแบบ AASHTO** → หาความหนาผิวทางคอนกรีต
    
    ✅ **เครื่องคำนวณนี้จัดการขั้นตอน 1-7 ให้ถูกต้อง**
    """)
    
    st.divider()
    
    st.markdown("""
    ### 🤔 ทำไม AASHTO 1993 ไม่ใช้ Multilayer Elastic Theory?
    
    #### เหตุผล:
    1. **ความเรียบง่ายในทางปฏิบัติ** - ง่ายต่อการใช้ในปี 1993
    2. **การตรวจสอบจากประวัติ** - วิธีนี้อ้างอิงจากข้อมูลเส้นทางหลายสิบปี
    3. **ความระมัดระวัง** - ไม่ต้องคำนวณ stress-strain ที่ซับซ้อน
    4. **ใช้ค่าเดียว (k)** - ง่ายต่อการใช้ในสมการออกแบบ
    
    #### หมายเหตุ:
    **วิธีใหม่กว่า** (MEPDG/AASHTOWare) ใช้ mechanistic theory
    
    แต่ **AASHTO 1993 ยังคงใช้กันอย่างแพร่หลาย** ในหลายประเทศ (รวมถึงไทย)
    """)
    
    st.divider()
    
    st.markdown("### 📋 ตารางอ้างอิง: ค่า E ของวัสดุ")
    
    ref_data = {
        "วัสดุ": [
            "คอนกรีตแอสฟัลต์ (AC)",
            "ชั้นฐานที่เสริมซีเมนต์ (CTB)",
            "หินผ่าปรุงแต่งด้วยซีเมนต์",
            "ดินเสริมปูนขาว",
            "มวลรวมทุบหรือสกัด (Granular)",
            "ดินสกัดหรือมวลรวม",
            "ดินแลตไรต์",
            "ดินฐาน (CBR 5%)"
        ],
        "E (MPa)": [2500, 1200, 800, 400, 300, 150, 200, 55],
        "หมายเหตุ": [
            "มีความแข็งแรงมากที่สุด",
            "ถือว่าดี สำหรับชั้นฐาน",
            "แทนที่ CTB ได้",
            "ไม่ใช้บ่อย",
            "แนะนำเป็น Reference Material",
            "ต่ำ เหมาะสำหรับการเปรียบเทียบ",
            "ใช้ในอ.ต.ว. (ประเทศเมืองร้อน)",
            "ตัวอย่าง: CBR 5%"
        ]
    }
    
    df_ref = pd.DataFrame(ref_data)
    st.dataframe(df_ref, use_container_width=True, hide_index=True)
    
    st.divider()
    
    st.markdown("""
    ### 📚 แหล่งอ้างอิง:
    - **AASHTO (1993)** - Guide for Design of Pavement Structures
    - **Odemark, N. (1974)** - Investigations of the Structural Behaviour of Asphalt Pavements
    - **NCHRP (2004)** - Mechanistic–Empirical Design of New and Rehabilitated Pavement Structures
    - **วิทยาลัยวิศวกรรมศาสตร์ มหาวิทยาลัยการวิทยาศาสตร์เทคโนโลยี** - มาตรฐาน JPCP ของประเทศไทย
    """)

# ═══════════════════════════════════════════════════════════════
# Footer
# ═══════════════════════════════════════════════════════════════
st.divider()

st.markdown("""
    <div style="text-align: center; color: #666; font-size: 13px; margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
        <p><b>🛣️ เครื่องคำนวณ AASHTO 1993 (วิธี Odemark)</b></p>
        <p>สำหรับการออกแบบผิวทางคอนกรีต (JPCP) ตามมาตรฐานอเมริกัน</p>
        <p style="font-style: italic; margin: 10px 0;">
        "เราแปลงระบบหลายชั้น เป็นความหนาเทียบเท่าของวัสดุอ้างอิง<br>
        ไม่ใช่ลดค่า Elastic Modulus ของวัสดุจริง"
        </p>
        <p style="color: #999; font-size: 12px;">
        อัปเดต: {}  |  เวอร์ชัน 3.0 (ภาษาไทย + UI ที่ปรับปรุง)
        </p>
    </div>
""".format(datetime.now().strftime('%d/%m/%Y')), unsafe_allow_html=True)

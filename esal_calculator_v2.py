"""
ESAL Calculator - AASHTO 1993
คำนวณปริมาณเพลาเดี่ยวมาตรฐานเทียบเท่า (Equivalent Single Axle Load)
พัฒนาสำหรับ: ภาควิชาครุศาสตร์โยธา มจพ.
"""

import streamlit as st
import pandas as pd
import math

# ============================================================
# ค่าคงที่
# ============================================================
TON_TO_KIP = 2.2046
AXLE_TYPES = {'Single': 1, 'Tandem': 2, 'Tridem': 3}

# ค่าเริ่มต้นรถบรรทุก 6 ชนิดตามกรมทางหลวง
DEFAULT_TRUCKS = {
    'MB': {'desc': 'Medium Bus', 'front': (3.1, 'Single'), 'rear': (12.2, 'Tandem')},
    'HB': {'desc': 'Heavy Bus', 'front': (4.0, 'Single'), 'rear': (14.3, 'Tandem')},
    'MT': {'desc': 'Medium Truck', 'front': (4.0, 'Single'), 'rear': (11.0, 'Single')},
    'HT': {'desc': 'Heavy Truck', 'front': (5.0, 'Single'), 'rear': (20.0, 'Tandem')},
    'STR': {'desc': 'Semi-Trailer', 'front': (5.0, 'Single'), 'rear': (20.0, 'Tandem'), 'trailer_rear': (20.0, 'Tandem')},
    'TR': {'desc': 'Full Trailer', 'front': (5.0, 'Single'), 'rear': (17.75, 'Tandem'), 'trailer_front': (10.0, 'Single'), 'trailer_rear': (17.75, 'Tandem')}
}

# ============================================================
# ฟังก์ชันคำนวณ LEF ตาม AASHTO 1993
# ============================================================
def calc_lef_flexible(Lx_kip, L2, pt, SN):
    """คำนวณ LEF สำหรับ Flexible Pavement (AASHTO Eq. 2-1)"""
    if Lx_kip <= 0:
        return 0
    Gt = math.log10((4.2 - pt) / (4.2 - 1.5))
    beta_x = 0.40 + (0.081 * ((Lx_kip + L2) ** 3.23)) / (((SN + 1) ** 5.19) * (L2 ** 3.23))
    beta_18 = 0.40 + (0.081 * ((18 + 1) ** 3.23)) / (((SN + 1) ** 5.19) * (1 ** 3.23))
    log_ratio = 4.79 * math.log10(19) - 4.79 * math.log10(Lx_kip + L2) + Gt / beta_x - Gt / beta_18
    return 1 / (10 ** log_ratio)

def calc_lef_rigid(Lx_kip, L2, pt, D):
    """คำนวณ LEF สำหรับ Rigid Pavement (AASHTO Eq. 2-5)"""
    if Lx_kip <= 0:
        return 0
    Gt = math.log10((4.5 - pt) / (4.5 - 1.5))
    beta_x = 1.0 + (3.63 * ((Lx_kip + L2) ** 5.20)) / (((D + 1) ** 8.46) * (L2 ** 3.52))
    beta_18 = 1.0 + (3.63 * ((18 + 1) ** 5.20)) / (((D + 1) ** 8.46) * (1 ** 3.52))
    log_ratio = 4.62 * math.log10(19) - 4.62 * math.log10(Lx_kip + L2) + Gt / beta_x - Gt / beta_18
    return 1 / (10 ** log_ratio)

def calc_truck_factor(axles, pavement_type, pt, param):
    """คำนวณ Truck Factor จากข้อมูลเพลาทั้งหมด"""
    total_lef = 0
    for load_ton, axle_type in axles:
        if load_ton > 0:
            Lx_kip = load_ton * TON_TO_KIP
            L2 = AXLE_TYPES[axle_type]
            if pavement_type == 'rigid':
                total_lef += calc_lef_rigid(Lx_kip, L2, pt, param)
            else:
                total_lef += calc_lef_flexible(Lx_kip, L2, pt, param)
    return total_lef

# ============================================================
# ฟังก์ชันช่วย
# ============================================================
def create_template():
    """สร้าง Template"""
    base = {'MB': 120, 'HB': 60, 'MT': 250, 'HT': 180, 'STR': 120, 'TR': 100}
    data = {'Year': list(range(1, 21))}
    for code, val in base.items():
        data[code] = [int(val * (1.045 ** i)) for i in range(20)]
    return pd.DataFrame(data)

def to_csv(df):
    """แปลง DataFrame เป็น CSV"""
    return df.to_csv(index=False).encode('utf-8-sig')

def calculate_esal(traffic_df, truck_factors, lane_factor, direction_factor):
    """คำนวณ ESAL"""
    results = []
    total_esal = 0
    
    for idx, row in traffic_df.iterrows():
        year = row.get('Year', idx + 1)
        year_data = {'ปีที่': year}
        year_esal = 0
        
        for code, tf in truck_factors.items():
            if code in traffic_df.columns:
                aadt = row[code]
                esal = aadt * tf * lane_factor * direction_factor * 365
                year_data[code] = f"{esal:,.0f}"
                year_esal += esal
        
        year_data['ESAL รวม'] = f"{year_esal:,.0f}"
        total_esal += year_esal
        results.append(year_data)
    
    return pd.DataFrame(results), total_esal

# ============================================================
# Streamlit App
# ============================================================
def main():
    st.set_page_config(page_title="ESAL Calculator", page_icon="🛣️", layout="wide")
    
    st.markdown("""
    <style>
    .main-title {font-size: 2.2rem; font-weight: bold; color: #1E3A5F; text-align: center; margin-bottom: 1.5rem;}
    .metric-box {background: linear-gradient(135deg, #1E3A5F, #4A6FA5); padding: 1rem; border-radius: 8px; color: white; text-align: center;}
    .metric-value {font-size: 1.8rem; font-weight: bold;}
    .metric-label {font-size: 0.85rem; opacity: 0.9;}
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="main-title">🛣️ ESAL Calculator - AASHTO 1993</p>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'trucks' not in st.session_state:
        st.session_state.trucks = {k: v.copy() for k, v in DEFAULT_TRUCKS.items()}
    
    # Sidebar - Parameters
    with st.sidebar:
        st.header("⚙️ พารามิเตอร์")
        
        pavement_type = st.selectbox("ประเภทผิวทาง", ['rigid', 'flexible'],
            format_func=lambda x: '🧱 Rigid (คอนกรีต)' if x == 'rigid' else '🛤️ Flexible (ลาดยาง)')
        
        pt = st.selectbox("Terminal Serviceability (pt)", [2.5, 2.0])
        
        if pavement_type == 'rigid':
            param = st.selectbox("ความหนา D (นิ้ว)", [10, 11, 12, 13, 14])
            param_label = f"D={param}\""
        else:
            param = st.selectbox("Structural Number (SN)", [4, 5, 6, 7])
            param_label = f"SN={param}"
        
        st.divider()
        lane_factor = st.slider("Lane Factor", 0.1, 1.0, 0.5, 0.05)
        direction_factor = st.slider("Direction Factor", 0.5, 1.0, 1.0, 0.1)
        
        st.divider()
        st.download_button("📄 ดาวน์โหลด Template (CSV)", to_csv(create_template()),
            "traffic_template.csv", "text/csv", use_container_width=True)
    
    # Main Tabs
    tab1, tab2, tab3 = st.tabs(["📊 คำนวณ ESAL", "🚛 ตั้งค่าน้ำหนักเพลา", "📘 คู่มือ"])
    
    # ============================================================
    # Tab 2: ตั้งค่าน้ำหนักเพลา
    # ============================================================
    with tab2:
        st.subheader("🚛 ตั้งค่าน้ำหนักลงเพลาและชนิดเพลา")
        
        col1, col2 = st.columns(2)
        
        # รถ 4 ประเภทแรก (มีแค่เพลาหน้า+หลัง)
        with col1:
            for code in ['MB', 'HB', 'MT', 'HT']:
                with st.expander(f"**{code}** - {DEFAULT_TRUCKS[code]['desc']}", expanded=False):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write("**เพลาหน้า**")
                        front_load = st.number_input(f"น้ำหนัก (ตัน)##{code}_f", 0.0, 50.0, 
                            st.session_state.trucks[code]['front'][0], 0.1, key=f"{code}_front_load")
                        front_type = st.selectbox(f"ชนิดเพลา##{code}_f", list(AXLE_TYPES.keys()),
                            index=list(AXLE_TYPES.keys()).index(st.session_state.trucks[code]['front'][1]), key=f"{code}_front_type")
                    with c2:
                        st.write("**เพลาหลัง**")
                        rear_load = st.number_input(f"น้ำหนัก (ตัน)##{code}_r", 0.0, 50.0,
                            st.session_state.trucks[code]['rear'][0], 0.1, key=f"{code}_rear_load")
                        rear_type = st.selectbox(f"ชนิดเพลา##{code}_r", list(AXLE_TYPES.keys()),
                            index=list(AXLE_TYPES.keys()).index(st.session_state.trucks[code]['rear'][1]), key=f"{code}_rear_type")
                    
                    st.session_state.trucks[code]['front'] = (front_load, front_type)
                    st.session_state.trucks[code]['rear'] = (rear_load, rear_type)
        
        # STR และ TR (มีเพลาพ่วง)
        with col2:
            # STR - มีเพลาพ่วงหลัง
            with st.expander(f"**STR** - {DEFAULT_TRUCKS['STR']['desc']}", expanded=False):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.write("**เพลาหน้า**")
                    str_f_load = st.number_input("น้ำหนัก (ตัน)##STR_f", 0.0, 50.0,
                        st.session_state.trucks['STR']['front'][0], 0.1, key="STR_front_load")
                    str_f_type = st.selectbox("ชนิด##STR_f", list(AXLE_TYPES.keys()),
                        index=list(AXLE_TYPES.keys()).index(st.session_state.trucks['STR']['front'][1]), key="STR_front_type")
                with c2:
                    st.write("**เพลาหลัง**")
                    str_r_load = st.number_input("น้ำหนัก (ตัน)##STR_r", 0.0, 50.0,
                        st.session_state.trucks['STR']['rear'][0], 0.1, key="STR_rear_load")
                    str_r_type = st.selectbox("ชนิด##STR_r", list(AXLE_TYPES.keys()),
                        index=list(AXLE_TYPES.keys()).index(st.session_state.trucks['STR']['rear'][1]), key="STR_rear_type")
                with c3:
                    st.write("**เพลาพ่วงหลัง**")
                    str_tr_load = st.number_input("น้ำหนัก (ตัน)##STR_tr", 0.0, 50.0,
                        st.session_state.trucks['STR']['trailer_rear'][0], 0.1, key="STR_trailer_rear_load")
                    str_tr_type = st.selectbox("ชนิด##STR_tr", list(AXLE_TYPES.keys()),
                        index=list(AXLE_TYPES.keys()).index(st.session_state.trucks['STR']['trailer_rear'][1]), key="STR_trailer_rear_type")
                
                st.session_state.trucks['STR'] = {
                    'desc': 'Semi-Trailer',
                    'front': (str_f_load, str_f_type),
                    'rear': (str_r_load, str_r_type),
                    'trailer_rear': (str_tr_load, str_tr_type)
                }
            
            # TR - มีเพลาพ่วงหน้าและหลัง
            with st.expander(f"**TR** - {DEFAULT_TRUCKS['TR']['desc']}", expanded=False):
                c1, c2 = st.columns(2)
                with c1:
                    st.write("**เพลาหน้า**")
                    tr_f_load = st.number_input("น้ำหนัก (ตัน)##TR_f", 0.0, 50.0,
                        st.session_state.trucks['TR']['front'][0], 0.1, key="TR_front_load")
                    tr_f_type = st.selectbox("ชนิด##TR_f", list(AXLE_TYPES.keys()),
                        index=list(AXLE_TYPES.keys()).index(st.session_state.trucks['TR']['front'][1]), key="TR_front_type")
                    
                    st.write("**เพลาหลัง**")
                    tr_r_load = st.number_input("น้ำหนัก (ตัน)##TR_r", 0.0, 50.0,
                        st.session_state.trucks['TR']['rear'][0], 0.1, key="TR_rear_load")
                    tr_r_type = st.selectbox("ชนิด##TR_r", list(AXLE_TYPES.keys()),
                        index=list(AXLE_TYPES.keys()).index(st.session_state.trucks['TR']['rear'][1]), key="TR_rear_type")
                with c2:
                    st.write("**เพลาพ่วงหน้า**")
                    tr_tf_load = st.number_input("น้ำหนัก (ตัน)##TR_tf", 0.0, 50.0,
                        st.session_state.trucks['TR']['trailer_front'][0], 0.1, key="TR_trailer_front_load")
                    tr_tf_type = st.selectbox("ชนิด##TR_tf", list(AXLE_TYPES.keys()),
                        index=list(AXLE_TYPES.keys()).index(st.session_state.trucks['TR']['trailer_front'][1]), key="TR_trailer_front_type")
                    
                    st.write("**เพลาพ่วงหลัง**")
                    tr_tr_load = st.number_input("น้ำหนัก (ตัน)##TR_tr", 0.0, 50.0,
                        st.session_state.trucks['TR']['trailer_rear'][0], 0.1, key="TR_trailer_rear_load")
                    tr_tr_type = st.selectbox("ชนิด##TR_tr", list(AXLE_TYPES.keys()),
                        index=list(AXLE_TYPES.keys()).index(st.session_state.trucks['TR']['trailer_rear'][1]), key="TR_trailer_rear_type")
                
                st.session_state.trucks['TR'] = {
                    'desc': 'Full Trailer',
                    'front': (tr_f_load, tr_f_type),
                    'rear': (tr_r_load, tr_r_type),
                    'trailer_front': (tr_tf_load, tr_tf_type),
                    'trailer_rear': (tr_tr_load, tr_tr_type)
                }
        
        st.divider()
        
        # แสดง Truck Factor ที่คำนวณได้
        st.subheader(f"📊 Truck Factor ({param_label}, pt={pt})")
        
        tf_data = []
        for code, truck in st.session_state.trucks.items():
            axles = [(v[0], v[1]) for k, v in truck.items() if k != 'desc' and isinstance(v, tuple)]
            tf = calc_truck_factor(axles, pavement_type, pt, param)
            axle_info = " + ".join([f"{v[0]}t({v[1]})" for k, v in truck.items() if k != 'desc' and isinstance(v, tuple)])
            tf_data.append({'รหัส': code, 'ประเภท': truck['desc'], 'เพลา': axle_info, 'Truck Factor': f"{tf:.4f}"})
        
        st.dataframe(pd.DataFrame(tf_data), use_container_width=True, hide_index=True)
        
        if st.button("🔄 รีเซ็ตเป็นค่าเริ่มต้น", use_container_width=True):
            st.session_state.trucks = {k: v.copy() for k, v in DEFAULT_TRUCKS.items()}
            st.rerun()
    
    # ============================================================
    # Tab 1: คำนวณ ESAL
    # ============================================================
    with tab1:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("📤 อัพโหลดข้อมูล")
            
            uploaded_file = st.file_uploader("เลือกไฟล์ CSV", type=['csv'])
            
            if 'use_sample' not in st.session_state:
                st.session_state.use_sample = False
            
            if uploaded_file:
                try:
                    traffic_df = pd.read_csv(uploaded_file)
                    st.success("✅ อัพโหลดสำเร็จ!")
                    st.session_state.use_sample = False
                except Exception as e:
                    st.error(f"❌ {e}")
                    traffic_df = None
            else:
                if st.button("🔄 ใช้ข้อมูลตัวอย่าง", use_container_width=True):
                    st.session_state.use_sample = True
                traffic_df = create_template() if st.session_state.use_sample else None
            
            if traffic_df is not None:
                st.dataframe(traffic_df, use_container_width=True, height=350)
        
        with col2:
            st.subheader("📈 ผลการคำนวณ")
            
            if traffic_df is not None:
                # คำนวณ Truck Factor
                truck_factors = {}
                for code, truck in st.session_state.trucks.items():
                    axles = [(v[0], v[1]) for k, v in truck.items() if k != 'desc' and isinstance(v, tuple)]
                    truck_factors[code] = calc_truck_factor(axles, pavement_type, pt, param)
                
                # คำนวณ ESAL
                results_df, total_esal = calculate_esal(traffic_df, truck_factors, lane_factor, direction_factor)
                
                # Metrics
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f'<div class="metric-box"><div class="metric-value">{total_esal:,.0f}</div><div class="metric-label">ESAL รวม</div></div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="metric-box"><div class="metric-value">{len(traffic_df)} ปี</div><div class="metric-label">ระยะเวลา</div></div>', unsafe_allow_html=True)
                with c3:
                    st.markdown(f'<div class="metric-box"><div class="metric-value">{param_label}</div><div class="metric-label">พารามิเตอร์</div></div>', unsafe_allow_html=True)
                
                st.divider()
                
                # Truck Factors
                st.write("**🚛 Truck Factor:**")
                tf_display = pd.DataFrame([{'รหัส': k, 'TF': f"{v:.4f}"} for k, v in truck_factors.items()])
                st.dataframe(tf_display.T, use_container_width=True)
                
                st.divider()
                
                # Results
                st.write("**📊 ESAL รายปี:**")
                st.dataframe(results_df, use_container_width=True, height=400)
                
                # Download CSV
                st.download_button("📥 ดาวน์โหลดผลลัพธ์ (CSV)", to_csv(results_df),
                    f"ESAL_{pavement_type}_{param}.csv", "text/csv", use_container_width=True)
            else:
                st.info("⬅️ กรุณาอัพโหลดข้อมูลหรือใช้ข้อมูลตัวอย่าง")
    
    # ============================================================
    # Tab 3: คู่มือ
    # ============================================================
    with tab3:
        st.subheader("📘 คู่มือการใช้งาน")
        st.markdown("""
        ### วิธีใช้งาน
        1. **ตั้งค่าน้ำหนักเพลา** (Tab 🚛) - กำหนดน้ำหนักและชนิดเพลาสำหรับรถแต่ละประเภท
        2. **ตั้งค่าพารามิเตอร์** (Sidebar) - เลือก Rigid/Flexible, pt, D/SN
        3. **อัพโหลดข้อมูล** (Tab 📊) - อัพโหลด Excel/CSV ปริมาณจราจรรายปี
        4. **ดาวน์โหลดผลลัพธ์** - บันทึกเป็นไฟล์ CSV
        
        ### รูปแบบไฟล์
        | Year | MB | HB | MT | HT | STR | TR |
        |------|----|----|----|----|-----|-----|
        | 1 | 120 | 60 | 250 | 180 | 120 | 100 |
        | 2 | ... | ... | ... | ... | ... | ... |
        
        ### สูตร ESAL
        """)
        st.latex(r'ESAL = \sum_{i=1}^{n} \sum_{j=1}^{6} (ADT_{ij} \times TF_j \times LF \times DF \times 365)')
        st.markdown("**อ้างอิง:** AASHTO Guide for Design of Pavement Structures (1993)")
    
    st.divider()
    st.caption("พัฒนาสำหรับภาควิชาครุศาสตร์โยธา มจพ. | ESAL Calculator v2.0")

if __name__ == "__main__":
    main()

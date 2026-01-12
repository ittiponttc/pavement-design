import streamlit as st
import numpy as np
import math
import pandas as pd


def bisection_method(func, a, b, tol=1e-6, max_iter=100):
    """
    Bisection Method สำหรับหาค่า root ของฟังก์ชัน
    
    Parameters:
    - func: ฟังก์ชันที่ต้องการหา root
    - a, b: ช่วงที่ค้นหา
    - tol: ความคลาดเคลื่อนที่ยอมรับได้
    - max_iter: จำนวนรอบสูงสุด
    
    Returns:
    - root: ค่า x ที่ทำให้ func(x) ≈ 0
    """
    fa = func(a)
    fb = func(b)
    
    if fa * fb > 0:
        return None
    
    for _ in range(max_iter):
        c = (a + b) / 2
        fc = func(c)
        
        if abs(fc) < tol or (b - a) / 2 < tol:
            return c
        
        if fa * fc < 0:
            b = c
            fb = fc
        else:
            a = c
            fa = fc
    
    return (a + b) / 2


def calculate_MR_from_CBR(CBR):
    """
    คำนวณ Resilient Modulus (MR) จากค่า CBR
    สูตร: MR (psi) = 1500 × CBR (สำหรับ CBR ≤ 10)
           MR (psi) = 3000 × CBR^0.65 (สำหรับ CBR > 10)
    
    Parameters:
    - CBR: California Bearing Ratio (%)
    
    Returns:
    - MR: Resilient Modulus (psi)
    """
    if CBR <= 10:
        return 1500 * CBR
    else:
        return 3000 * (CBR ** 0.65)


def calculate_log_W18_flexible(SN, params):
    """
    คำนวณ log₁₀(W₁₈) ตามสมการ AASHTO 1993 สำหรับ Flexible Pavement
    
    สมการ:
    log W₁₈ = ZR×S₀ + 9.36×log(SN+1) - 0.20 
            + log[ΔPSI/(4.2-1.5)] / [0.40 + 1094/(SN+1)^5.19]
            + 2.32×log(MR) - 8.07
    
    Parameters:
    - SN: Structural Number
    - params: dict ของพารามิเตอร์ออกแบบ
    
    Returns:
    - log₁₀(W₁₈)
    """
    ZR = params['ZR']
    S0 = params['S0']
    MR = params['MR']
    delta_PSI = params['delta_PSI']
    
    if SN <= 0:
        return -999
    
    # Term 1: ZR × S0
    term1 = ZR * S0
    
    # Term 2: 9.36 × log(SN+1) - 0.20
    term2 = 9.36 * math.log10(SN + 1) - 0.20
    
    # Term 3: log[ΔPSI/(4.2-1.5)] / [0.40 + 1094/(SN+1)^5.19]
    numerator3 = math.log10(delta_PSI / 2.7)
    denominator3 = 0.40 + 1094 / ((SN + 1) ** 5.19)
    term3 = numerator3 / denominator3
    
    # Term 4: 2.32 × log(MR) - 8.07
    term4 = 2.32 * math.log10(MR) - 8.07
    
    log_W18 = term1 + term2 + term3 + term4
    
    return log_W18


def find_required_SN(W18_design, params, SN_min=1, SN_max=15):
    """
    หาค่า Structural Number (SN) ที่ต้องการ
    
    Parameters:
    - W18_design: ค่า ESAL ออกแบบ
    - params: พารามิเตอร์ออกแบบ
    - SN_min, SN_max: ช่วง SN ที่ค้นหา
    
    Returns:
    - SN ที่ต้องการ
    """
    log_W18_design = math.log10(W18_design)
    
    def objective(SN):
        return calculate_log_W18_flexible(SN, params) - log_W18_design
    
    try:
        f_min = objective(SN_min)
        f_max = objective(SN_max)
        
        if f_min > 0:
            return SN_min
        if f_max < 0:
            return SN_max + 1
        
        SN_required = bisection_method(objective, SN_min, SN_max)
        return SN_required
    except:
        return None


def calculate_SN(layers):
    """
    คำนวณ Structural Number จากชั้นโครงสร้าง
    
    SN = Σ(aᵢ × Dᵢ × mᵢ)
    
    Parameters:
    - layers: list of dict with 'a', 'D_inch', 'm'
    
    Returns:
    - SN: Structural Number
    - details: รายละเอียดการคำนวณ
    """
    SN = 0
    details = []
    
    for i, layer in enumerate(layers):
        a = layer.get('a', 0)
        D = layer.get('D_inch', 0)
        m = layer.get('m', 1.0)
        
        SN_layer = a * D * m
        SN += SN_layer
        
        details.append({
            'layer': i + 1,
            'name': layer.get('name', f'Layer {i+1}'),
            'a': a,
            'D_inch': D,
            'D_cm': D * 2.54,
            'm': m,
            'SN_layer': SN_layer,
        })
    
    return SN, details


def design_layer_thickness(SN_required, layer_coefficients, drainage_coefficients, min_thicknesses):
    """
    ออกแบบความหนาชั้นโครงสร้างตาม SN ที่ต้องการ
    
    Parameters:
    - SN_required: Structural Number ที่ต้องการ
    - layer_coefficients: [a1, a2, a3] สำหรับ Surface, Base, Subbase
    - drainage_coefficients: [m2, m3] สำหรับ Base, Subbase
    - min_thicknesses: [D1_min, D2_min, D3_min] ความหนาต่ำสุด (นิ้ว)
    
    Returns:
    - thicknesses: [D1, D2, D3] ความหนาที่ออกแบบ (นิ้ว)
    - SN_provided: SN ที่ได้จริง
    """
    a1, a2, a3 = layer_coefficients
    m2, m3 = drainage_coefficients
    D1_min, D2_min, D3_min = min_thicknesses
    
    # เริ่มจากความหนาต่ำสุด
    D1 = D1_min
    D2 = D2_min
    D3 = D3_min
    
    # SN จาก Surface course
    SN1 = a1 * D1
    
    # SN ที่ต้องการจาก Base และ Subbase
    SN_remaining = SN_required - SN1
    
    if SN_remaining <= 0:
        # Surface course เพียงพอ
        SN_provided = SN1 + a2 * D2 * m2 + a3 * D3 * m3
        return [D1, D2, D3], SN_provided
    
    # SN จาก Base course (ใช้ความหนาต่ำสุด)
    SN2 = a2 * D2 * m2
    SN_remaining_after_base = SN_remaining - SN2
    
    if SN_remaining_after_base <= 0:
        # Base course เพียงพอ
        SN_provided = SN1 + SN2 + a3 * D3 * m3
        return [D1, D2, D3], SN_provided
    
    # คำนวณความหนา Subbase ที่ต้องการ
    D3_required = SN_remaining_after_base / (a3 * m3)
    D3 = max(D3_min, math.ceil(D3_required))
    
    SN_provided = a1 * D1 + a2 * D2 * m2 + a3 * D3 * m3
    
    return [D1, D2, D3], SN_provided


# ==========================================
# Streamlit App
# ==========================================

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="AASHTO 1993 Flexible Pavement Design",
    page_icon="🛣️",
    layout="wide"
)

# CSS สำหรับตกแต่ง
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A5F;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        background-color: #E8F4F8;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #FFF3E0;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FF9800;
        margin: 10px 0;
    }
    .success-box {
        background-color: #E8F5E9;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🛣️ โปรแกรมออกแบบโครงสร้างชั้นทางแบบยืดหยุ่น</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AASHTO Guide for Design of Pavement Structures (1993) - Flexible Pavement</p>', unsafe_allow_html=True)

# Sidebar - พารามิเตอร์ออกแบบ
st.sidebar.header("⚙️ พารามิเตอร์ออกแบบ")

# Reliability
st.sidebar.subheader("📊 Reliability")
reliability_options = {
    "80% (R = 0.80)": -0.841,
    "85% (R = 0.85)": -1.037,
    "90% (R = 0.90)": -1.282,
    "95% (R = 0.95)": -1.645,
    "99% (R = 0.99)": -2.327,
}
reliability_choice = st.sidebar.selectbox(
    "Reliability Level",
    options=list(reliability_options.keys()),
    index=2,
    help="ระดับความเชื่อมั่นในการออกแบบ"
)
ZR = reliability_options[reliability_choice]
st.sidebar.caption(f"Z_R = {ZR}")

# Standard Deviation
S0 = st.sidebar.slider(
    "Overall Standard Deviation (S₀)",
    min_value=0.40, max_value=0.50, value=0.45, step=0.01,
    help="ค่าเบี่ยงเบนมาตรฐานรวม (0.40-0.50 สำหรับ Flexible)"
)

# Serviceability
st.sidebar.subheader("📈 Serviceability")
Pi = st.sidebar.slider(
    "Initial Serviceability (Pᵢ)",
    min_value=4.0, max_value=4.5, value=4.2, step=0.1,
    help="ค่าความสามารถในการให้บริการเริ่มต้น"
)
pt = st.sidebar.slider(
    "Terminal Serviceability (pₜ)",
    min_value=2.0, max_value=3.0, value=2.5, step=0.1,
    help="ค่าความสามารถในการให้บริการสิ้นสุด"
)
delta_PSI = Pi - pt

# Layer Coefficients
st.sidebar.subheader("🔧 Layer Coefficients")

a1 = st.sidebar.slider(
    "a₁ - Surface Course (AC)",
    min_value=0.30, max_value=0.50, value=0.42, step=0.01,
    help="ค่าสัมประสิทธิ์ชั้นผิวทาง (AC)"
)

a2 = st.sidebar.slider(
    "a₂ - Base Course",
    min_value=0.10, max_value=0.40, value=0.14, step=0.01,
    help="ค่าสัมประสิทธิ์ชั้นพื้นทาง"
)

a3 = st.sidebar.slider(
    "a₃ - Subbase Course",
    min_value=0.05, max_value=0.20, value=0.11, step=0.01,
    help="ค่าสัมประสิทธิ์ชั้นรองพื้นทาง"
)

# Drainage Coefficients
st.sidebar.subheader("💧 Drainage Coefficients")
m2 = st.sidebar.slider(
    "m₂ - Base Course",
    min_value=0.40, max_value=1.40, value=1.00, step=0.05,
    help="ค่าสัมประสิทธิ์การระบายน้ำชั้นพื้นทาง"
)
m3 = st.sidebar.slider(
    "m₃ - Subbase Course",
    min_value=0.40, max_value=1.40, value=1.00, step=0.05,
    help="ค่าสัมประสิทธิ์การระบายน้ำชั้นรองพื้นทาง"
)

# Main content
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚛 ข้อมูลปริมาณจราจร")
    
    W18_input_method = st.radio(
        "วิธีการกรอกค่า W₁₈",
        ["กรอกค่าโดยตรง", "กรอกเป็นล้าน ESAL"],
        horizontal=True
    )
    
    if W18_input_method == "กรอกค่าโดยตรง":
        W18_input = st.number_input(
            "W₁₈ (ESAL)",
            min_value=100000,
            max_value=500000000,
            value=10000000,
            step=1000000,
            format="%d",
            help="ปริมาณจราจรเทียบเท่าเพลาเดี่ยวมาตรฐาน 18 kips"
        )
    else:
        W18_million = st.number_input(
            "W₁₈ (ล้าน ESAL)",
            min_value=0.1,
            max_value=500.0,
            value=10.0,
            step=1.0,
            format="%.1f"
        )
        W18_input = int(W18_million * 1e6)
    
    st.info(f"📊 W₁₈ = **{W18_input:,}** ESAL ({W18_input/1e6:.2f} ล้าน)")

with col2:
    st.subheader("🏔️ ข้อมูลดินฐานราก (Subgrade)")
    
    subgrade_method = st.radio(
        "วิธีการกำหนดค่า MR",
        ["จากค่า CBR", "กรอก MR โดยตรง"],
        horizontal=True
    )
    
    if subgrade_method == "จากค่า CBR":
        CBR_options = {
            "CBR 3% (ดินเหนียวอ่อน)": 3,
            "CBR 5% (ดินเหนียวปานกลาง)": 5,
            "CBR 6% (ดินเหนียวแข็ง)": 6,
            "CBR 10% (ดินทรายปนดินเหนียว)": 10,
            "CBR 15% (ดินทราย)": 15,
            "CBR 20% (กรวดปนทราย)": 20,
        }
        CBR_choice = st.selectbox(
            "เลือกประเภทดินฐานราก",
            options=list(CBR_options.keys()),
            index=1
        )
        CBR = CBR_options[CBR_choice]
        
        CBR = st.slider(
            "ปรับค่า CBR (%)",
            min_value=2.0, max_value=30.0, value=float(CBR), step=0.5
        )
        
        MR_subgrade = calculate_MR_from_CBR(CBR)
        st.info(f"📊 CBR = **{CBR:.1f}%** → M_R = **{MR_subgrade:,.0f}** psi")
    else:
        MR_subgrade = st.number_input(
            "Resilient Modulus - MR (psi)",
            min_value=1500,
            max_value=50000,
            value=7500,
            step=500,
            help="ค่า Resilient Modulus ของดินฐานราก"
        )
        # คำนวณ CBR ย้อนกลับ
        CBR = MR_subgrade / 1500 if MR_subgrade <= 15000 else (MR_subgrade / 3000) ** (1/0.65)
        st.info(f"📊 M_R = **{MR_subgrade:,}** psi (≈ CBR {CBR:.1f}%)")

# ส่วนโครงสร้างชั้นทาง
st.markdown("---")
st.subheader("🏗️ โครงสร้างชั้นทาง")

structure_mode = st.radio(
    "โหมดการออกแบบ",
    ["คำนวณ SN ที่ต้องการ แล้วออกแบบความหนา", "กำหนดความหนาเอง แล้วตรวจสอบ SN"],
    horizontal=True
)

# รวบรวมพารามิเตอร์
params = {
    'ZR': ZR,
    'S0': S0,
    'MR': MR_subgrade,
    'delta_PSI': delta_PSI,
}

if structure_mode == "คำนวณ SN ที่ต้องการ แล้วออกแบบความหนา":
    
    st.markdown("##### กำหนดความหนาต่ำสุด")
    
    min_col1, min_col2, min_col3 = st.columns(3)
    
    with min_col1:
        D1_min = st.number_input(
            "D₁ min - Surface (นิ้ว)",
            min_value=1.0, max_value=10.0, value=4.0, step=0.5,
            help="ความหนาต่ำสุดของชั้นผิวทาง"
        )
    
    with min_col2:
        D2_min = st.number_input(
            "D₂ min - Base (นิ้ว)",
            min_value=2.0, max_value=15.0, value=6.0, step=0.5,
            help="ความหนาต่ำสุดของชั้นพื้นทาง"
        )
    
    with min_col3:
        D3_min = st.number_input(
            "D₃ min - Subbase (นิ้ว)",
            min_value=2.0, max_value=20.0, value=6.0, step=0.5,
            help="ความหนาต่ำสุดของชั้นรองพื้นทาง"
        )
    
    if st.button("🔢 คำนวณโครงสร้างชั้นทาง", type="primary", use_container_width=True):
        
        # คำนวณ SN ที่ต้องการ
        SN_required = find_required_SN(W18_input, params)
        
        if SN_required is None or SN_required > 15:
            st.error("❌ ไม่สามารถคำนวณได้ กรุณาตรวจสอบพารามิเตอร์")
        else:
            st.subheader("📊 ผลการคำนวณ")
            
            # แสดง SN ที่ต้องการ
            res_col1, res_col2, res_col3 = st.columns(3)
            
            with res_col1:
                st.metric(
                    "SN ที่ต้องการ",
                    f"{SN_required:.2f}",
                    help="Structural Number ที่ต้องการ"
                )
            
            with res_col2:
                log_W18 = math.log10(W18_input)
                st.metric(
                    "log₁₀(W₁₈) ออกแบบ",
                    f"{log_W18:.4f}"
                )
            
            with res_col3:
                st.metric(
                    "ΔPSI",
                    f"{delta_PSI:.1f}",
                    f"({Pi:.1f} - {pt:.1f})"
                )
            
            # ออกแบบความหนา
            thicknesses, SN_provided = design_layer_thickness(
                SN_required,
                [a1, a2, a3],
                [m2, m3],
                [D1_min, D2_min, D3_min]
            )
            
            D1, D2, D3 = thicknesses
            
            st.markdown("---")
            st.markdown("##### โครงสร้างชั้นทางที่ออกแบบ")
            
            # สร้างตารางโครงสร้าง
            structure_data = [
                {
                    "ชั้น": "1. Surface Course (AC)",
                    "a": a1,
                    "D (นิ้ว)": D1,
                    "D (ซม.)": D1 * 2.54,
                    "m": 1.00,
                    "SN": a1 * D1 * 1.00,
                },
                {
                    "ชั้น": "2. Base Course",
                    "a": a2,
                    "D (นิ้ว)": D2,
                    "D (ซม.)": D2 * 2.54,
                    "m": m2,
                    "SN": a2 * D2 * m2,
                },
                {
                    "ชั้น": "3. Subbase Course",
                    "a": a3,
                    "D (นิ้ว)": D3,
                    "D (ซม.)": D3 * 2.54,
                    "m": m3,
                    "SN": a3 * D3 * m3,
                },
            ]
            
            df_structure = pd.DataFrame(structure_data)
            
            st.dataframe(
                df_structure,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ชั้น": st.column_config.TextColumn("ชั้นโครงสร้าง", width="large"),
                    "a": st.column_config.NumberColumn("Layer Coeff. (a)", format="%.2f"),
                    "D (นิ้ว)": st.column_config.NumberColumn("ความหนา (นิ้ว)", format="%.1f"),
                    "D (ซม.)": st.column_config.NumberColumn("ความหนา (ซม.)", format="%.1f"),
                    "m": st.column_config.NumberColumn("Drainage (m)", format="%.2f"),
                    "SN": st.column_config.NumberColumn("SN", format="%.3f"),
                }
            )
            
            # สรุป
            total_thickness_inch = D1 + D2 + D3
            total_thickness_cm = total_thickness_inch * 2.54
            
            sum_col1, sum_col2, sum_col3 = st.columns(3)
            
            with sum_col1:
                st.metric(
                    "ความหนารวม",
                    f"{total_thickness_cm:.0f} ซม.",
                    f"({total_thickness_inch:.1f} นิ้ว)"
                )
            
            with sum_col2:
                st.metric(
                    "SN ที่ได้",
                    f"{SN_provided:.3f}",
                    f"{((SN_provided/SN_required)-1)*100:+.1f}% จากที่ต้องการ"
                )
            
            with sum_col3:
                # คำนวณ W18 ที่รองรับได้
                log_W18_provided = calculate_log_W18_flexible(SN_provided, params)
                W18_provided = 10 ** log_W18_provided
                margin = (W18_provided / W18_input - 1) * 100
                
                st.metric(
                    "W₁₈ รองรับได้",
                    f"{W18_provided:,.0f}",
                    f"{margin:+.1f}%"
                )
            
            # ========================
            # ส่วนวิเคราะห์เปรียบเทียบ SN
            # ========================
            st.markdown("---")
            st.subheader("📊 วิเคราะห์เปรียบเทียบ W₁₈ สำหรับค่า SN ต่างๆ")
            
            SN_options = [3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
            
            comparison_data = []
            for SN_test in SN_options:
                log_W18_test = calculate_log_W18_flexible(SN_test, params)
                W18_test = 10 ** log_W18_test
                ratio = W18_test / W18_input
                margin_pct = (ratio - 1) * 100
                status = "✅ เพียงพอ" if W18_test >= W18_input else "❌ ไม่เพียงพอ"
                
                comparison_data.append({
                    "SN": SN_test,
                    "log₁₀(W₁₈)": f"{log_W18_test:.4f}",
                    "W₁₈ รองรับได้": f"{W18_test:,.0f}",
                    "W₁₈ (ล้าน)": W18_test / 1e6,
                    "อัตราส่วน": f"{ratio:.2f}",
                    "ส่วนเผื่อ (%)": f"{margin_pct:+.1f}%",
                    "สถานะ": status,
                    "W18_raw": W18_test,
                })
            
            df_comparison = pd.DataFrame(comparison_data)
            df_display = df_comparison[["SN", "log₁₀(W₁₈)", "W₁₈ รองรับได้", "อัตราส่วน", "ส่วนเผื่อ (%)", "สถานะ"]]
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # กราฟ
            chart_col1, chart_col2 = st.columns([2, 1])
            
            with chart_col1:
                chart_data = pd.DataFrame({
                    "SN": SN_options,
                    "W₁₈ (ล้าน ESAL)": [d["W18_raw"] / 1e6 for d in comparison_data],
                })
                st.bar_chart(chart_data.set_index("SN"), use_container_width=True)
                st.caption(f"🔴 W₁₈ ออกแบบ = {W18_input/1e6:.2f} ล้าน ESAL")
            
            with chart_col2:
                st.markdown("**สรุปผล:**")
                st.success(f"✅ SN ที่ต้องการ: **{SN_required:.2f}**")
                st.write(f"SN ที่ได้: **{SN_provided:.3f}**")
                st.write(f"W₁₈ รองรับได้: **{W18_provided:,.0f}** ESAL")

else:
    # โหมดกำหนดความหนาเอง
    st.markdown("##### กำหนดความหนาแต่ละชั้น")
    
    thick_col1, thick_col2, thick_col3 = st.columns(3)
    
    with thick_col1:
        D1_custom = st.number_input(
            "D₁ - Surface Course (นิ้ว)",
            min_value=1.0, max_value=15.0, value=4.0, step=0.5,
            help="ความหนาชั้นผิวทาง"
        )
        st.caption(f"= {D1_custom * 2.54:.1f} ซม.")
    
    with thick_col2:
        D2_custom = st.number_input(
            "D₂ - Base Course (นิ้ว)",
            min_value=2.0, max_value=20.0, value=6.0, step=0.5,
            help="ความหนาชั้นพื้นทาง"
        )
        st.caption(f"= {D2_custom * 2.54:.1f} ซม.")
    
    with thick_col3:
        D3_custom = st.number_input(
            "D₃ - Subbase Course (นิ้ว)",
            min_value=2.0, max_value=25.0, value=8.0, step=0.5,
            help="ความหนาชั้นรองพื้นทาง"
        )
        st.caption(f"= {D3_custom * 2.54:.1f} ซม.")
    
    if st.button("🔢 ตรวจสอบ Structural Number", type="primary", use_container_width=True):
        
        # คำนวณ SN
        layers_custom = [
            {'name': 'Surface Course (AC)', 'a': a1, 'D_inch': D1_custom, 'm': 1.00},
            {'name': 'Base Course', 'a': a2, 'D_inch': D2_custom, 'm': m2},
            {'name': 'Subbase Course', 'a': a3, 'D_inch': D3_custom, 'm': m3},
        ]
        
        SN_custom, details = calculate_SN(layers_custom)
        
        # คำนวณ SN ที่ต้องการ
        SN_required = find_required_SN(W18_input, params)
        
        st.subheader("📊 ผลการตรวจสอบ")
        
        # แสดงตารางโครงสร้าง
        structure_data = []
        for d in details:
            structure_data.append({
                "ชั้น": d['name'],
                "a": d['a'],
                "D (นิ้ว)": d['D_inch'],
                "D (ซม.)": d['D_cm'],
                "m": d['m'],
                "SN": d['SN_layer'],
            })
        
        df_structure = pd.DataFrame(structure_data)
        st.dataframe(df_structure, use_container_width=True, hide_index=True)
        
        # สรุป
        res_col1, res_col2, res_col3, res_col4 = st.columns(4)
        
        with res_col1:
            st.metric(
                "SN ที่ต้องการ",
                f"{SN_required:.2f}"
            )
        
        with res_col2:
            diff = SN_custom - SN_required
            st.metric(
                "SN ที่ได้",
                f"{SN_custom:.3f}",
                f"{diff:+.3f}"
            )
        
        with res_col3:
            log_W18_custom = calculate_log_W18_flexible(SN_custom, params)
            W18_custom = 10 ** log_W18_custom
            margin = (W18_custom / W18_input - 1) * 100
            
            st.metric(
                "W₁₈ รองรับได้",
                f"{W18_custom:,.0f}",
                f"{margin:+.1f}%"
            )
        
        with res_col4:
            total_thick = D1_custom + D2_custom + D3_custom
            st.metric(
                "ความหนารวม",
                f"{total_thick * 2.54:.0f} ซม.",
                f"({total_thick:.1f} นิ้ว)"
            )
        
        # ผลการตรวจสอบ
        if SN_custom >= SN_required:
            st.success(f"✅ **ผ่านการตรวจสอบ** - SN ที่ได้ ({SN_custom:.3f}) ≥ SN ที่ต้องการ ({SN_required:.2f})")
        else:
            st.error(f"❌ **ไม่ผ่านการตรวจสอบ** - SN ที่ได้ ({SN_custom:.3f}) < SN ที่ต้องการ ({SN_required:.2f})")
            st.warning(f"ต้องเพิ่ม SN อีก {SN_required - SN_custom:.3f}")

# ========================
# ส่วนข้อมูลอ้างอิง
# ========================
st.markdown("---")

with st.expander("📚 ข้อมูลอ้างอิงและสมการ"):
    st.markdown("""
    ### สมการ AASHTO 1993 สำหรับ Flexible Pavement
    
    $$\\log W_{18} = Z_R S_0 + 9.36 \\log(SN+1) - 0.20 + \\frac{\\log[\\Delta PSI / (4.2-1.5)]}{0.40 + \\frac{1094}{(SN+1)^{5.19}}} + 2.32 \\log(M_R) - 8.07$$
    
    ### Structural Number (SN)
    
    $$SN = a_1 D_1 + a_2 D_2 m_2 + a_3 D_3 m_3$$
    
    **โดยที่:**
    - $W_{18}$ = Equivalent Single Axle Load 18 kips (ESAL)
    - $Z_R$ = Standard Normal Deviate
    - $S_0$ = Overall Standard Deviation (0.40-0.50)
    - $SN$ = Structural Number
    - $\\Delta PSI$ = $P_i - p_t$ (การสูญเสียความสามารถในการให้บริการ)
    - $M_R$ = Resilient Modulus ของ Subgrade (psi)
    - $a_i$ = Layer Coefficient ของชั้นที่ i
    - $D_i$ = ความหนาของชั้นที่ i (นิ้ว)
    - $m_i$ = Drainage Coefficient ของชั้นที่ i
    
    ### การคำนวณ MR จาก CBR
    
    $$M_R = 1500 \\times CBR \\quad (CBR \\leq 10\\%)$$
    $$M_R = 3000 \\times CBR^{0.65} \\quad (CBR > 10\\%)$$
    
    ---
    
    ### ตาราง Layer Coefficients (a)
    
    | วัสดุ | Layer Coefficient (a) |
    |:---|:---:|
    | Asphalt Concrete (AC) | 0.40 - 0.44 |
    | Emulsified Asphalt Mix | 0.20 - 0.35 |
    | Cement Treated Base (CTB) | 0.15 - 0.23 |
    | Crushed Stone Base | 0.10 - 0.14 |
    | Soil Cement | 0.15 - 0.20 |
    | Granular Subbase | 0.08 - 0.14 |
    | Sand or Sandy Gravel | 0.05 - 0.10 |
    
    ### ตาราง Drainage Coefficients (m)
    
    | Quality of Drainage | % Time Saturated |
    |:---|:---:|:---:|:---:|:---:|
    | | < 1% | 1-5% | 5-25% | > 25% |
    | Excellent | 1.40-1.35 | 1.35-1.30 | 1.30-1.20 | 1.20 |
    | Good | 1.35-1.25 | 1.25-1.15 | 1.15-1.00 | 1.00 |
    | Fair | 1.25-1.15 | 1.15-1.05 | 1.00-0.80 | 0.80 |
    | Poor | 1.15-1.05 | 1.05-0.80 | 0.80-0.60 | 0.60 |
    | Very Poor | 1.05-0.95 | 0.95-0.75 | 0.75-0.40 | 0.40 |
    
    ---
    
    **อ้างอิง:** AASHTO Guide for Design of Pavement Structures (1993)
    """)

with st.expander("📋 สรุปพารามิเตอร์ที่ใช้"):
    param_col1, param_col2, param_col3 = st.columns(3)
    
    with param_col1:
        st.markdown(f"""
        **Reliability & Deviation**
        - Reliability = {reliability_choice.split('(')[0].strip()}
        - Z_R = {ZR}
        - S₀ = {S0}
        """)
    
    with param_col2:
        st.markdown(f"""
        **Serviceability**
        - Pᵢ = {Pi}
        - pₜ = {pt}
        - ΔPSI = {delta_PSI}
        """)
    
    with param_col3:
        st.markdown(f"""
        **Layer & Drainage Coefficients**
        - a₁ = {a1}, a₂ = {a2}, a₃ = {a3}
        - m₂ = {m2}, m₃ = {m3}
        - M_R = {MR_subgrade:,} psi
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>พัฒนาสำหรับการเรียนการสอนวิชาวิศวกรรมทาง</p>
    <p>ภาควิชาครุศาสตร์โยธา มหาวิทยาลัยเทคโนโลยีพระจอมเกล้าพระนครเหนือ</p>
</div>
""", unsafe_allow_html=True)

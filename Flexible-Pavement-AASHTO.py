import streamlit as st
import numpy as np
import math
import pandas as pd


# ==========================================
# ฐานข้อมูลวัสดุชั้นทาง (ตามมาตรฐานกรมทางหลวง)
# ==========================================

MATERIAL_DATABASE = {
    # ชั้นผิวทาง (Surface Course)
    "surface": {
        "ผิวทางลาดยาง AC": {"a": 0.40, "m": 1.00, "MR_psi": 362500, "MR_MPa": 2500},
        "ผิวทางลาดยาง PMA": {"a": 0.40, "m": 1.00, "MR_psi": 536500, "MR_MPa": 3700},
    },
    # ชั้นพื้นทาง (Base Course)
    "base": {
        "พื้นทางซีเมนต์ CTB": {"a": 0.15, "m": 1.00, "MR_psi": 174000, "MR_MPa": 1200},
        "พื้นทางหินคลุกผสมซีเมนต์ UCS 24.5 ksc": {"a": 0.15, "m": 1.00, "MR_psi": 123250, "MR_MPa": 850},
        "พื้นทางหินคลุก CBR 80%": {"a": 0.13, "m": 1.00, "MR_psi": 50750, "MR_MPa": 350},
        "พื้นทางดินซีเมนต์ UCS 17.5 ksc": {"a": 0.13, "m": 1.00, "MR_psi": 50750, "MR_MPa": 350},
        "พื้นทางวัสดุหมุนเวียน (Recycling)": {"a": 0.15, "m": 1.00, "MR_psi": 123250, "MR_MPa": 850},
    },
    # ชั้นรองพื้นทาง (Subbase Course)
    "subbase": {
        "รองพื้นทางวัสดุมวลรวม CBR 25%": {"a": 0.10, "m": 1.00, "MR_psi": 21750, "MR_MPa": 150},
        "วัสดุคัดเลือก ก": {"a": 0.08, "m": 1.00, "MR_psi": 11020, "MR_MPa": 76},
    },
    # ดินฐานราก (Subgrade)
    "subgrade": {
        "ดินถมคันทาง/ดินเดิม (CBR 6%)": {"MR_psi": 14939, "MR_MPa": 103, "CBR": 6},
        "ดินเหนียวอ่อน (CBR 3%)": {"MR_psi": 4500, "MR_MPa": 31, "CBR": 3},
        "ดินเหนียวปานกลาง (CBR 5%)": {"MR_psi": 7500, "MR_MPa": 52, "CBR": 5},
        "ดินทรายปนดินเหนียว (CBR 10%)": {"MR_psi": 15000, "MR_MPa": 103, "CBR": 10},
        "ดินทราย (CBR 15%)": {"MR_psi": 19673, "MR_MPa": 136, "CBR": 15},
        "กรวดปนทราย (CBR 20%)": {"MR_psi": 23604, "MR_MPa": 163, "CBR": 20},
    }
}


def cm_to_inch(cm):
    """แปลงเซนติเมตรเป็นนิ้ว"""
    return cm / 2.54


def inch_to_cm(inch):
    """แปลงนิ้วเป็นเซนติเมตร"""
    return inch * 2.54


def bisection_method(func, a, b, tol=1e-6, max_iter=100):
    """
    Bisection Method สำหรับหาค่า root ของฟังก์ชัน
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
    """
    ZR = params['ZR']
    S0 = params['S0']
    MR = params['MR']
    delta_PSI = params['delta_PSI']
    
    if SN <= 0:
        return -999
    
    term1 = ZR * S0
    term2 = 9.36 * math.log10(SN + 1) - 0.20
    numerator3 = math.log10(delta_PSI / 2.7)
    denominator3 = 0.40 + 1094 / ((SN + 1) ** 5.19)
    term3 = numerator3 / denominator3
    term4 = 2.32 * math.log10(MR) - 8.07
    
    log_W18 = term1 + term2 + term3 + term4
    
    return log_W18


def find_required_SN(W18_design, params, SN_min=1, SN_max=15):
    """
    หาค่า Structural Number (SN) ที่ต้องการ
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
    """
    SN = 0
    details = []
    
    for i, layer in enumerate(layers):
        a = layer.get('a', 0)
        D_inch = layer.get('D_inch', 0)
        m = layer.get('m', 1.0)
        
        SN_layer = a * D_inch * m
        SN += SN_layer
        
        details.append({
            'layer': i + 1,
            'name': layer.get('name', f'Layer {i+1}'),
            'a': a,
            'D_inch': D_inch,
            'D_cm': D_inch * 2.54,
            'm': m,
            'SN_layer': SN_layer,
        })
    
    return SN, details


# ==========================================
# Streamlit App
# ==========================================

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
    .material-box {
        background-color: #F0F7FF;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1E88E5;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🛣️ โปรแกรมออกแบบโครงสร้างชั้นทางแบบยืดหยุ่น</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AASHTO Guide for Design of Pavement Structures (1993) - Flexible Pavement</p>', unsafe_allow_html=True)

# ==========================================
# Sidebar - พารามิเตอร์ออกแบบ
# ==========================================
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

# ==========================================
# Main Content
# ==========================================

# ข้อมูลปริมาณจราจร
st.subheader("🚛 ข้อมูลปริมาณจราจร (Traffic)")

traffic_col1, traffic_col2 = st.columns(2)

with traffic_col1:
    W18_input_method = st.radio(
        "วิธีการกรอกค่า W₁₈",
        ["กรอกค่าโดยตรง", "กรอกเป็นล้าน ESAL"],
        horizontal=True
    )

with traffic_col2:
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

st.markdown("---")

# ==========================================
# โครงสร้างชั้นทาง - เลือกวัสดุและกำหนดความหนา
# ==========================================
st.subheader("🏗️ โครงสร้างชั้นทาง")

# ==========================================
# ชั้นที่ 1: ผิวทาง (Surface Course)
# ==========================================
st.markdown("#### 1️⃣ ชั้นผิวทาง (Surface Course)")

surf_col1, surf_col2, surf_col3, surf_col4 = st.columns([2, 1, 1, 1])

with surf_col1:
    surface_material = st.selectbox(
        "เลือกวัสดุชั้นผิวทาง",
        options=list(MATERIAL_DATABASE["surface"].keys()),
        index=0,
        key="surface_mat"
    )
    surf_props = MATERIAL_DATABASE["surface"][surface_material]

with surf_col2:
    D1_cm = st.number_input(
        "ความหนา D₁ (ซม.)",
        min_value=5.0, max_value=30.0, value=10.0, step=1.0,
        key="D1_cm",
        help="ความหนาชั้นผิวทาง"
    )
    D1_inch = cm_to_inch(D1_cm)
    st.caption(f"= {D1_inch:.2f} นิ้ว")

with surf_col3:
    a1 = st.number_input(
        "a₁",
        min_value=0.20, max_value=0.50, value=surf_props["a"], step=0.01,
        key="a1",
        help="Layer Coefficient"
    )

with surf_col4:
    m1 = st.number_input(
        "m₁",
        min_value=0.50, max_value=1.50, value=surf_props["m"], step=0.05,
        key="m1",
        help="Drainage Coefficient"
    )

st.caption(f"📋 {surface_material}: a = {surf_props['a']}, MR = {surf_props['MR_psi']:,} psi ({surf_props['MR_MPa']:,} MPa)")

# ==========================================
# ชั้นที่ 2: พื้นทาง (Base Course)
# ==========================================
st.markdown("#### 2️⃣ ชั้นพื้นทาง (Base Course)")

base_col1, base_col2, base_col3, base_col4 = st.columns([2, 1, 1, 1])

with base_col1:
    base_material = st.selectbox(
        "เลือกวัสดุชั้นพื้นทาง",
        options=list(MATERIAL_DATABASE["base"].keys()),
        index=0,
        key="base_mat"
    )
    base_props = MATERIAL_DATABASE["base"][base_material]

with base_col2:
    D2_cm = st.number_input(
        "ความหนา D₂ (ซม.)",
        min_value=10.0, max_value=50.0, value=20.0, step=1.0,
        key="D2_cm",
        help="ความหนาชั้นพื้นทาง"
    )
    D2_inch = cm_to_inch(D2_cm)
    st.caption(f"= {D2_inch:.2f} นิ้ว")

with base_col3:
    a2 = st.number_input(
        "a₂",
        min_value=0.05, max_value=0.30, value=base_props["a"], step=0.01,
        key="a2",
        help="Layer Coefficient"
    )

with base_col4:
    m2 = st.number_input(
        "m₂",
        min_value=0.50, max_value=1.50, value=base_props["m"], step=0.05,
        key="m2",
        help="Drainage Coefficient"
    )

st.caption(f"📋 {base_material}: a = {base_props['a']}, MR = {base_props['MR_psi']:,} psi ({base_props['MR_MPa']:,} MPa)")

# ==========================================
# ชั้นที่ 3: รองพื้นทาง (Subbase Course)
# ==========================================
st.markdown("#### 3️⃣ ชั้นรองพื้นทาง (Subbase Course)")

subbase_col1, subbase_col2, subbase_col3, subbase_col4 = st.columns([2, 1, 1, 1])

with subbase_col1:
    subbase_material = st.selectbox(
        "เลือกวัสดุชั้นรองพื้นทาง",
        options=list(MATERIAL_DATABASE["subbase"].keys()),
        index=0,
        key="subbase_mat"
    )
    subbase_props = MATERIAL_DATABASE["subbase"][subbase_material]

with subbase_col2:
    D3_cm = st.number_input(
        "ความหนา D₃ (ซม.)",
        min_value=10.0, max_value=60.0, value=15.0, step=1.0,
        key="D3_cm",
        help="ความหนาชั้นรองพื้นทาง"
    )
    D3_inch = cm_to_inch(D3_cm)
    st.caption(f"= {D3_inch:.2f} นิ้ว")

with subbase_col3:
    a3 = st.number_input(
        "a₃",
        min_value=0.05, max_value=0.20, value=subbase_props["a"], step=0.01,
        key="a3",
        help="Layer Coefficient"
    )

with subbase_col4:
    m3 = st.number_input(
        "m₃",
        min_value=0.50, max_value=1.50, value=subbase_props["m"], step=0.05,
        key="m3",
        help="Drainage Coefficient"
    )

st.caption(f"📋 {subbase_material}: a = {subbase_props['a']}, MR = {subbase_props['MR_psi']:,} psi ({subbase_props['MR_MPa']:,} MPa)")

# ==========================================
# ดินฐานราก (Subgrade)
# ==========================================
st.markdown("#### 4️⃣ ดินฐานราก (Subgrade)")

subgrade_col1, subgrade_col2 = st.columns([2, 2])

with subgrade_col1:
    subgrade_method = st.radio(
        "วิธีการกำหนดค่า MR",
        ["เลือกจากฐานข้อมูล", "กรอกค่า CBR", "กรอก MR โดยตรง"],
        horizontal=True
    )

with subgrade_col2:
    if subgrade_method == "เลือกจากฐานข้อมูล":
        subgrade_material = st.selectbox(
            "เลือกประเภทดินฐานราก",
            options=list(MATERIAL_DATABASE["subgrade"].keys()),
            index=0,
            key="subgrade_mat"
        )
        subgrade_props = MATERIAL_DATABASE["subgrade"][subgrade_material]
        MR_subgrade = subgrade_props["MR_psi"]
        CBR_display = subgrade_props.get("CBR", MR_subgrade / 1500)
        
    elif subgrade_method == "กรอกค่า CBR":
        CBR_display = st.number_input(
            "CBR (%)",
            min_value=2.0, max_value=30.0, value=6.0, step=0.5,
            help="California Bearing Ratio"
        )
        MR_subgrade = calculate_MR_from_CBR(CBR_display)
        
    else:  # กรอก MR โดยตรง
        MR_subgrade = st.number_input(
            "Resilient Modulus - MR (psi)",
            min_value=1500,
            max_value=50000,
            value=14939,
            step=500,
            help="ค่า Resilient Modulus ของดินฐานราก"
        )
        CBR_display = MR_subgrade / 1500 if MR_subgrade <= 15000 else (MR_subgrade / 3000) ** (1/0.65)

st.info(f"🏔️ **ดินฐานราก:** M_R = **{MR_subgrade:,.0f}** psi ({MR_subgrade * 0.00689476:.0f} MPa) | CBR ≈ **{CBR_display:.1f}%**")

# แสดงรวมความหนา
total_thickness_cm = D1_cm + D2_cm + D3_cm
total_thickness_inch = cm_to_inch(total_thickness_cm)
st.success(f"📏 **รวมความหนาโครงสร้างชั้นทาง = {total_thickness_cm:.0f} ซม.** ({total_thickness_inch:.2f} นิ้ว)")

# ==========================================
# ปุ่มคำนวณ
# ==========================================
st.markdown("---")

if st.button("🔢 คำนวณ Structural Number และตรวจสอบ", type="primary", use_container_width=True):
    
    # รวบรวมพารามิเตอร์
    params = {
        'ZR': ZR,
        'S0': S0,
        'MR': MR_subgrade,
        'delta_PSI': delta_PSI,
    }
    
    # คำนวณ SN ที่ได้จากโครงสร้าง
    layers = [
        {'name': surface_material, 'a': a1, 'D_inch': D1_inch, 'm': m1},
        {'name': base_material, 'a': a2, 'D_inch': D2_inch, 'm': m2},
        {'name': subbase_material, 'a': a3, 'D_inch': D3_inch, 'm': m3},
    ]
    
    SN_provided, sn_details = calculate_SN(layers)
    
    # คำนวณ SN ที่ต้องการ
    SN_required = find_required_SN(W18_input, params)
    
    if SN_required is None or SN_required > 15:
        st.error("❌ ไม่สามารถคำนวณได้ กรุณาตรวจสอบพารามิเตอร์")
    else:
        st.subheader("📊 ผลการคำนวณ")
        
        # แสดงตารางโครงสร้าง
        st.markdown("##### ตารางโครงสร้างชั้นทาง")
        
        structure_data = []
        for d in sn_details:
            structure_data.append({
                "ชั้น": f"{d['layer']}. {d['name'][:30]}",
                "a": d['a'],
                "D (ซม.)": d['D_cm'],
                "D (นิ้ว)": d['D_inch'],
                "m": d['m'],
                "SN = a×D×m": d['SN_layer'],
            })
        
        df_structure = pd.DataFrame(structure_data)
        st.dataframe(
            df_structure,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ชั้น": st.column_config.TextColumn("ชั้นโครงสร้าง", width="large"),
                "a": st.column_config.NumberColumn("a", format="%.2f"),
                "D (ซม.)": st.column_config.NumberColumn("D (ซม.)", format="%.1f"),
                "D (นิ้ว)": st.column_config.NumberColumn("D (นิ้ว)", format="%.2f"),
                "m": st.column_config.NumberColumn("m", format="%.2f"),
                "SN = a×D×m": st.column_config.NumberColumn("SN", format="%.3f"),
            }
        )
        
        # แสดงการคำนวณ SN
        st.markdown("##### การคำนวณ Structural Number (SN)")
        st.latex(f"SN = a_1 D_1 m_1 + a_2 D_2 m_2 + a_3 D_3 m_3")
        st.latex(f"SN = ({a1:.2f} \\times {D1_inch:.2f} \\times {m1:.2f}) + ({a2:.2f} \\times {D2_inch:.2f} \\times {m2:.2f}) + ({a3:.2f} \\times {D3_inch:.2f} \\times {m3:.2f})")
        st.latex(f"SN = {a1*D1_inch*m1:.3f} + {a2*D2_inch*m2:.3f} + {a3*D3_inch*m3:.3f} = {SN_provided:.3f}")
        
        st.markdown("---")
        
        # แสดงผลลัพธ์หลัก
        res_col1, res_col2, res_col3, res_col4 = st.columns(4)
        
        with res_col1:
            st.metric(
                "SN ที่ต้องการ",
                f"{SN_required:.3f}",
                help="Structural Number ที่ต้องการจาก W₁₈"
            )
        
        with res_col2:
            diff = SN_provided - SN_required
            st.metric(
                "SN ที่ได้",
                f"{SN_provided:.3f}",
                f"{diff:+.3f}",
                delta_color="normal" if diff >= 0 else "inverse"
            )
        
        with res_col3:
            log_W18_provided = calculate_log_W18_flexible(SN_provided, params)
            W18_provided = 10 ** log_W18_provided
            margin = (W18_provided / W18_input - 1) * 100
            
            st.metric(
                "W₁₈ รองรับได้",
                f"{W18_provided/1e6:.2f} ล้าน",
                f"{margin:+.1f}%"
            )
        
        with res_col4:
            st.metric(
                "ความหนารวม",
                f"{total_thickness_cm:.0f} ซม.",
                f"({total_thickness_inch:.2f} นิ้ว)"
            )
        
        # ผลการตรวจสอบ
        if SN_provided >= SN_required:
            st.success(f"✅ **ผ่านการตรวจสอบ** - SN ที่ได้ ({SN_provided:.3f}) ≥ SN ที่ต้องการ ({SN_required:.3f})")
        else:
            st.error(f"❌ **ไม่ผ่านการตรวจสอบ** - SN ที่ได้ ({SN_provided:.3f}) < SN ที่ต้องการ ({SN_required:.3f})")
            SN_deficit = SN_required - SN_provided
            st.warning(f"⚠️ ต้องเพิ่ม SN อีก **{SN_deficit:.3f}** โดยการเพิ่มความหนาหรือเปลี่ยนวัสดุ")
        
        # ========================
        # ตารางเปรียบเทียบ SN ต่างๆ
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
                "W₁₈ รองรับได้ (ESAL)": f"{W18_test:,.0f}",
                "W₁₈ (ล้าน)": f"{W18_test/1e6:.2f}",
                "อัตราส่วน": f"{ratio:.2f}",
                "ส่วนเผื่อ (%)": f"{margin_pct:+.1f}%",
                "สถานะ": status,
                "W18_raw": W18_test,
            })
        
        df_comparison = pd.DataFrame(comparison_data)
        df_display = df_comparison[["SN", "log₁₀(W₁₈)", "W₁₈ รองรับได้ (ESAL)", "W₁₈ (ล้าน)", "อัตราส่วน", "ส่วนเผื่อ (%)", "สถานะ"]]
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # กราฟ
        chart_col1, chart_col2 = st.columns([2, 1])
        
        with chart_col1:
            chart_data = pd.DataFrame({
                "SN": SN_options,
                "W₁₈ (ล้าน ESAL)": [d["W18_raw"] / 1e6 for d in comparison_data],
            })
            st.bar_chart(chart_data.set_index("SN"), use_container_width=True)
            st.caption(f"🔴 W₁₈ ออกแบบ = {W18_input/1e6:.2f} ล้าน ESAL | SN ที่ได้ = {SN_provided:.3f}")
        
        with chart_col2:
            st.markdown("**สรุปผล:**")
            st.write(f"**W₁₈ ออกแบบ:** {W18_input:,} ESAL")
            st.write(f"**SN ที่ต้องการ:** {SN_required:.3f}")
            st.write(f"**SN ที่ได้:** {SN_provided:.3f}")
            
            if SN_provided >= SN_required:
                st.success(f"✅ ผ่าน (+{(SN_provided-SN_required)/SN_required*100:.1f}%)")
            else:
                st.error(f"❌ ไม่ผ่าน ({(SN_provided-SN_required)/SN_required*100:.1f}%)")
        
        # สรุปพารามิเตอร์
        with st.expander("📋 สรุปพารามิเตอร์ที่ใช้ในการคำนวณ"):
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
                **Subgrade**
                - M_R = {MR_subgrade:,} psi
                - CBR ≈ {CBR_display:.1f}%
                """)

# ==========================================
# ตารางข้อมูลวัสดุ
# ==========================================
st.markdown("---")

with st.expander("📋 ตารางค่า สปส. สำหรับออกแบบ (ฐานข้อมูลวัสดุ)"):
    
    st.markdown("##### ค่าสัมประสิทธิ์ชั้นทาง (Layer Coefficients)")
    
    all_materials = []
    for category, materials in MATERIAL_DATABASE.items():
        if category == "subgrade":
            continue
        for name, props in materials.items():
            all_materials.append({
                "วัสดุชั้นทาง": name,
                "a": props.get("a", "-"),
                "m": props.get("m", "-"),
                "MR (psi)": f"{props.get('MR_psi', 0):,}",
                "MR (MPa)": props.get("MR_MPa", 0),
            })
    
    # เพิ่มดินฐานราก
    for name, props in MATERIAL_DATABASE["subgrade"].items():
        all_materials.append({
            "วัสดุชั้นทาง": name,
            "a": "-",
            "m": "-",
            "MR (psi)": f"{props.get('MR_psi', 0):,}",
            "MR (MPa)": props.get("MR_MPa", 0),
        })
    
    df_materials = pd.DataFrame(all_materials)
    st.dataframe(df_materials, use_container_width=True, hide_index=True)

with st.expander("📚 สมการ AASHTO 1993 สำหรับ Flexible Pavement"):
    st.markdown("""
    ### สมการหลัก
    
    $$\\log W_{18} = Z_R S_0 + 9.36 \\log(SN+1) - 0.20 + \\frac{\\log[\\Delta PSI / (4.2-1.5)]}{0.40 + \\frac{1094}{(SN+1)^{5.19}}} + 2.32 \\log(M_R) - 8.07$$
    
    ### Structural Number (SN)
    
    $$SN = a_1 D_1 m_1 + a_2 D_2 m_2 + a_3 D_3 m_3$$
    
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
    
    **อ้างอิง:** AASHTO Guide for Design of Pavement Structures (1993)
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>พัฒนาสำหรับการเรียนการสอนวิชาวิศวกรรมทาง</p>
    <p>ภาควิชาครุศาสตร์โยธา มหาวิทยาลัยเทคโนโลยีพระจอมเกล้าพระนครเหนือ</p>
</div>
""", unsafe_allow_html=True)

"""
โปรแกรมออกแบบโครงสร้างชั้นทางคอนกรีต (Rigid Pavement Design)
ตามวิธี AASHTO Guide for Design of Pavement Structures 1993

พัฒนาโดย: Claude AI
สำหรับ: อาจารย์อิทธิพล, ภาควิชาครุศาสตร์โยธา, มจพ.
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import math

# =============================================
# Page Configuration
# =============================================
st.set_page_config(
    page_title="AASHTO 1993 Rigid Pavement Design",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================
# Custom CSS
# =============================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: bold;
        color: #1E3A5F;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #E8F4FD 0%, #D1E8FA 100%);
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    .sub-header {
        font-size: 1.3rem;
        color: #2E5077;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
        margin-top: 1.5rem;
    }
    .result-box {
        background-color: #E8F8F5;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #27AE60;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #FDF2E9;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #E67E22;
    }
    .info-box {
        background-color: #EBF5FB;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #3498DB;
    }
    .layer-input {
        background-color: #F8F9FA;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# =============================================
# Header
# =============================================
st.markdown('<div class="main-header">🛣️ การออกแบบโครงสร้างชั้นทางคอนกรีต<br>AASHTO Guide 1993</div>', unsafe_allow_html=True)

# =============================================
# Sidebar - Design Parameters
# =============================================
st.sidebar.header("📊 พารามิเตอร์การออกแบบ")

# Traffic Parameters
st.sidebar.subheader("🚛 ข้อมูลจราจร")
W18 = st.sidebar.number_input(
    "ESAL (W₁₈) - 18-kip Equivalent Single Axle Load",
    min_value=1e5,
    max_value=1e9,
    value=5e6,
    format="%.2e",
    help="จำนวนเพลาสมมูลมาตรฐาน 18,000 ปอนด์ ตลอดอายุการใช้งาน"
)

# Reliability Parameters
st.sidebar.subheader("📈 ความน่าเชื่อถือ")
R = st.sidebar.slider(
    "Reliability (R) %",
    min_value=50,
    max_value=99,
    value=90,
    help="ความน่าเชื่อถือของการออกแบบ"
)

# Standard Normal Deviate (ZR) lookup table
ZR_table = {
    50: 0.000, 60: -0.253, 70: -0.524, 75: -0.674,
    80: -0.841, 85: -1.037, 90: -1.282, 91: -1.340,
    92: -1.405, 93: -1.476, 94: -1.555, 95: -1.645,
    96: -1.751, 97: -1.881, 98: -2.054, 99: -2.327
}
ZR = ZR_table.get(R, -1.282)

So = st.sidebar.number_input(
    "Overall Standard Deviation (S₀)",
    min_value=0.30,
    max_value=0.50,
    value=0.35,
    step=0.01,
    help="ค่าเบี่ยงเบนมาตรฐานรวม (แนะนำ 0.30-0.40 สำหรับ Rigid)"
)

# Serviceability
st.sidebar.subheader("📉 Serviceability")
Pi = st.sidebar.number_input(
    "Initial Serviceability (P₀)",
    min_value=4.0,
    max_value=5.0,
    value=4.5,
    step=0.1,
    help="ค่าดัชนีความสามารถใช้งานเริ่มต้น"
)

Pt = st.sidebar.number_input(
    "Terminal Serviceability (Pₜ)",
    min_value=1.5,
    max_value=3.5,
    value=2.5,
    step=0.1,
    help="ค่าดัชนีความสามารถใช้งานสุดท้าย (ค่า PT)"
)

delta_PSI = Pi - Pt

# Drainage Coefficient
st.sidebar.subheader("💧 Drainage")
Cd = st.sidebar.number_input(
    "Drainage Coefficient (Cₐ)",
    min_value=0.70,
    max_value=1.25,
    value=1.00,
    step=0.05,
    help="สัมประสิทธิ์การระบายน้ำ (0.70-1.25)"
)

# Load Transfer
st.sidebar.subheader("🔗 Load Transfer")
J = st.sidebar.number_input(
    "Load Transfer Coefficient (J)",
    min_value=2.5,
    max_value=4.4,
    value=3.2,
    step=0.1,
    help="สัมประสิทธิ์การถ่ายแรง (2.5-3.2 มี dowel, 3.8-4.4 ไม่มี dowel)"
)

# =============================================
# Main Content - Material Properties
# =============================================
col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown('<div class="sub-header">🧱 คุณสมบัติวัสดุคอนกรีต</div>', unsafe_allow_html=True)
    
    col_sc, col_ec = st.columns(2)
    with col_sc:
        Sc = st.number_input(
            "กำลังดัดคอนกรีต Sc' (psi)",
            min_value=400,
            max_value=900,
            value=650,
            step=10,
            help="Modulus of Rupture (28 วัน)"
        )
    with col_ec:
        Ec = st.number_input(
            "Modulus of Elasticity Ec (psi)",
            min_value=2e6,
            max_value=6e6,
            value=4e6,
            format="%.2e",
            help="ค่าโมดูลัสยืดหยุ่นของคอนกรีต"
        )
    
    st.markdown('<div class="sub-header">🌍 คุณสมบัติชั้นดินเดิม (Subgrade)</div>', unsafe_allow_html=True)
    
    col_k, col_ls = st.columns(2)
    with col_k:
        k_subgrade = st.number_input(
            "Modulus of Subgrade Reaction k (pci)",
            min_value=50,
            max_value=800,
            value=150,
            step=10,
            help="ค่าโมดูลัสปฏิกิริยาของดินเดิม"
        )
    with col_ls:
        LS = st.number_input(
            "Loss of Support (LS)",
            min_value=0.0,
            max_value=3.0,
            value=1.0,
            step=0.5,
            help="ค่าการสูญเสียการรองรับ (0-3)"
        )

# =============================================
# Layer Input Section
# =============================================
st.markdown('<div class="sub-header">📚 ข้อมูลชั้นทาง (5 ชั้น)</div>', unsafe_allow_html=True)

# Material Types
material_types = [
    "PCC (Portland Cement Concrete)",
    "Cement Treated Base (CTB)",
    "Lime Treated Base (LTB)",
    "Asphalt Treated Base (ATB)",
    "Crushed Stone Base",
    "Soil Cement",
    "Granular Subbase",
    "Sand Subbase",
    "Improved Subgrade",
    "Natural Subgrade",
    "ไม่ใช้ชั้นนี้"
]

# Default modulus values (psi)
default_modulus = {
    "PCC (Portland Cement Concrete)": 4000000,
    "Cement Treated Base (CTB)": 1000000,
    "Lime Treated Base (LTB)": 40000,
    "Asphalt Treated Base (ATB)": 350000,
    "Crushed Stone Base": 30000,
    "Soil Cement": 500000,
    "Granular Subbase": 20000,
    "Sand Subbase": 15000,
    "Improved Subgrade": 10000,
    "Natural Subgrade": 5000,
    "ไม่ใช้ชั้นนี้": 0
}

# Colors for visualization
material_colors = {
    "PCC (Portland Cement Concrete)": "#808080",  # Gray
    "Cement Treated Base (CTB)": "#D2B48C",  # Tan
    "Lime Treated Base (LTB)": "#F5DEB3",  # Wheat
    "Asphalt Treated Base (ATB)": "#2C2C2C",  # Dark gray
    "Crushed Stone Base": "#A0522D",  # Sienna
    "Soil Cement": "#CD853F",  # Peru
    "Granular Subbase": "#DEB887",  # Burlywood
    "Sand Subbase": "#F4A460",  # Sandy brown
    "Improved Subgrade": "#8B4513",  # Saddle brown
    "Natural Subgrade": "#654321",  # Dark brown
    "ไม่ใช้ชั้นนี้": "#FFFFFF"
}

# Layer names in Thai
layer_names_th = {
    "PCC (Portland Cement Concrete)": "คอนกรีตแผ่นพื้น (PCC)",
    "Cement Treated Base (CTB)": "พื้นทางปรับปรุงด้วยซีเมนต์",
    "Lime Treated Base (LTB)": "พื้นทางปรับปรุงด้วยปูนขาว",
    "Asphalt Treated Base (ATB)": "พื้นทางแอสฟัลต์",
    "Crushed Stone Base": "หินคลุกบดอัด",
    "Soil Cement": "ดินซีเมนต์",
    "Granular Subbase": "รองพื้นทางวัสดุมวลรวม",
    "Sand Subbase": "รองพื้นทางทราย",
    "Improved Subgrade": "ดินเดิมปรับปรุง",
    "Natural Subgrade": "ดินเดิม",
    "ไม่ใช้ชั้นนี้": "-"
}

# Initialize layer data
layers = []

# Create input for each layer
st.markdown("#### กำหนดวัสดุและความหนาแต่ละชั้น")

for i in range(5):
    with st.expander(f"📋 ชั้นที่ {i+1}", expanded=(i < 3)):
        col_mat, col_thick, col_mod = st.columns([2, 1, 1])
        
        with col_mat:
            if i == 0:
                default_idx = 0  # PCC
            elif i == 1:
                default_idx = 1  # CTB
            elif i == 2:
                default_idx = 6  # Granular Subbase
            else:
                default_idx = 10  # ไม่ใช้
            
            material = st.selectbox(
                f"ชนิดวัสดุ",
                material_types,
                index=default_idx,
                key=f"mat_{i}"
            )
        
        with col_thick:
            if material == "ไม่ใช้ชั้นนี้":
                thickness = 0.0
                st.number_input("ความหนา (นิ้ว)", value=0.0, disabled=True, key=f"thick_{i}")
            else:
                if i == 0:
                    default_thick = 10.0
                elif i == 1:
                    default_thick = 6.0
                elif i == 2:
                    default_thick = 6.0
                else:
                    default_thick = 4.0
                
                thickness = st.number_input(
                    "ความหนา (นิ้ว)",
                    min_value=0.0,
                    max_value=24.0,
                    value=default_thick,
                    step=0.5,
                    key=f"thick_{i}"
                )
        
        with col_mod:
            if material == "ไม่ใช้ชั้นนี้":
                modulus = 0
                st.number_input("Modulus (psi)", value=0, disabled=True, key=f"mod_{i}")
            else:
                modulus = st.number_input(
                    "Modulus (psi)",
                    min_value=1000,
                    max_value=10000000,
                    value=default_modulus[material],
                    format="%d",
                    key=f"mod_{i}"
                )
        
        layers.append({
            "material": material,
            "thickness": thickness,
            "modulus": modulus,
            "color": material_colors[material],
            "name_th": layer_names_th[material]
        })

# =============================================
# Calculate Composite k-value (k-effective)
# =============================================
def calculate_composite_k(k_subgrade, layers, Ec):
    """
    คำนวณ Composite Modulus of Subgrade Reaction
    ตาม AASHTO 1993 Figure 3.3
    """
    # Get subbase/base layers (exclude PCC - layer 0)
    subbase_layers = [l for l in layers[1:] if l["material"] != "ไม่ใช้ชั้นนี้" and l["thickness"] > 0]
    
    if not subbase_layers:
        return k_subgrade
    
    # Calculate total subbase thickness
    total_subbase_thickness = sum(l["thickness"] for l in subbase_layers)
    
    # Calculate weighted average modulus of subbase
    if total_subbase_thickness > 0:
        weighted_modulus = sum(l["modulus"] * l["thickness"] for l in subbase_layers) / total_subbase_thickness
    else:
        weighted_modulus = k_subgrade
    
    # Composite k calculation using AASHTO method
    # k_composite = k_subgrade * (1 + (Dsb/19.4) * (Esb/k_subgrade)^(1/3))
    # Simplified approach based on Figure 3.3
    
    Dsb = total_subbase_thickness  # inches
    Esb = weighted_modulus  # psi
    
    # Calculate composite k (simplified AASHTO approach)
    # Based on subbase thickness and modulus improvement
    improvement_factor = 1 + (Dsb / 20) * (Esb / 30000) ** 0.33
    k_composite = min(k_subgrade * improvement_factor, 800)  # Max k = 800 pci
    
    return k_composite

# Calculate k_composite
k_composite = calculate_composite_k(k_subgrade, layers, Ec)

# Apply Loss of Support factor
# k_effective = k_composite * 10^(-LS/3) (approximation based on AASHTO Figure 3.6)
k_effective = k_composite * (10 ** (-LS / 3))
k_effective = max(k_effective, 25)  # Minimum k_effective

# =============================================
# AASHTO 1993 Rigid Pavement Design Equation
# =============================================
def calculate_log_W18(D, ZR, So, delta_PSI, Sc, Cd, J, Ec, k):
    """
    AASHTO 1993 Rigid Pavement Design Equation
    
    log10(W18) = ZR*So + 7.35*log10(D+1) - 0.06 
                 + log10(ΔPSI/(4.5-1.5)) / (1 + (1.624*10^7)/((D+1)^8.46))
                 + (4.22 - 0.32*Pt) * log10(Sc*Cd*(D^0.75 - 1.132) / (215.63*J*(D^0.75 - 18.42/(Ec/k)^0.25)))
    """
    # Term 1
    term1 = ZR * So
    
    # Term 2
    term2 = 7.35 * np.log10(D + 1) - 0.06
    
    # Term 3 (Serviceability loss term)
    numerator3 = np.log10(delta_PSI / (4.5 - 1.5))
    denominator3 = 1 + (1.624e7) / ((D + 1) ** 8.46)
    term3 = numerator3 / denominator3
    
    # Term 4 (Combined stiffness term)
    Pt_val = 4.5 - delta_PSI  # Terminal serviceability
    coeff4 = 4.22 - 0.32 * Pt_val
    
    # Check for valid D values
    D_power = D ** 0.75
    Ec_k_ratio = (Ec / k) ** 0.25
    
    numerator4 = Sc * Cd * (D_power - 1.132)
    denominator4 = 215.63 * J * (D_power - 18.42 / Ec_k_ratio)
    
    if denominator4 <= 0 or numerator4 <= 0:
        return -999  # Invalid
    
    term4 = coeff4 * np.log10(numerator4 / denominator4)
    
    log_W18 = term1 + term2 + term3 + term4
    
    return log_W18

def find_required_thickness(W18, ZR, So, delta_PSI, Sc, Cd, J, Ec, k):
    """
    ค้นหาความหนาที่ต้องการโดยใช้ Iterative method
    """
    target_log_W18 = np.log10(W18)
    
    # Binary search for D
    D_min, D_max = 6.0, 16.0  # inches
    tolerance = 0.01
    
    for _ in range(100):
        D_mid = (D_min + D_max) / 2
        calc_log_W18 = calculate_log_W18(D_mid, ZR, So, delta_PSI, Sc, Cd, J, Ec, k)
        
        if calc_log_W18 == -999:
            D_min = D_mid
            continue
        
        if abs(calc_log_W18 - target_log_W18) < tolerance:
            return D_mid
        
        if calc_log_W18 < target_log_W18:
            D_min = D_mid
        else:
            D_max = D_mid
    
    return D_mid

# =============================================
# Calculate Required Thickness
# =============================================
st.markdown("---")
st.markdown('<div class="sub-header">📐 ผลการคำนวณ</div>', unsafe_allow_html=True)

# Calculate required thickness
D_required = find_required_thickness(W18, ZR, So, delta_PSI, Sc, Cd, J, Ec, k_effective)
D_design = np.ceil(D_required * 2) / 2  # Round up to nearest 0.5 inch

# Update layer 0 (PCC) thickness with calculated value
layers[0]["thickness"] = D_design

# Calculate verification
log_W18_check = calculate_log_W18(D_design, ZR, So, delta_PSI, Sc, Cd, J, Ec, k_effective)
W18_capacity = 10 ** log_W18_check if log_W18_check > 0 else 0

# Display results
col_res1, col_res2, col_res3 = st.columns(3)

with col_res1:
    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    st.metric(
        label="ความหนา PCC ที่ต้องการ",
        value=f"{D_required:.2f} นิ้ว",
        delta=f"({D_required * 2.54:.1f} ซม.)"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col_res2:
    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    st.metric(
        label="ความหนาออกแบบ (ปัดเศษ)",
        value=f"{D_design:.1f} นิ้ว",
        delta=f"({D_design * 2.54:.1f} ซม.)"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col_res3:
    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    st.metric(
        label="k-effective",
        value=f"{k_effective:.1f} pci",
        delta=f"จาก k = {k_subgrade} pci"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Detail calculation results
with st.expander("📊 รายละเอียดการคำนวณ", expanded=True):
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        st.markdown("**พารามิเตอร์ที่ใช้ในการคำนวณ:**")
        st.write(f"- ESAL (W₁₈) = {W18:,.0f}")
        st.write(f"- Reliability (R) = {R}%")
        st.write(f"- Standard Normal Deviate (ZR) = {ZR:.3f}")
        st.write(f"- Standard Deviation (S₀) = {So}")
        st.write(f"- ΔPSI = {delta_PSI:.1f}")
        st.write(f"- Drainage Coefficient (Cd) = {Cd}")
        st.write(f"- Load Transfer (J) = {J}")
    
    with col_d2:
        st.markdown("**คุณสมบัติวัสดุ:**")
        st.write(f"- Modulus of Rupture (Sc') = {Sc} psi")
        st.write(f"- Concrete Modulus (Ec) = {Ec:,.0f} psi")
        st.write(f"- Subgrade k = {k_subgrade} pci")
        st.write(f"- Composite k = {k_composite:.1f} pci")
        st.write(f"- Loss of Support (LS) = {LS}")
        st.write(f"- **k-effective = {k_effective:.1f} pci**")

    st.markdown("**การตรวจสอบ:**")
    st.write(f"- log₁₀(W₁₈) ที่ต้องการ = {np.log10(W18):.4f}")
    st.write(f"- log₁₀(W₁₈) ที่คำนวณได้ = {log_W18_check:.4f}")
    st.write(f"- ความสามารถรับ ESAL = {W18_capacity:,.0f}")

# =============================================
# Draw Pavement Structure
# =============================================
st.markdown("---")
st.markdown('<div class="sub-header">🎨 โครงสร้างชั้นทาง</div>', unsafe_allow_html=True)

# Filter active layers
active_layers = [l for l in layers if l["material"] != "ไม่ใช้ชั้นนี้" and l["thickness"] > 0]

# Create figure
fig, ax = plt.subplots(figsize=(14, 10))
ax.set_xlim(0, 14)

# Calculate total height
total_thickness = sum(l["thickness"] for l in active_layers)
scale_factor = 0.4  # Scale for visualization
base_y = 9  # Starting y position

# Draw title
ax.text(7, 9.8, "โครงสร้างชั้นทางคอนกรีต (Rigid Pavement Structure)", 
        fontsize=16, fontweight='bold', ha='center', va='center',
        fontname='Tahoma')
ax.text(7, 9.4, f"AASHTO 1993 | ความหนา PCC = {D_design:.1f} นิ้ว ({D_design*2.54:.1f} ซม.)", 
        fontsize=12, ha='center', va='center', fontname='Tahoma')

current_y = base_y

# Draw each layer
for i, layer in enumerate(active_layers):
    height = layer["thickness"] * scale_factor
    
    # Draw layer rectangle
    rect = FancyBboxPatch(
        (2, current_y - height), 10, height,
        boxstyle="round,pad=0.02,rounding_size=0.1",
        facecolor=layer["color"],
        edgecolor='black',
        linewidth=2,
        alpha=0.9
    )
    ax.add_patch(rect)
    
    # Add hatch pattern for different materials
    if "PCC" in layer["material"]:
        # Concrete pattern
        for j in range(int(10/0.5)):
            for k in range(int(height/0.3)):
                if (j + k) % 2 == 0:
                    ax.plot(2.2 + j*0.5, current_y - 0.15 - k*0.3, 'o', 
                           color='darkgray', markersize=2, alpha=0.5)
    elif "Crushed" in layer["material"] or "Granular" in layer["material"]:
        # Granular pattern
        for j in range(20):
            for k in range(int(height/0.4)):
                ax.plot(2.5 + j*0.5 + np.random.uniform(-0.1, 0.1), 
                       current_y - 0.2 - k*0.4 + np.random.uniform(-0.05, 0.05), 
                       '.', color='saddlebrown', markersize=3, alpha=0.4)
    
    # Layer name and thickness (left side)
    mid_y = current_y - height/2
    ax.annotate(
        f"{layer['name_th']}",
        xy=(1.8, mid_y),
        ha='right', va='center',
        fontsize=11, fontweight='bold',
        fontname='Tahoma'
    )
    
    # Thickness dimension (right side)
    # Draw dimension lines
    ax.annotate('', xy=(12.3, current_y), xytext=(12.3, current_y - height),
                arrowprops=dict(arrowstyle='<->', color='red', lw=1.5))
    
    ax.text(12.8, mid_y, f'{layer["thickness"]:.1f}"', 
            fontsize=11, fontweight='bold', va='center',
            color='red', fontname='Arial')
    ax.text(13.5, mid_y, f'({layer["thickness"]*2.54:.1f} cm)', 
            fontsize=9, va='center', color='darkred', fontname='Arial')
    
    # Modulus annotation
    if layer["modulus"] > 0:
        if layer["modulus"] >= 1e6:
            mod_text = f'E = {layer["modulus"]/1e6:.1f} Mpsi'
        else:
            mod_text = f'E = {layer["modulus"]:,} psi'
        ax.text(7, mid_y, mod_text, fontsize=9, ha='center', va='center',
               fontname='Arial', style='italic', alpha=0.8,
               bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))
    
    current_y -= height

# Draw subgrade
subgrade_height = 1.5
rect_sub = FancyBboxPatch(
    (2, current_y - subgrade_height), 10, subgrade_height,
    boxstyle="round,pad=0.02,rounding_size=0.1",
    facecolor='#8B4513',
    edgecolor='black',
    linewidth=2,
    alpha=0.7
)
ax.add_patch(rect_sub)

# Subgrade pattern
for j in range(25):
    for k in range(3):
        ax.plot(2.3 + j*0.4 + np.random.uniform(-0.05, 0.05), 
               current_y - 0.25 - k*0.5 + np.random.uniform(-0.05, 0.05), 
               '.', color='#654321', markersize=2, alpha=0.5)

ax.text(1.8, current_y - subgrade_height/2, "ชั้นดินเดิม (Subgrade)", 
        ha='right', va='center', fontsize=11, fontweight='bold', fontname='Tahoma')
ax.text(7, current_y - subgrade_height/2, f'k = {k_subgrade} pci', 
        ha='center', va='center', fontsize=9, fontname='Arial', style='italic',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))

# Draw total thickness
total_height_drawn = (base_y) - (current_y)
ax.annotate('', xy=(0.8, base_y), xytext=(0.8, current_y),
            arrowprops=dict(arrowstyle='<->', color='blue', lw=2))
total_inch = sum(l["thickness"] for l in active_layers)
ax.text(0.5, (base_y + current_y)/2, f'รวม\n{total_inch:.1f}"', 
        fontsize=10, ha='center', va='center', fontweight='bold',
        color='blue', fontname='Tahoma',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.9))

# Design info box
info_text = (
    f"Design Parameters:\n"
    f"ESAL = {W18:,.0f}\n"
    f"R = {R}%, ZR = {ZR:.3f}\n"
    f"Sc' = {Sc} psi\n"
    f"k-eff = {k_effective:.1f} pci\n"
    f"Cd = {Cd}, J = {J}"
)
ax.text(13.8, base_y - 1, info_text, fontsize=8, fontname='Arial',
        va='top', ha='left',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#E8F4FD', 
                 edgecolor='#3498db', alpha=0.9))

# Set axis properties
ax.set_ylim(current_y - subgrade_height - 0.5, 10.2)
ax.set_aspect('equal')
ax.axis('off')

# Add grid background
ax.set_facecolor('#FAFAFA')

plt.tight_layout()
st.pyplot(fig)

# =============================================
# Summary Table
# =============================================
st.markdown('<div class="sub-header">📋 สรุปโครงสร้างชั้นทาง</div>', unsafe_allow_html=True)

summary_data = []
for i, layer in enumerate(active_layers):
    summary_data.append({
        "ลำดับ": i + 1,
        "ชนิดวัสดุ": layer["name_th"],
        "ความหนา (นิ้ว)": layer["thickness"],
        "ความหนา (ซม.)": round(layer["thickness"] * 2.54, 1),
        "Modulus (psi)": f"{layer['modulus']:,}"
    })

import pandas as pd
df_summary = pd.DataFrame(summary_data)
st.dataframe(df_summary, use_container_width=True, hide_index=True)

# Total
st.markdown(f"""
<div class="info-box">
<b>สรุป:</b><br>
• ความหนารวมของโครงสร้างชั้นทาง = <b>{sum(l['thickness'] for l in active_layers):.1f} นิ้ว ({sum(l['thickness'] for l in active_layers)*2.54:.1f} ซม.)</b><br>
• ความหนาแผ่นพื้นคอนกรีต (PCC) ที่ต้องการ = <b>{D_required:.2f} นิ้ว</b><br>
• ความหนาแผ่นพื้นคอนกรีต (PCC) ออกแบบ = <b>{D_design:.1f} นิ้ว ({D_design*2.54:.1f} ซม.)</b><br>
• k-effective = <b>{k_effective:.1f} pci</b>
</div>
""", unsafe_allow_html=True)

# =============================================
# Footer
# =============================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.9rem;">
    📚 อ้างอิง: AASHTO Guide for Design of Pavement Structures, 1993<br>
    🏫 ภาควิชาครุศาสตร์โยธา คณะครุศาสตร์อุตสาหกรรม มหาวิทยาลัยเทคโนโลยีพระจอมเกล้าพระนครเหนือ
</div>
""", unsafe_allow_html=True)

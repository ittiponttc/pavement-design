"""
โปรแกรมออกแบบโครงสร้างชั้นทางคอนกรีต (Rigid Pavement Design)
ตามวิธี AASHTO Guide for Design of Pavement Structures 1993

พัฒนาโดย: Claude AI
สำหรับ: อาจารย์อิทธิพล, ภาควิชาครุศาสตร์โยธา, มจพ.
"""

import streamlit as st
import numpy as np
import math
import pandas as pd

# Import matplotlib with proper backend
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

# Configure matplotlib
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# =============================================
# Unit Conversion Constants
# =============================================
KSC_TO_PSI = 14.223          # 1 ksc = 14.223 psi
PSI_TO_KSC = 1 / 14.223      # 1 psi = 0.0703 ksc
CM_TO_INCH = 1 / 2.54        # 1 cm = 0.3937 inch
INCH_TO_CM = 2.54            # 1 inch = 2.54 cm
MPA_TO_PSI = 145.038         # 1 MPa = 145.038 psi
PSI_TO_MPA = 1 / 145.038     # 1 psi = 0.006895 MPa
PCI_TO_MPA_M = 0.2714        # 1 pci = 0.2714 MPa/m (MN/m³)
MPA_M_TO_PCI = 1 / 0.2714    # 1 MPa/m = 3.684 pci

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
    .info-box {
        background-color: #EBF5FB;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #3498DB;
    }
    .unit-note {
        font-size: 0.85rem;
        color: #666;
        font-style: italic;
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
    "ESAL (W₁₈)",
    min_value=1e5,
    max_value=1e9,
    value=5e6,
    format="%.2e",
    help="จำนวนเพลาสมมูลมาตรฐาน 18,000 ปอนด์"
)

# Reliability Parameters
st.sidebar.subheader("📈 ความน่าเชื่อถือ")
R = st.sidebar.slider("Reliability (R) %", min_value=50, max_value=99, value=90)

# Standard Normal Deviate (ZR) lookup table
ZR_table = {
    50: 0.000, 60: -0.253, 70: -0.524, 75: -0.674,
    80: -0.841, 85: -1.037, 90: -1.282, 91: -1.340,
    92: -1.405, 93: -1.476, 94: -1.555, 95: -1.645,
    96: -1.751, 97: -1.881, 98: -2.054, 99: -2.327
}
ZR = ZR_table.get(R, -1.282)

So = st.sidebar.number_input(
    "Standard Deviation (S₀)",
    min_value=0.30, max_value=0.50, value=0.35, step=0.01
)

# Serviceability
st.sidebar.subheader("📉 Serviceability")
Pi = st.sidebar.number_input("Initial Serviceability (P₀)", min_value=4.0, max_value=5.0, value=4.5, step=0.1)
Pt = st.sidebar.number_input("Terminal Serviceability (Pₜ)", min_value=1.5, max_value=3.5, value=2.5, step=0.1)
delta_PSI = Pi - Pt

# Drainage Coefficient
st.sidebar.subheader("💧 Drainage")
Cd = st.sidebar.number_input("Drainage Coefficient (Cₐ)", min_value=0.70, max_value=1.25, value=1.00, step=0.05)

# Load Transfer
st.sidebar.subheader("🔗 Load Transfer")
J = st.sidebar.number_input("Load Transfer Coefficient (J)", min_value=2.5, max_value=4.4, value=3.2, step=0.1)

# =============================================
# Main Content - Material Properties
# =============================================
col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown('<div class="sub-header">🧱 คุณสมบัติวัสดุคอนกรีต</div>', unsafe_allow_html=True)
    
    col_sc, col_ec = st.columns(2)
    with col_sc:
        # Concrete Modulus of Rupture in ksc
        Sc_ksc = st.number_input(
            "กำลังดัดคอนกรีต Sc' (ksc)",
            min_value=28.0,
            max_value=65.0,
            value=45.0,
            step=1.0,
            help="Modulus of Rupture (28 วัน)"
        )
        Sc_psi = Sc_ksc * KSC_TO_PSI
        st.markdown(f'<span class="unit-note">= {Sc_psi:.1f} psi</span>', unsafe_allow_html=True)
        
    with col_ec:
        # Concrete Modulus of Elasticity in MPa
        Ec_mpa = st.number_input(
            "Modulus of Elasticity Ec (MPa)",
            min_value=15000.0,
            max_value=40000.0,
            value=28000.0,
            step=1000.0,
            help="ค่าโมดูลัสยืดหยุ่นของคอนกรีต"
        )
        Ec_psi = Ec_mpa * MPA_TO_PSI
        st.markdown(f'<span class="unit-note">= {Ec_psi:,.0f} psi</span>', unsafe_allow_html=True)
    
    st.markdown('<div class="sub-header">🌍 คุณสมบัติชั้นดินเดิม (Subgrade)</div>', unsafe_allow_html=True)
    
    col_k, col_ls = st.columns(2)
    with col_k:
        # Modulus of Subgrade Reaction in MPa/m (MN/m³)
        k_subgrade_mpa_m = st.number_input(
            "Modulus of Subgrade Reaction k (MPa/m)",
            min_value=13.0,
            max_value=220.0,
            value=40.0,
            step=5.0,
            help="ค่าโมดูลัสปฏิกิริยาของดินเดิม (MN/m³)"
        )
        k_subgrade_pci = k_subgrade_mpa_m * MPA_M_TO_PCI
        st.markdown(f'<span class="unit-note">= {k_subgrade_pci:.1f} pci</span>', unsafe_allow_html=True)
        
    with col_ls:
        LS = st.number_input("Loss of Support (LS)", min_value=0.0, max_value=3.0, value=1.0, step=0.5)

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
    "Not Used"
]

# Default modulus values in MPa
default_modulus_mpa = {
    "PCC (Portland Cement Concrete)": 28000,
    "Cement Treated Base (CTB)": 7000,
    "Lime Treated Base (LTB)": 280,
    "Asphalt Treated Base (ATB)": 2400,
    "Crushed Stone Base": 200,
    "Soil Cement": 3500,
    "Granular Subbase": 140,
    "Sand Subbase": 100,
    "Improved Subgrade": 70,
    "Natural Subgrade": 35,
    "Not Used": 0
}

# Default thickness in cm
default_thickness_cm = {
    0: 25.0,   # PCC
    1: 15.0,   # CTB
    2: 15.0,   # Granular Subbase
    3: 10.0,
    4: 10.0
}

# Colors for visualization
material_colors = {
    "PCC (Portland Cement Concrete)": "#808080",
    "Cement Treated Base (CTB)": "#D2B48C",
    "Lime Treated Base (LTB)": "#F5DEB3",
    "Asphalt Treated Base (ATB)": "#2C2C2C",
    "Crushed Stone Base": "#A0522D",
    "Soil Cement": "#CD853F",
    "Granular Subbase": "#DEB887",
    "Sand Subbase": "#F4A460",
    "Improved Subgrade": "#8B4513",
    "Natural Subgrade": "#654321",
    "Not Used": "#FFFFFF"
}

# Short names for figure
layer_names_short = {
    "PCC (Portland Cement Concrete)": "PCC",
    "Cement Treated Base (CTB)": "CTB",
    "Lime Treated Base (LTB)": "LTB",
    "Asphalt Treated Base (ATB)": "ATB",
    "Crushed Stone Base": "Crushed Stone",
    "Soil Cement": "Soil Cement",
    "Granular Subbase": "Granular Subbase",
    "Sand Subbase": "Sand Subbase",
    "Improved Subgrade": "Improved Subgrade",
    "Natural Subgrade": "Natural Subgrade",
    "Not Used": "-"
}

# Initialize layer data
layers = []

st.markdown("#### กำหนดวัสดุและความหนาแต่ละชั้น")

for i in range(5):
    with st.expander(f"📋 ชั้นที่ {i+1} (Layer {i+1})", expanded=(i < 3)):
        col_mat, col_thick, col_mod = st.columns([2, 1, 1])
        
        with col_mat:
            if i == 0:
                default_idx = 0
            elif i == 1:
                default_idx = 1
            elif i == 2:
                default_idx = 6
            else:
                default_idx = 10
            
            material = st.selectbox(f"Material Type", material_types, index=default_idx, key=f"mat_{i}")
        
        with col_thick:
            if material == "Not Used":
                thickness_cm = 0.0
                st.number_input("ความหนา (cm)", value=0.0, disabled=True, key=f"thick_{i}")
            else:
                thickness_cm = st.number_input(
                    "ความหนา (cm)", 
                    min_value=0.0, 
                    max_value=60.0,
                    value=default_thickness_cm.get(i, 10.0), 
                    step=1.0, 
                    key=f"thick_{i}"
                )
                thickness_in = thickness_cm * CM_TO_INCH
                st.markdown(f'<span class="unit-note">({thickness_in:.2f} in)</span>', unsafe_allow_html=True)
        
        with col_mod:
            if material == "Not Used":
                modulus_mpa = 0
                st.number_input("Modulus (MPa)", value=0, disabled=True, key=f"mod_{i}")
            else:
                modulus_mpa = st.number_input(
                    "Modulus (MPa)", 
                    min_value=10.0, 
                    max_value=70000.0,
                    value=float(default_modulus_mpa[material]), 
                    step=10.0, 
                    key=f"mod_{i}"
                )
                modulus_psi = modulus_mpa * MPA_TO_PSI
                st.markdown(f'<span class="unit-note">({modulus_psi:,.0f} psi)</span>', unsafe_allow_html=True)
        
        # Convert to inches and psi for calculations
        thickness_in = thickness_cm * CM_TO_INCH
        modulus_psi = modulus_mpa * MPA_TO_PSI
        
        layers.append({
            "material": material,
            "thickness_cm": thickness_cm,
            "thickness_in": thickness_in,
            "modulus_mpa": modulus_mpa,
            "modulus_psi": modulus_psi,
            "color": material_colors[material],
            "name_short": layer_names_short[material]
        })

# =============================================
# Calculate Composite k-value
# =============================================
def calculate_composite_k(k_subgrade_pci, layers, Ec_psi):
    subbase_layers = [l for l in layers[1:] if l["material"] != "Not Used" and l["thickness_in"] > 0]
    
    if not subbase_layers:
        return k_subgrade_pci
    
    total_subbase_thickness = sum(l["thickness_in"] for l in subbase_layers)
    
    if total_subbase_thickness > 0:
        weighted_modulus = sum(l["modulus_psi"] * l["thickness_in"] for l in subbase_layers) / total_subbase_thickness
    else:
        weighted_modulus = k_subgrade_pci
    
    Dsb = total_subbase_thickness
    Esb = weighted_modulus
    
    improvement_factor = 1 + (Dsb / 20) * (Esb / 30000) ** 0.33
    k_composite = min(k_subgrade_pci * improvement_factor, 800)
    
    return k_composite

k_composite_pci = calculate_composite_k(k_subgrade_pci, layers, Ec_psi)
k_effective_pci = k_composite_pci * (10 ** (-LS / 3))
k_effective_pci = max(k_effective_pci, 25)

# Convert k_effective to MPa/m for display
k_effective_mpa_m = k_effective_pci * PCI_TO_MPA_M
k_composite_mpa_m = k_composite_pci * PCI_TO_MPA_M

# =============================================
# AASHTO 1993 Design Equation
# =============================================
def calculate_log_W18(D, ZR, So, delta_PSI, Sc, Cd, J, Ec, k):
    """D in inches, Sc in psi, Ec in psi, k in pci"""
    term1 = ZR * So
    term2 = 7.35 * np.log10(D + 1) - 0.06
    
    numerator3 = np.log10(delta_PSI / (4.5 - 1.5))
    denominator3 = 1 + (1.624e7) / ((D + 1) ** 8.46)
    term3 = numerator3 / denominator3
    
    Pt_val = 4.5 - delta_PSI
    coeff4 = 4.22 - 0.32 * Pt_val
    
    D_power = D ** 0.75
    Ec_k_ratio = (Ec / k) ** 0.25
    
    numerator4 = Sc * Cd * (D_power - 1.132)
    denominator4 = 215.63 * J * (D_power - 18.42 / Ec_k_ratio)
    
    if denominator4 <= 0 or numerator4 <= 0:
        return -999
    
    term4 = coeff4 * np.log10(numerator4 / denominator4)
    
    return term1 + term2 + term3 + term4

def find_required_thickness(W18, ZR, So, delta_PSI, Sc, Cd, J, Ec, k):
    """Returns thickness in inches"""
    target_log_W18 = np.log10(W18)
    D_min, D_max = 6.0, 16.0
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
st.markdown('<div class="sub-header">📐 ผลการคำนวณ (Design Results)</div>', unsafe_allow_html=True)

# Calculate using psi and inches (AASHTO units)
D_required_in = find_required_thickness(W18, ZR, So, delta_PSI, Sc_psi, Cd, J, Ec_psi, k_effective_pci)
D_required_cm = D_required_in * INCH_TO_CM

# Round up to nearest 0.5 cm
D_design_cm = np.ceil(D_required_cm * 2) / 2
D_design_in = D_design_cm * CM_TO_INCH

# Update layer 0 (PCC) thickness
layers[0]["thickness_cm"] = D_design_cm
layers[0]["thickness_in"] = D_design_in

log_W18_check = calculate_log_W18(D_design_in, ZR, So, delta_PSI, Sc_psi, Cd, J, Ec_psi, k_effective_pci)
W18_capacity = 10 ** log_W18_check if log_W18_check > 0 else 0

col_res1, col_res2, col_res3 = st.columns(3)

with col_res1:
    st.metric(
        label="ความหนา PCC ที่ต้องการ",
        value=f"{D_required_cm:.2f} cm",
        delta=f"({D_required_in:.2f} in)"
    )

with col_res2:
    st.metric(
        label="ความหนาออกแบบ (ปัดเศษ)",
        value=f"{D_design_cm:.1f} cm",
        delta=f"({D_design_in:.2f} in)"
    )

with col_res3:
    st.metric(
        label="k-effective",
        value=f"{k_effective_mpa_m:.1f} MPa/m",
        delta=f"({k_effective_pci:.1f} pci)"
    )

# Detail calculation results
with st.expander("📊 รายละเอียดการคำนวณ (Calculation Details)", expanded=True):
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        st.markdown("**Design Parameters:**")
        st.write(f"- ESAL (W₁₈) = {W18:,.0f}")
        st.write(f"- Reliability (R) = {R}%")
        st.write(f"- Standard Normal Deviate (ZR) = {ZR:.3f}")
        st.write(f"- Standard Deviation (S₀) = {So}")
        st.write(f"- ΔPSI = {delta_PSI:.1f}")
        st.write(f"- Drainage Coefficient (Cd) = {Cd}")
        st.write(f"- Load Transfer (J) = {J}")
    
    with col_d2:
        st.markdown("**Material Properties:**")
        st.write(f"- Modulus of Rupture (Sc') = {Sc_ksc} ksc ({Sc_psi:.1f} psi)")
        st.write(f"- Concrete Modulus (Ec) = {Ec_mpa:,.0f} MPa ({Ec_psi:,.0f} psi)")
        st.write(f"- Subgrade k = {k_subgrade_mpa_m:.1f} MPa/m ({k_subgrade_pci:.1f} pci)")
        st.write(f"- Composite k = {k_composite_mpa_m:.1f} MPa/m ({k_composite_pci:.1f} pci)")
        st.write(f"- Loss of Support (LS) = {LS}")
        st.write(f"- **k-effective = {k_effective_mpa_m:.1f} MPa/m ({k_effective_pci:.1f} pci)**")

# =============================================
# Draw Pavement Structure
# =============================================
st.markdown("---")
st.markdown('<div class="sub-header">🎨 Pavement Structure Diagram</div>', unsafe_allow_html=True)

active_layers = [l for l in layers if l["material"] != "Not Used" and l["thickness_cm"] > 0]

fig, ax = plt.subplots(figsize=(14, 10))
ax.set_xlim(0, 14)

scale_factor = 0.12  # Scale for cm visualization
base_y = 9

# Draw title
ax.text(7, 9.8, "Rigid Pavement Structure (AASHTO 1993)", 
        fontsize=16, fontweight='bold', ha='center', va='center')
ax.text(7, 9.4, f"PCC Thickness = {D_design_cm:.1f} cm ({D_design_in:.2f} in)", 
        fontsize=12, ha='center', va='center')

current_y = base_y

# Draw each layer
for i, layer in enumerate(active_layers):
    height = layer["thickness_cm"] * scale_factor
    
    rect = FancyBboxPatch(
        (2, current_y - height), 10, height,
        boxstyle="round,pad=0.02,rounding_size=0.1",
        facecolor=layer["color"],
        edgecolor='black',
        linewidth=2,
        alpha=0.9
    )
    ax.add_patch(rect)
    
    # Add texture patterns
    if "PCC" in layer["material"]:
        for j in range(int(10/0.5)):
            for k in range(max(1, int(height/0.3))):
                if (j + k) % 2 == 0:
                    ax.plot(2.2 + j*0.5, current_y - 0.15 - k*0.3, 'o', 
                           color='darkgray', markersize=2, alpha=0.5)
    elif "Crushed" in layer["material"] or "Granular" in layer["material"]:
        np.random.seed(42 + i)
        for j in range(20):
            for k in range(max(1, int(height/0.4))):
                ax.plot(2.5 + j*0.5 + np.random.uniform(-0.1, 0.1), 
                       current_y - 0.2 - k*0.4 + np.random.uniform(-0.05, 0.05), 
                       '.', color='saddlebrown', markersize=3, alpha=0.4)
    
    mid_y = current_y - height/2
    
    # Layer name (left side)
    ax.annotate(layer['name_short'], xy=(1.8, mid_y), ha='right', va='center',
                fontsize=11, fontweight='bold')
    
    # Dimension lines (right side)
    ax.annotate('', xy=(12.3, current_y), xytext=(12.3, current_y - height),
                arrowprops=dict(arrowstyle='<->', color='red', lw=1.5))
    
    # Show thickness in cm (in)
    ax.text(12.8, mid_y, f'{layer["thickness_cm"]:.1f} cm', 
            fontsize=11, fontweight='bold', va='center', color='red')
    ax.text(13.6, mid_y, f'({layer["thickness_in"]:.2f} in)', 
            fontsize=9, va='center', color='darkred')
    
    # Modulus annotation in MPa (psi)
    if layer["modulus_mpa"] > 0:
        if layer["modulus_mpa"] >= 1000:
            mod_text = f'E = {layer["modulus_mpa"]/1000:.1f} GPa'
        else:
            mod_text = f'E = {layer["modulus_mpa"]:.0f} MPa'
        ax.text(7, mid_y, mod_text, fontsize=9, ha='center', va='center',
               style='italic', alpha=0.8,
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

np.random.seed(123)
for j in range(25):
    for k in range(3):
        ax.plot(2.3 + j*0.4 + np.random.uniform(-0.05, 0.05), 
               current_y - 0.25 - k*0.5 + np.random.uniform(-0.05, 0.05), 
               '.', color='#654321', markersize=2, alpha=0.5)

ax.text(1.8, current_y - subgrade_height/2, "Subgrade", 
        ha='right', va='center', fontsize=11, fontweight='bold')
ax.text(7, current_y - subgrade_height/2, f'k = {k_subgrade_mpa_m:.1f} MPa/m ({k_subgrade_pci:.1f} pci)', 
        ha='center', va='center', fontsize=9, style='italic',
        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))

# Total thickness dimension
ax.annotate('', xy=(0.8, base_y), xytext=(0.8, current_y),
            arrowprops=dict(arrowstyle='<->', color='blue', lw=2))
total_cm = sum(l["thickness_cm"] for l in active_layers)
total_in = total_cm * CM_TO_INCH
ax.text(0.5, (base_y + current_y)/2, f'Total\n{total_cm:.1f} cm', 
        fontsize=10, ha='center', va='center', fontweight='bold', color='blue',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.9))

# Design info box
info_text = (
    f"Design Parameters:\n"
    f"ESAL = {W18:,.0f}\n"
    f"R = {R}%, ZR = {ZR:.3f}\n"
    f"Sc' = {Sc_ksc} ksc\n"
    f"k-eff = {k_effective_mpa_m:.1f} MPa/m\n"
    f"Cd = {Cd}, J = {J}"
)
ax.text(13.8, base_y - 1, info_text, fontsize=8, va='top', ha='left',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#E8F4FD', 
                 edgecolor='#3498db', alpha=0.9))

ax.set_ylim(current_y - subgrade_height - 0.5, 10.2)
ax.set_aspect('equal')
ax.axis('off')
ax.set_facecolor('#FAFAFA')

plt.tight_layout()
st.pyplot(fig)

# =============================================
# Summary Table
# =============================================
st.markdown('<div class="sub-header">📋 Pavement Structure Summary</div>', unsafe_allow_html=True)

summary_data = []
for i, layer in enumerate(active_layers):
    summary_data.append({
        "Layer": i + 1,
        "Material": layer["name_short"],
        "Thickness (cm)": f"{layer['thickness_cm']:.1f}",
        "Thickness (in)": f"{layer['thickness_in']:.2f}",
        "Modulus (MPa)": f"{layer['modulus_mpa']:,.0f}",
        "Modulus (psi)": f"{layer['modulus_psi']:,.0f}"
    })

df_summary = pd.DataFrame(summary_data)
st.dataframe(df_summary, use_container_width=True, hide_index=True)

# Total Summary
total_thickness_cm = sum(l['thickness_cm'] for l in active_layers)
total_thickness_in = total_thickness_cm * CM_TO_INCH

st.markdown(f"""
<div class="info-box">
<b>สรุปผลการออกแบบ (Design Summary):</b><br>
• ความหนารวมของโครงสร้างชั้นทาง = <b>{total_thickness_cm:.1f} cm ({total_thickness_in:.2f} in)</b><br>
• ความหนา PCC ที่ต้องการ = <b>{D_required_cm:.2f} cm ({D_required_in:.2f} in)</b><br>
• ความหนา PCC ออกแบบ = <b>{D_design_cm:.1f} cm ({D_design_in:.2f} in)</b><br>
• กำลังดัดคอนกรีต (Sc') = <b>{Sc_ksc} ksc ({Sc_psi:.1f} psi)</b><br>
• k-effective = <b>{k_effective_mpa_m:.1f} MPa/m ({k_effective_pci:.1f} pci)</b>
</div>
""", unsafe_allow_html=True)

# =============================================
# Footer
# =============================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.9rem;">
    📚 Reference: AASHTO Guide for Design of Pavement Structures, 1993<br>
    🏫 Department of Civil Engineering Education, KMUTNB
</div>
""", unsafe_allow_html=True)

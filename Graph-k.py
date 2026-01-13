"""
AASHTO 1993 Nomograph - Figure 3.3
Chart for Estimating Composite Modulus of Subgrade Reaction, k∞
Assuming a Semi-Infinite Subgrade Depth

พัฒนาสำหรับการเรียนการสอนวิศวกรรมถนนและผิวทาง
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import matplotlib.ticker as ticker

# =====================================================
# ตั้งค่าหน้าเว็บ
# =====================================================
st.set_page_config(
    page_title="AASHTO 1993 - Figure 3.3 Nomograph",
    page_icon="🛣️",
    layout="wide"
)

# =====================================================
# CSS สำหรับ UI
# =====================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    .main-header {
        background: linear-gradient(135deg, #1a365d 0%, #2c5282 50%, #2b6cb0 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .main-header h1 {
        color: white;
        font-family: 'Sarabun', sans-serif;
        font-size: 1.8rem;
        margin: 0;
        font-weight: 700;
    }
    
    .main-header p {
        color: #bee3f8;
        font-family: 'Sarabun', sans-serif;
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
    }
    
    .result-box {
        background: linear-gradient(145deg, #2d3748, #1a202c);
        border: 2px solid #4299e1;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 25px rgba(66, 153, 225, 0.3);
    }
    
    .result-label {
        color: #a0aec0;
        font-family: 'Sarabun', sans-serif;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .result-value {
        color: #f6e05e;
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.5rem;
        font-weight: 700;
        text-shadow: 0 0 20px rgba(246, 224, 94, 0.5);
    }
    
    .result-unit {
        color: #63b3ed;
        font-family: 'Sarabun', sans-serif;
        font-size: 1.2rem;
    }
    
    .input-section {
        background: #f7fafc;
        border-radius: 10px;
        padding: 1.2rem;
        border-left: 4px solid #4299e1;
        margin-bottom: 1rem;
    }
    
    .formula-box {
        background: #1a202c;
        border-radius: 8px;
        padding: 1rem;
        font-family: 'JetBrains Mono', monospace;
        color: #e2e8f0;
        font-size: 0.85rem;
        margin: 1rem 0;
        border: 1px solid #4a5568;
    }
    
    .info-text {
        font-family: 'Sarabun', sans-serif;
        color: #4a5568;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    .stSlider > div > div > div > div {
        background-color: #4299e1 !important;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# Header
# =====================================================
st.markdown("""
<div class="main-header">
    <h1>🛣️ AASHTO 1993 Nomograph - Figure 3.3</h1>
    <p>Chart for Estimating Composite Modulus of Subgrade Reaction (k∞)</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# สูตรการคำนวณ k∞ ตาม AASHTO 1993
# =====================================================
def calculate_k_inf(M_R, D_SB, E_SB):
    """
    คำนวณ Composite Modulus of Subgrade Reaction (k∞)
    ตาม AASHTO 1993 Guide for Design of Pavement Structures
    
    Parameters:
    -----------
    M_R : float
        Roadbed Soil Resilient Modulus (psi)
    D_SB : float
        Subbase Thickness (inches)
    E_SB : float
        Subbase Elastic Modulus (psi)
    
    Returns:
    --------
    k_inf : float
        Composite Modulus of Subgrade Reaction (pci)
    """
    # ค่า k จาก roadbed โดยไม่มี subbase
    # k_roadbed ≈ M_R / 19.4 (สัมพันธ์จาก AASHTO)
    k_roadbed = M_R / 19.4
    
    # สูตร composite k-value เมื่อมี subbase
    # k∞ = k_roadbed × [1 + (D_SB/38) × (E_SB/M_R)^(1/3)]^2.32
    if D_SB > 0 and E_SB > 0:
        ratio = (E_SB / M_R) ** (1/3)
        factor = 1 + (D_SB / 38) * ratio
        k_inf = k_roadbed * (factor ** 2.32)
    else:
        k_inf = k_roadbed
    
    return k_inf

def calculate_intermediate_k(M_R, D_SB, E_SB):
    """
    คำนวณค่า k ที่จุดต่างๆ บน Nomograph สำหรับการวาดเส้น
    """
    # k จาก M_R เพียงอย่างเดียว (ก่อนถึง turning line)
    k_from_MR = M_R / 19.4
    
    # k สุดท้าย (k∞)
    k_inf = calculate_k_inf(M_R, D_SB, E_SB)
    
    return k_from_MR, k_inf

# =====================================================
# Layout: Input และ Output
# =====================================================
col_input, col_chart = st.columns([1, 2.5])

with col_input:
    st.markdown("### 📊 ข้อมูลนำเข้า (Input Parameters)")
    
    # Subbase Thickness
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("**1️⃣ Subbase Thickness (D_SB)**")
    D_SB = st.slider(
        "ความหนาชั้น Subbase (inches)",
        min_value=4.0,
        max_value=18.0,
        value=8.0,
        step=0.5,
        key="dsb"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Subbase Elastic Modulus
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("**2️⃣ Subbase Elastic Modulus (E_SB)**")
    E_SB_options = [15000, 20000, 25000, 30000, 40000, 50000, 75000, 100000, 
                   150000, 200000, 300000, 400000, 500000, 750000, 1000000]
    E_SB = st.select_slider(
        "โมดูลัสยืดหยุ่นชั้น Subbase (psi)",
        options=E_SB_options,
        value=75000,
        format_func=lambda x: f"{x:,}",
        key="esb"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Roadbed Soil Resilient Modulus
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("**3️⃣ Roadbed Soil Resilient Modulus (M_R)**")
    M_R_options = list(range(1000, 21000, 500))
    M_R = st.select_slider(
        "โมดูลัสความยืดหยุ่นดินคันทาง (psi)",
        options=M_R_options,
        value=5000,
        format_func=lambda x: f"{x:,}",
        key="mr"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # คำนวณผลลัพธ์
    k_from_MR, k_inf = calculate_intermediate_k(M_R, D_SB, E_SB)
    
    # แสดงผลลัพธ์
    st.markdown("---")
    st.markdown("### 🎯 ผลการคำนวณ")
    
    st.markdown(f"""
    <div class="result-box">
        <div class="result-label">Composite Modulus of Subgrade Reaction</div>
        <div class="result-value">{k_inf:.0f}</div>
        <div class="result-unit">pci (k∞)</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ค่า k จาก M_R อย่างเดียว
    st.info(f"📌 **k จาก M_R (ไม่มี Subbase):** {k_from_MR:.1f} pci")
    
    # สูตรที่ใช้
    with st.expander("📐 สูตรการคำนวณ"):
        st.markdown("""
        **AASHTO 1993 Composite k-value Formula:**
        
        ```
        k_roadbed = M_R / 19.4
        
        k∞ = k_roadbed × [1 + (D_SB/38) × (E_SB/M_R)^(1/3)]^2.32
        ```
        
        **โดยที่:**
        - M_R = Roadbed Soil Resilient Modulus (psi)
        - D_SB = Subbase Thickness (inches)
        - E_SB = Subbase Elastic Modulus (psi)
        - k∞ = Composite Modulus of Subgrade Reaction (pci)
        
        **หมายเหตุ:** สูตรนี้สมมติ Semi-Infinite Subgrade Depth 
        (ความลึก > 10 ft จากผิว Subgrade)
        """)

# =====================================================
# วาด Nomograph
# =====================================================
with col_chart:
    st.markdown("### 📈 AASHTO 1993 Nomograph - Figure 3.3")
    
    # สร้าง Figure
    fig, ax = plt.subplots(figsize=(14, 10), dpi=100)
    fig.patch.set_facecolor('#f8f9fa')
    ax.set_facecolor('#ffffff')
    
    # =====================================================
    # กำหนดขอบเขตของ Nomograph
    # =====================================================
    # แกน X: 0 ถึง 100 (normalized)
    # แกน Y: 0 ถึง 100 (normalized)
    
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    
    # =====================================================
    # วาดเส้น Grid พื้นฐาน
    # =====================================================
    # เส้น Grid แนวนอนสำหรับ E_SB (ส่วนบน: y = 50-100)
    E_SB_values = [15000, 20000, 30000, 50000, 75000, 100000, 200000, 400000, 600000, 1000000]
    E_SB_log_min = np.log10(15000)
    E_SB_log_max = np.log10(1000000)
    
    for E in E_SB_values:
        y_pos = 50 + 50 * (np.log10(E) - E_SB_log_min) / (E_SB_log_max - E_SB_log_min)
        ax.axhline(y=y_pos, color='#d0d0d0', linewidth=0.5, linestyle='-', alpha=0.7, xmin=0, xmax=0.7)
    
    # เส้น Grid แนวตั้งสำหรับ D_SB (x = 0-35)
    D_SB_values = [6, 8, 10, 12, 14, 16, 18]
    D_SB_min, D_SB_max = 6, 18
    
    for D in D_SB_values:
        x_pos = 35 * (D - D_SB_min) / (D_SB_max - D_SB_min)
        ax.axvline(x=x_pos, color='#d0d0d0', linewidth=0.5, linestyle='-', alpha=0.7, ymin=0.25, ymax=0.75)
    
    # เส้น Grid แนวนอนสำหรับ M_R (ส่วนล่าง: y = 0-25)
    M_R_values = [1000, 2000, 3000, 5000, 7000, 10000, 12000, 16000, 20000]
    M_R_log_min = np.log10(1000)
    M_R_log_max = np.log10(20000)
    
    for M in M_R_values:
        y_pos = 25 - 25 * (np.log10(M) - M_R_log_min) / (M_R_log_max - M_R_log_min)
        ax.axhline(y=y_pos, color='#d0d0d0', linewidth=0.5, linestyle='-', alpha=0.7, xmin=0, xmax=0.95)
    
    # เส้น Grid แนวตั้งสำหรับ k∞ (x = 70-100)
    k_values = [50, 100, 200, 300, 400, 500, 600, 800, 1000, 1500, 2000]
    k_log_min = np.log10(50)
    k_log_max = np.log10(2000)
    
    for k in k_values:
        x_pos = 70 + 30 * (np.log10(k) - k_log_min) / (k_log_max - k_log_min)
        ax.axvline(x=x_pos, color='#d0d0d0', linewidth=0.5, linestyle='-', alpha=0.7, ymin=0, ymax=1)
    
    # =====================================================
    # วาดเส้นเฉียงสำหรับ E_SB - D_SB relationship
    # =====================================================
    for E in E_SB_values:
        y_start = 50 + 50 * (np.log10(E) - E_SB_log_min) / (E_SB_log_max - E_SB_log_min)
        # เส้นเฉียงลงจาก E_SB ไปยัง D_SB
        for D in [6, 18]:
            x_end = 35 * (D - D_SB_min) / (D_SB_max - D_SB_min)
            y_end = 50 + (y_start - 50) * (1 - x_end/35) * 0.3
        ax.plot([0, 35], [y_start, 50 + (y_start-50)*0.2], 
                color='#404040', linewidth=0.8, alpha=0.6)
    
    # =====================================================
    # วาดเส้น Turning Line (เส้นทแยงมุมหลัก)
    # =====================================================
    ax.plot([35, 70], [50, 25], color='#1a1a1a', linewidth=2.5, 
            label='Turning Line', linestyle='-')
    ax.text(52, 40, 'Turning Line', fontsize=10, rotation=-33, 
            color='#1a1a1a', fontweight='bold', style='italic')
    
    # =====================================================
    # วาดเส้นเฉียงสำหรับ M_R - k∞ relationship
    # =====================================================
    for M in M_R_values:
        y_mr = 25 - 25 * (np.log10(M) - M_R_log_min) / (M_R_log_max - M_R_log_min)
        # คำนวณ k จาก M_R
        k_base = M / 19.4
        if k_base >= 50 and k_base <= 2000:
            x_k = 70 + 30 * (np.log10(k_base) - k_log_min) / (k_log_max - k_log_min)
            ax.plot([70, min(x_k + 10, 100)], [y_mr, y_mr], 
                    color='#404040', linewidth=0.8, alpha=0.6)
    
    # =====================================================
    # วาดเส้นสีแดง - เส้นที่ผู้ใช้กำหนด
    # =====================================================
    # คำนวณตำแหน่งบน Nomograph
    
    # 1. ตำแหน่ง E_SB บนแกน Y (ส่วนบน)
    y_E_SB = 50 + 50 * (np.log10(E_SB) - E_SB_log_min) / (E_SB_log_max - E_SB_log_min)
    
    # 2. ตำแหน่ง D_SB บนแกน X
    x_D_SB = 35 * (D_SB - D_SB_min) / (D_SB_max - D_SB_min)
    
    # 3. จุดบน Turning Line
    # การ interpolate บน turning line
    t_ratio = x_D_SB / 35  # 0 ถึง 1
    x_turning = 35 + t_ratio * 35  # 35 ถึง 70
    y_turning = 50 - t_ratio * 25   # 50 ถึง 25
    
    # 4. ตำแหน่ง M_R บนแกน Y (ส่วนล่าง)
    y_M_R = 25 - 25 * (np.log10(M_R) - M_R_log_min) / (M_R_log_max - M_R_log_min)
    
    # 5. ตำแหน่ง k∞ บนแกน X (ส่วนขวา)
    k_inf_clipped = np.clip(k_inf, 50, 2000)
    x_k_inf = 70 + 30 * (np.log10(k_inf_clipped) - k_log_min) / (k_log_max - k_log_min)
    
    # วาดเส้นสีแดง
    line_width = 2.5
    line_color = '#e53e3e'
    marker_size = 12
    
    # เส้นที่ 1: E_SB → D_SB (แนวนอนจาก E_SB)
    ax.plot([0, x_D_SB], [y_E_SB, y_E_SB], color=line_color, 
            linewidth=line_width, linestyle='-', zorder=10)
    
    # เส้นที่ 2: D_SB → Turning Line (แนวตั้งลง)
    y_at_DSB = 50 + (y_E_SB - 50) * (1 - x_D_SB/70)  # ปรับตาม fan lines
    ax.plot([x_D_SB, x_D_SB], [y_E_SB, y_turning], color=line_color, 
            linewidth=line_width, linestyle='-', zorder=10)
    
    # เส้นที่ 3: Turning Line → M_R (แนวเฉียงลง)
    ax.plot([x_turning, 70], [y_turning, y_M_R], color=line_color, 
            linewidth=line_width, linestyle='-', zorder=10)
    
    # เส้นที่ 4: M_R → k∞ (แนวนอนไปขวา)
    ax.plot([70, x_k_inf], [y_M_R, y_M_R], color=line_color, 
            linewidth=line_width, linestyle='-', zorder=10)
    
    # เส้นที่ 5: k∞ ขึ้นไปด้านบน (แนวตั้งขึ้น)
    ax.plot([x_k_inf, x_k_inf], [y_M_R, 100], color=line_color, 
            linewidth=line_width, linestyle='-', zorder=10)
    
    # วาดจุดที่สำคัญ
    points = [
        (0, y_E_SB, f'E_SB = {E_SB:,} psi'),
        (x_D_SB, y_E_SB, f'D_SB = {D_SB:.1f}"'),
        (x_turning, y_turning, 'Turning Point'),
        (70, y_M_R, f'M_R = {M_R:,} psi'),
        (x_k_inf, y_M_R, f'k∞ = {k_inf:.0f} pci'),
    ]
    
    for px, py, label in points:
        ax.plot(px, py, 'o', color=line_color, markersize=marker_size, 
                zorder=11, markeredgecolor='white', markeredgewidth=2)
    
    # =====================================================
    # Labels และ Annotations
    # =====================================================
    # ชื่อแกน E_SB
    ax.text(-3, 75, 'Subbase Elastic\nModulus, E_SB (psi)', 
            fontsize=10, fontweight='bold', ha='right', va='center',
            rotation=90, color='#2d3748')
    
    # ตัวเลขแกน E_SB
    for E in [15000, 30000, 50000, 100000, 200000, 400000, 1000000]:
        y_pos = 50 + 50 * (np.log10(E) - E_SB_log_min) / (E_SB_log_max - E_SB_log_min)
        ax.text(-1, y_pos, f'{E//1000}k' if E >= 1000 else str(E), 
                fontsize=8, ha='right', va='center', color='#4a5568')
    
    # ชื่อแกน D_SB
    ax.text(17, 48, 'Subbase Thickness, D_SB (inches)', 
            fontsize=10, fontweight='bold', ha='center', va='top', color='#2d3748')
    
    # ตัวเลขแกน D_SB
    for D in D_SB_values:
        x_pos = 35 * (D - D_SB_min) / (D_SB_max - D_SB_min)
        ax.text(x_pos, 49, str(int(D)), fontsize=8, ha='center', va='top', color='#4a5568')
    
    # ชื่อแกน M_R
    ax.text(-3, 12, 'Roadbed Soil\nResilient Modulus,\nM_R (psi)', 
            fontsize=10, fontweight='bold', ha='right', va='center',
            rotation=90, color='#2d3748')
    
    # ตัวเลขแกน M_R
    for M in [1000, 2000, 5000, 10000, 20000]:
        y_pos = 25 - 25 * (np.log10(M) - M_R_log_min) / (M_R_log_max - M_R_log_min)
        ax.text(-1, y_pos, f'{M//1000}k' if M >= 1000 else str(M), 
                fontsize=8, ha='right', va='center', color='#4a5568')
    
    # ชื่อแกน k∞
    ax.text(85, 102, 'Composite Modulus of\nSubgrade Reaction, k∞ (pci)', 
            fontsize=10, fontweight='bold', ha='center', va='bottom', color='#2d3748')
    
    # ตัวเลขแกน k∞
    for k in [50, 100, 200, 300, 500, 800, 1000, 1500, 2000]:
        x_pos = 70 + 30 * (np.log10(k) - k_log_min) / (k_log_max - k_log_min)
        ax.text(x_pos, 101, str(k), fontsize=8, ha='center', va='bottom', 
                color='#4a5568', rotation=45)
    
    # =====================================================
    # กรอบและ Legend
    # =====================================================
    # กรอบรอบกราฟ
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color('#2d3748')
        spine.set_linewidth(1.5)
    
    # ซ่อนแกน
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='#404040', linewidth=1, label='Standard Nomograph Lines'),
        Line2D([0], [0], color='#1a1a1a', linewidth=2.5, label='Turning Line'),
        Line2D([0], [0], color=line_color, linewidth=2.5, label='User Input Path'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=line_color, 
               markersize=10, label='Intersection Points')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=9,
              framealpha=0.95, edgecolor='#cbd5e0')
    
    # =====================================================
    # Annotation box แสดงค่า
    # =====================================================
    textstr = f'Input Values:\n'
    textstr += f'  E_SB = {E_SB:,} psi\n'
    textstr += f'  D_SB = {D_SB:.1f} inches\n'
    textstr += f'  M_R = {M_R:,} psi\n\n'
    textstr += f'Result:\n'
    textstr += f'  k∞ = {k_inf:.0f} pci'
    
    props = dict(boxstyle='round,pad=0.5', facecolor='#edf2f7', 
                 edgecolor='#4299e1', alpha=0.95)
    ax.text(0.02, 0.02, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='bottom', bbox=props, fontfamily='monospace',
            color='#2d3748')
    
    # Title
    ax.set_title('AASHTO 1993 Guide - Figure 3.3\nChart for Estimating Composite Modulus of Subgrade Reaction (k∞)',
                 fontsize=12, fontweight='bold', color='#1a365d', pad=15)
    
    plt.tight_layout()
    st.pyplot(fig)

# =====================================================
# ตารางสรุป
# =====================================================
st.markdown("---")
st.markdown("### 📋 สรุปการคำนวณ")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🔹 E_SB (Subbase Modulus)",
        value=f"{E_SB:,} psi"
    )

with col2:
    st.metric(
        label="🔹 D_SB (Subbase Thickness)",
        value=f"{D_SB:.1f} inches"
    )

with col3:
    st.metric(
        label="🔹 M_R (Roadbed Modulus)",
        value=f"{M_R:,} psi"
    )

with col4:
    st.metric(
        label="🎯 k∞ (Composite k-value)",
        value=f"{k_inf:.0f} pci",
        delta=f"+{(k_inf/k_from_MR - 1)*100:.1f}% from base k"
    )

# =====================================================
# คำอธิบายเพิ่มเติม
# =====================================================
with st.expander("📚 ทฤษฎีและหลักการ"):
    st.markdown("""
    ### Composite Modulus of Subgrade Reaction (k∞)
    
    **k∞** คือ ค่าโมดูลัสปฏิกิริยาของดินใต้ทางแบบผสม (Composite) ที่รวมผลของ:
    1. ความแข็งแรงของดินคันทาง (Roadbed Soil)
    2. ความแข็งแรงของชั้น Subbase
    3. ความหนาของชั้น Subbase
    
    ### สมมติฐานของ Figure 3.3
    
    - **Semi-Infinite Subgrade Depth:** ความลึกของ Subgrade มากกว่า 10 ฟุต จากผิว Subgrade
    - ใช้หลักการ Odemark's Equivalent Thickness Method
    
    ### ความสัมพันธ์พื้นฐาน
    
    1. **k จาก M_R อย่างเดียว:**
       ```
       k_roadbed ≈ M_R / 19.4
       ```
    
    2. **k Composite (k∞):**
       - เมื่อเพิ่มชั้น Subbase ที่มีความแข็งแรงสูงกว่าดินคันทาง
       - ค่า k จะเพิ่มขึ้นตามความหนาและความแข็งแรงของ Subbase
    
    ### ขั้นตอนการอ่าน Nomograph
    
    1. เริ่มจากค่า **E_SB** ที่แกนซ้ายบน
    2. ลากเส้นแนวนอนไปตัดเส้นความหนา **D_SB**
    3. จากจุดตัด ลากเส้นลงไปยัง **Turning Line**
    4. จาก Turning Line ลากเส้นไปตัดค่า **M_R** ที่แกนซ้ายล่าง
    5. จากจุดตัด M_R ลากเส้นแนวนอนไปอ่านค่า **k∞**
    
    ### Reference
    
    - AASHTO Guide for Design of Pavement Structures, 1993
    - Part II, Chapter 3: Rigid Pavement Design
    """)

# =====================================================
# Footer
# =====================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #718096; font-size: 0.85rem;'>
    <p>🛣️ AASHTO 1993 Nomograph Calculator | Figure 3.3</p>
    <p>พัฒนาสำหรับการเรียนการสอนวิศวกรรมถนนและผิวทาง</p>
    <p>ภาควิชาครุศาสตร์โยธา มหาวิทยาลัยเทคโนโลยีพระจอมเกล้าพระนครเหนือ</p>
</div>
""", unsafe_allow_html=True)

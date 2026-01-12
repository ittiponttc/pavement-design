"""
Equivalent Subbase Thickness & Composite k-value Calculator
Based on AASHTO 1993 Rigid Pavement Design Guide
Using Odemark's Equivalent Thickness Method
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import interp2d, interp1d

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="Equivalent Thickness & k-value Calculator",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&family=Kanit:wght@400;500;600;700&display=swap');
    
    :root {
        --primary: #1e3a5f;
        --secondary: #2d5a87;
        --accent: #f0a500;
        --success: #28a745;
        --bg-light: #f8fafc;
        --text-dark: #1a1a2e;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
    }
    
    .main-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(30, 58, 95, 0.3);
    }
    
    .main-header h1 {
        color: white;
        font-family: 'Kanit', sans-serif;
        font-size: 2rem;
        font-weight: 600;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-family: 'Sarabun', sans-serif;
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
    }
    
    .result-card {
        background: white;
        border-radius: 16px;
        padding: 1.8rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-left: 5px solid var(--accent);
        margin: 1rem 0;
    }
    
    .result-card h3 {
        color: var(--primary);
        font-family: 'Kanit', sans-serif;
        font-size: 1rem;
        font-weight: 500;
        margin: 0 0 0.5rem 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .result-value {
        color: var(--secondary);
        font-family: 'Kanit', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    .result-unit {
        color: #666;
        font-family: 'Sarabun', sans-serif;
        font-size: 1rem;
        margin-left: 0.5rem;
    }
    
    .info-box {
        background: linear-gradient(135deg, #e8f4fd 0%, #d1e9fa 100%);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin: 1rem 0;
        border: 1px solid #b8daef;
    }
    
    .info-box p {
        color: var(--primary);
        font-family: 'Sarabun', sans-serif;
        margin: 0;
        font-size: 0.95rem;
    }
    
    .formula-box {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        font-family: 'Courier New', monospace;
        color: #00ff88;
        font-size: 1.1rem;
        text-align: center;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.3);
    }
    
    .section-header {
        background: linear-gradient(90deg, var(--primary) 0%, transparent 100%);
        padding: 0.8rem 1.2rem;
        border-radius: 8px;
        margin: 1.5rem 0 1rem 0;
    }
    
    .section-header h2 {
        color: white;
        font-family: 'Kanit', sans-serif;
        font-size: 1.2rem;
        font-weight: 500;
        margin: 0;
    }
    
    .stSelectbox > div > div {
        background: white;
        border-radius: 8px;
    }
    
    .stNumberInput > div > div > input {
        background: white;
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        font-family: 'Sarabun', sans-serif;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: var(--accent);
        box-shadow: 0 0 0 3px rgba(240, 165, 0, 0.2);
    }
    
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--primary) 0%, #0d1f33 100%);
    }
    
    div[data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    div[data-testid="stSidebar"] label {
        color: rgba(255,255,255,0.9) !important;
        font-family: 'Sarabun', sans-serif;
    }
    
    .layer-info {
        background: white;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin: 0.8rem 0;
        border: 1px solid #e0e0e0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .step-indicator {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        background: var(--accent);
        color: white;
        border-radius: 50%;
        font-family: 'Kanit', sans-serif;
        font-weight: 600;
        margin-right: 12px;
    }
    
    .calculation-step {
        background: white;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin: 0.8rem 0;
        border-left: 4px solid var(--secondary);
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffe69c 100%);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        border: 1px solid #ffc107;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==================== FUNCTIONS ====================

def get_typical_modulus(material_type: str) -> dict:
    """Get typical modulus values for common materials"""
    materials = {
        "Cement Treated Base (CTB)": {"E_min": 3500, "E_max": 7000, "E_typical": 5000},
        "Lean Concrete Base": {"E_min": 7000, "E_max": 14000, "E_typical": 10000},
        "Crushed Stone Base": {"E_min": 200, "E_max": 500, "E_typical": 300},
        "Soil-Cement": {"E_min": 1400, "E_max": 3500, "E_typical": 2000},
        "Asphalt Treated Base (ATB)": {"E_min": 2000, "E_max": 4000, "E_typical": 3000},
        "Granular Subbase": {"E_min": 100, "E_max": 300, "E_typical": 150},
        "Lime Treated Subgrade": {"E_min": 140, "E_max": 400, "E_typical": 200},
        "Natural Subgrade (Poor)": {"E_min": 20, "E_max": 50, "E_typical": 35},
        "Natural Subgrade (Fair)": {"E_min": 50, "E_max": 100, "E_typical": 70},
        "Natural Subgrade (Good)": {"E_min": 100, "E_max": 200, "E_typical": 140},
        "Custom Value": {"E_min": 0, "E_max": 0, "E_typical": 0}
    }
    return materials.get(material_type, {"E_min": 0, "E_max": 0, "E_typical": 0})


def calculate_equivalent_thickness(h_sb: float, E_sb: float, E_sg: float) -> float:
    """
    Calculate equivalent thickness using Odemark's Method
    h_e = h_sb × (E_sb / E_sg)^(1/3)
    """
    if E_sg <= 0:
        return 0
    ratio = E_sb / E_sg
    h_e = h_sb * (ratio ** (1/3))
    return h_e


def calculate_composite_k(k_sg: float, h_e: float) -> float:
    """
    Calculate composite k-value based on AASHTO 1993 Figure 3.3
    Using polynomial approximation of the chart
    
    Parameters:
    - k_sg: Subgrade k-value (pci or MPa/m)
    - h_e: Equivalent subbase thickness (inches or cm)
    
    Returns:
    - Composite k-value (same unit as k_sg)
    """
    # Conversion: if h_e in cm, convert to inches for calculation
    # The AASHTO chart uses inches
    
    # Approximation based on AASHTO 1993 Figure 3.3
    # k_composite = k_sg × multiplier
    # multiplier depends on h_e (in inches)
    
    if h_e <= 0:
        return k_sg
    
    # Thickness breakpoints (inches): 0, 4, 6, 8, 10, 12
    # Multipliers vary by subgrade k-value
    
    # Simplified approximation formula based on curve fitting
    # For treated base (high E_sb/E_sg ratio)
    h_inches = h_e / 2.54  # Convert cm to inches if needed
    
    # Cap the thickness effect (diminishing returns after ~12 inches)
    h_effective = min(h_inches, 18)
    
    # Logarithmic relationship approximation
    if h_effective < 1:
        multiplier = 1.0
    else:
        # Base multiplier increases with thickness
        # Higher k_sg values show less percentage increase
        base_increase = 0.08 * h_effective + 0.005 * (h_effective ** 1.5)
        
        # Adjustment factor for subgrade k-value
        # Lower k values benefit more from subbase
        if k_sg < 50:
            k_factor = 1.3
        elif k_sg < 100:
            k_factor = 1.15
        elif k_sg < 200:
            k_factor = 1.0
        else:
            k_factor = 0.85
        
        multiplier = 1.0 + (base_increase * k_factor)
    
    # Cap maximum multiplier (typically doesn't exceed 3x)
    multiplier = min(multiplier, 3.0)
    
    k_composite = k_sg * multiplier
    
    return k_composite


def interpolate_k_from_chart(k_sg: float, h_sb_inches: float) -> float:
    """
    Interpolate composite k-value from AASHTO 1993 Figure 3.3 data
    More accurate than formula approximation
    """
    # AASHTO 1993 Figure 3.3 data points
    # Subbase thickness (inches): 4, 6, 9, 12
    # Subgrade k (pci): 50, 100, 200
    
    thickness_points = np.array([0, 4, 6, 9, 12, 18])
    k_sg_points = np.array([50, 100, 200, 300])
    
    # Composite k values from chart (k_sg × rows, thickness × cols)
    k_composite_data = np.array([
        [50, 65, 75, 85, 110, 130],     # k_sg = 50
        [100, 130, 140, 160, 190, 220],  # k_sg = 100
        [200, 230, 270, 300, 320, 350],  # k_sg = 200
        [300, 350, 400, 430, 470, 500],  # k_sg = 300
    ])
    
    # Clamp input values
    h_clamped = np.clip(h_sb_inches, 0, 18)
    k_clamped = np.clip(k_sg, 50, 300)
    
    # Create interpolation function
    f = interp2d(thickness_points, k_sg_points, k_composite_data, kind='linear')
    
    result = f(h_clamped, k_clamped)[0]
    return result


def k_pci_to_mpa_m(k_pci: float) -> float:
    """Convert k-value from pci to MPa/m"""
    return k_pci * 0.2714


def k_mpa_m_to_pci(k_mpa_m: float) -> float:
    """Convert k-value from MPa/m to pci"""
    return k_mpa_m / 0.2714


def create_k_value_chart(k_sg: float, h_e_cm: float, k_composite: float):
    """Create visualization chart for k-value relationship"""
    
    # Generate data for different subgrade k-values
    h_range = np.linspace(0, 50, 100)  # cm
    
    fig = go.Figure()
    
    k_values = [30, 50, 75, 100, 150, 200]
    colors = ['#ff6b6b', '#feca57', '#48dbfb', '#1dd1a1', '#5f27cd', '#222f3e']
    
    for k, color in zip(k_values, colors):
        k_comp_range = [calculate_composite_k(k, h) for h in h_range]
        fig.add_trace(go.Scatter(
            x=h_range,
            y=k_comp_range,
            mode='lines',
            name=f'k = {k} pci',
            line=dict(color=color, width=2),
            hovertemplate=f'k_sg = {k} pci<br>h_e = %{{x:.1f}} cm<br>k_eff = %{{y:.1f}} pci<extra></extra>'
        ))
    
    # Add current point
    fig.add_trace(go.Scatter(
        x=[h_e_cm],
        y=[k_composite],
        mode='markers',
        name='Current Design',
        marker=dict(
            size=15,
            color='#f0a500',
            symbol='star',
            line=dict(color='white', width=2)
        ),
        hovertemplate=f'<b>Design Point</b><br>h_e = {h_e_cm:.1f} cm<br>k_eff = {k_composite:.1f} pci<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='Composite k-value vs Equivalent Subbase Thickness',
            font=dict(size=18, family='Kanit')
        ),
        xaxis_title='Equivalent Subbase Thickness (cm)',
        yaxis_title='Composite k-value (pci)',
        font=dict(family='Sarabun'),
        plot_bgcolor='rgba(248,250,252,1)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255,255,255,0.8)'
        ),
        hovermode='closest',
        margin=dict(l=60, r=30, t=60, b=60)
    )
    
    fig.update_xaxes(gridcolor='rgba(0,0,0,0.1)', zeroline=False)
    fig.update_yaxes(gridcolor='rgba(0,0,0,0.1)', zeroline=False)
    
    return fig


def create_layer_diagram(h_sb: float, h_e: float, E_sb: float, E_sg: float):
    """Create a schematic diagram of pavement layers"""
    
    fig = go.Figure()
    
    # Layer heights for visualization
    pcc_height = 25
    sb_height = h_sb
    sg_height = 30
    
    total_height = pcc_height + sb_height + sg_height
    
    # PCC Layer
    fig.add_shape(type="rect",
        x0=0, y0=total_height - pcc_height, x1=100, y1=total_height,
        fillcolor="#95a5a6", line=dict(color="#7f8c8d", width=2)
    )
    fig.add_annotation(x=50, y=total_height - pcc_height/2,
        text="<b>PCC Slab</b>", showarrow=False,
        font=dict(size=14, color="white", family="Kanit"))
    
    # Subbase Layer
    fig.add_shape(type="rect",
        x0=0, y0=total_height - pcc_height - sb_height, 
        x1=100, y1=total_height - pcc_height,
        fillcolor="#e67e22", line=dict(color="#d35400", width=2)
    )
    fig.add_annotation(x=50, y=total_height - pcc_height - sb_height/2,
        text=f"<b>Subbase</b><br>h = {h_sb:.1f} cm | E = {E_sb:.0f} MPa",
        showarrow=False, font=dict(size=12, color="white", family="Sarabun"))
    
    # Subgrade Layer
    fig.add_shape(type="rect",
        x0=0, y0=0, x1=100, y1=total_height - pcc_height - sb_height,
        fillcolor="#8b4513", line=dict(color="#654321", width=2)
    )
    fig.add_annotation(x=50, y=(total_height - pcc_height - sb_height)/2,
        text=f"<b>Subgrade</b><br>E = {E_sg:.0f} MPa",
        showarrow=False, font=dict(size=12, color="white", family="Sarabun"))
    
    # Equivalent thickness indicator
    fig.add_shape(type="line",
        x0=105, y0=total_height - pcc_height, x1=105, y1=total_height - pcc_height - h_e,
        line=dict(color="#f0a500", width=3)
    )
    fig.add_shape(type="line",
        x0=102, y0=total_height - pcc_height, x1=108, y1=total_height - pcc_height,
        line=dict(color="#f0a500", width=2)
    )
    fig.add_shape(type="line",
        x0=102, y0=total_height - pcc_height - h_e, x1=108, y1=total_height - pcc_height - h_e,
        line=dict(color="#f0a500", width=2)
    )
    fig.add_annotation(x=115, y=total_height - pcc_height - h_e/2,
        text=f"<b>h<sub>e</sub> = {h_e:.1f} cm</b>",
        showarrow=False, font=dict(size=13, color="#f0a500", family="Kanit"))
    
    fig.update_layout(
        showlegend=False,
        xaxis=dict(visible=False, range=[-5, 130]),
        yaxis=dict(visible=False, range=[-5, total_height + 10]),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=10, b=10),
        height=300
    )
    
    return fig


# ==================== MAIN APP ====================

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🛣️ Equivalent Subbase Thickness & k-value Calculator</h1>
        <p>การคำนวณความหนาเทียบเท่าและค่า k-value ตามวิธี Odemark | AASHTO 1993</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for input
    with st.sidebar:
        st.markdown("### 📐 ข้อมูลนำเข้า")
        st.markdown("---")
        
        # Unit system
        unit_system = st.radio(
            "ระบบหน่วย",
            ["SI (MPa, cm)", "US (psi, inch)"],
            horizontal=True
        )
        
        is_si = unit_system == "SI (MPa, cm)"
        
        st.markdown("---")
        st.markdown("#### 🔹 ชั้น Subbase")
        
        # Subbase material selection
        sb_material = st.selectbox(
            "ประเภทวัสดุ Subbase",
            [
                "Cement Treated Base (CTB)",
                "Lean Concrete Base",
                "Crushed Stone Base",
                "Soil-Cement",
                "Asphalt Treated Base (ATB)",
                "Granular Subbase",
                "Custom Value"
            ]
        )
        
        mat_info = get_typical_modulus(sb_material)
        
        if sb_material != "Custom Value":
            st.info(f"E typical: {mat_info['E_typical']} MPa\n\n"
                   f"Range: {mat_info['E_min']} - {mat_info['E_max']} MPa")
        
        if is_si:
            h_sb = st.number_input(
                "ความหนา Subbase (cm)",
                min_value=5.0,
                max_value=100.0,
                value=15.0,
                step=1.0
            )
            
            E_sb = st.number_input(
                "Modulus ของ Subbase, E_sb (MPa)",
                min_value=50.0,
                max_value=50000.0,
                value=float(mat_info['E_typical']) if mat_info['E_typical'] > 0 else 500.0,
                step=50.0
            )
        else:
            h_sb_inch = st.number_input(
                "ความหนา Subbase (inch)",
                min_value=2.0,
                max_value=40.0,
                value=6.0,
                step=0.5
            )
            h_sb = h_sb_inch * 2.54
            
            E_sb_psi = st.number_input(
                "Modulus ของ Subbase, E_sb (psi)",
                min_value=7000.0,
                max_value=7000000.0,
                value=float(mat_info['E_typical'] * 145) if mat_info['E_typical'] > 0 else 72500.0,
                step=1000.0
            )
            E_sb = E_sb_psi / 145.038
        
        st.markdown("---")
        st.markdown("#### 🔸 ชั้น Subgrade")
        
        sg_material = st.selectbox(
            "ประเภท Subgrade",
            [
                "Natural Subgrade (Poor)",
                "Natural Subgrade (Fair)",
                "Natural Subgrade (Good)",
                "Lime Treated Subgrade",
                "Custom Value"
            ]
        )
        
        sg_info = get_typical_modulus(sg_material)
        
        if sg_material != "Custom Value":
            st.info(f"E typical: {sg_info['E_typical']} MPa\n\n"
                   f"Range: {sg_info['E_min']} - {sg_info['E_max']} MPa")
        
        if is_si:
            E_sg = st.number_input(
                "Modulus ของ Subgrade, E_sg (MPa)",
                min_value=10.0,
                max_value=500.0,
                value=float(sg_info['E_typical']) if sg_info['E_typical'] > 0 else 50.0,
                step=5.0
            )
            
            k_sg = st.number_input(
                "k-value ของ Subgrade (MPa/m)",
                min_value=10.0,
                max_value=200.0,
                value=27.0,
                step=1.0,
                help="ค่า k เริ่มต้นของดินเดิม (Modulus of Subgrade Reaction)"
            )
            k_sg_pci = k_mpa_m_to_pci(k_sg)
        else:
            E_sg_psi = st.number_input(
                "Modulus ของ Subgrade, E_sg (psi)",
                min_value=1500.0,
                max_value=75000.0,
                value=float(sg_info['E_typical'] * 145) if sg_info['E_typical'] > 0 else 7250.0,
                step=500.0
            )
            E_sg = E_sg_psi / 145.038
            
            k_sg_pci = st.number_input(
                "k-value ของ Subgrade (pci)",
                min_value=30.0,
                max_value=750.0,
                value=100.0,
                step=5.0,
                help="ค่า k เริ่มต้นของดินเดิม (Modulus of Subgrade Reaction)"
            )
            k_sg = k_pci_to_mpa_m(k_sg_pci)
    
    # Main content
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown("""
        <div class="section-header">
            <h2>📊 ผลการคำนวณ</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Calculate equivalent thickness
        h_e = calculate_equivalent_thickness(h_sb, E_sb, E_sg)
        h_e_inch = h_e / 2.54
        
        # Calculate composite k-value
        k_composite_pci = interpolate_k_from_chart(k_sg_pci, h_e_inch)
        k_composite = k_pci_to_mpa_m(k_composite_pci)
        
        # Modulus ratio
        modulus_ratio = E_sb / E_sg
        
        # Display results
        res_col1, res_col2 = st.columns(2)
        
        with res_col1:
            if is_si:
                st.markdown(f"""
                <div class="result-card">
                    <h3>ความหนาเทียบเท่า (h<sub>e</sub>)</h3>
                    <p class="result-value">{h_e:.2f}<span class="result-unit">cm</span></p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="result-card">
                    <h3>ความหนาเทียบเท่า (h<sub>e</sub>)</h3>
                    <p class="result-value">{h_e_inch:.2f}<span class="result-unit">inch</span></p>
                </div>
                """, unsafe_allow_html=True)
        
        with res_col2:
            if is_si:
                st.markdown(f"""
                <div class="result-card">
                    <h3>ค่า k-value รวม (k<sub>eff</sub>)</h3>
                    <p class="result-value">{k_composite:.1f}<span class="result-unit">MPa/m</span></p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="result-card">
                    <h3>ค่า k-value รวม (k<sub>eff</sub>)</h3>
                    <p class="result-value">{k_composite_pci:.1f}<span class="result-unit">pci</span></p>
                </div>
                """, unsafe_allow_html=True)
        
        # Additional info
        st.markdown(f"""
        <div class="info-box">
            <p><strong>อัตราส่วน Modulus:</strong> E<sub>sb</sub>/E<sub>sg</sub> = {modulus_ratio:.2f}</p>
            <p><strong>ค่าเพิ่มของ k-value:</strong> {((k_composite_pci/k_sg_pci - 1)*100):.1f}% จาก k<sub>subgrade</sub></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Formula display
        st.markdown("""
        <div class="section-header">
            <h2>📝 สูตรการคำนวณ (Odemark's Method)</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="formula-box">
            h<sub>e</sub> = h<sub>sb</sub> × (E<sub>sb</sub> / E<sub>sg</sub>)<sup>1/3</sup><br><br>
            h<sub>e</sub> = {h_sb:.1f} × ({E_sb:.0f} / {E_sg:.0f})<sup>1/3</sup> = {h_sb:.1f} × {modulus_ratio**(1/3):.3f} = <b>{h_e:.2f} cm</b>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="section-header">
            <h2>🏗️ แผนผังชั้นทาง</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Layer diagram
        layer_fig = create_layer_diagram(h_sb, h_e, E_sb, E_sg)
        st.plotly_chart(layer_fig, use_container_width=True, config={'displayModeBar': False})
    
    # Chart section
    st.markdown("""
    <div class="section-header">
        <h2>📈 กราฟความสัมพันธ์ k-value</h2>
    </div>
    """, unsafe_allow_html=True)
    
    chart_fig = create_k_value_chart(k_sg_pci, h_e, k_composite_pci)
    st.plotly_chart(chart_fig, use_container_width=True)
    
    # Calculation steps
    with st.expander("📋 ขั้นตอนการคำนวณโดยละเอียด", expanded=False):
        st.markdown(f"""
        <div class="calculation-step">
            <span class="step-indicator">1</span>
            <strong>กำหนดค่า Input</strong><br>
            • ความหนา Subbase (h<sub>sb</sub>) = {h_sb:.1f} cm<br>
            • Modulus ของ Subbase (E<sub>sb</sub>) = {E_sb:.0f} MPa<br>
            • Modulus ของ Subgrade (E<sub>sg</sub>) = {E_sg:.0f} MPa<br>
            • k-value เริ่มต้น (k<sub>sg</sub>) = {k_sg:.1f} MPa/m ({k_sg_pci:.0f} pci)
        </div>
        
        <div class="calculation-step">
            <span class="step-indicator">2</span>
            <strong>คำนวณอัตราส่วน Modulus</strong><br>
            E<sub>sb</sub> / E<sub>sg</sub> = {E_sb:.0f} / {E_sg:.0f} = {modulus_ratio:.3f}
        </div>
        
        <div class="calculation-step">
            <span class="step-indicator">3</span>
            <strong>คำนวณ Equivalent Thickness (Odemark's Method)</strong><br>
            h<sub>e</sub> = h<sub>sb</sub> × (E<sub>sb</sub> / E<sub>sg</sub>)<sup>1/3</sup><br>
            h<sub>e</sub> = {h_sb:.1f} × ({modulus_ratio:.3f})<sup>1/3</sup><br>
            h<sub>e</sub> = {h_sb:.1f} × {modulus_ratio**(1/3):.4f}<br>
            <strong>h<sub>e</sub> = {h_e:.2f} cm ({h_e_inch:.2f} inch)</strong>
        </div>
        
        <div class="calculation-step">
            <span class="step-indicator">4</span>
            <strong>หาค่า Composite k-value จาก AASHTO Figure 3.3</strong><br>
            จาก k<sub>sg</sub> = {k_sg_pci:.0f} pci และ h<sub>e</sub> = {h_e_inch:.1f} inch<br>
            <strong>k<sub>eff</sub> = {k_composite_pci:.1f} pci ({k_composite:.1f} MPa/m)</strong>
        </div>
        """, unsafe_allow_html=True)
    
    # Reference section
    with st.expander("📚 ทฤษฎีและเอกสารอ้างอิง", expanded=False):
        st.markdown("""
        ### Odemark's Equivalent Thickness Method
        
        วิธีของ Odemark (1949) ใช้แปลงความหนาของชั้นทางที่มี Modulus ต่างกัน 
        ให้เป็นความหนาเทียบเท่าของวัสดุที่มี Modulus เท่ากับชั้นดินเดิม
        
        **สมมติฐาน:**
        - ชั้นทางมีความหนาสม่ำเสมอและขยายไปไม่มีที่สิ้นสุดในแนวราบ
        - วัสดุมีคุณสมบัติเป็น Linear Elastic และ Isotropic
        - ค่า Poisson's Ratio ของแต่ละชั้นใกล้เคียงกัน
        
        **ข้อจำกัด:**
        - ไม่คำนึงถึงผลของ Bonding ระหว่างชั้น
        - เหมาะสำหรับการประมาณค่าเบื้องต้น
        
        ### AASHTO 1993 Figure 3.3
        
        กราฟแสดงความสัมพันธ์ระหว่าง:
        - ค่า k ของดินเดิม (Subgrade k-value)
        - ความหนาของ Subbase
        - ค่า k รวม (Composite k-value)
        
        **เอกสารอ้างอิง:**
        - AASHTO Guide for Design of Pavement Structures, 1993
        - Odemark, N. (1949). "Investigations as to the Elastic Properties of Soils 
          and Design of Pavements According to the Theory of Elasticity"
        - Huang, Y.H. (2004). "Pavement Analysis and Design", 2nd Edition
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-family: 'Sarabun', sans-serif; padding: 1rem;">
        <p>🎓 พัฒนาสำหรับการเรียนการสอนวิศวกรรมทาง | AASHTO 1993 Rigid Pavement Design</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

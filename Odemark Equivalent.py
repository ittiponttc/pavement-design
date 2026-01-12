import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AASHTO 1993 Odemark & k-value Calculator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .header-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .info-box {
        background-color: #cfe2ff;
        border-left: 5px solid #0d6efd;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .concept-box {
        background-color: #f8f9fa;
        border-left: 5px solid #6c757d;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════
st.markdown("""
    <div class="header-section">
        <h1>🛣️ AASHTO 1993 Pavement Design Calculator</h1>
        <p><b>Odemark Equivalent Thickness Method + Composite k-value</b></p>
        <small>For Rigid Pavement (JPCP) Design - CORRECT Concept</small>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.header("📚 Material Database")
    
    material_db = {
        "Asphalt Concrete (AC)": 2500,
        "Cement Treated Base (CTB)": 1200,
        "Cement Modified Crushed Rock": 800,
        "Lime Stabilized": 400,
        "Crushed Aggregate (Granular)": 300,
        "Soil Aggregate": 150,
        "Laterite": 200
    }
    
    st.subheader("📊 Elastic Modulus (E) by Material")
    for material, e_value in material_db.items():
        st.caption(f"• {material}: **{e_value} MPa**")
    
    st.divider()
    
    st.subheader("💡 AASHTO 1993 Concept")
    st.markdown("""
    **❌ WRONG Approach:**
    - "Reduce E of AC, CTB"
    - "Keep h actual"
    
    **✅ CORRECT Approach:**
    - "Keep all E actual (no reduction!)"
    - "Keep all h actual"
    - "Convert to: equivalent thickness of 
    **Reference Material**"
    
    **Question AASHTO asks:**
    > "This multi-layer system (40 cm total) 
    is equivalent to how much thickness 
    of **Reference Material**?"
    """)

# ═══════════════════════════════════════════════════════════════
# MAIN TABS
# ═══════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "📐 Step 1: Subgrade", 
    "🏗️ Step 2: Equivalent Thickness",
    "🔧 Step 3: Effective k-value",
    "📖 Help & Theory"
])

# ═══════════════════════════════════════════════════════════════
# TAB 1: SUBGRADE PROPERTIES
# ═══════════════════════════════════════════════════════════════
with tab1:
    st.subheader("🔹 Subgrade Properties (Reference)")
    
    st.markdown("""
    <div class="concept-box">
    <b>📌 Step 1:</b> Determine subgrade properties from CBR test
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cbr_sg = st.number_input(
            "Subgrade CBR (%)",
            min_value=1.0,
            max_value=30.0,
            value=5.0,
            step=0.5,
            key="cbr_sg_main",
            help="California Bearing Ratio from lab test"
        )
    
    # Calculate E_SG from CBR
    e_sg = 17.6 * (cbr_sg ** 0.64)
    mr_sg_mpa = e_sg
    mr_sg_psi = e_sg * 145.038
    k1 = mr_sg_psi / 19.4
    
    with col2:
        st.metric(
            label="E (Subgrade)",
            value=f"{e_sg:.1f} MPa",
            delta=f"{mr_sg_psi:.0f} psi"
        )
    
    with col3:
        st.metric(
            label="k₁ (Subgrade only)",
            value=f"{k1:.1f} pci",
            delta="No loss of support"
        )
    
    st.markdown("---")
    
    st.subheader("📊 Calculation Details")
    
    calc_col1, calc_col2 = st.columns(2)
    
    with calc_col1:
        st.markdown("""
        **Formula: E from CBR**
        ```
        E = 17.6 × CBR^0.64
        ```
        """)
        st.write(f"E = 17.6 × {cbr_sg}^0.64 = **{e_sg:.2f} MPa**")
    
    with calc_col2:
        st.markdown("""
        **Formula: k from M_R**
        ```
        k = M_R / 19.4
        M_R (psi) = E (MPa) × 145.038
        ```
        """)
        st.write(f"M_R = {e_sg:.2f} × 145.038 = {mr_sg_psi:.0f} psi")
        st.write(f"k₁ = {mr_sg_psi:.0f} / 19.4 = **{k1:.1f} pci**")
    
    # Store in session state
    st.session_state.cbr_sg = cbr_sg
    st.session_state.e_sg = e_sg
    st.session_state.mr_sg_psi = mr_sg_psi
    st.session_state.k1 = k1

# ═══════════════════════════════════════════════════════════════
# TAB 2: EQUIVALENT THICKNESS (CORE CALCULATION)
# ═══════════════════════════════════════════════════════════════
with tab2:
    st.subheader("🔹 Pavement Layers & Equivalent Thickness")
    
    st.markdown("""
    <div class="concept-box">
    <b>📌 Step 2:</b> Define actual layers + choose Reference Material
    <br><br>
    <b>Key Point:</b> We are NOT reducing E of any layer!
    <br>
    We are CONVERTING the entire system to:
    <br>
    <b>"Equivalent thickness of Reference Material"</b>
    </div>
    """, unsafe_allow_html=True)
    
    # Get subgrade E from previous tab
    if 'e_sg' in st.session_state:
        e_sg_ref = st.session_state.e_sg
        cbr_sg_ref = st.session_state.cbr_sg
    else:
        e_sg_ref = 17.6 * (5 ** 0.64)
        cbr_sg_ref = 5
    
    st.markdown("---")
    
    # SELECT REFERENCE MATERIAL
    st.subheader("Step 2a: Select Reference Material")
    
    material_db = {
        "Asphalt Concrete (AC)": 2500,
        "Cement Treated Base (CTB)": 1200,
        "Cement Modified Crushed Rock": 800,
        "Lime Stabilized": 400,
        "Crushed Aggregate (Granular) - RECOMMENDED": 300,
        "Soil Aggregate": 150,
        "Laterite": 200
    }
    
    ref_material = st.selectbox(
        "Choose Reference Material (E_ref)",
        list(material_db.keys()),
        index=4,  # Default to Granular
        help="This is the baseline material we'll compare all layers to"
    )
    
    e_ref = material_db[ref_material]
    
    col_ref1, col_ref2 = st.columns(2)
    with col_ref1:
        st.metric(
            label="Reference Material",
            value=ref_material.split(" - ")[0] if " - " in ref_material else ref_material
        )
    with col_ref2:
        st.metric(
            label="E_ref",
            value=f"{e_ref} MPa"
        )
    
    st.markdown("---")
    
    # INPUT LAYERS
    st.subheader("Step 2b: Define Actual Pavement Layers")
    
    num_layers = st.selectbox(
        "Number of pavement layers above subgrade",
        [1, 2, 3, 4, 5],
        index=2,
        key="num_layers_tab2"
    )
    
    layers = []
    
    for i in range(num_layers):
        with st.expander(f"Layer {i+1}", expanded=(i==0)):
            col_mat, col_h, col_e = st.columns(3)
            
            with col_mat:
                mat = st.selectbox(
                    f"Material",
                    list(material_db.keys()),
                    index=0 if i==0 else (1 if i==1 else 4),
                    key=f"mat_tab2_{i}",
                    label_visibility="collapsed"
                )
            
            with col_h:
                h = st.number_input(
                    f"Thickness (cm)",
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
            
            st.caption(f"Layer {i+1}: {h} cm of {mat.split(' - ')[0]} @ {e} MPa")
            
            layers.append({
                "Layer": i + 1,
                "Material": mat.split(" - ")[0],
                "h_actual (cm)": h,
                "E_actual (MPa)": e
            })
    
    st.markdown("---")
    
    # CALCULATION BUTTON
    if st.button("🧮 Calculate Equivalent Thickness", use_container_width=True, key="calc_heq"):
        st.session_state.calculate_heq = True
    
    # RESULTS
    if 'calculate_heq' in st.session_state and st.session_state.calculate_heq:
        st.markdown("---")
        st.subheader("📊 Results: Odemark Equivalent Thickness")
        
        # Prepare results table
        results = []
        total_h_actual = 0
        total_h_eq = 0
        
        for layer in layers:
            h = layer["h_actual (cm)"]
            e = layer["E_actual (MPa)"]
            
            # Odemark formula: h_eq = h * (E / E_ref)^(1/3)
            # NOTE: We are NOT reducing E!
            # We are converting h from this material to equivalent h of reference material
            h_eq = h * ((e / e_ref) ** (1/3))
            
            total_h_actual += h
            total_h_eq += h_eq
            
            results.append({
                "Layer": layer["Layer"],
                "Material": layer["Material"],
                "h actual (cm)": round(h, 2),
                "E actual (MPa)": round(e, 0),
                "E/E_ref": round(e/e_ref, 3),
                "(E/E_ref)^(1/3)": round((e/e_ref)**(1/3), 3),
                "h_eq (cm)": round(h_eq, 2)
            })
        
        df_results = pd.DataFrame(results)
        
        st.markdown("### 📋 Layer-by-Layer Calculation")
        st.dataframe(df_results, use_container_width=True, hide_index=True)
        
        st.markdown("### 🎯 Summary")
        
        summary_col1, summary_col2, summary_col3 = st.columns(3)
        
        with summary_col1:
            st.metric(
                label="Total Actual Thickness",
                value=f"{total_h_actual:.1f} cm",
                delta=f"{total_h_actual/2.54:.2f} in"
            )
        
        with summary_col2:
            st.metric(
                label="Reference Material (E_ref)",
                value=f"{e_ref} MPa",
                delta=ref_material.split(" - ")[0]
            )
        
        with summary_col3:
            st.metric(
                label="Total Equivalent Thickness",
                value=f"{total_h_eq:.1f} cm",
                delta=f"{total_h_eq/2.54:.2f} in"
            )
        
        st.markdown("---")
        
        st.markdown(f"""
        <div class="success-box">
        <h4>✅ INTERPRETATION (CORRECT CONCEPT):</h4>
        <p>Your pavement system with <b>actual total thickness of {total_h_actual:.1f} cm</b> 
        (consisting of multiple materials with different E values) 
        is <b>structurally equivalent</b> to a single layer of 
        <b>{ref_material.split(" - ")[0]}</b> that is <b>{total_h_eq:.1f} cm</b> thick.</p>
        
        <p>In other words:</p>
        <ul>
        <li>❌ We did NOT reduce E of AC from 2500 to something lower</li>
        <li>❌ We did NOT change actual thickness of any layer</li>
        <li>✅ We CONVERTED: "3-layer system" → "equivalent thickness of Reference Material"</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Store for next tab
        st.session_state.total_h_eq = total_h_eq
        st.session_state.layers_data = layers
        st.session_state.e_ref = e_ref
        st.session_state.ref_material_name = ref_material.split(" - ")[0]

# ═══════════════════════════════════════════════════════════════
# TAB 3: EFFECTIVE k-VALUE
# ═══════════════════════════════════════════════════════════════
with tab3:
    st.subheader("🔹 Effective Modulus of Subgrade Reaction (k_eff)")
    
    st.markdown("""
    <div class="concept-box">
    <b>📌 Step 3:</b> Calculate composite k-value for design
    <br>
    This k_eff accounts for support from the subbase system
    </div>
    """, unsafe_allow_html=True)
    
    if 'k1' in st.session_state:
        k1_val = st.session_state.k1
        e_sg_val = st.session_state.e_sg
        cbr_sg_val = st.session_state.cbr_sg
    else:
        cbr_sg_val = st.number_input(
            "Subgrade CBR (%)",
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
            label="k₁ (Subgrade Only, No Support)",
            value=f"{k1_val:.1f} pci",
            delta=f"CBR = {cbr_sg_val}%, E = {e_sg_val:.1f} MPa"
        )
    
    with col_k1b:
        st.info("""
        **k₁** = k-value of subgrade WITHOUT any subbase support
        """)
    
    st.markdown("---")
    
    st.subheader("Step 3a: Loss of Support Factor (f_LS)")
    
    st.markdown("""
    **Loss of Support Factor (f_LS)** accounts for:
    - Subbase thickness and quality
    - Drainage conditions
    - Potential erosion/pumping
    
    **Formula:**
    ```
    k_eff = k₁ / f_LS
    ```
    """)
    
    ls_options = {
        "No Loss (Excellent Support)": 1.0,
        "LS = 1 (Good Granular + Good Drainage)": 0.9,
        "LS = 2 (Fair Subbase or Fair Drainage)": 0.8,
        "LS = 3 (Poor Subbase or Poor Drainage)": 0.6
    }
    
    ls_description = st.selectbox(
        "Loss of Support Condition",
        list(ls_options.keys()),
        help="Select based on your subbase type and drainage"
    )
    
    f_ls = ls_options[ls_description]
    
    col_fls1, col_fls2 = st.columns(2)
    
    with col_fls1:
        st.metric(
            label="f_LS Factor",
            value=f"{f_ls}",
            delta=ls_description.split("(")[0]
        )
    
    with col_fls2:
        st.info(f"""
        **Selected condition:**
        
        {ls_description}
        """)
    
    # Custom f_LS input
    st.markdown("Or enter custom f_LS value:")
    f_ls_custom = st.slider(
        "Custom f_LS (0 = no loss, 1.0 = standard, >1.0 = high loss)",
        min_value=0.5,
        max_value=2.0,
        value=f_ls,
        step=0.05,
        key="f_ls_slider"
    )
    
    f_ls = f_ls_custom
    
    st.markdown("---")
    
    st.subheader("Step 3b: Calculate k_eff")
    
    if st.button("🧮 Calculate k_eff", use_container_width=True, key="calc_keff"):
        st.session_state.calculate_keff = True
    
    if 'calculate_keff' in st.session_state and st.session_state.calculate_keff:
        k_eff = k1_val / f_ls
        
        st.markdown("---")
        st.subheader("📊 Results: Composite k-value")
        
        calc_col1, calc_col2, calc_col3 = st.columns(3)
        
        with calc_col1:
            st.markdown(f"""
            <div class="info-box">
            <h4 style="margin: 0;">k₁ (Base)</h4>
            <h3 style="margin: 0;"><b>{k1_val:.1f} pci</b></h3>
            <small>Subgrade only</small>
            </div>
            """, unsafe_allow_html=True)
        
        with calc_col2:
            st.markdown(f"""
            <div class="warning-box">
            <h4 style="margin: 0;">f_LS</h4>
            <h3 style="margin: 0;"><b>{f_ls:.2f}</b></h3>
            <small>Loss of support</small>
            </div>
            """, unsafe_allow_html=True)
        
        with calc_col3:
            st.markdown(f"""
            <div class="success-box">
            <h4 style="margin: 0;">k_eff (FOR DESIGN)</h4>
            <h3 style="margin: 0;"><b>{k_eff:.1f} pci</b></h3>
            <small>With subbase support</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="info-box">
        <b>📌 Calculation:</b><br>
        k_eff = k₁ / f_LS<br>
        k_eff = {k1_val:.1f} / {f_ls:.2f} = <b>{k_eff:.1f} pci</b>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.subheader("📋 Design Summary")
        
        summary_table = {
            "Parameter": [
                "Subgrade CBR",
                "Subgrade E",
                "Subgrade M_R",
                "k₁ (Subgrade only)",
                "f_LS (Loss of Support)",
                "k_eff (For JPCP Design)"
            ],
            "Value": [
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
        
        st.markdown(f"""
        <div class="success-box">
        <h4>✅ USE THIS k VALUE FOR JPCP DESIGN:</h4>
        <p><b>k_eff = {k_eff:.1f} pci</b></p>
        <p>This is the composite modulus of subgrade reaction that accounts for:</p>
        <ul>
        <li>The subgrade properties (CBR = {cbr_sg_val}%)</li>
        <li>Support from the subbase system (f_LS = {f_ls})</li>
        </ul>
        <p>Use this k-value in the AASHTO 1993 design equation for concrete thickness.</p>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TAB 4: HELP & THEORY
# ═══════════════════════════════════════════════════════════════
with tab4:
    st.subheader("📚 Complete Guide & Theory")
    
    st.markdown("""
    ## 🎯 Core Concept (THE KEY POINT)
    
    ### ❌ WRONG Understanding:
    - "AASHTO 1993 wants us to reduce the elastic modulus (E) of layers"
    - "We should lower E of AC from 2500 to something smaller"
    - "We modify material properties to fit the design"
    
    ### ✅ CORRECT Understanding:
    - **AASHTO 1993 does NOT do layer-by-layer elastic analysis**
    - **Instead, it asks:** "How thick would one reference material be 
    to provide the same support as this multi-layer system?"
    - **We CONVERT** multi-layer system → equivalent single layer
    - **We NEVER change** E or h of actual materials
    """)
    
    st.markdown("---")
    
    st.subheader("📐 Odemark Method Formula")
    
    st.markdown("""
    ### The Formula (CORRECT)
    
    $$h_e = \\sum_{i=1}^{n} h_i \\sqrt[3]{\\frac{E_i}{E_{ref}}}$$
    
    **Where:**
    - **h_i** = actual thickness of layer i (unchanged!)
    - **E_i** = actual elastic modulus of layer i (unchanged!)
    - **E_ref** = elastic modulus of reference material
    - **h_e** = equivalent thickness (what we calculate)
    
    ### What This Means:
    
    ✅ **We keep all E_i actual values**
    ✅ **We keep all h_i actual values**  
    ✅ **We calculate h_e** = "how thick would reference material be?"
    
    ❌ **We do NOT reduce E_i values**
    ❌ **We do NOT change h_i values**
    """)
    
    st.markdown("---")
    
    st.subheader("📊 Worked Example")
    
    example_data = {
        "Layer": ["AC", "CTB", "Granular Subbase"],
        "h actual (cm)": [5, 20, 15],
        "E actual (MPa)": [2500, 1200, 300],
        "E_ref (MPa)": [300, 300, 300],
        "E/E_ref": [8.33, 4.00, 1.00],
        "(E/E_ref)^(1/3)": [2.03, 1.59, 1.00],
        "h_eq (cm)": [10.2, 31.8, 15.0]
    }
    
    df_example = pd.DataFrame(example_data)
    st.dataframe(df_example, use_container_width=True, hide_index=True)
    
    st.markdown(f"""
    **Total h actual = 40 cm**
    
    **Total h_eq = 57.0 cm** (equivalent Granular thickness)
    
    **Interpretation:**
    Your 40 cm thick system (AC + CTB + Granular) provides the same support 
    as 57 cm of pure Granular material (300 MPa).
    
    This h_eq is then used to determine k using AASHTO charts/tables.
    """)
    
    st.markdown("---")
    
    st.subheader("🔄 Complete Design Flow (AASHTO 1993)")
    
    st.markdown("""
    1. **Determine Subgrade CBR** → Calculate E_SG
    2. **Calculate k₁** from E_SG (subgrade without support)
    3. **Define Pavement Layers** (actual h and E)
    4. **Choose Reference Material** (E_ref)
    5. **Calculate h_eq** using Odemark formula
    6. **Determine Loss of Support Factor (f_LS)**
    7. **Calculate k_eff** = k₁ / f_LS
    8. **Use k_eff in AASHTO design equation** → get concrete thickness
    
    This calculator handles steps 1-7 correctly.
    """)
    
    st.markdown("---")
    
    st.subheader("📋 Why AASHTO Doesn't Use Multilayer Elastic Theory")
    
    st.markdown("""
    **AASHTO 1993 Design Method is NOT Mechanistic-Empirical.**
    
    It uses a **simplified empirical approach** because:
    
    1. **Practical simplicity** - easier to use in 1993
    2. **Historical validation** - method based on decades of road performance data
    3. **Conservative** - doesn't require complex stress-strain calculations
    4. **One number (k)** - easier to apply in design equations
    
    **Modern approach (MEPDG/AASHTOWare)** uses mechanistic theory,
    but AASHTO 1993 is still widely used in many countries (including Thailand).
    """)
    
    st.markdown("---")
    
    st.subheader("📚 References & Material Database")
    
    ref_data = {
        "Material": [
            "Asphalt Concrete (AC)",
            "Cement Treated Base (CTB)",
            "Cement Modified Crushed Rock",
            "Lime Stabilized",
            "Crushed Aggregate (Granular)",
            "Soil Aggregate",
            "Subgrade (CBR 5%)"
        ],
        "E (MPa)": [2500, 1200, 800, 400, 300, 150, 55],
        "E (psi)": [362541, 174047, 116029, 58016, 43511, 21756, 7977]
    }
    
    df_ref = pd.DataFrame(ref_data)
    st.dataframe(df_ref, use_container_width=True, hide_index=True)
    
    st.markdown("""
    ### Sources:
    - **AASHTO (1993)** - Guide for Design of Pavement Structures
    - **Odemark, N. (1974)** - Investigations of the Structural Behaviour of Asphalt Pavements
    - **NCHRP (2004)** - Mechanistic–Empirical Design of New and Rehabilitated Pavement Structures
    - **Thai Department of Highways** - JPCP Design Standards
    """)

# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: gray; font-size: 12px; margin-top: 20px;">
        <p><b>AASHTO 1993 Odemark Equivalent Thickness & k-value Calculator</b></p>
        <p>For Rigid Pavement (JPCP) Design - CORRECT Conceptual Approach</p>
        <p style="font-style: italic;">
        "We CONVERT multi-layer systems to equivalent thickness of reference material,
        NOT reduce elastic modulus values"
        </p>
        <p>Last updated: {}  |  Version 2.0 (Corrected Concept)</p>
    </div>
""".format(datetime.now().strftime('%Y-%m-%d')), unsafe_allow_html=True)

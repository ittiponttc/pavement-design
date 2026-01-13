import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="Composite k∞ (AASHTO)", layout="wide")

st.title("📈 Composite Modulus of Subgrade Reaction (k∞)")
st.markdown("แนวคิดตาม **AASHTO 1993 Nomograph (Figure 3.3)**")

# ======================================================
# INPUT
# ======================================================
st.sidebar.header("🔧 กำหนดค่า")

D_eq = st.sidebar.number_input(
    "Equivalent thickness, D_eq (inch)",
    min_value=4.0,
    max_value=24.0,
    value=12.0,
    step=0.5
)

E_ref = st.sidebar.number_input(
    "Subbase modulus, E_ref (psi)",
    min_value=10000.0,
    max_value=300000.0,
    value=80000.0,
    step=5000.0
)

MR = st.sidebar.number_input(
    "Subgrade resilient modulus, M_R (psi)",
    min_value=1000.0,
    max_value=30000.0,
    value=8000.0,
    step=500.0
)

# ======================================================
# AASHTO-type empirical model (nomograph equivalent)
# ======================================================
C = 0.6
a = 0.65
b = 0.20
c = 0.45

k_inf = C * (MR ** a) * (E_ref ** b) / (D_eq ** c)

st.metric(
    "Composite modulus of subgrade reaction, k∞",
    f"{k_inf:,.1f} pci"
)

# ======================================================
# Create nomograph-like curve (black line)
# ======================================================
D_range = np.linspace(4, 24, 80)
k_curve = C * (MR ** a) * (E_ref ** b) / (D_range ** c)

df_curve = pd.DataFrame({
    "D (inch)": D_range,
    "k (pci)": k_curve
})

# User-defined intersection (red point)
df_point = pd.DataFrame({
    "D (inch)": [D_eq],
    "k (pci)": [k_inf]
})

# ======================================================
# Plot (Cloud-safe)
# ======================================================
st.subheader("📊 Nomograph-equivalent Plot")

st.line_chart(
    df_curve.set_index("D (inch)"),
    use_container_width=True
)

st.scatter_chart(
    df_point.set_index("D (inch)"),
    use_container_width=True
)

# ======================================================
# Explanation
# ======================================================
with st.expander("🧮 หลักการคำนวณ (Nomograph → สมการ)", expanded=False):

    st.latex(
        r"k_\infty = C \; M_R^{\,a} \; E_{SB}^{\,b} \; D_{SB}^{-c}"
    )

    st.markdown(
        f"""
- C = {C}  
- a = {a} (ผลของ subgrade)  
- b = {b} (ผลของ subbase stiffness)  
- c = {c} (ผลของความหนา)  

ค่าที่คำนวณได้:
"""
    )

    st.latex(
        rf"k_\infty = {k_inf:.1f}\ \mathrm{{pci}}"
    )

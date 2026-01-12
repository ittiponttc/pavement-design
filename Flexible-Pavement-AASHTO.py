import streamlit as st
import math
import pandas as pd

# =========================================================
# CORE CALCULATION (DO NOT TOUCH – VALIDATED)
# =========================================================

def bisection_method(func, a, b, tol=1e-6, max_iter=100):
    fa, fb = func(a), func(b)
    if fa * fb > 0:
        return None
    for _ in range(max_iter):
        c = (a + b) / 2
        fc = func(c)
        if abs(fc) < tol or (b - a) / 2 < tol:
            return c
        if fa * fc < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc
    return (a + b) / 2


def calculate_MR_from_CBR(CBR):
    return 1500 * CBR if CBR <= 10 else 3000 * (CBR ** 0.65)


def calculate_log_W18_flexible(SN, params):
    if SN <= 0:
        return -999

    ZR = params["ZR"]
    S0 = params["S0"]
    MR = params["MR"]
    dPSI = params["delta_PSI"]

    return (
        ZR * S0
        + 9.36 * math.log10(SN + 1) - 0.20
        + math.log10(dPSI / 2.7) / (0.40 + 1094 / (SN + 1) ** 5.19)
        + 2.32 * math.log10(MR) - 8.07
    )


def find_required_SN(W18, params, SN_min=1.0, SN_max=15.0):
    logW = math.log10(W18)

    def f(SN):
        return calculate_log_W18_flexible(SN, params) - logW

    if f(SN_min) > 0:
        return SN_min
    if f(SN_max) < 0:
        return SN_max

    return bisection_method(f, SN_min, SN_max)


def calculate_SN(layers):
    SN = 0.0
    rows = []
    for L in layers:
        SN_i = L["a"] * L["D_inch"] * L["m"]
        SN += SN_i
        rows.append({
            "Layer": L["name"],
            "a": L["a"],
            "D (inch)": L["D_inch"],
            "D (cm)": L["D_inch"] * 2.54,
            "m": L["m"],
            "SN": SN_i
        })
    return SN, pd.DataFrame(rows)

# =========================================================
# MATERIAL LIBRARY (AASHTO 1993 DEFAULTS)
# =========================================================

MATERIAL_LIBRARY = {
    "Surface Course": {
        "Asphalt Concrete (Dense-graded)": {"a": 0.42, "m": 1.00},
        "Asphalt Concrete (Open-graded)": {"a": 0.38, "m": 1.00},
        "Stone Mastic Asphalt (SMA)": {"a": 0.44, "m": 1.00},
    },
    "Base Course": {
        "Crushed Stone Base": {"a": 0.14, "m": 1.00},
        "Cement Treated Base (CTB)": {"a": 0.20, "m": 1.00},
        "Emulsified Asphalt Base": {"a": 0.25, "m": 1.00},
    },
    "Subbase Course": {
        "Granular Subbase": {"a": 0.11, "m": 1.00},
        "Sand / Sandy Gravel": {"a": 0.08, "m": 1.00},
        "Soil Cement": {"a": 0.15, "m": 1.00},
    }
}

DEFAULT_THICKNESS = {
    "Surface Course": 4.0,
    "Base Course": 6.0,
    "Subbase Course": 6.0
}

# =========================================================
# STREAMLIT UI
# =========================================================

st.set_page_config(page_title="AASHTO 1993 Flexible Pavement", layout="wide")
st.title("🛣️ AASHTO 1993 – Flexible Pavement Design (Material-Based)")
st.caption("Validated AASHTO engine + editable material table")

# ---------------------------------------------------------
# SIDEBAR – DESIGN INPUT
# ---------------------------------------------------------

st.sidebar.header("Design Parameters")

ZR = st.sidebar.selectbox(
    "Reliability",
    {
        "80%": -0.841,
        "85%": -1.037,
        "90%": -1.282,
        "95%": -1.645,
        "99%": -2.327
    }.items(),
    index=2,
    format_func=lambda x: x[0]
)[1]

S0 = st.sidebar.slider("Overall Std. Dev. (S₀)", 0.40, 0.50, 0.45, 0.01)

Pi = st.sidebar.slider("Initial Serviceability (Pᵢ)", 4.0, 4.5, 4.2, 0.1)
pt = st.sidebar.slider("Terminal Serviceability (pₜ)", 2.0, 3.0, 2.5, 0.1)

W18 = st.sidebar.number_input(
    "Design Traffic W₁₈ (ESAL)",
    min_value=100_000,
    max_value=500_000_000,
    value=10_000_000,
    step=1_000_000
)

CBR = st.sidebar.slider("Subgrade CBR (%)", 2.0, 30.0, 5.0, 0.5)
MR = calculate_MR_from_CBR(CBR)

params = {
    "ZR": ZR,
    "S0": S0,
    "MR": MR,
    "delta_PSI": Pi - pt
}

# ---------------------------------------------------------
# MATERIAL TABLE
# ---------------------------------------------------------

st.subheader("🧱 Layer Materials & Parameters")

rows = []
for layer, mats in MATERIAL_LIBRARY.items():
    mat = st.selectbox(layer, list(mats.keys()), key=layer)
    rows.append({
        "Layer": layer,
        "Material": mat,
        "a": mats[mat]["a"],
        "D (inch)": DEFAULT_THICKNESS[layer],
        "m": mats[mat]["m"]
    })

df_layers = st.data_editor(
    pd.DataFrame(rows),
    hide_index=True,
    use_container_width=True,
    column_config={
        "Layer": st.column_config.TextColumn(disabled=True),
        "Material": st.column_config.TextColumn(disabled=True),
        "a": st.column_config.NumberColumn("Layer Coefficient (a)", format="%.2f"),
        "D (inch)": st.column_config.NumberColumn("Thickness (inch)", format="%.1f"),
        "m": st.column_config.NumberColumn("Drainage Coefficient (m)", format="%.2f"),
    }
)

# ---------------------------------------------------------
# CALCULATION
# ---------------------------------------------------------

layers = []
for _, r in df_layers.iterrows():
    layers.append({
        "name": r["Layer"],
        "a": r["a"],
        "D_inch": r["D (inch)"],
        "m": r["m"]
    })

SN_provided, df_SN = calculate_SN(layers)
SN_required = find_required_SN(W18, params)

logW = calculate_log_W18_flexible(SN_provided, params)
W18_supported = 10 ** logW

# ---------------------------------------------------------
# RESULTS
# ---------------------------------------------------------

st.subheader("📊 Results")

c1, c2, c3 = st.columns(3)
c1.metric("SN Required", f"{SN_required:.2f}")
c2.metric("SN Provided", f"{SN_provided:.3f}", f"{SN_provided - SN_required:+.3f}")
c3.metric("W₁₈ Supported", f"{W18_supported:,.0f}",
          f"{(W18_supported / W18 - 1) * 100:+.1f}%")

st.dataframe(df_SN, use_container_width=True)

if SN_provided >= SN_required:
    st.success("✅ Design satisfies AASHTO 1993 requirements")
else:
    st.error("❌ Design does NOT satisfy AASHTO 1993 requirements")

st.markdown("---")
st.caption("For teaching & research – AASHTO 1993 Flexible Pavement")

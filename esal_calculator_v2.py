"""
ESAL Calculator – AASHTO 1993 (Equation-based)
Correct implementation of EALF / Truck Factor
For teaching & engineering use

Developed for:
Department of Civil Engineering Education
King Mongkut’s University of Technology North Bangkok
"""

import math
import pandas as pd
import streamlit as st

# ============================================================
# CONSTANTS
# ============================================================
TON_TO_KIP = 2.20462
AXLE_GROUP = {"Single": 1, "Tandem": 2, "Tridem": 3}

# Default truck configurations (DOH-style)
DEFAULT_TRUCKS = {
    "MB": {"desc": "Medium Bus", "axles": [(4.0, "Single"), (11.0, "Single")]},
    "HB": {"desc": "Heavy Bus", "axles": [(4.0, "Single"), (11.0, "Single")]},
    "MT": {"desc": "Medium Truck (6 wheels)", "axles": [(4.0, "Single"), (11.0, "Single")]},
    "HT": {"desc": "Heavy Truck (10 wheels)", "axles": [(5.0, "Single"), (20.0, "Tandem")]},
    "ST": {"desc": "Semi-Trailer (18 wheels)", "axles": [(5.0, "Single"), (20.0, "Tandem"), (20.0, "Tandem")]},
    "FT": {"desc": "Full Trailer (18 wheels)", "axles": [(5.0, "Single"), (20.0, "Tandem"), (11.0, "Single"), (11.0, "Single")]}
}

# ============================================================
# AASHTO 1993 – CORE THEORY
# ============================================================

def calc_Gt(pt: float) -> float:
    """
    Gt = log10((4.5 - pt) / (4.5 - 1.5))
    """
    return math.log10((4.5 - pt) / (4.5 - 1.5))


def calc_Bx_flexible(SN: float, axle_group: int) -> float:
    """
    Bx for Flexible Pavement (AASHTO 1993)
    """
    base = 1094 / (SN + 1) ** 5.19

    if axle_group == 1:      # Single
        return 0.40 + base
    elif axle_group == 2:    # Tandem
        return 0.30 + base
    elif axle_group == 3:    # Tridem
        return 0.22 + base
    else:
        raise ValueError("Invalid axle group")


def ealf_flexible(load_kip: float, axle_group: int, SN: float, pt: float) -> float:
    """
    Equivalent Axle Load Factor (Flexible Pavement)
    AASHTO 1993 – Equation-based
    """

    Gt = calc_Gt(pt)

    Bx = calc_Bx_flexible(SN, axle_group)

    # B18 evaluated at standard axle (18 kip)
    L18 = 18.0
    B18 = Bx * (L18 / load_kip) ** 4.0

    log_ratio = (Bx - B18) / (1.0 + Gt)

    return 10 ** log_ratio


def truck_factor_flexible(axles, SN, pt) -> float:
    """
    Truck Factor = sum of EALF of all axles
    """
    tf = 0.0
    for load_ton, axle_type in axles:
        load_kip = load_ton * TON_TO_KIP
        group = AXLE_GROUP[axle_type]
        tf += ealf_flexible(load_kip, group, SN, pt)
    return tf


# ============================================================
# ESAL CALCULATION
# ============================================================

def calc_esal(df, truck_factors, lane_factor, direction_factor):
    rows = []
    total_esal = 0.0

    for _, r in df.iterrows():
        year_esal = 0.0
        row = {"Year": int(r["Year"])}

        for code, tf in truck_factors.items():
            if code in df.columns:
                aadt = float(r[code])
                esal = aadt * tf * lane_factor * direction_factor * 365
                row[code] = f"{esal:,.0f}"
                year_esal += esal

        row["ESAL Total"] = f"{year_esal:,.0f}"
        total_esal += year_esal
        rows.append(row)

    return pd.DataFrame(rows), total_esal


def traffic_template():
    base = {"MB": 120, "HB": 60, "MT": 250, "HT": 180, "ST": 120, "FT": 100}
    data = {"Year": list(range(1, 21))}
    for k, v in base.items():
        data[k] = [int(v * (1.045 ** i)) for i in range(20)]
    return pd.DataFrame(data)


# ============================================================
# STREAMLIT APP
# ============================================================

def main():
    st.set_page_config("ESAL Calculator – AASHTO 1993", "🛣️", layout="wide")
    st.title("🛣️ ESAL Calculator – AASHTO 1993 (Equation-based)")

    with st.sidebar:
        st.header("Design Parameters")
        SN = st.selectbox("Structural Number (SN)", [4, 5, 6, 7], index=1)
        pt = st.selectbox("Terminal Serviceability (pt)", [2.5, 2.0], index=0)
        lane_factor = st.slider("Lane Distribution Factor", 0.1, 1.0, 0.9, 0.05)
        direction_factor = st.slider("Directional Distribution Factor", 0.1, 1.0, 0.5, 0.05)

    # Truck factors
    st.subheader("🚛 Truck Factors (AASHTO 1993)")
    tf_data = []

    truck_factors = {}
    for code, t in DEFAULT_TRUCKS.items():
        tf = truck_factor_flexible(t["axles"], SN, pt)
        truck_factors[code] = tf
        axle_desc = " + ".join([f"{a[0]} t ({a[1]})" for a in t["axles"]])
        tf_data.append({
            "Code": code,
            "Vehicle": t["desc"],
            "Axles": axle_desc,
            "Truck Factor": round(tf, 3)
        })

    st.dataframe(pd.DataFrame(tf_data), use_container_width=True)

    st.divider()

    # Traffic input
    st.subheader("📊 Traffic Data")
    uploaded = st.file_uploader("Upload CSV", type="csv")

    if uploaded:
        traffic_df = pd.read_csv(uploaded)
    else:
        traffic_df = traffic_template()

    st.dataframe(traffic_df, use_container_width=True)

    st.divider()

    # ESAL result
    result_df, total_esal = calc_esal(
        traffic_df,
        truck_factors,
        lane_factor,
        direction_factor
    )

    st.subheader("📈 ESAL Results")
    st.metric("Total ESAL", f"{total_esal:,.0f}")
    st.dataframe(result_df, use_container_width=True)

    st.caption("AASHTO Guide for Design of Pavement Structures (1993) – Equation-based implementation")


if __name__ == "__main__":
    main()

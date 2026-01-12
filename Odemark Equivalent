import streamlit as st
import pandas as pd

st.set_page_config(page_title="Odemark Equivalent Thickness", layout="centered")

st.title("Equivalent Thickness Calculator")
st.caption("Odemark (1974) – AASHTO 1993 Subbase Evaluation")

# ----------------------------
# Material database (editable)
# ----------------------------
material_db = {
    "Asphalt Concrete (AC)": 2500,
    "Cement Treated Base (CTB)": 1200,
    "Cement Modified Crushed Rock": 800,
    "Crushed Aggregate": 300,
    "Soil Aggregate": 150
}

# ----------------------------
# User inputs
# ----------------------------
st.subheader("1️⃣ General Settings")

num_layers = st.selectbox("Number of layers", [1, 2, 3, 4], index=2)

ref_material = st.selectbox(
    "Reference Material (E_ref)",
    list(material_db.keys()),
    index=1
)

E_ref = material_db[ref_material]

f = st.slider(
    "Correction factor (f)",
    min_value=0.7,
    max_value=1.0,
    value=0.9,
    step=0.05
)

st.markdown(f"**E_ref = {E_ref} MPa**")

# ----------------------------
# Layer inputs
# ----------------------------
st.subheader("2️⃣ Pavement Layers")

layers = []

for i in range(num_layers):
    with st.expander(f"Layer {i+1}", expanded=True):
        mat = st.selectbox(
            f"Material – Layer {i+1}",
            list(material_db.keys()),
            key=f"mat_{i}"
        )
        h = st.number_input(
            f"Thickness (cm) – Layer {i+1}",
            min_value=0.0,
            value=10.0,
            step=1.0,
            key=f"h_{i}"
        )
        E = st.number_input(
            f"Elastic Modulus E (MPa) – Layer {i+1}",
            min_value=10.0,
            value=float(material_db[mat]),
            step=50.0,
            key=f"E_{i}"
        )

        layers.append({
            "Layer": i + 1,
            "Material": mat,
            "Thickness (cm)": h,
            "E (MPa)": E
        })

# ----------------------------
# Calculation
# ----------------------------
st.subheader("3️⃣ Results")

if st.button("Calculate Equivalent Thickness"):
    results = []
    total_heq = 0.0

    for layer in layers:
        h = layer["Thickness (cm)"]
        E = layer["E (MPa)"]
        heq = f * h * (E / E_ref) ** (1 / 3)
        total_heq += heq

        results.append({
            "Layer": layer["Layer"],
            "Material": layer["Material"],
            "h (cm)": h,
            "E (MPa)": E,
            "h_eq (cm)": round(heq, 2)
        })

    df = pd.DataFrame(results)

    st.markdown("### 🔹 Equivalent Thickness by Layer")
    st.dataframe(df, use_container_width=True)

    st.markdown("### 🔹 Total Equivalent Thickness")
    st.success(f"{total_heq:.2f} cm  |  {total_heq/2.54:.2f} inch")

    st.markdown("---")
    st.caption(
        "Note: Odemark method with correction factor "
        "is used for equivalent subbase thickness evaluation "
        "prior to effective k-value determination (AASHTO 1993)."
    )

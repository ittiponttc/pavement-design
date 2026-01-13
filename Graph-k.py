import numpy as np
import matplotlib.pyplot as plt

# ==============================
# INPUT (จากผู้ใช้)
# ==============================
D_eq = 12.0        # equivalent thickness (inch)
E_ref = 80000.0    # subbase modulus (psi)
MR = 8000.0        # subgrade resilient modulus (psi)

# ==============================
# Empirical AASHTO-type equation
# ==============================
# k_infinity = C * MR^a * E^b * D^c
C = 0.6
a = 0.65
b = 0.20
c = 0.45

k_inf = C * (MR**a) * (E_ref**b) / (D_eq**c)

# ==============================
# Create reference curves (black)
# ==============================
D_range = np.linspace(4, 20, 100)
k_ref = C * (MR**a) * (E_ref**b) / (D_range**c)

# ==============================
# Plot
# ==============================
plt.figure(figsize=(7, 8))

# Standard curve (black)
plt.loglog(D_range, k_ref, 'k-', label="Nomograph trend")

# User-defined point & lines (red)
plt.axvline(D_eq, color='red', linestyle='--')
plt.axhline(k_inf, color='red', linestyle='--')
plt.plot(D_eq, k_inf, 'ro', label="User-defined point")

plt.xlabel("Equivalent Subbase Thickness, D (inch)")
plt.ylabel("Composite Modulus of Subgrade Reaction, k∞ (pci)")
plt.title("Composite Modulus of Subgrade Reaction (AASHTO concept)")
plt.grid(True, which="both", linestyle="--", alpha=0.5)
plt.legend()

plt.show()

print(f"Composite modulus k∞ = {k_inf:.1f} pci")

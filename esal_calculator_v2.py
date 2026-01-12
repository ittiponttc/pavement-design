"""
ESAL Calculator - AASHTO 1993
คำนวณปริมาณเพลาเดี่ยวมาตรฐานเทียบเท่า (Equivalent Single Axle Load)
ใช้ Lookup Table จาก AASHTO 1993 พร้อม Linear Interpolation
พัฒนาสำหรับ: ภาควิชาครุศาสตร์โยธา มจพ.
"""

import streamlit as st
import pandas as pd

# ============================================================
# ค่าคงที่
# ============================================================
TON_TO_KIP = 2.2046
AXLE_TYPES = {'Single': 1, 'Tandem': 2, 'Tridem': 3}

# ค่าเริ่มต้นรถบรรทุก 6 ชนิดตามกรมทางหลวง
DEFAULT_TRUCKS = {
    'MB': {'desc': 'Medium Bus', 'front': (3.1, 'Single'), 'rear': (12.2, 'Tandem')},
    'HB': {'desc': 'Heavy Bus', 'front': (4.0, 'Single'), 'rear': (14.3, 'Tandem')},
    'MT': {'desc': 'Medium Truck', 'front': (4.0, 'Single'), 'rear': (11.0, 'Single')},
    'HT': {'desc': 'Heavy Truck', 'front': (5.0, 'Single'), 'rear': (20.0, 'Tandem')},
    'STR': {'desc': 'Semi-Trailer', 'front': (5.0, 'Single'), 'rear': (20.0, 'Tandem'), 'trailer_rear': (20.0, 'Tandem')},
    'TR': {'desc': 'Full Trailer', 'front': (5.0, 'Single'), 'rear': (17.75, 'Tandem'), 'trailer_front': (10.0, 'Single'), 'trailer_rear': (17.75, 'Tandem')}
}

# ============================================================
# AASHTO 1993 LEF Lookup Tables
# Source: AASHTO Guide for Design of Pavement Structures (1993)
# Tables D.4-D.16
# ============================================================

# Rigid Pavement - Single Axle (kip -> LEF)
# Format: {D: {pt: {kip: LEF}}}
LEF_RIGID_SINGLE = {
    10: {
        2.5: {2:0.0002, 4:0.003, 6:0.01, 8:0.03, 10:0.08, 12:0.18, 14:0.35, 16:0.61, 18:1.00, 20:1.55, 22:2.32, 24:3.37, 26:4.76, 28:6.58, 30:8.92, 32:11.9, 34:15.5, 36:20.0, 38:25.5, 40:32.2},
        2.0: {2:0.0002, 4:0.003, 6:0.01, 8:0.04, 10:0.09, 12:0.19, 14:0.36, 16:0.62, 18:1.00, 20:1.53, 22:2.27, 24:3.27, 26:4.59, 28:6.29, 30:8.47, 32:11.2, 34:14.6, 36:18.7, 38:23.8, 40:29.9}
    },
    11: {
        2.5: {2:0.0002, 4:0.002, 6:0.01, 8:0.03, 10:0.08, 12:0.17, 14:0.34, 16:0.60, 18:1.00, 20:1.57, 22:2.38, 24:3.50, 26:5.01, 28:7.02, 30:9.63, 32:12.9, 34:17.1, 36:22.2, 38:28.5, 40:36.2},
        2.0: {2:0.0002, 4:0.002, 6:0.01, 8:0.03, 10:0.08, 12:0.18, 14:0.35, 16:0.61, 18:1.00, 20:1.56, 22:2.34, 24:3.42, 26:4.86, 28:6.76, 30:9.21, 32:12.3, 34:16.2, 36:21.0, 38:26.9, 40:34.1}
    },
    12: {
        2.5: {2:0.0002, 4:0.002, 6:0.01, 8:0.03, 10:0.07, 12:0.17, 14:0.34, 16:0.60, 18:1.00, 20:1.58, 22:2.42, 24:3.60, 26:5.21, 28:7.38, 30:10.24, 32:13.9, 34:18.6, 36:24.4, 38:31.6, 40:40.5},
        2.0: {2:0.0002, 4:0.002, 6:0.01, 8:0.03, 10:0.08, 12:0.17, 14:0.34, 16:0.61, 18:1.00, 20:1.57, 22:2.39, 24:3.53, 26:5.07, 28:7.14, 30:9.87, 32:13.4, 34:17.8, 36:23.3, 38:30.1, 40:38.6}
    },
    13: {
        2.5: {2:0.0002, 4:0.002, 6:0.01, 8:0.03, 10:0.07, 12:0.17, 14:0.34, 16:0.60, 18:1.00, 20:1.59, 22:2.45, 24:3.67, 26:5.36, 28:7.67, 30:10.76, 32:14.8, 34:20.0, 36:26.5, 38:34.6, 40:44.7},
        2.0: {2:0.0002, 4:0.002, 6:0.01, 8:0.03, 10:0.07, 12:0.17, 14:0.34, 16:0.60, 18:1.00, 20:1.58, 22:2.42, 24:3.61, 26:5.24, 28:7.44, 30:10.4, 32:14.2, 34:19.2, 36:25.4, 38:33.2, 40:42.9}
    },
    14: {
        2.5: {2:0.0002, 4:0.002, 6:0.01, 8:0.03, 10:0.07, 12:0.17, 14:0.33, 16:0.60, 18:1.00, 20:1.59, 22:2.47, 24:3.73, 26:5.48, 28:7.90, 30:11.2, 32:15.5, 34:21.2, 36:28.4, 38:37.5, 40:48.8},
        2.0: {2:0.0002, 4:0.002, 6:0.01, 8:0.03, 10:0.07, 12:0.17, 14:0.34, 16:0.60, 18:1.00, 20:1.59, 22:2.45, 24:3.67, 26:5.38, 28:7.70, 30:10.8, 32:15.0, 34:20.4, 36:27.3, 38:36.0, 40:46.8}
    }
}

# Rigid Pavement - Tandem Axle (kip -> LEF)
LEF_RIGID_TANDEM = {
    10: {
        2.5: {10:0.01, 14:0.04, 18:0.10, 22:0.21, 26:0.40, 30:0.69, 34:1.11, 38:1.69, 42:2.48, 46:3.53, 50:4.88, 54:6.61, 58:8.79, 62:11.5, 66:14.7, 70:18.6, 74:23.3, 78:28.8, 82:35.2, 86:42.7, 90:51.4},
        2.0: {10:0.01, 14:0.04, 18:0.10, 22:0.22, 26:0.41, 30:0.70, 34:1.11, 38:1.68, 42:2.44, 46:3.44, 50:4.72, 54:6.34, 58:8.36, 62:10.9, 66:13.8, 70:17.4, 74:21.6, 78:26.6, 82:32.4, 86:39.1, 90:46.9}
    },
    11: {
        2.5: {10:0.01, 14:0.03, 18:0.09, 22:0.19, 26:0.37, 30:0.65, 34:1.06, 38:1.64, 42:2.44, 46:3.52, 50:4.93, 54:6.75, 58:9.09, 62:12.0, 66:15.6, 70:20.0, 74:25.2, 78:31.5, 82:38.9, 86:47.5, 90:57.6},
        2.0: {10:0.01, 14:0.04, 18:0.09, 22:0.20, 26:0.38, 30:0.66, 34:1.07, 38:1.64, 42:2.42, 46:3.46, 50:4.81, 54:6.54, 58:8.73, 62:11.5, 66:14.8, 70:18.9, 74:23.8, 78:29.6, 82:36.5, 86:44.5, 90:53.9}
    },
    12: {
        2.5: {10:0.01, 14:0.03, 18:0.08, 22:0.18, 26:0.35, 30:0.61, 34:1.01, 38:1.58, 42:2.39, 46:3.48, 50:4.95, 54:6.86, 58:9.35, 62:12.5, 66:16.4, 70:21.2, 74:27.1, 78:34.1, 82:42.5, 86:52.3, 90:63.8},
        2.0: {10:0.01, 14:0.03, 18:0.08, 22:0.18, 26:0.36, 30:0.62, 34:1.02, 38:1.59, 42:2.38, 46:3.45, 50:4.87, 54:6.70, 58:9.07, 62:12.1, 66:15.8, 70:20.3, 74:25.9, 78:32.6, 82:40.5, 86:49.8, 90:60.6}
    },
    13: {
        2.5: {10:0.01, 14:0.03, 18:0.08, 22:0.17, 26:0.33, 30:0.58, 34:0.97, 38:1.53, 42:2.33, 46:3.44, 50:4.95, 54:6.93, 58:9.56, 62:12.9, 66:17.1, 70:22.4, 74:28.9, 78:36.6, 82:46.0, 86:57.0, 90:70.0},
        2.0: {10:0.01, 14:0.03, 18:0.08, 22:0.17, 26:0.34, 30:0.59, 34:0.98, 38:1.53, 42:2.33, 46:3.42, 50:4.90, 54:6.82, 58:9.35, 62:12.6, 66:16.6, 70:21.7, 74:27.8, 78:35.3, 82:44.2, 86:54.8, 90:67.2}
    },
    14: {
        2.5: {10:0.01, 14:0.03, 18:0.07, 22:0.16, 26:0.32, 30:0.56, 34:0.93, 38:1.48, 42:2.28, 46:3.39, 50:4.93, 54:6.99, 58:9.74, 62:13.3, 66:17.8, 70:23.5, 74:30.6, 78:39.2, 82:49.5, 86:61.8, 90:76.3},
        2.0: {10:0.01, 14:0.03, 18:0.07, 22:0.16, 26:0.32, 30:0.57, 34:0.94, 38:1.49, 42:2.28, 46:3.38, 50:4.89, 54:6.90, 58:9.54, 62:13.0, 66:17.4, 70:22.8, 74:29.6, 78:37.9, 82:47.8, 86:59.7, 90:73.6}
    }
}

# Flexible Pavement - Single Axle (kip -> LEF)
# Format: {SN: {pt: {kip: LEF}}}
LEF_FLEX_SINGLE = {
    4: {
        2.5: {2:0.0003, 4:0.004, 6:0.02, 8:0.05, 10:0.12, 12:0.26, 14:0.50, 16:0.91, 18:1.57, 20:2.61, 22:4.21, 24:6.60, 26:10.1, 28:15.2, 30:22.4, 32:32.5, 34:46.6, 36:66.0, 38:92.4, 40:128},
        2.0: {2:0.0002, 4:0.003, 6:0.01, 8:0.04, 10:0.09, 12:0.18, 14:0.34, 16:0.60, 18:1.00, 20:1.61, 22:2.52, 24:3.85, 26:5.76, 28:8.45, 30:12.2, 32:17.3, 34:24.3, 36:33.6, 38:46.0, 40:62.4}
    },
    5: {
        2.5: {2:0.0002, 4:0.003, 6:0.01, 8:0.04, 10:0.10, 12:0.21, 14:0.40, 16:0.72, 18:1.23, 20:2.02, 22:3.22, 24:4.99, 26:7.55, 28:11.2, 30:16.3, 32:23.4, 34:33.2, 36:46.4, 38:64.2, 40:88.0},
        2.0: {2:0.0002, 4:0.003, 6:0.01, 8:0.04, 10:0.08, 12:0.16, 14:0.30, 16:0.53, 18:0.87, 20:1.38, 22:2.14, 24:3.23, 26:4.78, 28:6.92, 30:9.88, 32:13.9, 34:19.3, 36:26.5, 38:36.0, 40:48.5}
    },
    6: {
        2.5: {2:0.0002, 4:0.002, 6:0.01, 8:0.03, 10:0.08, 12:0.17, 14:0.33, 16:0.59, 18:1.00, 20:1.63, 22:2.57, 24:3.95, 26:5.92, 28:8.71, 30:12.6, 32:17.9, 34:25.1, 36:34.8, 38:47.7, 40:64.8},
        2.0: {2:0.0002, 4:0.002, 6:0.01, 8:0.03, 10:0.07, 12:0.14, 14:0.27, 16:0.47, 18:0.77, 20:1.21, 22:1.86, 24:2.78, 26:4.08, 28:5.86, 30:8.28, 32:11.6, 34:15.9, 36:21.7, 38:29.2, 40:39.0}
    },
    7: {
        2.5: {2:0.0002, 4:0.002, 6:0.01, 8:0.03, 10:0.07, 12:0.15, 14:0.29, 16:0.51, 18:0.86, 20:1.40, 22:2.19, 24:3.34, 26:4.99, 28:7.28, 30:10.5, 32:14.8, 34:20.7, 36:28.5, 38:38.8, 40:52.4},
        2.0: {2:0.0002, 4:0.002, 6:0.01, 8:0.03, 10:0.07, 12:0.13, 14:0.24, 16:0.43, 18:0.70, 20:1.10, 22:1.68, 24:2.49, 26:3.63, 28:5.17, 30:7.27, 32:10.1, 34:13.7, 36:18.6, 38:24.9, 40:33.0}
    }
}

# Flexible Pavement - Tandem Axle (kip -> LEF)
LEF_FLEX_TANDEM = {
    4: {
        2.5: {10:0.01, 14:0.04, 18:0.10, 22:0.22, 26:0.43, 30:0.76, 34:1.25, 38:1.96, 42:2.95, 46:4.28, 50:6.04, 54:8.32, 58:11.3, 62:15.0, 66:19.7, 70:25.6, 74:32.8, 78:41.5, 82:52.0, 86:64.6, 90:79.5},
        2.0: {10:0.01, 14:0.03, 18:0.07, 22:0.14, 26:0.26, 30:0.44, 34:0.70, 38:1.06, 42:1.55, 46:2.18, 50:3.00, 54:4.03, 58:5.33, 62:6.93, 66:8.88, 70:11.3, 74:14.1, 78:17.5, 82:21.5, 86:26.2, 90:31.7}
    },
    5: {
        2.5: {10:0.01, 14:0.03, 18:0.08, 22:0.17, 26:0.33, 30:0.58, 34:0.95, 38:1.48, 42:2.21, 46:3.20, 50:4.49, 54:6.16, 58:8.28, 62:10.9, 66:14.3, 70:18.4, 74:23.4, 78:29.5, 82:36.7, 86:45.3, 90:55.5},
        2.0: {10:0.01, 14:0.03, 18:0.06, 22:0.11, 26:0.21, 30:0.35, 34:0.55, 38:0.83, 42:1.20, 46:1.69, 50:2.31, 54:3.10, 58:4.08, 62:5.28, 66:6.74, 70:8.51, 74:10.6, 78:13.1, 82:16.0, 86:19.4, 90:23.4}
    },
    6: {
        2.5: {10:0.01, 14:0.03, 18:0.07, 22:0.14, 26:0.26, 30:0.46, 34:0.75, 38:1.16, 42:1.73, 46:2.49, 50:3.50, 54:4.80, 58:6.45, 62:8.50, 66:11.0, 70:14.2, 74:18.0, 78:22.6, 82:28.1, 86:34.6, 90:42.2},
        2.0: {10:0.01, 14:0.02, 18:0.05, 22:0.10, 26:0.18, 30:0.29, 34:0.46, 38:0.69, 42:0.99, 46:1.38, 50:1.88, 54:2.51, 58:3.29, 62:4.25, 66:5.42, 70:6.82, 74:8.49, 78:10.5, 82:12.8, 86:15.5, 90:18.6}
    },
    7: {
        2.5: {10:0.01, 14:0.02, 18:0.06, 22:0.12, 26:0.22, 30:0.38, 34:0.62, 38:0.96, 42:1.43, 46:2.05, 50:2.88, 54:3.95, 58:5.30, 62:6.98, 66:9.04, 70:11.6, 74:14.6, 78:18.3, 82:22.7, 86:28.0, 90:34.1},
        2.0: {10:0.01, 14:0.02, 18:0.05, 22:0.09, 26:0.15, 30:0.25, 34:0.40, 38:0.59, 42:0.85, 46:1.18, 50:1.60, 54:2.13, 58:2.78, 62:3.58, 66:4.55, 70:5.72, 74:7.11, 78:8.74, 82:10.7, 86:12.9, 90:15.5}
    }
}

# ============================================================
# ฟังก์ชัน Interpolation
# ============================================================
def interpolate_lef(table, load_kip):
    """Linear interpolation สำหรับค่า LEF"""
    kips = sorted(table.keys())
    
    if load_kip <= kips[0]:
        return table[kips[0]] * (load_kip / kips[0]) ** 4  # Fourth power law for extrapolation
    if load_kip >= kips[-1]:
        return table[kips[-1]] * (load_kip / kips[-1]) ** 4
    
    for i in range(len(kips) - 1):
        if kips[i] <= load_kip <= kips[i+1]:
            x0, x1 = kips[i], kips[i+1]
            y0, y1 = table[x0], table[x1]
            return y0 + (y1 - y0) * (load_kip - x0) / (x1 - x0)
    
    return 0

def get_lef(load_ton, axle_type, pavement_type, pt, param):
    """ดึงค่า LEF จาก lookup table"""
    load_kip = load_ton * TON_TO_KIP
    L2 = AXLE_TYPES[axle_type]
    
    if pavement_type == 'rigid':
        if L2 == 1:
            table = LEF_RIGID_SINGLE.get(param, {}).get(pt, {})
        else:  # Tandem
            table = LEF_RIGID_TANDEM.get(param, {}).get(pt, {})
    else:  # flexible
        if L2 == 1:
            table = LEF_FLEX_SINGLE.get(param, {}).get(pt, {})
        else:  # Tandem
            table = LEF_FLEX_TANDEM.get(param, {}).get(pt, {})
    
    if not table:
        return 0
    
    return interpolate_lef(table, load_kip)

def calc_truck_factor(axles, pavement_type, pt, param):
    """คำนวณ Truck Factor จากข้อมูลเพลาทั้งหมด"""
    total_lef = 0
    for load_ton, axle_type in axles:
        if load_ton > 0:
            total_lef += get_lef(load_ton, axle_type, pavement_type, pt, param)
    return total_lef

# ============================================================
# ฟังก์ชันช่วย
# ============================================================
def create_template():
    """สร้าง Template"""
    base = {'MB': 120, 'HB': 60, 'MT': 250, 'HT': 180, 'STR': 120, 'TR': 100}
    data = {'Year': list(range(1, 21))}
    for code, val in base.items():
        data[code] = [int(val * (1.045 ** i)) for i in range(20)]
    return pd.DataFrame(data)

def to_csv(df):
    return df.to_csv(index=False).encode('utf-8-sig')

def calculate_esal(traffic_df, truck_factors, lane_factor, direction_factor):
    """คำนวณ ESAL"""
    results = []
    total_esal = 0
    
    for idx, row in traffic_df.iterrows():
        year = row.get('Year', idx + 1)
        year_data = {'ปีที่': int(year) if pd.notna(year) else idx + 1}
        year_esal = 0
        
        for code, tf in truck_factors.items():
            if code in traffic_df.columns:
                try:
                    aadt = float(row[code]) if pd.notna(row[code]) else 0
                except:
                    aadt = 0
                esal = aadt * tf * lane_factor * direction_factor * 365
                year_data[code] = f"{esal:,.0f}"
                year_esal += esal
        
        year_data['ESAL รวม'] = f"{year_esal:,.0f}"
        total_esal += year_esal
        results.append(year_data)
    
    return pd.DataFrame(results), total_esal

# ============================================================
# Streamlit App
# ============================================================
def main():
    st.set_page_config(page_title="ESAL Calculator", page_icon="🛣️", layout="wide")
    
    st.markdown("""
    <style>
    .main-title {font-size: 2.2rem; font-weight: bold; color: #1E3A5F; text-align: center; margin-bottom: 1.5rem;}
    .metric-box {background: linear-gradient(135deg, #1E3A5F, #4A6FA5); padding: 1rem; border-radius: 8px; color: white; text-align: center;}
    .metric-value {font-size: 1.8rem; font-weight: bold;}
    .metric-label {font-size: 0.85rem; opacity: 0.9;}
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="main-title">🛣️ ESAL Calculator - AASHTO 1993</p>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'trucks' not in st.session_state:
        st.session_state.trucks = {k: v.copy() for k, v in DEFAULT_TRUCKS.items()}
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ พารามิเตอร์")
        
        pavement_type = st.selectbox("ประเภทผิวทาง", ['rigid', 'flexible'],
            format_func=lambda x: '🧱 Rigid (คอนกรีต)' if x == 'rigid' else '🛤️ Flexible (ลาดยาง)')
        
        pt = st.selectbox("Terminal Serviceability (pt)", [2.5, 2.0])
        
        if pavement_type == 'rigid':
            param = st.selectbox("ความหนา D (นิ้ว)", [10, 11, 12, 13, 14])
            param_label = f"D={param}\""
        else:
            param = st.selectbox("Structural Number (SN)", [4, 5, 6, 7])
            param_label = f"SN={param}"
        
        st.divider()
        lane_factor = st.slider("Lane Factor", 0.1, 1.0, 0.5, 0.05)
        direction_factor = st.slider("Direction Factor", 0.5, 1.0, 1.0, 0.1)
        
        st.divider()
        st.download_button("📄 ดาวน์โหลด Template (CSV)", to_csv(create_template()),
            "traffic_template.csv", "text/csv", use_container_width=True)
    
    # Main Tabs
    tab1, tab2, tab3 = st.tabs(["📊 คำนวณ ESAL", "🚛 ตั้งค่าน้ำหนักเพลา", "📘 คู่มือ"])
    
    # Tab 2: ตั้งค่าน้ำหนักเพลา
    with tab2:
        st.subheader("🚛 ตั้งค่าน้ำหนักลงเพลาและชนิดเพลา")
        
        col1, col2 = st.columns(2)
        
        with col1:
            for code in ['MB', 'HB', 'MT', 'HT']:
                with st.expander(f"**{code}** - {DEFAULT_TRUCKS[code]['desc']}", expanded=False):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write("**เพลาหน้า**")
                        front_load = st.number_input(f"น้ำหนัก (ตัน)##{code}_f", 0.0, 50.0, 
                            st.session_state.trucks[code]['front'][0], 0.1, key=f"{code}_front_load")
                        front_type = st.selectbox(f"ชนิดเพลา##{code}_f", list(AXLE_TYPES.keys()),
                            index=list(AXLE_TYPES.keys()).index(st.session_state.trucks[code]['front'][1]), key=f"{code}_front_type")
                    with c2:
                        st.write("**เพลาหลัง**")
                        rear_load = st.number_input(f"น้ำหนัก (ตัน)##{code}_r", 0.0, 50.0,
                            st.session_state.trucks[code]['rear'][0], 0.1, key=f"{code}_rear_load")
                        rear_type = st.selectbox(f"ชนิดเพลา##{code}_r", list(AXLE_TYPES.keys()),
                            index=list(AXLE_TYPES.keys()).index(st.session_state.trucks[code]['rear'][1]), key=f"{code}_rear_type")
                    
                    st.session_state.trucks[code]['front'] = (front_load, front_type)
                    st.session_state.trucks[code]['rear'] = (rear_load, rear_type)
        
        with col2:
            with st.expander(f"**STR** - {DEFAULT_TRUCKS['STR']['desc']}", expanded=False):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.write("**เพลาหน้า**")
                    str_f_load = st.number_input("น้ำหนัก (ตัน)##STR_f", 0.0, 50.0,
                        st.session_state.trucks['STR']['front'][0], 0.1, key="STR_front_load")
                    str_f_type = st.selectbox("ชนิด##STR_f", list(AXLE_TYPES.keys()),
                        index=list(AXLE_TYPES.keys()).index(st.session_state.trucks['STR']['front'][1]), key="STR_front_type")
                with c2:
                    st.write("**เพลาหลัง**")
                    str_r_load = st.number_input("น้ำหนัก (ตัน)##STR_r", 0.0, 50.0,
                        st.session_state.trucks['STR']['rear'][0], 0.1, key="STR_rear_load")
                    str_r_type = st.selectbox("ชนิด##STR_r", list(AXLE_TYPES.keys()),
                        index=list(AXLE_TYPES.keys()).index(st.session_state.trucks['STR']['rear'][1]), key="STR_rear_type")
                with c3:
                    st.write("**เพลาพ่วงหลัง**")
                    str_tr_load = st.number_input("น้ำหนัก (ตัน)##STR_tr", 0.0, 50.0,
                        st.session_state.trucks['STR']['trailer_rear'][0], 0.1, key="STR_trailer_rear_load")
                    str_tr_type = st.selectbox("ชนิด##STR_tr", list(AXLE_TYPES.keys()),
                        index=list(AXLE_TYPES.keys()).index(st.session_state.trucks['STR']['trailer_rear'][1]), key="STR_trailer_rear_type")
                
                st.session_state.trucks['STR'] = {
                    'desc': 'Semi-Trailer', 'front': (str_f_load, str_f_type),
                    'rear': (str_r_load, str_r_type), 'trailer_rear': (str_tr_load, str_tr_type)
                }
            
            with st.expander(f"**TR** - {DEFAULT_TRUCKS['TR']['desc']}", expanded=False):
                c1, c2 = st.columns(2)
                with c1:
                    st.write("**เพลาหน้า**")
                    tr_f_load = st.number_input("น้ำหนัก (ตัน)##TR_f", 0.0, 50.0,
                        st.session_state.trucks['TR']['front'][0], 0.1, key="TR_front_load")
                    tr_f_type = st.selectbox("ชนิด##TR_f", list(AXLE_TYPES.keys()),
                        index=list(AXLE_TYPES.keys()).index(st.session_state.trucks['TR']['front'][1]), key="TR_front_type")
                    st.write("**เพลาหลัง**")
                    tr_r_load = st.number_input("น้ำหนัก (ตัน)##TR_r", 0.0, 50.0,
                        st.session_state.trucks['TR']['rear'][0], 0.1, key="TR_rear_load")
                    tr_r_type = st.selectbox("ชนิด##TR_r", list(AXLE_TYPES.keys()),
                        index=list(AXLE_TYPES.keys()).index(st.session_state.trucks['TR']['rear'][1]), key="TR_rear_type")
                with c2:
                    st.write("**เพลาพ่วงหน้า**")
                    tr_tf_load = st.number_input("น้ำหนัก (ตัน)##TR_tf", 0.0, 50.0,
                        st.session_state.trucks['TR']['trailer_front'][0], 0.1, key="TR_trailer_front_load")
                    tr_tf_type = st.selectbox("ชนิด##TR_tf", list(AXLE_TYPES.keys()),
                        index=list(AXLE_TYPES.keys()).index(st.session_state.trucks['TR']['trailer_front'][1]), key="TR_trailer_front_type")
                    st.write("**เพลาพ่วงหลัง**")
                    tr_tr_load = st.number_input("น้ำหนัก (ตัน)##TR_tr", 0.0, 50.0,
                        st.session_state.trucks['TR']['trailer_rear'][0], 0.1, key="TR_trailer_rear_load")
                    tr_tr_type = st.selectbox("ชนิด##TR_tr", list(AXLE_TYPES.keys()),
                        index=list(AXLE_TYPES.keys()).index(st.session_state.trucks['TR']['trailer_rear'][1]), key="TR_trailer_rear_type")
                
                st.session_state.trucks['TR'] = {
                    'desc': 'Full Trailer', 'front': (tr_f_load, tr_f_type),
                    'rear': (tr_r_load, tr_r_type), 'trailer_front': (tr_tf_load, tr_tf_type),
                    'trailer_rear': (tr_tr_load, tr_tr_type)
                }
        
        st.divider()
        st.subheader(f"📊 Truck Factor ({param_label}, pt={pt})")
        
        tf_data = []
        for code, truck in st.session_state.trucks.items():
            axles = [(v[0], v[1]) for k, v in truck.items() if k != 'desc' and isinstance(v, tuple)]
            tf = calc_truck_factor(axles, pavement_type, pt, param)
            axle_info = " + ".join([f"{v[0]}t({v[1]})" for k, v in truck.items() if k != 'desc' and isinstance(v, tuple)])
            tf_data.append({'รหัส': code, 'ประเภท': truck['desc'], 'เพลา': axle_info, 'Truck Factor': f"{tf:.4f}"})
        
        st.dataframe(pd.DataFrame(tf_data), use_container_width=True, hide_index=True)
        
        if st.button("🔄 รีเซ็ตเป็นค่าเริ่มต้น", use_container_width=True):
            st.session_state.trucks = {k: v.copy() for k, v in DEFAULT_TRUCKS.items()}
            st.rerun()
    
    # Tab 1: คำนวณ ESAL
    with tab1:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("📤 อัพโหลดข้อมูล")
            uploaded_file = st.file_uploader("เลือกไฟล์ CSV", type=['csv'])
            
            if 'use_sample' not in st.session_state:
                st.session_state.use_sample = False
            
            if uploaded_file:
                try:
                    traffic_df = pd.read_csv(uploaded_file)
                    st.success("✅ อัพโหลดสำเร็จ!")
                    st.session_state.use_sample = False
                except Exception as e:
                    st.error(f"❌ {e}")
                    traffic_df = None
            else:
                if st.button("🔄 ใช้ข้อมูลตัวอย่าง", use_container_width=True):
                    st.session_state.use_sample = True
                traffic_df = create_template() if st.session_state.use_sample else None
            
            if traffic_df is not None:
                st.dataframe(traffic_df, use_container_width=True, height=350)
        
        with col2:
            st.subheader("📈 ผลการคำนวณ")
            
            if traffic_df is not None:
                truck_factors = {}
                for code, truck in st.session_state.trucks.items():
                    axles = [(v[0], v[1]) for k, v in truck.items() if k != 'desc' and isinstance(v, tuple)]
                    truck_factors[code] = calc_truck_factor(axles, pavement_type, pt, param)
                
                results_df, total_esal = calculate_esal(traffic_df, truck_factors, lane_factor, direction_factor)
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f'<div class="metric-box"><div class="metric-value">{total_esal:,.0f}</div><div class="metric-label">ESAL รวม</div></div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="metric-box"><div class="metric-value">{len(traffic_df)} ปี</div><div class="metric-label">ระยะเวลา</div></div>', unsafe_allow_html=True)
                with c3:
                    st.markdown(f'<div class="metric-box"><div class="metric-value">{param_label}</div><div class="metric-label">พารามิเตอร์</div></div>', unsafe_allow_html=True)
                
                st.divider()
                st.write("**🚛 Truck Factor:**")
                tf_display = pd.DataFrame([{'รหัส': k, 'TF': f"{v:.4f}"} for k, v in truck_factors.items()])
                st.dataframe(tf_display.T, use_container_width=True)
                
                st.divider()
                st.write("**📊 ESAL รายปี:**")
                st.dataframe(results_df, use_container_width=True, height=400)
                
                st.download_button("📥 ดาวน์โหลดผลลัพธ์ (CSV)", to_csv(results_df),
                    f"ESAL_{pavement_type}_{param}.csv", "text/csv", use_container_width=True)
            else:
                st.info("⬅️ กรุณาอัพโหลดข้อมูลหรือใช้ข้อมูลตัวอย่าง")
    
    # Tab 3: คู่มือ
    with tab3:
        st.subheader("📘 คู่มือการใช้งาน")
        st.markdown("""
        ### วิธีใช้งาน
        1. **ตั้งค่าน้ำหนักเพลา** (Tab 🚛)
        2. **ตั้งค่าพารามิเตอร์** (Sidebar)
        3. **อัพโหลดข้อมูล CSV** (Tab 📊)
        4. **ดาวน์โหลดผลลัพธ์**
        
        ### รูปแบบไฟล์ CSV
        | Year | MB | HB | MT | HT | STR | TR |
        |------|----|----|----|----|-----|-----|
        | 1 | 120 | 60 | 250 | 180 | 120 | 100 |
        
        ### หมายเหตุ
        - ค่า LEF ใช้ Lookup Table จาก AASHTO 1993 โดยตรง
        - ใช้ Linear Interpolation สำหรับค่าที่ไม่ตรงกับตาราง
        
        **อ้างอิง:** AASHTO Guide for Design of Pavement Structures (1993)
        """)
    
    st.divider()
    st.caption("พัฒนาสำหรับภาควิชาครุศาสตร์โยธา มจพ. | ESAL Calculator v2.1")

if __name__ == "__main__":
    main()

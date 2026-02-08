# 🔧 Update #3: เพิ่มการอ่าน ประเภทผิวทาง และ ความหนา จาก Excel

## 🎯 เป้าหมาย

ให้โปรแกรมอ่านและอัพเดทข้อมูลจาก Excel ครบทั้ง:
1. ✅ **ต้นทุนก่อสร้าง** (ทำได้แล้ว)
2. ✅ **ประเภทผิวทาง** (เพิ่มใหม่!)
3. ✅ **ความหนาผิวทาง** (เพิ่มใหม่!)

---

## 📋 รูปแบบ Excel ที่รองรับ

### Template Excel
```
| ผิวทาง | ประเภทผิวทาง | ความหนาผิวทาง (ซม.) | ต้นทุนก่อสร้าง (บาท/ตร.ม.) |
|--------|--------------|---------------------|----------------------------|
| AC     | ลาดยาง       | 15                  | 1800                       |
| JPCP   | คอนกรีต      | 30                  | 1660                       |
| JRCP   | คอนกรีต      | 28                  | 1662                       |
| CRCP   | คอนกรีต      | 25                  | 2066                       |
```

### การแมพข้อมูล

#### 1. ชื่อผิวทาง
```python
'AC' → 'ผิวทางยืดหยุ่น (AC)'
'JPCP' → 'JPCP'
'JRCP' → 'JRCP'
'CRCP' → 'CRCP'
```

#### 2. ประเภทผิวทาง
```python
'ลาดยาง' → 'Flexible'
'คอนกรีต' → 'JPCP'  # Default สำหรับคอนกรีต
```

**หมายเหตุ:** ถ้า Excel ไม่มีคอลัมน์นี้ หรือเป็นค่าว่าง → ข้ามไป (ใช้ค่าเดิม)

#### 3. ความหนาผิวทาง
```python
'15' → 15.0 (ซม.)
'30' → 30.0 (ซม.)
```

**หมายเหตุ:** ถ้า Excel ไม่มีคอลัมน์นี้ หรือเป็นค่าว่าง → ข้ามไป (ใช้ค่าเดิม)

---

## 🔧 การแก้ไขโค้ด

### 1. แก้ไขฟังก์ชัน `อ่านข้อมูลจาก_excel()`

#### ก่อนแก้ไข
```python
def อ่านข้อมูลจาก_excel(uploaded_file) -> Dict[str, float]:
    # อ่านเฉพาะต้นทุน
    return {
        'ผิวทางยืดหยุ่น (AC)': 1800.0,
        'JPCP': 1660.0,
        ...
    }
```

#### หลังแก้ไข
```python
def อ่านข้อมูลจาก_excel(uploaded_file) -> Dict[str, Dict]:
    """
    Returns:
        Dict mapping ชื่อผิวทางเต็ม -> {ต้นทุน, ความหนา, ประเภท}
    """
    # แมพประเภทผิวทาง
    ประเภทแมพ = {
        'ลาดยาง': 'Flexible',
        'คอนกรีต': 'JPCP'
    }
    
    for idx, row in df.iterrows():
        # อ่านต้นทุน
        ต้นทุน = float(...)
        
        # อ่านความหนา (ถ้ามี)
        ความหนา = None
        if 'ความหนาผิวทาง (ซม.)' in row:
            ความหนา = float(...)
        
        # อ่านประเภท (ถ้ามี)
        ประเภท = None
        if 'ประเภทผิวทาง' in row:
            ประเภท_str = str(row['ประเภทผิวทาง'])
            ประเภท = ประเภทแมพ.get(ประเภท_str, None)
        
        # เก็บข้อมูลทั้งหมด
        return {
            'ผิวทางยืดหยุ่น (AC)': {
                'ต้นทุน': 1800.0,
                'ความหนา': 15.0,
                'ประเภท': 'Flexible'
            },
            ...
        }
```

---

### 2. แก้ไข Selectbox ประเภทผิวทาง

#### ก่อนแก้ไข
```python
ประเภทใหม่ = st.selectbox(
    "ประเภทผิวทาง",
    options=[...],
    index=...,
    key=f"type_{i}"  # Static key
)
```

#### หลังแก้ไข
```python
# Get uploaded data
uploaded_data = st.session_state.get('uploaded_cost_data', {})

# ถ้ามีข้อมูล upload และมีประเภท → ใช้ค่านั้น
ประเภทเริ่มต้น = ทางเลือก.ประเภท
if ทางเลือก.ชื่อ in uploaded_data and isinstance(uploaded_data[ทางเลือก.ชื่อ], dict):
    if uploaded_data[ทางเลือก.ชื่อ].get('ประเภท'):
        ประเภทเริ่มต้น = uploaded_data[ทางเลือก.ชื่อ]['ประเภท']

upload_version = st.session_state.get('upload_version', 'default')
ประเภทใหม่ = st.selectbox(
    "ประเภทผิวทาง",
    options=[...],
    index=...,
    key=f"type_{ทางเลือก.ชื่อ}_{upload_version}"  # Dynamic key!
)
```

---

### 3. แก้ไข Number Input ความหนา

#### ก่อนแก้ไข
```python
ความหนาปัจจุบัน = getattr(ทางเลือก, 'ความหนา', 0.0)

ความหนาใหม่ = st.number_input(
    "ความหนา (ซม.)",
    value=ความหนาปัจจุบัน,
    key=f"thickness_{i}"  # Static key
)
```

#### หลังแก้ไข
```python
uploaded_data = st.session_state.get('uploaded_cost_data', {})
ความหนาปัจจุบัน = getattr(ทางเลือก, 'ความหนา', 0.0)

# ถ้ามีข้อมูล upload และมีความหนา → ใช้ค่านั้น
if ทางเลือก.ชื่อ in uploaded_data and isinstance(uploaded_data[ทางเลือก.ชื่อ], dict):
    if uploaded_data[ทางเลือก.ชื่อ].get('ความหนา'):
        ความหนาปัจจุบัน = uploaded_data[ทางเลือก.ชื่อ]['ความหนา']

upload_version = st.session_state.get('upload_version', 'default')
ความหนาใหม่ = st.number_input(
    "ความหนา (ซม.)",
    value=ความหนาปัจจุบัน,
    key=f"thickness_{ทางเลือก.ชื่อ}_{upload_version}"  # Dynamic key!
)
```

---

### 4. แก้ไขการแสดงข้อมูลที่ Upload (Sidebar)

#### ก่อนแก้ไข
```python
for ชื่อ, ต้นทุน in ข้อมูลต้นทุน.items():
    st.write(f"• {ชื่อ}: {ต้นทุน:,.0f} บาท/ตร.ม.")
```

#### หลังแก้ไข
```python
for ชื่อ, ข้อมูล in ข้อมูลต้นทุน.items():
    if isinstance(ข้อมูล, dict):
        # รูปแบบใหม่ (มี ต้นทุน, ความหนา, ประเภท)
        ต้นทุน = ข้อมูล.get('ต้นทุน', 0)
        ความหนา = ข้อมูล.get('ความหนา')
        ประเภท = ข้อมูล.get('ประเภท')
        
        info_parts = [f"{ต้นทุน:,.0f} บาท/ตร.ม."]
        if ประเภท:
            info_parts.append(f"ประเภท: {ประเภท}")
        if ความหนา:
            info_parts.append(f"หนา: {ความหนา:.1f} ซม.")
        
        st.write(f"• **{ชื่อ}**: {', '.join(info_parts)}")
    else:
        # Backward compatible - รูปแบบเก่า
        st.write(f"• {ชื่อ}: {ข้อมูล:,.0f} บาท/ตร.ม.")
```

---

## 🎯 ผลลัพธ์

### Before (Update #2)
```
Upload Excel:
  ✅ ต้นทุน → อัพเดท
  ❌ ประเภท → ไม่เปลี่ยน
  ❌ ความหนา → ไม่เปลี่ยน
```

### After (Update #3)
```
Upload Excel:
  ✅ ต้นทุน → อัพเดท
  ✅ ประเภท → อัพเดท!
  ✅ ความหนา → อัพเดท!
```

---

## 📊 ตัวอย่างการทำงาน

### Step 1: Excel Input
```
AC: ลาดยาง, 15 ซม., 1800 บาท
```

### Step 2: อ่านและแมพ
```python
{
    'ผิวทางยืดหยุ่น (AC)': {
        'ต้นทุน': 1800.0,
        'ความหนา': 15.0,
        'ประเภท': 'Flexible'
    }
}
```

### Step 3: แสดงใน Sidebar
```
✅ อ่านข้อมูลสำเร็จ! (4 รายการ)

👀 ดูข้อมูลที่อัปโหลด
  • ผิวทางยืดหยุ่น (AC): 1,800 บาท/ตร.ม., ประเภท: Flexible, หนา: 15.0 ซม.
  • JPCP: 1,660 บาท/ตร.ม., ประเภท: JPCP, หนา: 30.0 ซม.
```

### Step 4: อัพเดท Widget
```
ชื่อทางเลือก: ผิวทางยืดหยุ่น (AC)
ประเภทผิวทาง: Flexible ← อัพเดท!
ความหนา: 15.0 ← อัพเดท!
ต้นทุนก่อสร้าง: 1800 ← อัพเดท!
```

---

## 🔑 Key Features

### 1. Nested Dictionary Structure
```python
uploaded_cost_data = {
    'ผิวทางยืดหยุ่น (AC)': {
        'ต้นทุน': float,
        'ความหนา': float or None,
        'ประเภท': str or None
    }
}
```

### 2. Backward Compatible
```python
# รองรับทั้งรูปแบบเก่าและใหม่
if isinstance(uploaded_info, dict):
    # รูปแบบใหม่
    ต้นทุน = uploaded_info.get('ต้นทุน', ...)
else:
    # รูปแบบเก่า (float เดี่ยว)
    ต้นทุน = uploaded_info
```

### 3. Dynamic Keys for All Widgets
```python
# ต้นทุน
key=f"cost_{ทางเลือก.ชื่อ}_{upload_version}"

# ประเภท
key=f"type_{ทางเลือก.ชื่อ}_{upload_version}"

# ความหนา
key=f"thickness_{ทางเลือก.ชื่อ}_{upload_version}"
```

---

## ✅ Checklist

- [x] แก้ไขฟังก์ชัน `อ่านข้อมูลจาก_excel()` ให้อ่านครบ 3 ค่า
- [x] แก้ไข selectbox ประเภท ให้รองรับ upload
- [x] แก้ไข number_input ความหนา ให้รองรับ upload
- [x] แก้ไข number_input ต้นทุน ให้รองรับ nested dict
- [x] แก้ไขการแสดงข้อมูลใน Sidebar
- [x] เพิ่ม dynamic keys ทุก widget
- [x] รองรับ backward compatibility
- [x] ทดสอบ syntax

---

## 🧪 การทดสอบ

### Test Case 1: Upload ครบทุกคอลัมน์
```
Input:
  AC | ลาดยาง | 15 | 1800

Expected:
  ประเภท: Flexible ✅
  ความหนา: 15 ✅
  ต้นทุน: 1800 ✅
```

### Test Case 2: Upload ไม่มีประเภท
```
Input:
  AC | [ว่าง] | 15 | 1800

Expected:
  ประเภท: Flexible (ค่าเดิม) ✅
  ความหนา: 15 ✅
  ต้นทุน: 1800 ✅
```

### Test Case 3: Upload เฉพาะต้นทุน
```
Input:
  AC | [ว่าง] | [ว่าง] | 1800

Expected:
  ประเภท: Flexible (ค่าเดิม) ✅
  ความหนา: 15.0 (ค่าเดิม) ✅
  ต้นทุน: 1800 ✅
```

---

## 📝 Code Changes Summary

### Files Modified
1. `Life-Cycle_Cost_Analysis_v2.1_Updated.py`

### Functions Modified
1. `อ่านข้อมูลจาก_excel()` - อ่านครบ 3 ค่า
2. Widget ประเภทผิวทาง - รองรับ upload + dynamic key
3. Widget ความหนา - รองรับ upload + dynamic key
4. Widget ต้นทุน - รองรับ nested dict
5. Sidebar display - แสดงครบ 3 ค่า

### Lines Added
~50 บรรทัด (net addition)

---

## 🎉 สรุป

**ตอนนี้โปรแกรมรองรับการ upload Excel แบบครบถ้วน:**

✅ ต้นทุนก่อสร้าง  
✅ ประเภทผิวทาง  
✅ ความหนาผิวทาง  

**ทุกอย่างอัพเดทพร้อมกัน เร็ว และถูกต้อง!**

---

**Version:** 2.1.3 (Update #3)  
**Date:** February 8, 2025  
**Status:** ✅ Complete - Full Excel Integration

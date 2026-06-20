import pandas as pd
import numpy as np

# ลิงก์ CSV จาก Google Sheets ที่พี่ Publish to web ไว้ (เอาลิงก์จริงมาเปลี่ยนตรงนี้ครับ)
LOG_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTx-f6AauRF_G_Bvu48qKaMzUNXqDfKpF0LYNdvcdhP5cLqvvHcMWkpnVFTOIPg7o0iq16osYN4VGfk/pub?gid=1309464566&single=true&output=csv"
INV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTx-f6AauRF_G_Bvu48qKaMzUNXqDfKpF0LYNdvcdhP5cLqvvHcMWkpnVFTOIPg7o0iq16osYN4VGfk/pub?gid=222167185&single=true&output=csv"
MASTER_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTx-f6AauRF_G_Bvu48qKaMzUNXqDfKpF0LYNdvcdhP5cLqvvHcMWkpnVFTOIPg7o0iq16osYN4VGfk/pub?gid=0&single=true&output=csv"
LJ_CALC_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTx-f6AauRF_G_Bvu48qKaMzUNXqDfKpF0LYNdvcdhP5cLqvvHcMWkpnVFTOIPg7o0iq16osYN4VGfk/pub?gid=2029348689&single=true&output=csv"

try:
    log_df = pd.read_csv(LOG_URL)
    inv_df = pd.read_csv(INV_URL)
    master_df = pd.read_csv(MASTER_URL)
    lj_calc_df = pd.read_csv(LJ_CALC_URL)
except Exception as e:
    print(f"Error loading data: {e}")
    exit(1)

# ข้อ 1: จัดการแปลงเวลาแปลงเพื่อทำกรอง รายวัน รายเดือน รายปี
# ตรวจสอบรูปแบบคอลัมน์ Timestamp ของพี่
log_df['Timestamp'] = pd.to_datetime(log_df['Timestamp'], errors='coerce')
log_df['วัน'] = log_df['Timestamp'].dt.strftime('%Y-%m-%d')
log_df['เดือน'] = log_df['Timestamp'].dt.strftime('%Y-%m')
log_df['ปี'] = log_df['Timestamp'].dt.strftime('%Y')

# --- ข้อ 2: คิดร้อยละการทำ IQC ต่อรายการทั้งหมดที่เปิดในแล็บ ---
total_open = master_df[master_df['สถานะเปิดตรวจ'] == 'เปิด']['รายการทดสอบ'].nunique()
total_done = log_df['รายการทดสอบ'].nunique()
p_done = (total_done / total_open) * 100 if total_open > 0 else 0
pd.DataFrame([{'เปิดทั้งหมด': total_open, 'ทำIQC': total_done, 'ร้อยละ': round(p_done, 2)}]).to_csv('out_2_percentage.csv', index=False)

# --- ข้อ 3 & 5: ตารางสรุปใหญ่ทั้งปี และรายการไม่ผ่านเกณฑ์แยกตามสาขา ---
# รวมข้อมูลดิบ Log เข้ากับเกณฑ์ Master
m_df = pd.merge(log_df, master_df, on='รายการทดสอบ', how='left')
# เอาสาขาหลักจาก Master มาทับช่องสาขาเดิม (ป้องกันการพิมพ์ผิดจากฟอร์ม)
if 'สาขา_y' in m_df.columns:
    m_df['สาขา'] = m_df['สาขา_y']
m_df.to_csv('out_3_yearly_summary.csv', index=False)

# คัดกรองรายการที่ไม่ผ่านเกณฑ์
failed_df = m_df[(m_df['สถานะ Level 1'] == 'ไม่ผ่าน') | (m_df['สถานะ Level 2'] == 'ไม่ผ่าน') | (m_df['สถานะ Re-run'] == 'ไม่ผ่าน')]
failed_summary = failed_df[['สาขา', 'วัน', 'เดือน', 'รายการทดสอบ', 'สาเหตุของปัญหา', 'วิธีการแก้ไขและ Comment']]
failed_summary.to_csv('out_5_failed_report.csv', index=False)

# --- ข้อ 4: สรุปงานรายคน + ผูกข้อมูลคุม Lot และวันหมดอายุจาก Inventory ---
# ดึงรายชื่อผู้รับผิดชอบจาก Master ไปจับคู่กับข้อมูล Lot ใน Inventory
staff_df = pd.merge(master_df[['ผู้รับผิดชอบหลัก', 'รายการทดสอบ']], inv_df, on='รายการทดสอบ', how='left')
staff_df.to_csv('out_4_staff_lots.csv', index=False)

# --- ข้อ 6: สรุปสถิติจำนวนครั้งที่ไม่ผ่านแยกตามสาขา (สำหรับใช้พล็อตแผนภูมิเปรียบเทียบ) ---
failed_chart = failed_summary.groupby(['สาขา', 'รายการทดสอบ']).size().reset_index(name='จำนวนไม่ผ่าน')
failed_chart.to_csv('out_6_chart_data.csv', index=False)

# --- ข้อ 7: ตรวจ Westgard Multi-rule โดยใช้ข้อมูลและ Z-Score จากชีต LJ_Calculation ---
def evaluate_westgard(df):
    if 'Timestamp' in df.columns:
        df['Timestamp_dt'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        df = df.sort_values(by='Timestamp_dt').reset_index(drop=True)
    
    status = []
    for i in range(len(df)):
        rules = []
        z1 = df.loc[i, 'Z-Score L1'] if 'Z-Score L1' in df.columns and not pd.isna(df.loc[i, 'Z-Score L1']) else 0
        z2 = df.loc[i, 'Z-Score L2'] if 'Z-Score L2' in df.columns and not pd.isna(df.loc[i, 'Z-Score L2']) else 0
        
        # กฎ 13s (หลุด 3 SD แถวใดแถวหนึ่ง)
        if abs(z1) > 3 or abs(z2) > 3:
            rules.append("13s Violate")
            
        # กฎ 22s (Z-score เกิน 2 ทั้งคู่และไปในทิศทางเดียวกันในรันเดียวกัน)
        if (z1 > 2 and z2 > 2) or (z1 < -2 and z2 < -2):
            rules.append("22s Violate")
            
        # กฎ R4s (เช็คข้ามรันกับข้อมูลก่อนหน้าตัวมันเองในฐานข้อมูล)
        if i > 0:
            prev_z1 = df.loc[i-1, 'Z-Score L1'] if 'Z-Score L1' in df.columns and not pd.isna(df.loc[i-1, 'Z-Score L1']) else 0
            if abs(z1 - prev_z1) > 4:
                rules.append("R4s Violate")
                
        status.append(", ".join(rules) if rules else "Normal")
        
    df['Westgard_Result'] = status
    if 'Timestamp_dt' in df.columns:
        df = df.drop(columns=['Timestamp_dt'])
    return df

lj_output = evaluate_westgard(lj_calc_df)
lj_output.to_csv('out_7_lj_multi_rule.csv', index=False)

print("IQC Analytics Data Pipeline Processed Successfully!")

import pandas as pd
import numpy as np

# ลิงก์ CSV จริงจาก Google Sheets ของพี่
LOG_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTx-f6AauRF_G_Bvu48qKaMzUNXqDfKpF0LYNdvcdhP5cLqvvHcMWkpnVFTOIPg7o0iq16osYN4VGfk/pub?gid=1309464566&single=true&output=csv"
INV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTx-f6AauRF_G_Bvu48qKaMzUNXqDfKpF0LYNdvcdhP5cLqvvHcMWkpnVFTOIPg7o0iq16osYN4VGfk/pub?gid=222167185&single=true&output=csv"
MASTER_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTx-f6AauRF_G_Bvu48qKaMzUNXqDfKpF0LYNdvcdhP5cLqvvHcMWkpnVFTOIPg7o0iq16osYN4VGfk/pub?gid=0&single=true&output=csv"
LJ_CALC_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTx-f6AauRF_G_Bvu48qKaMzUNXqDfKpF0LYNdvcdhP5cLqvvHcMWkpnVFTOIPg7o0iq16osYN4VGfk/pub?gid=2029348689&single=true&output=csv"

try:
    # โหลดข้อมูลและเซ็ตให้อ่านเป็น String ป้องกันจัดฟอร์แมตเพี้ยน
    log_df = pd.read_csv(LOG_URL, dtype=str)
    inv_df = pd.read_csv(INV_URL, dtype=str)
    master_df = pd.read_csv(MASTER_URL, dtype=str)
    lj_calc_df = pd.read_csv(LJ_CALC_URL, dtype=str)
except Exception as e:
    print(f"Error loading data from Google Sheets: {e}")
    exit(1)

# จัดการคอลัมน์ตัวเลขให้พร้อมใช้
for col in ['ผล Level 1', 'ผล Level 2', 'ผล Re-run']:
    if col in log_df.columns:
        log_df[col] = pd.to_numeric(log_df[col], errors='coerce')

# แปลงวันเวลาแบบยืดหยุ่น (แก้ปัญหาวันที่ว่างหรือฟอร์แมตผสม)
if 'Timestamp' in log_df.columns:
    log_df['Timestamp_dt'] = pd.to_datetime(log_df['Timestamp'], errors='coerce')
    log_df['วัน'] = log_df['Timestamp_dt'].dt.strftime('%Y-%m-%d')
    log_df['เดือน'] = log_df['Timestamp_dt'].dt.strftime('%Y-%m')
    log_df['ปี'] = log_df['Timestamp_dt'].dt.strftime('%Y')
else:
    log_df['วัน'] = log_df['เดือน'] = log_df['ปี'] = "ไม่ระบุ"

# --- ข้อ 2: คิดร้อยละการทำ IQC ต่อรายการทั้งหมดที่เปิดในแล็บ ---
total_open = master_df[master_df['สถานะเปิดตรวจ'] == 'เปิด']['รายการทดสอบ'].nunique() if 'สถานะเปิดตรวจ' in master_df.columns else 1
total_done = log_df['รายการทดสอบ'].nunique() if 'รายการทดสอบ' in log_df.columns else 0
p_done = (total_done / total_open) * 100 if total_open > 0 else 0
pd.DataFrame([{'เปิดทั้งหมด': total_open, 'ทำIQC': total_done, 'ร้อยละ': round(p_done, 2)}]).to_csv('out_2_percentage.csv', index=False)

# --- ข้อ 3 & 5: ตารางสรุปใหญ่ทั้งปี และรายการไม่ผ่านเกณฑ์แยกตามสาขา ---
m_df = pd.merge(log_df, master_df, on='รายการทดสอบ', how='left', suffixes=('', '_master'))
m_df.to_csv('out_3_yearly_summary.csv', index=False)

# คัดกรองรายการที่ไม่ผ่านเกณฑ์ (Level 1, Level 2 หรือ Re-run)
f1 = m_df['สถานะ Level 1'] == 'ไม่ผ่าน'
f2 = m_df['สถานะ Level 2'] == 'ไม่ผ่าน'
f3 = m_df['สถานะ Re-run'] == 'ไม่ผ่าน'
failed_df = m_df[f1 | f2 | f3]

cols_to_save = [c for c in ['สาขา', 'วัน', 'เดือน', 'รายการทดสอบ', 'สาเหตุของปัญหา', 'วิธีการแก้ไขและ Comment'] if c in failed_df.columns]
if not failed_df.empty:
    failed_df[cols_to_save].to_csv('out_5_failed_report.csv', index=False)
else:
    pd.DataFrame(columns=cols_to_save).to_csv('out_5_failed_report.csv', index=False)

# --- ข้อ 4: สรุปงานรายคน + ผูกข้อมูลคุม Lot และวันหมดอายุ ---
# เปลี่ยนมาเชื่อมข้อมูลด้วยคำว่า 'สาขา' ตามโครงสร้างจริงของชีต Inventory พี่ครับ
inv_df_renamed = inv_df.rename(columns={'รายการทดสอบ': 'สาขา'})
staff_df = pd.merge(master_df[['ผู้รับผิดชอบหลัก', 'สาขา', 'รายการทดสอบ']], inv_df_renamed, on='สาขา', how='left')
staff_df.to_csv('out_4_staff_lots.csv', index=False)

# --- ข้อ 6: สรุปสถิติจำนวนครั้งที่ไม่ผ่านแยกตามสาขา ---
if not failed_df.empty and 'สาขา' in failed_df.columns and 'รายการทดสอบ' in failed_df.columns:
    failed_chart = failed_df.groupby(['สาขา', 'รายการทดสอบ']).size().reset_index(name='จำนวนไม่ผ่าน')
    failed_chart.to_csv('out_6_chart_data.csv', index=False)
else:
    pd.DataFrame(columns=['สาขา', 'รายการทดสอบ', 'จำนวนไม่ผ่าน']).to_csv('out_6_chart_data.csv', index=False)

# --- ข้อ 7: ตรวจ Westgard Multi-rule โดยใช้ข้อมูลและ Z-Score จากชีต LJ_Calculation ---
def evaluate_westgard(df):
    if df.empty:
        return df
    
    # แปลง Z-Score เป็นตัวเลขเพื่อเช็คกฎ
    for col in ['Z-Score L1', 'Z-Score L2']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    status = []
    for i in range(len(df)):
        rules = []
        z1 = df.loc[i, 'Z-Score L1'] if 'Z-Score L1' in df.columns else 0
        z2 = df.loc[i, 'Z-Score L2'] if 'Z-Score L2' in df.columns else 0
        
        # กฎ 13s
        if abs(z1) > 3 or abs(z2) > 3:
            rules.append("13s Violate")
        # กฎ 22s
        if (z1 > 2 and z2 > 2) or (z1 < -2 and z2 < -2):
            rules.append("22s Violate")
            
        # กฎ R4s (เช็คข้ามรันย้อนหลัง)
        if i > 0:
            prev_z1 = df.loc[i-1, 'Z-Score L1'] if 'Z-Score L1' in df.columns else 0
            if abs(z1 - prev_z1) > 4:
                rules.append("R4s Violate")
                
        status.append(", ".join(rules) if rules else "Normal")
        
    df['Westgard_Result'] = status
    return df

lj_output = evaluate_westgard(lj_calc_df)
lj_output.to_csv('out_7_lj_multi_rule.csv', index=False)

print("IQC Analytics Data Pipeline Processed Successfully with Real Links!")

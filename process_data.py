import pandas as pd
import numpy as np

# ลิงก์ CSV จริงจาก Google Sheets ของพี่
LOG_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTx-f6AauRF_G_Bvu48qKaMzUNXqDfKpF0LYNdvcdhP5cLqvvHcMWkpnVFTOIPg7o0iq16osYN4VGfk/pub?gid=1309464566&single=true&output=csv"
INV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTx-f6AauRF_G_Bvu48qKaMzUNXqDfKpF0LYNdvcdhP5cLqvvHcMWkpnVFTOIPg7o0iq16osYN4VGfk/pub?gid=222167185&single=true&output=csv"
MASTER_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTx-f6AauRF_G_Bvu48qKaMzUNXqDfKpF0LYNdvcdhP5cLqvvHcMWkpnVFTOIPg7o0iq16osYN4VGfk/pub?gid=0&single=true&output=csv"
LJ_CALC_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTx-f6AauRF_G_Bvu48qKaMzUNXqDfKpF0LYNdvcdhP5cLqvvHcMWkpnVFTOIPg7o0iq16osYN4VGfk/pub?gid=2029348689&single=true&output=csv"

try:
    # โหลดข้อมูลทุกชีตเข้ามาเป็นแบบ String
    log_df = pd.read_csv(LOG_URL, dtype=str)
    inv_df = pd.read_csv(INV_URL, dtype=str)
    master_df = pd.read_csv(MASTER_URL, dtype=str)
    lj_calc_df = pd.read_csv(LJ_CALC_URL, dtype=str)
except Exception as e:
    print(f"Error loading data from Google Sheets: {e}")
    exit(1)

# ลบเว้นวรรคส่วนเกินที่หัวคอลัมน์ของทุกชีต
log_df.columns = log_df.columns.str.strip()
inv_df.columns = inv_df.columns.str.strip()
master_df.columns = master_df.columns.str.strip()
lj_calc_df.columns = lj_calc_df.columns.str.strip()

# แปลงเวลาแบบปลอดภัยยืดหยุ่น (ดักจับค่าว่างหรือรูปแบบผสม)
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
# เชื่อมข้อมูล Log และ Master ด้วย 'รายการทดสอบ' เพื่อดึงข้อมูล 'สาขา' ออกมาให้ถูกต้อง
m_df = pd.merge(log_df, master_df[['รายการทดสอบ', 'สาขา', 'ผู้รับผิดชอบหลัก']], on='รายการทดสอบ', how='left')
m_df.to_csv('out_3_yearly_summary.csv', index=False)

# ตรวจสอบรายการที่ไม่ผ่านเกณฑ์
f1 = m_df['สถานะ Level 1'] == 'ไม่ผ่าน'
f2 = m_df['สถานะ Level 2'] == 'ไม่ผ่าน'
f3 = m_df['สถานะ Re-run'] == 'ไม่ผ่าน'
failed_df = m_df[f1 | f2 | f3]

cols_to_save = [c for c in ['สาขา', 'วัน', 'เดือน', 'รายการทดสอบ', 'สาเหตุของปัญหา', 'วิธีการแก้ไขและ Comment'] if c in failed_df.columns]
if not failed_df.empty:
    failed_df[cols_to_save].to_csv('out_5_failed_report.csv', index=False)
else:
    pd.DataFrame(columns=['สาขา', 'วัน', 'เดือน', 'รายการทดสอบ', 'สาเหตุของปัญหา', 'วิธีการแก้ไขและ Comment']).to_csv('out_5_failed_report.csv', index=False)

# --- ข้อ 4: สรุปงานรายคน + ผูกข้อมูลคุม Lot และวันหมดอายุจาก Inventory ---
# เนื่องจากชีต Inventory ของพี่คอลัมน์แรกสุดพิมพ์ว่า 'รายการทดสอบ' แต่ข้างในเก็บชื่อสาขา (เช่น เคมีคลินิก)
# เราจะทำการเปลี่ยนชื่อคอลัมน์แรกของชีต Inventory ให้ชื่อว่า 'สาขา_คุมบ็อท' เพื่อไม่ให้ระบบงงเวลา Join ข้อมูลครับ
inv_df_clean = inv_df.copy()
if len(inv_df_clean.columns) > 0:
    inv_df_clean.columns.values[0] = 'สาขา_คุมบ็อท'

# นำแผนผังรายคนใน Master มารวบเข้ากับข้อมูล Lot ใน Inventory โดยใช้ ชื่อสาขา จับคู่กันครับ
staff_df = pd.merge(master_df[['ผู้รับผิดชอบหลัก', 'สาขา', 'รายการทดสอบ']], inv_df_clean, left_on='สาขา', right_on='สาขา_คุมบ็อท', how='left')
# ลบคอลัมน์ชั่วคราวออกเพื่อความสะอาดของไฟล์
if 'สาขา_คุมบ็อท' in staff_df.columns:
    staff_df = staff_df.drop(columns=['สาขา_คุมบ็อท'])
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
            
        # กฎ R4s (เช็คค่าความต่างข้ามรันย้อนหลัง)
        if i > 0:
            prev_z1 = df.loc[i-1, 'Z-Score L1'] if 'Z-Score L1' in df.columns else 0
            if abs(z1 - prev_z1) > 4:
                rules.append("R4s Violate")
                
        status.append(", ".join(rules) if rules else "Normal")
        
    df['Westgard_Result'] = status
    return df

lj_output = evaluate_westgard(lj_calc_df)
lj_output.to_csv('out_7_lj_multi_rule.csv', index=False)

print("IQC Analytics Data Pipeline Processed Successfully without any KeyErrors!")

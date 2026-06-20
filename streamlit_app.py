import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="POCT IQC Dashboard 2026", layout="wide")
st.title("📊 ระบบ IQC Dashboard")

# 2. ดึงข้อมูล
SHEET_ID = "16maoziMQKJiFtn-Rkzj_ZD7SZ7MqUBRcCj8MmYuwhxM"
URL_LJ = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=LJ_Calculation"

# ฟังก์ชันทำความสะอาดชื่อคอลัมน์ (ตัด _x, _y ออก)
def clean_columns(df):
    df.columns = [c.replace('_x', '').replace('_y', '') for c in df.columns]
    return df

# --- ส่วนที่ 1: ตารางและกราฟรายวัน ---
st.header("1. ตารางและกราฟรายวัน")
try:
    df = pd.read_csv(URL_LJ)
    df = clean_columns(df)
    df['Date_only'] = pd.to_datetime(df['Timestamp']).dt.strftime('%d/%m/%Y')
    
    selected_test = st.selectbox("🎯 เลือกรายการทดสอบ:", df['รายการทดสอบ'].unique())
    final_df = df[df['รายการทดสอบ'] == selected_test].copy()
    
    # เลือกโชว์เฉพาะคอลัมน์ที่พี่ต้องการ
    cols_to_show = ['Date_only', 'สาขา', 'รายการทดสอบ', 'ผล Level 1', 'ผล Level 2', 'สถานะ Re-run', 'สาเหตุของปัญหา', 'วิธีการแก้ไขและComment', 'ชื่อผู้ปฏิบัติงาน']
    available_cols = [c for c in cols_to_show if c in final_df.columns]
    st.dataframe(final_df[available_cols].sort_values(by='Date_only', ascending=False), use_container_width=True)
    
    # กราฟ LJ ที่สะอาดตา
    def plot_lj(df_data, level_col, mean_col, sd_col, title):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_data['Date_only'], y=df_data[level_col], mode='lines+markers', name='Result', line=dict(color='#1f77b4', width=3)))
        m = df_data[mean_col].iloc[0] if mean_col in df_data.columns else df_data[level_col].mean()
        s = df_data[sd_col].iloc[0] if sd_col in df_data.columns else df_data[level_col].std()
        fig.add_hline(y=m, line_color="green", line_width=3, annotation_text="Mean")
        fig.add_hline(y=m+(2*s), line_dash="dash", line_color="red", line_width=2, annotation_text="+2SD")
        fig.add_hline(y=m-(2*s), line_dash="dash", line_color="red", line_width=2, annotation_text="-2SD")
        fig.update_layout(title=title, height=400, template="plotly_white")
        return fig
    
    st.plotly_chart(plot_lj(final_df, 'ผล Level 1', 'Mean L1', 'SD L1', "🔵 Level 1"), use_container_width=True)
    st.plotly_chart(plot_lj(final_df, 'ผล Level 2', 'Mean L2', 'SD L2', "🔴 Level 2"), use_container_width=True)

except Exception as e:
    st.error(f"โหลดข้อมูลไม่ได้: {e}")

# --- ส่วนที่ 2-7: ข้อมูลสรุป (ใช้ไฟล์เดิมจาก GitHub) ---
def load_github_csv(file_name):
    try:
        BASE_GITHUB_URL = "https://raw.githubusercontent.com/soysaena2013-creator/IQC_Dashboard_2026/main/"
        data = pd.read_csv(f"{BASE_GITHUB_URL}{file_name}", encoding='utf-8')
        return clean_columns(data) # ทำความสะอาดชื่อคอลัมน์ที่นี่ด้วย
    except:
        return None

sections = [
    ("2. % Passing", "out_2_percentage.csv"),
    ("3. Yearly Summary", "out_3_yearly_summary.csv"),
    ("4. Staff & Lots", "out_4_staff_lots.csv"),
    ("5. Failed Report", "out_5_failed_report.csv"),
    ("6. Raw Data", "out_6_chart_data.csv"),
    ("7. Westgard Rules", "out_7_lj_multi_rule.csv")
]

for title, file in sections:
    st.markdown("---")
    st.header(title)
    data = load_github_csv(file)
    if data is not None:
        st.dataframe(data, use_container_width=True)
    else:
        st.warning(f"⚠️ กำลังรอไฟล์ {file}")

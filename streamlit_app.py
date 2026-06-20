import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="POCT IQC Dashboard 2026", layout="wide")
st.title("📊 ระบบ IQC Dashboard")

# 2. ดึงข้อมูล
SHEET_ID = "16maoziMQKJiFtn-Rkzj_ZD7SZ7MqUBRcCj8MmYuwhxM"
URL_LJ = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=LJ_Calculation"

# ฟังก์ชันทำความสะอาดข้อมูล
def clean_df(df):
    # ลบ _x, _y ออกจากชื่อคอลัมน์
    df.columns = [c.replace('_x', '').replace('_y', '') for c in df.columns]
    # แปลง Timestamp ให้แสดงแค่วันที่ (DD/MM/YYYY)
    if 'Timestamp' in df.columns:
        df['Date_only'] = pd.to_datetime(df['Timestamp']).dt.strftime('%d/%m/%Y')
    return df

# --- ส่วนที่ 1: กราฟและตารางรายวัน ---
st.header("1. ตารางและกราฟสรุปผลรายวัน")
try:
    df_raw = pd.read_csv(URL_LJ)
    df = clean_df(df_raw)
    
    selected_test = st.selectbox("🎯 เลือกรายการทดสอบ:", df['รายการทดสอบ'].unique())
    final_df = df[df['รายการทดสอบ'] == selected_test].copy()
    
    # แสดงตาราง
    st.dataframe(final_df, use_container_width=True)
    
    # วาดกราฟ LJ
    def plot_lj(df_data, level_col, title):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_data['Date_only'], y=df_data[level_col], mode='lines+markers', name=level_col))
        fig.update_layout(title=title, height=400, template="plotly_white")
        return fig
    
    col1, col2 = st.columns(2)
    with col1: st.plotly_chart(plot_lj(final_df, 'ผล Level 1', 'กราฟ Level 1'), use_container_width=True)
    with col2: st.plotly_chart(plot_lj(final_df, 'ผล Level 2', 'กราฟ Level 2'), use_container_width=True)

except Exception as e:
    st.error(f"โหลดข้อมูลไม่ได้: {e}")

# --- ส่วนที่ 2-7: ข้อมูลสรุป ---
def load_github_csv(file_name):
    try:
        BASE_GITHUB_URL = "https://raw.githubusercontent.com/soysaena2013-creator/IQC_Dashboard_2026/main/"
        data = pd.read_csv(f"{BASE_GITHUB_URL}{file_name}", encoding='utf-8')
        return clean_df(data)
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
        st.warning(f"⚠️ รอการซิงค์ไฟล์ {file}")

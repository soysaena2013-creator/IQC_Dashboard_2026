import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import urllib.parse

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="POCT IQC Dashboard 2026", layout="wide")
st.title("📊 ระบบ IQC Dashboard")

# 2. ดึงข้อมูลจาก "การตอบแบบฟอร์ม 1"
SHEET_ID = "16maoziMQKJiFtn-Rkzj_ZD7SZ7MqUBRcCj8MmYuwhxM"
SHEET_NAME = "การตอบแบบฟอร์ม 1"
url_sheet_name = urllib.parse.quote(SHEET_NAME)
URL_FORM = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={url_sheet_name}"

try:
    # ดึงข้อมูลและทำความสะอาด
    df = pd.read_csv(URL_FORM)
    df = df.loc[:, ~df.columns.duplicated()] # ลบคอลัมน์ซ้ำ
    
    # ตรวจสอบว่ามีคอลัมน์ Timestamp หรือไม่
    if 'Timestamp' in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['Date'] = df['Timestamp'].dt.date
    else:
        st.error("ไม่พบข้อมูล 'Timestamp' ใน Sheet โปรดตรวจสอบหัวตารางครับ")
        st.stop()

    # Sidebar: ตัวเลือกช่วงเวลาและรายการ
    st.sidebar.header("🔍 ตัวเลือกการดูข้อมูล")
    selected_test = st.sidebar.selectbox("เลือกรายการทดสอบ:", df['รายการทดสอบ'].unique())
    start_date = st.sidebar.date_input("วันที่เริ่มต้น", df['Date'].min())
    end_date = st.sidebar.date_input("วันที่สิ้นสุด", df['Date'].max())
    
    # กรองข้อมูล
    mask = (df['รายการทดสอบ'] == selected_test) & (df['Date'] >= start_date) & (df['Date'] <= end_date)
    final_df = df[mask].sort_values(by='Timestamp', ascending=False)
    
    # 1. แสดงตาราง
    st.header(f"📋 ตารางข้อมูล: {selected_test}")
    st.dataframe(final_df, use_container_width=True)
    
    # 2. กราฟ LJ ที่ชัดเจน
    st.header("📈 กราฟ Levey-Jennings")
    
    def plot_lj(df_plot, level_col, title):
        fig = go.Figure()
        # ใช้ markers และ lines ให้ชัดเจน
        fig.add_trace(go.Scatter(x=df_plot['Timestamp'], y=df_plot[level_col], mode='lines+markers', name=level_col, line=dict(width=3, color='#1f77b4')))
        
        # คำนวณ Mean และ SD
        m = df_plot[level_col].mean()
        s = df_plot[level_col].std()
        
        # เส้น Mean/SD
        fig.add_hline(y=m, line_color="green", line_width=3, annotation_text="Mean")
        fig.add_hline(y=m+(2*s), line_dash="dash", line_color="red", line_width=2, annotation_text="+2SD")
        fig.add_hline(y=m-(2*s), line_dash="dash", line_color="red", line_width=2, annotation_text="-2SD")
        
        fig.update_layout(title=title, height=400, template="plotly_white", xaxis_title="วันที่/เวลา")
        return fig

    # แสดงกราฟ (ตรวจสอบว่ามีคอลัมน์ผลทดสอบหรือไม่)
    if 'ผล Level 1' in final_df.columns:
        st.plotly_chart(plot_lj(final_df, 'ผล Level 1', 'Level 1'), use_container_width=True)
    if 'ผล Level 2' in final_df.columns:
        st.plotly_chart(plot_lj(final_df, 'ผล Level 2', 'Level 2'), use_container_width=True)

except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")

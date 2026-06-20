import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import urllib.parse

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="POCT IQC Dashboard 2026", layout="wide")
st.title("📊 ระบบ IQC Dashboard")

# 2. ข้อมูลจาก Google Sheets (Sheet: การตอบแบบฟอร์ม 1)
SHEET_ID = "16maoziMQKJiFtn-Rkzj_ZD7SZ7MqUBRcCj8MmYuwhxM"
SHEET_NAME = "การตอบแบบฟอร์ม 1"
URL_FORM = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(SHEET_NAME)}"

try:
    # ดึงข้อมูล
    df = pd.read_csv(URL_FORM)
    # ลบช่องว่างรอบชื่อคอลัมน์
    df.columns = df.columns.str.strip()
    
    # แปลงคอลัมน์ 'ประทับเวลา'
    df['Timestamp_dt'] = pd.to_datetime(df['ประทับเวลา'], errors='coerce')
    
    # 3. เลือกรายการทดสอบ
    selected_test = st.selectbox("🎯 เลือกรายการทดสอบ:", df['รายการทดสอบ'].unique())
    display_df = df[df['รายการทดสอบ'] == selected_test].copy()
    
    # 4. แสดงตาราง (เลือกเฉพาะคอลัมน์ที่จำเป็นและไม่ซ้ำซ้อน)
    cols_to_show = [
        'ประทับเวลา', 'สาขา', 'รายการทดสอบ', 'ผล Level 1', 
        'ผล Level 2', 'สาเหตุของปัญหา', 'วิธีการแก้ไขและ Comment', 'ชื่อผู้ปฏิบัติงาน'
    ]
    st.header(f"📋 ตารางบันทึก IQC: {selected_test}")
    st.dataframe(display_df[cols_to_show].sort_values(by='Timestamp_dt', ascending=False), use_container_width=True)
    
    # 5. กราฟ Levey-Jennings
    st.header("📈 กราฟ Levey-Jennings")
    
    def plot_lj(data, col_name, title):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['Timestamp_dt'], y=data[col_name], mode='lines+markers', name=col_name))
        
        # คำนวณจากข้อมูลจริงในตาราง
        m, s = data[col_name].mean(), data[col_name].std()
        
        fig.add_hline(y=m, line_color="green", line_width=3, annotation_text="Mean")
        fig.add_hline(y=m+(2*s), line_dash="dash", line_color="red", line_width=2, annotation_text="+2SD")
        fig.add_hline(y=m-(2*s), line_dash="dash", line_color="red", line_width=2, annotation_text="-2SD")
        fig.update_layout(title=title, template="plotly_white")
        return fig

    # แสดงกราฟ Level 1 และ Level 2
    st.plotly_chart(plot_lj(display_df, 'ผล Level 1', 'Level 1'), use_container_width=True)
    st.plotly_chart

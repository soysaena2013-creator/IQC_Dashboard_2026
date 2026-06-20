import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import urllib.parse

st.set_page_config(page_title="POCT IQC Dashboard 2026", layout="wide")
st.title("📊 ระบบ IQC Dashboard: รวมทุกชีต")

SHEET_ID = "16maoziMQKJiFtn-Rkzj_ZD7SZ7MqUBRcCj8MmYuwhxM"

# รายชื่อชีตทั้งหมดที่พี่มี (ถ้ามีเพิ่ม พี่เติมชื่อในลิสต์นี้ได้เลยครับ)
sheet_names = ["การตอบแบบฟอร์ม 1"] 

# ฟังก์ชันดึงข้อมูลแต่ละชีต
def load_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(sheet_name)}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip() # ลบช่องว่างหัวคอลัมน์
    return df

# 1. เลือกชีตก่อน
selected_sheet = st.sidebar.selectbox("📂 เลือกชีตที่ต้องการดู:", sheet_names)

try:
    # 2. โหลดข้อมูลตามชีตที่เลือก
    df = load_data(selected_sheet)
    df['ประทับเวลา'] = pd.to_datetime(df['ประทับเวลา'], errors='coerce')
    
    # 3. เลือกรายการทดสอบ
    selected_test = st.selectbox("🎯 เลือกรายการทดสอบ:", df['รายการทดสอบ'].unique())
    display_df = df[df['รายการทดสอบ'] == selected_test].copy()
    
    # 4. แสดงตาราง
    st.header(f"📋 ข้อมูลจากชีต: {selected_sheet} | รายการ: {selected_test}")
    st.dataframe(display_df.sort_values(by='ประทับเวลา', ascending=False), use_container_width=True)
    
    # 5. กราฟ LJ
    st.header("📈 กราฟ Levey-Jennings")
    def plot_lj(data, col_name, title):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['ประทับเวลา'], y=data[col_name], mode='lines+markers', name=col_name))
        m, s = data[col_name].mean(), data[col_name].std()
        fig.add_hline(y=m, line_color="green", line_width=3, annotation_text="Mean")
        fig.add_hline(y=m+(2*s), line_dash="dash", line_color="red", line_width=2, annotation_text="+2SD")
        fig.add_hline(y=m-(2*s), line_dash="dash", line_color="red", line_width=2, annotation_text="-2SD")
        fig.update_layout(title=title, template="plotly_white")
        return fig

    st.plotly_chart(plot_lj(display_df, 'ผล Level 1', 'Level 1'), use_container_width=True)
    st.plotly_chart(plot_lj(display_df, 'ผล Level 2', 'Level 2'), use_container_width=True)

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")

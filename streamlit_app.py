import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import urllib.parse

st.set_page_config(page_title="POCT IQC Dashboard 2026", layout="wide")
st.title("📊 ระบบ IQC Dashboard")

SHEET_ID = "16maoziMQKJiFtn-Rkzj_ZD7SZ7MqUBRcCj8MmYuwhxM"

@st.cache_data
def get_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(sheet_name)}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

try:
    # 1. โหลดข้อมูลแยกไฟล์ตามชื่อไฟล์ที่พี่ส่งมา
    df_log = get_data("การตอบแบบฟอร์ม 1")
    df_master = get_data("Master_Tests")
    
    # 2. จัดการข้อมูล (อ้างอิงชื่อคอลัมน์จากไฟล์จริง)
    df_log['ประทับเวลา'] = pd.to_datetime(df_log['ประทับเวลา'], errors='coerce')
    
    # 3. เลือกรายการทดสอบ
    selected_test = st.selectbox("🎯 เลือกรายการทดสอบ:", df_log['รายการทดสอบ'].unique())
    display_df = df_log[df_log['รายการทดสอบ'] == selected_test].sort_values(by='ประทับเวลา', ascending=False)
    
    # ดึงค่าจาก Master_Tests (ต้องมีชื่อรายการทดสอบตรงกัน)
    master_info = df_master[df_master['รายการทดสอบ'] == selected_test].iloc[0]
    
    # 4. ฟังก์ชันกราฟ LJ มาตรฐาน (Mean, +/- 1, 2, 3 SD)
    def plot_lj(data, mean, sd, col, title):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['ประทับเวลา'], y=data[col], mode='lines+markers', name=col))
        
        # เส้น Mean
        fig.add_hline(y=mean, line_color="black", line_width=2, annotation_text="Mean")
        
        # เส้น SD 1, 2, 3
        colors = {1: "gray", 2: "orange", 3: "red"}
        for i in [1, 2, 3]:
            fig.add_hline(y=mean+(i*sd), line_dash="dash", line_color=colors[i], annotation_text=f"+{i}SD")
            fig.add_hline(y=mean-(i*sd), line_dash="dash", line_color=colors[i], annotation_text=f"-{i}SD")
            
        fig.update_layout(title=f"LJ Chart: {title}", template="plotly_white", yaxis_title="Result")
        return fig

    # แสดงกราฟ 2 ฝั่ง (Level 1 และ Level 2)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(plot_lj(display_df, master_info['L1_Mean'], master_info['L1_SD'], 'ผล Level 1', 'Level 1'), use_container_width=True)
    with c2:
        st.plotly_chart(plot_lj(display_df, master_info['L2_Mean'], master_info['L2_SD'], 'ผล Level 2', 'Level 2'), use_container_width=True)

    # 5. ตารางข้อมูล
    st.header("📋 ข้อมูลการบันทึก")
    st.dataframe(display_df, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")

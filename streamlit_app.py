import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import urllib.parse

# [ส่วนที่พี่ใช้งานได้ดีอยู่แล้ว ผมล็อกไว้ให้ครับ]
st.set_page_config(page_title="POCT IQC Dashboard 2026", layout="wide")
st.title("📊 ระบบ IQC Dashboard")

SHEET_ID = "16maoziMQKJiFtn-Rkzj_ZD7SZ7MqUBRcCj8MmYuwhxM"
URL_FORM = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote('การตอบแบบฟอร์ม 1')}"

try:
    df = pd.read_csv(URL_FORM)
    df.columns = df.columns.str.strip()
    df['ประทับเวลา'] = pd.to_datetime(df['ประทับเวลา'], errors='coerce')
    
    selected_test = st.selectbox("🎯 เลือกรายการทดสอบ:", df['รายการทดสอบ'].unique())
    display_df = df[df['รายการทดสอบ'] == selected_test].copy()
    
    # ส่วนแสดงตารางที่พี่ต้องการ (คงไว้เหมือนเดิม)
    st.header(f"📋 ตารางบันทึก IQC: {selected_test}")
    st.dataframe(display_df.sort_values(by='ประทับเวลา', ascending=False), use_container_width=True)

    # [ส่วนที่แก้ไขเฉพาะเรื่องกราฟ LJ ให้มีเส้น SD]
    st.header("📈 กราฟ Levey-Jennings")

# วางโค้ดนี้แทนที่ฟังก์ชันวาดกราฟเดิมของพี่ได้เลยครับ
def plot_lj_standard(data, mean, sd, col, title):
    fig = go.Figure()
    # จุดข้อมูล
    fig.add_trace(go.Scatter(x=data['ประทับเวลา'], y=data[col], mode='lines+markers', name=col))
    
    # เส้น Mean (เส้นทึบสีดำ)
    fig.add_hline(y=mean, line_color="black", line_width=2, line_dash="solid", annotation_text="Mean")
    
    # เส้น SD +/- 1, 2, 3 (สีตามมาตรฐานแล็บ)
    sd_colors = {1: "gray", 2: "orange", 3: "red"}
    
    for i in [1, 2, 3]:
        # เส้นบวก SD
        fig.add_hline(y=mean+(i*sd), line_dash="dash", line_color=sd_colors[i], annotation_text=f"+{i}SD")
        # เส้นลบ SD
        fig.add_hline(y=mean-(i*sd), line_dash="dash", line_color=sd_colors[i], annotation_text=f"-{i}SD")
        
    fig.update_layout(title=f"LJ Chart: {title}", template="plotly_white", yaxis_title="Result")
    return fig

    # เรียกใช้ฟังก์ชันเดิมโดยไม่กระทบโครงสร้างอื่น
    st.plotly_chart(draw_lj_with_sd(display_df, 'ผล Level 1', 'Level 1'), use_container_width=True)
    st.plotly_chart(draw_lj_with_sd(display_df, 'ผล Level 2', 'Level 2'), use_container_width=True)

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")

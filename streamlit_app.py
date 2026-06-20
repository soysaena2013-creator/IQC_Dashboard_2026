import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import urllib.parse

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="POCT IQC Dashboard 2026", layout="wide")
st.title("📊 ระบบ IQC Dashboard")

# กำหนดค่าคงที่
SHEET_ID = "16maoziMQKJiFtn-Rkzj_ZD7SZ7MqUBRcCj8MmYuwhxM"
SHEET_NAME = "การตอบแบบฟอร์ม 1"
URL_FORM = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(SHEET_NAME)}"

try:
    # 1. ดึงข้อมูล
    df = pd.read_csv(URL_FORM)
    
    # Debug: แสดงชื่อคอลัมน์ให้พี่เห็นในหน้าจอ เพื่อให้เราแก้ไขได้ตรงจุด
    # st.write("ชื่อคอลัมน์ที่พบ:", df.columns.tolist()) 

    # 2. ปรับปรุงข้อมูล (ใช้ชื่อคอลัมน์ที่คาดการณ์จากภาพ)
    # ตัดคอลัมน์ซ้ำออก
    df = df.loc[:, ~df.columns.duplicated()]
    
    # ตรวจสอบชื่อคอลัมน์วันที่ (บางครั้งอาจเป็น 'Timestamp' หรือชื่ออื่น)
    # ถ้า Error ว่าไม่พบ 'Timestamp' ให้ลองดูชื่อที่แสดงใน Debug ด้านบน
    if 'Timestamp' in df.columns:
        df['Timestamp_dt'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        df['Date'] = df['Timestamp_dt'].dt.date
    else:
        st.error("❌ ไม่พบชื่อคอลัมน์ 'Timestamp' ในตาราง! โปรดดูชื่อคอลัมน์ที่ถูกต้องใน Google Sheets ของพี่")
        st.stop()

    # 3. ส่วนการเลือกข้อมูล
    test_list = df['รายการทดสอบ'].unique()
    selected_test = st.selectbox("🎯 เลือกรายการทดสอบ:", test_list)
    final_df = df[df['รายการทดสอบ'] == selected_test].copy()

    # 4. แสดงตาราง
    st.header(f"📋 ตารางบันทึก IQC รายวัน: {selected_test}")
    st.dataframe(final_df, use_container_width=True)

    # 5. กราฟ LJ
    st.header("📈 กราฟ Levey-Jennings")
    
    def plot_lj(data, col_name, title):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['Timestamp_dt'], y=data[col_name], mode='lines+markers', name=col_name))
        
        # คำนวณ Mean และ SD จากข้อมูลที่เลือกมา
        mean_val = data[col_name].mean()
        sd_val = data[col_name].std()
        
        fig.add_hline(y=mean_val, line_color="green", line_width=3, annotation_text="Mean")
        fig.add_hline(y=mean_val+(2*sd_val), line_dash="dash", line_color="red", line_width=2, annotation_text="+2SD")
        fig.add_hline(y=mean_val-(2*sd_val), line_dash="dash", line_color="red", line_width=2, annotation_text="-2SD")
        
        fig.update_layout(title=title, template="plotly_white")
        return fig

    # ตรวจสอบว่ามีคอลัมน์ ผล Level 1 / 2 จริงไหม
    if 'ผล Level 1' in final_df.columns:
        st.plotly_chart(plot_lj(final_df, 'ผล Level 1', 'Level 1'), use_container_width=True)
    if 'ผล Level 2' in final_df.columns:
        st.plotly_chart(plot_lj(final_df, 'ผล Level 2', 'Level 2'), use_container_width=True)

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")

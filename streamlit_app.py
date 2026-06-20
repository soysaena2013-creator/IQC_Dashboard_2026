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
    return pd.read_csv(url)

try:
    # 1. โหลดข้อมูล
    df = get_data("การตอบแบบฟอร์ม 1")
    df.columns = df.columns.str.strip()
    df['ประทับเวลา'] = pd.to_datetime(df['ประทับเวลา'], errors='coerce')
    
    df_master = get_data("Master_Tests")
    df_master.columns = df_master.columns.str.strip()

    # 2. ตัวเลือก
    selected_test = st.selectbox("🎯 เลือกรายการทดสอบ:", df['รายการทดสอบ'].unique())
    display_df = df[df['รายการทดสอบ'] == selected_test].copy()
    
    # 3. ดึงค่า Master (แก้ปัญหา out-of-bounds)
    master_row = df_master[df_master['รายการทดสอบ'] == selected_test]
    
    st.header(f"📋 ตารางบันทึก IQC: {selected_test}")
    st.dataframe(display_df.sort_values(by='ประทับเวลา', ascending=False), use_container_width=True)

    st.header("📈 กราฟ Levey-Jennings")

    # ฟังก์ชันวาดกราฟ
    def plot_lj_standard(data, mean_val, sd_val, col_name, title):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['ประทับเวลา'], y=data[col_name], mode='lines+markers', name=col_name))
        fig.add_hline(y=mean_val, line_color="black", line_width=2, annotation_text="Mean")
        
        sd_config = {1: "gray", 2: "orange", 3: "red"}
        for i in [1, 2, 3]:
            fig.add_hline(y=mean_val+(i*sd_val), line_dash="dash", line_color=sd_config[i], annotation_text=f"+{i}SD")
            fig.add_hline(y=mean_val-(i*sd_val), line_dash="dash", line_color=sd_config[i], annotation_text=f"-{i}SD")
        fig.update_layout(title=f"LJ Chart: {title}", template="plotly_white")
        return fig

    # ตรวจสอบว่ามีข้อมูลใน Master หรือไม่ก่อนวาด
    if not master_row.empty:
        m = master_row.iloc[0]
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(plot_lj_standard(display_df, m['L1_Mean'], m['L1_SD'], 'ผล Level 1', 'Level 1'), use_container_width=True)
        with c2:
            st.plotly_chart(plot_lj_standard(display_df, m['L2_Mean'], m['L2_SD'], 'ผล Level 2', 'Level 2'), use_container_width=True)
    else:
        st.warning("⚠️ ไม่พบข้อมูลค่าอ้างอิง (Mean/SD) สำหรับรายการทดสอบนี้ในไฟล์ Master_Tests")

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")

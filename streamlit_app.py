import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import urllib.parse

st.set_page_config(page_title="POCT IQC Dashboard 2026", layout="wide")
st.title("📊 ระบบ IQC Dashboard")

SHEET_ID = "16maoziMQKJiFtn-Rkzj_ZD7SZ7MqUBRcCj8MmYuwhxM"

# ฟังก์ชันดึงข้อมูล (ดึงแยกกันเพื่อไม่ให้คอลัมน์ตีกัน)
@st.cache_data
def get_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(sheet_name)}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

try:
    df_log = get_data("การตอบแบบฟอร์ม 1")
    df_master = get_data("Master_Tests")
    
    df_log['ประทับเวลา'] = pd.to_datetime(df_log['ประทับเวลา'], errors='coerce')
    selected_test = st.selectbox("🎯 เลือกรายการทดสอบ:", df_log['รายการทดสอบ'].unique())
    display_df = df_log[df_log['รายการทดสอบ'] == selected_test].copy()
    
    # ดึงค่า Mean/SD จากไฟล์ Master
    master_info = df_master[df_master['รายการทดสอบ'] == selected_test].iloc[0]
    
    st.header(f"📋 ตารางบันทึก IQC: {selected_test}")
    st.dataframe(display_df.sort_values(by='ประทับเวลา', ascending=False), use_container_width=True)

    # ฟังก์ชันวาดกราฟที่ถูกต้อง
    def plot_lj_standard(data, mean, sd, col, title):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['ประทับเวลา'], y=data[col], mode='lines+markers', name=col))
        fig.add_hline(y=mean, line_color="black", line_width=2, line_dash="solid", annotation_text="Mean")
        
        sd_colors = {1: "gray", 2: "orange", 3: "red"}
        for i in [1, 2, 3]:
            fig.add_hline(y=mean+(i*sd), line_dash="dash", line_color=sd_colors[i], annotation_text=f"+{i}SD")
            fig.add_hline(y=mean-(i*sd), line_dash="dash", line_color=sd_colors[i], annotation_text=f"-{i}SD")
        fig.update_layout(title=f"LJ Chart: {title}", template="plotly_white", yaxis_title="Result")
        return fig

    st.header("📈 กราฟ Levey-Jennings")
    # เรียกใช้ฟังก์ชันให้ตรงชื่อและส่งค่า Mean/SD เข้าไป
    st.plotly_chart(plot_lj_standard(display_df, master_info['L1_Mean'], master_info['L1_SD'], 'ผล Level 1', 'Level 1'), use_container_width=True)
    st.plotly_chart(plot_lj_standard(display_df, master_info['L2_Mean'], master_info['L2_SD'], 'ผล Level 2', 'Level 2'), use_container_width=True)

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import urllib.parse

st.set_page_config(page_title="POCT IQC Dashboard 2026", layout="wide")
st.title("📊 ระบบ IQC Dashboard")

# 1. ฟังก์ชันดึงข้อมูลจาก Google Sheets (ไม่ Merge)
SHEET_ID = "16maoziMQKJiFtn-Rkzj_ZD7SZ7MqUBRcCj8MmYuwhxM"
def get_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(sheet_name)}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

try:
    # ดึงข้อมูลแยกชีตเพื่อไม่ให้คอลัมน์ตีกัน
    df_log = get_data("การตอบแบบฟอร์ม 1")
    df_master = get_data("Master_Tests")
    
    # แปลงเวลา
    df_log['ประทับเวลา'] = pd.to_datetime(df_log['ประทับเวลา'], errors='coerce')
    
    # เลือกรายการทดสอบ
    selected_test = st.selectbox("🎯 เลือกรายการทดสอบ:", df_log['รายการทดสอบ'].unique())
    display_df = df_log[df_log['รายการทดสอบ'] == selected_test].copy()
    
    # ดึงค่าอ้างอิงจาก Master_Tests
    master_info = df_master[df_master['รายการทดสอบ'] == selected_test].iloc[0]
    
    # 2. กราฟ LJ ที่ถูกต้องตามมาตรฐานแล็บ (Mean, +/-1,2,3 SD)
    st.header(f"📈 กราฟ Levey-Jennings: {selected_test}")
    
    def plot_lj_lab(data, mean_val, sd_val, col_name, title):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['ประทับเวลา'], y=data[col_name], mode='lines+markers', name=col_name))
        
        # เส้น Mean
        fig.add_hline(y=mean_val, line_color="black", line_width=2, annotation_text="Mean")
        
        # เส้น SD 1, 2, 3
        sd_colors = {1: "gray", 2: "orange", 3: "red"}
        for i in [1, 2, 3]:
            fig.add_hline(y=mean_val+(i*sd_val), line_dash="dash", line_color=sd_colors[i], annotation_text=f"+{i}SD")
            fig.add_hline(y=mean_val-(i*sd_val), line_dash="dash", line_color=sd_colors[i], annotation_text=f"-{i}SD")
            
        fig.update_layout(title=title, template="plotly_white", yaxis_title="Result")
        return fig

    # แสดงกราฟ 2 ระดับ
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(plot_lj_lab(display_df, master_info['L1_Mean'], master_info['L1_SD'], 'ผล Level 1', 'Level 1'), use_container_width=True)
    with c2:
        st.plotly_chart(plot_lj_lab(display_df, master_info['L2_Mean'], master_info['L2_SD'], 'ผล Level 2', 'Level 2'), use_container_width=True)

    # 3. ตารางข้อมูล (ตัดคอลัมน์เกินออก)
    st.header("📋 ข้อมูลการบันทึก")
    st.dataframe(display_df.sort_values(by='ประทับเวลา', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")

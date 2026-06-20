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
    df = get_data("การตอบแบบฟอร์ม 1")
    df.columns = df.columns.str.strip()
    df['ประทับเวลา'] = pd.to_datetime(df['ประทับเวลา'], errors='coerce')
    # สร้างคอลัมน์วันที่เพื่อแสดงผลที่แกน X
    df['วันที่'] = df['ประทับเวลา'].dt.date
    
    df_master = get_data("Master_Tests")
    df_master.columns = df_master.columns.str.strip()
    
    selected_test = st.selectbox("🎯 เลือกรายการทดสอบ:", df['รายการทดสอบ'].unique())
    display_df = df[df['รายการทดสอบ'] == selected_test].copy()
    
    # ตรวจสอบว่ารายการนี้มีใน Master หรือไม่
    master_row = df_master[df_master['รายการทดสอบ'] == selected_test]
    
    st.header(f"📋 ตารางบันทึก IQC: {selected_test}")
    st.dataframe(display_df.sort_values(by='ประทับเวลา', ascending=False), use_container_width=True)

    st.header("📈 กราฟ Levey-Jennings")

    def plot_lj(data, mean, sd, col, title):
        fig = go.Figure()
        # ใช้ 'วันที่' เป็นแกน X
        fig.add_trace(go.Scatter(x=data['วันที่'], y=data[col], mode='lines+markers', name=col))
        fig.add_hline(y=mean, line_color="black", line_width=2, annotation_text="Mean")
        # เส้น SD +/- 1, 2, 3
        for i in [1, 2, 3]:
            fig.add_hline(y=mean+(i*sd), line_dash="dash", line_color="red")
            fig.add_hline(y=mean-(i*sd), line_dash="dash", line_color="red")
        fig.update_layout(title=title, template="plotly_white", xaxis_title="วันที่")
        return fig

    if not master_row.empty:
        m = master_row.iloc[0]
        c1, c2 = st.columns(2)
        with c1: st.plotly_chart(plot_lj(display_df, m['L1_Mean'], m['L1_SD'], 'ผล Level 1', 'Level 1'), use_container_width=True)
        with c2: st.plotly_chart(plot_lj(display_df, m['L2_Mean'], m['L2_SD'], 'ผล Level 2', 'Level 2'), use_container_width=True)
    else:
        st.warning(f"⚠️ ไม่พบค่าอ้างอิงใน Master_Tests สำหรับรายการ: {selected_test}")

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")

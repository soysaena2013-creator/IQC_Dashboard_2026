import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import urllib.parse

st.set_page_config(layout="wide")
st.title("📊 ระบบ IQC Dashboard")

SHEET_ID = "16maoziMQKJiFtn-Rkzj_ZD7SZ7MqUBRcCj8MmYuwhxM"

@st.cache_data
def get_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(sheet_name)}"
    return pd.read_csv(url)

try:
    # โหลดข้อมูล
    df = get_data("การตอบแบบฟอร์ม 1")
    df.columns = df.columns.str.strip()
    df['ประทับเวลา'] = pd.to_datetime(df['ประทับเวลา'], errors='coerce')
    df['วันที่'] = df['ประทับเวลา'].dt.strftime('%Y-%m-%d')
    
    df_master = get_data("Master_Tests")
    df_master.columns = df_master.columns.str.strip()
    
    # จัดการชื่อรายการให้เหมือนกัน (ตัวเล็กหมด)
    df['รายการทดสอบ'] = df['รายการทดสอบ'].astype(str).str.strip().str.lower()
    df_master['รายการทดสอบ'] = df_master['รายการทดสอบ'].astype(str).str.strip().str.lower()
    
    # เลือกรายการ
    options = df['รายการทดสอบ'].unique()
    selected_test = st.selectbox("🎯 เลือกรายการทดสอบ:", options)
    
    display_df = df[df['รายการทดสอบ'] == selected_test].copy()
    master_row = df_master[df_master['รายการทดสอบ'] == selected_test]
    
    # --- กราฟ ---
    st.header(f"📈 กราฟ Levey-Jennings: {selected_test}")
    
    def draw_graph(data, m_row, l_mean, l_sd, col, title):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['วันที่'], y=data[col], mode='lines+markers', name=col))
        if not m_row.empty:
            mean = m_row.iloc[0][l_mean]
            sd = m_row.iloc[0][l_sd]
            fig.add_hline(y=mean, line_color="black", annotation_text="Mean")
            for i in [1, 2, 3]:
                fig.add_hline(y=mean+(i*sd), line_dash="dash", line_color="red")
                fig.add_hline(y=mean-(i*sd), line_dash="dash", line_color="red")
        fig.update_layout(title=title, template="plotly_white")
        return fig

    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(draw_graph(display_df, master_row, 'L1_Mean', 'L1_SD', 'ผล Level 1', 'Level 1'), use_container_width=True)
    with c2: st.plotly_chart(draw_graph(display_df, master_row, 'L2_Mean', 'L2_SD', 'ผล Level 2', 'Level 2'), use_container_width=True)
    
    # --- ตาราง ---
    st.header("📋 ตารางสรุปข้อมูล")
    st.dataframe(display_df.sort_values(by='ประทับเวลา', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")

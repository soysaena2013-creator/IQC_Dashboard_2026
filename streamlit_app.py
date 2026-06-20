import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import urllib.parse

# 1. ดึงข้อมูล
SHEET_ID = "16maoziMQKJiFtn-Rkzj_ZD7SZ7MqUBRcCj8MmYuwhxM"
def get_df(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(sheet_name)}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

try:
    df_log = get_df("การตอบแบบฟอร์ม 1")
    df_master = get_df("Master_Tests") # ไฟล์นี้มีค่า Mean/SD อ้างอิง
    
    df_log['ประทับเวลา'] = pd.to_datetime(df_log['ประทับเวลา'], errors='coerce')
    
    selected_test = st.selectbox("🎯 เลือกรายการทดสอบ:", df_log['รายการทดสอบ'].unique())
    display_df = df_log[df_log['รายการทดสอบ'] == selected_test].copy()
    
    # ดึงค่า Mean/SD มาจาก Master_Tests
    master = df_master[df_master['รายการทดสอบ'] == selected_test].iloc[0]
    
    # 2. ฟังก์ชันวาดกราฟ LJ พร้อมเส้น SD ครบชุด
    def plot_lj_full(data, mean_val, sd_val, col_name, title):
        fig = go.Figure()
        # จุดข้อมูล
        fig.add_trace(go.Scatter(x=data['ประทับเวลา'], y=data[col_name], mode='lines+markers', name=col_name))
        
        # เส้น Mean
        fig.add_hline(y=mean_val, line_color="black", line_width=2, name="Mean")
        
        # เส้น SD (บวกและลบ)
        for i in [1, 2, 3]:
            fig.add_hline(y=mean_val+(i*sd_val), line_dash="dash", line_color="red" if i==3 else "orange" if i==2 else "gray")
            fig.add_hline(y=mean_val-(i*sd_val), line_dash="dash", line_color="red" if i==3 else "orange" if i==2 else "gray")
            
        fig.update_layout(title=f"LJ Chart: {title}", template="plotly_white", yaxis_title="Result")
        return fig

    # วาดกราฟสำหรับ Level 1 และ 2
    st.plotly_chart(plot_lj_full(display_df, master['L1_Mean'], master['L1_SD'], 'ผล Level 1', 'Level 1'), use_container_width=True)
    st.plotly_chart(plot_lj_full(display_df, master['L2_Mean'], master['L2_SD'], 'ผล Level 2', 'Level 2'), use_container_width=True)

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")

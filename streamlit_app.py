import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="IQC Dashboard", layout="wide")
st.title("📊 ระบบ IQC Analytics & Westgard Multi-rule Dashboard")

# 1. ใส่รหัสไฟล์ Google Sheets ของพี่ที่นี่ (ดูจาก URL บนเบราว์เซอร์ หลัง /d/)
SHEET_ID = "วางรหัสไฟล์ตรงนี้"
SHEET_NAME = "LJ_Calculation"

# ลิงก์เชื่อมโยงไปยังแท็บที่ผูกสูตรไว้
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

try:
    df = pd.read_csv(URL)
    
    if not df.empty:
        st.success("⚡ เชื่อมต่อแผ่นงานสูตรคำนวณสำเร็จ!")
        
        # คัดกรองตัวเลือกรายการทดสอบ
        tests = df['รายการทดสอบ'].dropna().unique()
        selected_test = st.selectbox("เลือกรายการทดสอบ:", tests)
        
        test_df = df[df['รายการทดสอบ'] == selected_test].reset_index()
        
        if not test_df.empty:
            mean_l1 = float(test_df.loc[0, 'Mean L1'])
            sd_l1 = float(test_df.loc[0, 'SD L1'])
            
            # พล็อตกราฟ Levey-Jennings
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=test_df['Timestamp'], y=test_df['ผล Level 1'], mode='lines+markers', name='ผล Level 1'))
            
            # เส้น Mean & SD
            fig.add_hline(y=mean_l1, line_color="green", annotation_text="Mean")
            fig.add_hline(y=mean_l1 + (2*sd_l1), line_dash="dash", line_color="orange", annotation_text="+2SD")
            fig.add_hline(y=mean_l1 - (2*sd_l1), line_dash="dash", line_color="orange", annotation_text="-2SD")
            fig.add_hline(y=mean_l1 + (3*sd_l1), line_dash="dash", line_color="red", annotation_text="+3SD")
            fig.add_hline(y=mean_l1 - (3*sd_l1), line_dash="dash", line_color="red", annotation_text="-3SD")
            
            st.plotly_chart(fig, use_container_width=True)
            
            # ตารางสรุปผล
            st.subheader("📋 บันทึกข้อมูลควบคุมคุณภาพ")
            st.dataframe(test_df[['Timestamp', 'สาขา', 'รายการทดสอบ', 'ผล Level 1', 'Z-Score L1', 'Westgard_Result']])
            
except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")

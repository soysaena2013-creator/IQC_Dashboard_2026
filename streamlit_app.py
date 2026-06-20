import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import urllib.parse

st.set_page_config(layout="wide")
st.title("📊 ระบบ IQC Dashboard")

SHEET_ID = "16maoziMQKJiFtn-Rkzj_ZD7SZ7MqUBRcCj8MmYuwhxM"

@st.cache_data(ttl=0)
def get_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(sheet_name)}"
    return pd.read_csv(url)

try:
    # 1. โหลดจาก "การตอบแบบฟอร์ม 1" ตามที่พี่บอกครับ
    df = get_data("การตอบแบบฟอร์ม 1")
    df.columns = df.columns.str.strip()
    
    # 2. บังคับแปลงคอลัมน์ผลให้เป็นตัวเลข เพื่อแก้ค่า None
    df['ผล Level 1'] = pd.to_numeric(df['ผล Level 1'], errors='coerce')
    df['ผล Level 2'] = pd.to_numeric(df['ผล Level 2'], errors='coerce')
    
    df['ประทับเวลา'] = pd.to_datetime(df['ประทับเวลา'], errors='coerce')
    
    df_master = get_data("Master_Tests")
    df_master.columns = df_master.columns.str.strip()
    
    # ทำความสะอาดชื่อรายการ
    df['รายการทดสอบ'] = df['รายการทดสอบ'].astype(str).str.strip()
    df_master['รายการทดสอบ'] = df_master['รายการทดสอบ'].astype(str).str.strip()
    
    # เลือกรายการ
    options = df['รายการทดสอบ'].unique()
    selected_test = st.selectbox("🎯 เลือกรายการทดสอบ:", options)
    
    display_df = df[df['รายการทดสอบ'] == selected_test].copy()
    master_row = df_master[df_master['รายการทดสอบ'] == selected_test]
    
    st.header(f"📋 ตารางบันทึก IQC: {selected_test}")
    st.dataframe(display_df.sort_values(by='ประทับเวลา', ascending=False), use_container_width=True)

    if not master_row.empty:
        st.success(f"✅ พบค่าอ้างอิงสำหรับ: {selected_test}")
    else:
        st.warning(f"⚠️ ยังไม่พบ '{selected_test}' ใน Master_Tests โปรดเช็คชื่อในไฟล์ Master ว่าตรงกับที่เลือกในตารางไหม")

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")

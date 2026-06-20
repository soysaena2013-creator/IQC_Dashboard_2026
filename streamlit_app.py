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
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

try:
    # 1. โหลดข้อมูล (แก้ชื่อเป็น Form_Responses ตามที่พี่ใช้)
    df = get_data("Form_Responses")
    df.columns = df.columns.str.strip()
    
    # 2. บังคับเปลี่ยนผลเป็นตัวเลข
    df['ผล Level 1'] = pd.to_numeric(df['ผล Level 1'], errors='coerce')
    df['ผล Level 2'] = pd.to_numeric(df['ผล Level 2'], errors='coerce')
    
    df['ประทับเวลา'] = pd.to_datetime(df['ประทับเวลา'], errors='coerce')
    df['วันที่'] = df['ประทับเวลา'].dt.strftime('%Y-%m-%d')
    
    df_master = get_data("Master_Tests")
    df_master.columns = df_master.columns.str.strip()
    
    # ทำความสะอาดชื่อรายการ
    df['รายการทดสอบ'] = df['รายการทดสอบ'].astype(str).str.strip()
    df_master['รายการทดสอบ'] = df_master['รายการทดสอบ'].astype(str).str.strip()
    
    # เลือกรายการทดสอบ
    selected_test = st.selectbox("🎯 เลือกรายการทดสอบ:", df['รายการทดสอบ'].unique())
    display_df = df[df['รายการทดสอบ'] == selected_test].copy()
    master_row = df_master[df_master['รายการทดสอบ'] == selected_test]
    
    # แสดงตาราง
    st.header(f"📋 ตารางบันทึก IQC: {selected_test}")
    st.dataframe(display_df.sort_values(by='ประทับเวลา', ascending=False), use_container_width=True)

    # วาดกราฟ
    if not master_row.empty:
        m = master_row.iloc[0]
        st.header("📈 กราฟ Levey-Jennings")
        # (ส่วนวาดกราฟ LJ ของพี่สามารถต่อจากตรงนี้ได้เลยครับ)
    else:
        st.warning(f"⚠️ ไม่พบข้อมูล '{selected_test}' ใน Master_Tests โปรดตรวจสอบชื่อให้ตรงกัน")

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")

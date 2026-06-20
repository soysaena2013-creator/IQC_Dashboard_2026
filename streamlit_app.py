import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import urllib.parse

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="POCT IQC Dashboard 2026", layout="wide")
st.title("📊 ระบบ IQC Dashboard")

SHEET_ID = "16maoziMQKJiFtn-Rkzj_ZD7SZ7MqUBRcCj8MmYuwhxM"
SHEET_NAME = "การตอบแบบฟอร์ม 1"
URL_FORM = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(SHEET_NAME)}"

try:
    # ดึงข้อมูล
    df = pd.read_csv(URL_FORM)
    
    # 1. แก้ไขชื่อคอลัมน์ให้สะอาด (ลบช่องว่างหัวท้าย และลบ _x, _y ที่อาจติดมา)
    df.columns = df.columns.str.strip().str.replace('_x', '').str.replace('_y', '')
    
    # Debug: แสดงชื่อคอลัมน์ให้พี่เห็นเผื่อว่าชื่อใน Sheet จะแปลกไปจากนี้
    # st.write("ชื่อคอลัมน์ที่ระบบอ่านได้คือ:", df.columns.tolist())

    # 2. ค้นหาคอลัมน์ Timestamp แบบยืดหยุ่น
    ts_col = next((col for col in df.columns if 'Timestamp' in col), None)
    
    if ts_col:
        df['Timestamp_dt'] = pd.to_datetime(df[ts_col], errors='coerce')
        df['Date'] = df['Timestamp_dt'].dt.date
    else:
        st.error(f"❌ ไม่พบข้อมูลคอลัมน์เกี่ยวกับ 'Timestamp' ในตาราง! ชื่อคอลัมน์ที่พบคือ: {df.columns.tolist()}")
        st.stop()

    # 3. เลือกรายการทดสอบ
    if 'รายการทดสอบ' in df.columns:
        selected_test = st.selectbox("🎯 เลือกรายการทดสอบ:", df['รายการทดสอบ'].unique())
        final_df = df[df['รายการทดสอบ'] == selected_test].copy()
    else:
        st.error("ไม่พบชื่อคอลัมน์ 'รายการทดสอบ'")
        st.stop()

    # 4. แสดงตาราง
    st.header(f"📋 ตารางบันทึก IQC: {selected_test}")
    st.dataframe(final_df, use_container_width=True)

    # 5. กราฟ LJ
    st.header("📈 กราฟ Levey-Jennings")
    
    def plot_lj(data, col_name, title):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['Timestamp_dt'], y=data[col_name], mode='lines+markers', name=col_name))
        m, s = data[col_name].mean(), data[col_name].std()
        fig.add_hline(y=m, line_color="green", line_width=3, annotation_text="Mean")
        fig.add_hline(y=m+(2*s), line_dash="dash", line_color="red", line_width=2, annotation_text="+2SD")
        fig.add_hline(y=m-(2*s), line_dash="dash", line_color="red", line_width=2, annotation_text="-2SD")
        fig.update_layout(title=title, template="plotly_white")
        return fig

    # ตรวจสอบชื่อคอลัมน์ผลทดสอบ
    for col in ['ผล Level 1', 'ผล Level 2']:
        if col in final_df.columns:
            st.plotly_chart(plot_lj(final_df, col, col), use_container_width=True)

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")

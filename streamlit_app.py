import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import urllib.parse

st.set_page_config(page_title="POCT IQC Dashboard 2026", layout="wide")
st.title("📊 ระบบ IQC Dashboard")

SHEET_ID = "16maoziMQKJiFtn-Rkzj_ZD7SZ7MqUBRcCj8MmYuwhxM"
SHEET_NAME = "การตอบแบบฟอร์ม 1"
URL_FORM = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(SHEET_NAME)}"

try:
    # 1. ดึงข้อมูล
    df = pd.read_csv(URL_FORM)
    
    # 2. ทำความสะอาดชื่อคอลัมน์ให้หมดจด
    # ลบช่องว่าง และลบชื่อที่ลงท้ายด้วย _x, _y ออกทั้งหมด
    df.columns = df.columns.str.strip().str.replace(r'_[xy]$', '', regex=True)
    
    # 3. ลบคอลัมน์ที่ชื่อซ้ำทิ้งทันที เหลือไว้แค่ชื่อละ 1 คอลัมน์
    df = df.loc[:, ~df.columns.duplicated()]
    
    # 4. แปลงเวลา (ใช้ชื่อคอลัมน์ 'ประทับเวลา' ตามไฟล์พี่เป๊ะ)
    df['Timestamp_dt'] = pd.to_datetime(df['ประทับเวลา'], errors='coerce')
    
    # 5. เลือกรายการ
    selected_test = st.selectbox("🎯 เลือกรายการทดสอบ:", df['รายการทดสอบ'].unique())
    display_df = df[df['รายการทดสอบ'] == selected_test].copy()
    
    # 6. เลือกคอลัมน์ที่จะโชว์ (จำกัดแค่รายการนี้เท่านั้น)
    # ถ้าเห็นคอลัมน์ไหนเกินมาอีก บอกผมได้เลยครับ
    cols_to_show = [
        'ประทับเวลา', 'สาขา', 'รายการทดสอบ', 'ผล Level 1', 
        'ผล Level 2', 'สาเหตุของปัญหา', 'วิธีการแก้ไขและ Comment', 'ชื่อผู้ปฏิบัติงาน'
    ]
    final_cols = [c for c in cols_to_show if c in display_df.columns]
    
    st.header(f"📋 ตารางบันทึก IQC: {selected_test}")
    st.dataframe(display_df[final_cols].sort_values(by='Timestamp_dt', ascending=False), use_container_width=True)
    
    # 7. กราฟ LJ
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

    if 'ผล Level 1' in display_df.columns:
        st.plotly_chart(plot_lj(display_df, 'ผล Level 1', 'Level 1'), use_container_width=True)
    if 'ผล Level 2' in display_df.columns:
        st.plotly_chart(plot_lj(display_df, 'ผล Level 2', 'Level 2'), use_container_width=True)

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")

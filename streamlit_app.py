import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="POCT IQC Dashboard 2026", layout="wide")
st.title("📊 ระบบ IQC Dashboard")

# 2. ดึงข้อมูลจาก "การตอบแบบฟอร์ม 1"
# หมายเหตุ: พี่ต้องตรวจสอบชื่อ Sheet ใน Google Sheets ให้ตรงกับที่ระบุใน URL นี้ครับ
SHEET_ID = "16maoziMQKJiFtn-Rkzj_ZD7SZ7MqUBRcCj8MmYuwhxM"
URL_FORM = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=การตอบแบบฟอร์ม 1"

try:
    df = pd.read_csv(URL_FORM)
    
    # จัดการวันที่
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Date'] = df['Timestamp'].dt.date
    
    # 3. ระบบเลือกรายการทดสอบและช่วงเวลา
    st.sidebar.header("🔍 ตัวกรองข้อมูล")
    selected_test = st.sidebar.selectbox("เลือกรายการทดสอบ:", df['รายการทดสอบ'].unique())
    start_date = st.sidebar.date_input("วันที่เริ่มต้น", df['Date'].min())
    end_date = st.sidebar.date_input("วันที่สิ้นสุด", df['Date'].max())
    
    # กรองข้อมูล
    mask = (df['รายการทดสอบ'] == selected_test) & (df['Date'] >= start_date) & (df['Date'] <= end_date)
    final_df = df[mask].sort_values(by='Timestamp', ascending=False)
    
    # แสดงตาราง (เอาตามคอลัมน์ใน "การตอบแบบฟอร์ม 1" เป๊ะๆ)
    st.header(f"📋 ตารางข้อมูล: {selected_test}")
    st.dataframe(final_df, use_container_width=True)
    
    # 4. ทำกราฟ LJ (ชัดเจนและมีเส้น Mean, 2SD)
    st.header("📈 กราฟ Levey-Jennings")
    
    def plot_lj(df_plot, level_col, title):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_plot['Timestamp'], y=df_plot[level_col], mode='lines+markers', name=level_col, line=dict(width=3)))
        
        # คำนวณ Mean และ SD
        m = df_plot[level_col].mean()
        s = df_plot[level_col].std()
        
        fig.add_hline(y=m, line_color="green", line_width=3, annotation_text="Mean")
        fig.add_hline(y=m+(2*s), line_dash="dash", line_color="red", line_width=2, annotation_text="+2SD")
        fig.add_hline(y=m-(2*s), line_dash="dash", line_color="red", line_width=2, annotation_text="-2SD")
        
        fig.update_layout(title=title, height=400, template="plotly_white")
        return fig

    # ตรวจสอบว่ามีคอลัมน์ Level หรือไม่ (ปรับชื่อคอลัมน์ตามจริงใน Sheet ได้เลยครับ)
    if 'ผล Level 1' in final_df.columns:
        st.plotly_chart(plot_lj(final_df, 'ผล Level 1', 'Level 1'), use_container_width=True)
    if 'ผล Level 2' in final_df.columns:
        st.plotly_chart(plot_lj(final_df, 'ผล Level 2', 'Level 2'), use_container_width=True)

except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: โปรดตรวจสอบว่าชื่อ Sheet 'การตอบแบบฟอร์ม 1' มีอยู่จริงและเป็นสาธารณะ - {e}")

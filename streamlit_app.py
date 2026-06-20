import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import urllib.parse

st.set_page_config(layout="wide")
st.title("📊 ระบบ IQC Dashboard")

SHEET_ID = "16maoziMQKJiFtn-Rkzj_ZD7SZ7MqUBRcCj8MmYuwhxM"

def get_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(sheet_name)}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

try:
    df_log = get_data("การตอบแบบฟอร์ม 1")
    df_master = get_data("Master_Tests")
    
    # ทำความสะอาดข้อมูลชื่อรายการ (ตัดช่องว่าง)
    df_log['รายการทดสอบ'] = df_log['รายการทดสอบ'].astype(str).str.strip()
    df_master['รายการทดสอบ'] = df_master['รายการทดสอบ'].astype(str).str.strip()
    
    selected_test = st.selectbox("🎯 เลือกรายการทดสอบ:", df_log['รายการทดสอบ'].unique())
    display_df = df_log[df_log['รายการทดสอบ'] == selected_test]
    master_info = df_master[df_master['รายการทดสอบ'] == selected_test]

    if not master_info.empty:
        m = master_info.iloc[0]
        
        # ฟังก์ชันวาดกราฟ
        def draw_lj(data, mean, sd, col, title):
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data['ประทับเวลา'], y=data[col], mode='lines+markers', name=col))
            fig.add_hline(y=mean, line_color="black", line_width=2, annotation_text="Mean")
            for i in [1, 2, 3]:
                fig.add_hline(y=mean+(i*sd), line_dash="dash", line_color="red" if i==3 else "orange")
                fig.add_hline(y=mean-(i*sd), line_dash="dash", line_color="red" if i==3 else "orange")
            fig.update_layout(title=title, template="plotly_white")
            return fig

        c1, c2 = st.columns(2)
        with c1: st.plotly_chart(draw_lj(display_df, m['L1_Mean'], m['L1_SD'], 'ผล Level 1', 'Level 1'), use_container_width=True)
        with c2: st.plotly_chart(draw_lj(display_df, m['L2_Mean'], m['L2_SD'], 'ผล Level 2', 'Level 2'), use_container_width=True)
    else:
        st.error(f"⚠️ ไม่พบข้อมูล '{selected_test}' ในไฟล์ Master_Tests โปรดตรวจสอบชื่อให้ตรงกัน")

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")
# 4. ทำตารางสรุป IQC รายวัน
    st.header(f"📋 สรุปรายการบันทึก: {selected_test}")
    
    # เลือกคอลัมน์ที่พี่ต้องการแสดง (พี่สามารถปรับชื่อคอลัมน์ในลิสต์นี้ได้ตามต้องการ)
    cols_to_show = [
        'ประทับเวลา', 'สาขา', 'Lot_ชุดตรวจ', 'Exp_ชุดตรวจ', 
        'Lot_IQC-L1', 'Exp_IQC-L1', 'ผล Level 1', 'สถานะ Level 1',
        'Lot_IQC-L2', 'Exp_IQC-L2', 'ผล Level 2', 'สถานะ Level 2'
    ]
    
    # สร้างตารางที่คัดกรองเฉพาะคอลัมน์ที่เลือก
    summary_df = display_df[cols_to_show].sort_values(by='ประทับเวลา', ascending=False)
    
    # ใส่สีให้สถานะ "ผ่าน" เป็นเขียว และอื่นๆ เป็นแดง (เพื่อให้พี่ดูง่าย)
    def color_status(val):
        color = 'green' if val == 'ผ่าน' else 'red'
        return f'color: {color}; font-weight: bold'

    # แสดงผลตารางแบบ Interactive
    st.dataframe(
        summary_df.style.applymap(color_status, subset=['สถานะ Level 1', 'สถานะ Level 2']),
        use_container_width=True
    )
    
    # เพิ่มปุ่มดาวน์โหลดเป็น Excel
    @st.cache_data
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')
    
    csv = convert_df(summary_df)
    st.download_button("📥 ดาวน์โหลดข้อมูลเป็น CSV", csv, "iqc_summary.csv", "text/csv")

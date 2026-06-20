import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="POCT IQC Dashboard 2026", layout="wide")
st.title("📊 ระบบ IQC Dashboard - Full Version")

# 2. ตัวแปร
SHEET_ID = "16maoziMQKJiFtn-Rkzj_ZD7SZ7MqUBRcCj8MmYuwhxM"
URL_LJ = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=LJ_Calculation"
BASE_GITHUB_URL = "https://raw.githubusercontent.com/soysaena2013-creator/IQC_Dashboard_2026/main/"

# 3. สร้าง Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "1. กราฟและตารางรายวัน", "2. % Passing", "3. Yearly", "4. Staff", "5. Failed", "6. Raw Data", "7. Westgard"
])

with tab1:
    st.header("📈 กราฟ Levey-Jennings & ตารางสรุปรายวัน")
    try:
        df_master = pd.read_csv(URL_LJ)
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_test = st.selectbox("🎯 1. รายการทดสอบ:", df_master['รายการทดสอบ'].unique())
            df_step = df_master[df_master['รายการทดสอบ'] == selected_test]
        with col2:
            selected_loc = st.selectbox("🏥 2. หน่วยงาน:", df_step['หน่วยงาน/ที่ตั้ง'].unique())
            df_step = df_step[df_step['หน่วยงาน/ที่ตั้ง'] == selected_loc]
        with col3:
            selected_sn = st.selectbox("📟 3. Serial No:", df_step['Serial_No'].unique())
            final_df = df_step[df_step['Serial_No'] == selected_sn]

        if not final_df.empty:
            st.subheader(f"📅 ตารางบันทึก IQC รายวัน: {selected_sn}")
            cols = ['Timestamp', 'ผู้บันทึก', 'ผล Level 1', 'ผล Level 2', 'ผ่านเกณฑ์', 'การแก้ไข/หมายเหตุ']
            st.dataframe(final_df[cols].sort_values(by='Timestamp', ascending=False), use_container_width=True)
            
            m1, s1 = float(final_df['Mean L1'].iloc[0]), float(final_df['SD L1'].iloc[0])
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(x=final_df['Timestamp'], y=final_df['ผล Level 1'], mode='lines+markers'))
            fig1.add_hline(y=m1, line_color="green", annotation_text="Mean")
            fig1.add_hline(y=m1+(3*s1), line_dash="dash", line_color="red")
            fig1.add_hline(y=m1-(3*s1), line_dash="dash", line_color="red")
            st.plotly_chart(fig1, use_container_width=True)
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")

def load_github_csv(file_name):
    try:
        df = pd.read_csv(f"{BASE_GITHUB_URL}{file_name}", encoding='utf-8')
        st.dataframe(df, use_container_width=True)
    except:
        st.warning(f"⚠️ กำลังรอไฟล์ {file_name} ซิงค์ข้อมูล")

with tab2:
    load_github_csv("out_2_percentage.csv")
with tab3:
    load_github_csv("out_3_yearly_summary.csv")
with tab4:
    load_github_csv("out_4_staff_lots.csv")
with tab5:
    load_github_csv("out_5_failed_report.csv")
with tab6:
    load_github_csv("out_6_chart_data.csv")
with tab7:
    load_github_csv("out_7_lj_multi_rule.csv")

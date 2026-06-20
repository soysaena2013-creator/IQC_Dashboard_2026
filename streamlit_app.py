import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="POCT IQC Dashboard 2026", layout="wide")
st.title("📊 ระบบ IQC Dashboard - Full Version")

# URL ข้อมูล
SHEET_ID = "16maoziMQKJiFtn-Rkzj_ZD7SZ7MqUBRcCj8MmYuwhxM"
URL_LJ = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=LJ_Calculation"
BASE_GITHUB_URL = "https://raw.githubusercontent.com/soysaena2013-creator/IQC_Dashboard_2026/main/"

# สร้าง Tabs 7 ข้อ
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "1. กราฟและตารางรายวัน", "2. % Passing", "3. Yearly", "4. Staff", "5. Failed", "6. Raw Data", "7. Westgard"
])

with tab1:
    # [ใส่โค้ด Cascading Filter + ตารางสรุปรายวัน + กราฟ LJ ที่ผมให้ไปด้านบนตรงนี้ครับ]
    # ระบบจะทำงานแยกเครื่อง Serial No. ตามที่พี่ต้องการเป๊ะครับ

def load_github_csv(file_name):
    try:
        df = pd.read_csv(f"{BASE_GITHUB_URL}{file_name}", encoding='utf-8')
        st.dataframe(df, use_container_width=True)
    except:
        st.warning(f"⚠️ กำลังรอไฟล์ {file_name} ซิงค์ข้อมูล")

with tab2:
    st.header("📊 2. เปอร์เซ็นต์การผ่านเกณฑ์มาตรฐาน (% Passing)")
    load_github_csv("out_2_percentage.csv")
with tab3:
    st.header("📅 3. รายงานสรุปผลรายปี")
    load_github_csv("out_3_yearly_summary.csv")
with tab4:
    st.header("👥 4. สถิติรายชื่อเจ้าหน้าที่")
    load_github_csv("out_4_staff_lots.csv")
with tab5:
    st.header("❌ 5. รายงานผลตรวจที่ตกเกณฑ์")
    load_github_csv("out_5_failed_report.csv")
with tab6:
    st.header("📋 6. ข้อมูลดิบ")
    load_github_csv("out_6_chart_data.csv")
with tab7:
    st.header("🛡️ 7. บันทึก Westgard Multi-rule")
    load_github_csv("out_7_lj_multi_rule.csv")

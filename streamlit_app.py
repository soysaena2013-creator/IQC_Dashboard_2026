import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ตั้งค่าหน้าจอแดชบอร์ดแล็บแบบกว้างเต็มหน้าจอ
st.set_page_config(page_title="IQC Lab Dashboard 2026", layout="wide")
st.title("📊 ระบบ IQC Analytics & Westgard Multi-rule Dashboard (ระบบเต็ม)")
st.markdown("---")

# 📍 ฐานข้อมูลหลัก Google Sheets ของพี่
SHEET_ID = "16maoziMQKJiFtn-Rkzj_ZD7SZ7MqUBRcCj8MmYuwhxM"

# 📍 ที่อยู่ไฟล์ข้อมูลดิบ 7 ตัวบน GitHub ของพี่เพื่อดึงมาแสดงผลร่วมกัน
BASE_GITHUB_URL = "https://raw.githubusercontent.com/soysaena2013-creator/IQC_Dashboard_2026/refs/heads/main/"

# --- สร้างระบบ 7 แท็บเมนูตามหัวข้องานที่พี่ต้องการ ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "1. กราฟ Levey-Jennings (Real-time)",
    "2. สรุปเปอร์เซ็นต์ผ่านเกณฑ์ (% Passing)",
    "3. รายงานสรุปรายปี (Yearly Summary)",
    "4. สถิติแยกตามรายชื่อเจ้าหน้าที่ (Staff Stats)",
    "5. รายงานผลตรวจที่ตกเกณฑ์ (Failed Report)",
    "6. ข้อมูลพล็อตแผนภูมิ (Chart Data)",
    "7. ระบบ Westgard Multi-rule (Full Log)"
])

# ==========================================
# ข้อที่ 1: กราฟ Levey-Jennings (Real-time จาก Google Sheets)
# ==========================================
with tab1:
    st.header("📈 1. แผนภูมิวิเคราะห์ Levey-Jennings Real-time")
    try:
        URL_LJ = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=LJ_Calculation"
        df_sheets = pd.read_csv(URL_LJ)
        if not df_sheets.empty and 'รายการทดสอบ' in df_sheets.columns:
            tests = df_sheets['รายการทดสอบ'].dropna().unique()
            selected_test = st.selectbox("🎯 เลือกรายการสารควบคุมคุณภาพ:", tests, key="test_select")
            test_df = df_sheets[df_sheets['รายการทดสอบ'] == selected_test].reset_index(drop=True)
            
            if not test_df.empty:
                mean_l1 = float(test_df.loc[0, 'Mean L1']) if 'Mean L1' in test_df.columns else 100
                sd_l1 = float(test_df.loc[0, 'SD L1']) if 'SD L1' in test_df.columns else 2
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=test_df['Timestamp'], y=test_df['ผล Level 1'], mode='lines+markers', name='ผล Level 1'))
                fig.add_hline(y=mean_l1, line_color="green", annotation_text="Mean")
                fig.add_hline(y=mean_l1 + (2*sd_l1), line_dash="dash", line_color="orange", annotation_text="+2SD")
                fig.add_hline(y=mean_l1 - (2*sd_l1), line_dash="dash", line_color="orange", annotation_text="-2SD")
                fig.add_hline(y=mean_l1 + (3*sd_l1), line_dash="dash", line_color="red", annotation_text="+3SD")
                fig.add_hline(y=mean_l1 - (3*sd_l1), line_dash="dash", line_color="red", annotation_text="-3SD")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("กำลังรอข้อมูลบันทึกเข้าสู่ระบบ Google Sheets...")
    except Exception as e:
        st.error(f"ไม่สามารถเชื่อมต่อ Google Sheets ได้: {e}")

# ==========================================
# ข้อที่ 2: สรุปเปอร์เซ็นต์ผ่านเกณฑ์ (% Passing)
# ==========================================
with tab2:
    st.header("📊 2. สรุปอัตราส่วนเปอร์เซ็นต์การผ่านเกณฑ์มาตรฐาน")
    try:
        df2 = pd.read_csv(f"{BASE_GITHUB_URL}out_2_percentage.csv")
        st.dataframe(df2, use_container_width=True)
    except:
        st.warning("ไม่พบไฟล์ out_2_percentage.csv บน GitHub")

# ==========================================
# ข้อที่ 3: รายงานสรุปรายปี (Yearly Summary)
# ==========================================
with tab3:
    st.header("📅 3. รายงานสรุปผลการควบคุมคุณภาพภาพรวมรายปี")
    try:
        df3 = pd.read_csv(f"{BASE_GITHUB_URL}out_3_yearly_summary.csv")
        st.dataframe(df3, use_container_width=True)
    except:
        st.warning("ไม่พบไฟล์ out_3_yearly_summary.csv บน GitHub")

# ==========================================
# ข้อที่ 4: สถิติแยกตามรายชื่อเจ้าหน้าที่ (Staff Stats)
# ==========================================
with tab4:
    st.header("👥 4. สถิติการบันทึกผลแยกตามรายชื่อเจ้าหน้าที่ผู้ตรวจวิเคราะห์")
    try:
        df4 = pd.read_csv(f"{BASE_GITHUB_URL}out_4_staff_lots.csv")
        st.dataframe(df4, use_container_width=True)
    except:
        st.warning("ไม่พบไฟล์ out_4_staff_lots.csv บน GitHub")

# ==========================================
# ข้อที่ 5: รายงานผลตรวจที่ตกเกณฑ์ (Failed Report)
# ==========================================
with tab5:
    st.header("❌ 5. รายงานและบันทึกเหตุการณ์กรณีผลควบคุมตกเกณฑ์ (Out of Control)")
    try:
        df5 = pd.read_csv(f"{BASE_GITHUB_URL}out_5_failed_report.csv")
        st.dataframe(df5, use_container_width=True)
    except:
        st.warning("ไม่พบไฟล์ out_5_failed_report.csv บน GitHub")

# ==========================================
# ข้อที่ 6: ข้อมูลพล็อตแผนภูมิ (Chart Data)
# ==========================================
with tab6:
    st.header("📋 6. ชุดข้อมูลดิบสำหรับพล็อตแผนภูมิควบคุม")
    try:
        df6 = pd.read_csv(f"{BASE_GITHUB_URL}out_6_chart_data.csv")
        st.dataframe(df6, use_container_width=True)
    except:
        st.warning("ไม่พบไฟล์ out_6_chart_data.csv บน GitHub")

# ==========================================
# ข้อที่ 7: ระบบ Westgard Multi-rule (Full Log)
# ==========================================
with tab7:
    st.header("🛡️ 7. บันทึกการวิเคราะห์ Westgard Multi-rule แบบละเอียด")
    try:
        df7 = pd.read_csv(f"{BASE_GITHUB_URL}out_7_lj_multi_rule.csv")
        st.dataframe(df7, use_container_width=True)
    except:
        st.warning("ไม่พบไฟล์ out_7_lj_multi_rule.csv บน GitHub")

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. ตั้งค่าหน้าจอแดชบอร์ดแล็บแบบกว้างเต็มหน้าจอ
st.set_page_config(page_title="IQC Lab Dashboard 2026", layout="wide")
st.title("📊 ระบบ IQC Analytics & Westgard Multi-rule Dashboard (ระบบเต็ม 7 ข้อ)")
st.markdown("---")

# 2. ตัวแปรฐานข้อมูลหลักของพี่
SHEET_ID = "16maoziMQKJiFtn-Rkzj_ZD7SZ7MqUBRcCj8MmYuwhxM"
BASE_GITHUB_URL = "https://raw.githubusercontent.com/soysaena2013-creator/IQC_Dashboard_2026/main/"

# 3. คำสั่งสร้างแท็บเมนู 7 ข้อ (ห้ามลบบรรทัดนี้เด็ดขาดเพื่อป้องกัน NameError ครับพี่)
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
# ข้อที่ 1: กราฟ Levey-Jennings 2 ระดับ (ดึง Real-time จาก Google Sheets)
# ==========================================
with tab1:
    st.header("📈 1. แผนภูมิวิเคราะห์ Levey-Jennings Real-time (Level 1 & Level 2)")
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
                
                # 🔵 พล็อตเส้นข้อมูลของ Level 1
                if 'ผล Level 1' in test_df.columns:
                    fig.add_trace(go.Scatter(x=test_df['Timestamp'], y=test_df['ผล Level 1'], mode='lines+markers', name='ผล QC Level 1', line=dict(color='#1f77b4')))
                
                # 🔴 พล็อตเส้นข้อมูลของ Level 2 เพิ่มเติมเข้ามาคู่กัน
                if 'ผล Level 2' in test_df.columns:
                    fig.add_trace(go.Scatter(x=test_df['Timestamp'], y=test_df['ผล Level 2'], mode='lines+markers', name='ผล QC Level 2', line=dict(color='#d62728')))
                
                fig.add_hline(y=mean_l1, line_color="green", annotation_text="Mean L1")
                fig.add_hline(y=mean_l1 + (2*sd_l1), line_dash="dash", line_color="orange", annotation_text="+2SD L1")
                fig.add_hline(y=mean_l1 - (2*sd_l1), line_dash="dash", line_color="orange", annotation_text="-2SD L1")
                
                fig.update_layout(xaxis_title="วัน-เวลาบันทึกผล", yaxis_title="ค่าวิเคราะห์", hovermode="x")
                st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"การเชื่อมต่อกูเกิลชีตขัดข้อง: {e}")

# ==========================================
# ข้อที่ 2 - 7: ดึงรายงานสถิติไฟล์จากคลัง GitHub ของพี่
# ==========================================
def load_github_csv(file_name):
    try:
        df = pd.read_csv(f"{BASE_GITHUB_URL}{file_name}", encoding='utf-8')
        st.dataframe(df, use_container_width=True)
    except:
        st.warning(f"⚠️ กำลังรอไฟล์ {file_name} ซิงค์ข้อมูลเข้าสู่คลังหลัก")

with tab2:
    st.header("📊 2. สรุปอัตราส่วนเปอร์เซ็นต์การผ่านเกณฑ์มาตรฐาน (% Passing)")
    load_github_csv("out_2_percentage.csv")
with tab3:
    st.header("📅 3. รายงานสรุปผลการควบคุมคุณภาพภาพรวมรายปี")
    load_github_csv("out_3_yearly_summary.csv")
with tab4:
    st.header("👥 4. สถิติการบันทึกผลแยกตามรายชื่อเจ้าหน้าที่ผู้ตรวจวิเคราะห์")
    load_github_csv("out_4_staff_lots.csv")
with tab5:
    st.header("❌ 5. รายงานและบันทึกเหตุการณ์กรณีผลควบคุมตกเกณฑ์")
    load_github_csv("out_5_failed_report.csv")
with tab6:
    st.header("📋 6. ชุดข้อมูลดิบสำหรับพล็อตแผนภูมิควบคุม")
    load_github_csv("out_6_chart_data.csv")
with tab7:
    st.header("🛡️ 7. บันทึกการวิเคราะห์เกณฑ์ Westgard Multi-rule แบบละเอียด")
    load_github_csv("out_7_lj_multi_rule.csv")

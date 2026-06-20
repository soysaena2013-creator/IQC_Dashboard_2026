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

# 3. คำสั่งสร้างแท็บเมนู 7 ข้อ
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
# ข้อที่ 1: กราฟ Levey-Jennings (แยก 2 กราฟเด็ดขาด ระดับ 1 และ ระดับ 2)
# ==========================================
with tab1:
    st.header("📈 1. แผนภูมิวิเคราะห์ Levey-Jennings Real-time (แยกระดับระดับสารควบคุม)")
    try:
        URL_LJ = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=LJ_Calculation"
        df_sheets = pd.read_csv(URL_LJ)
        
        if not df_sheets.empty and 'รายการทดสอบ' in df_sheets.columns:
            tests = df_sheets['รายการทดสอบ'].dropna().unique()
            selected_test = st.selectbox("🎯 เลือกรายการสารควบคุมคุณภาพ:", tests, key="test_select")
            test_df = df_sheets[df_sheets['รายการทดสอบ'] == selected_test].reset_index(drop=True)
            
            if not test_df.empty:
                # ----------------------------------------------------
                # กราฟที่ 1: สารควบคุมคุณภาพ Level 1 (สีน้ำเงิน)
                # ----------------------------------------------------
                st.subheader("🔵 แผนภูมิควบคุมคุณภาพ Level 1")
                mean_l1 = float(test_df.loc[0, 'Mean L1']) if 'Mean L1' in test_df.columns else 100
                sd_l1 = float(test_df.loc[0, 'SD L1']) if 'SD L1' in test_df.columns else 2
                
                fig1 = go.Figure()
                if 'ผล Level 1' in test_df.columns:
                    fig1.add_trace(go.Scatter(x=test_df['Timestamp'], y=test_df['ผล Level 1'], mode='lines+markers', name='ผล QC Level 1', line=dict(color='#1f77b4', width=2), marker=dict(size=8)))
                
                # วาดเส้นเกณฑ์ควบคุมสำหรับ L1
                fig1.add_hline(y=mean_l1, line_color="green", annotation_text="Mean")
                fig1.add_hline(y=mean_l1 + (2*sd_l1), line_dash="dash", line_color="orange", annotation_text="+2SD")
                fig1.add_hline(y=mean_l1 - (2*sd_l1), line_dash="dash", line_color="orange", annotation_text="-2SD")
                fig1.add_hline(y=mean_l1 + (3*sd_l1), line_dash="dash", line_color="red", annotation_text="+3SD")
                fig1.add_hline(y=mean_l1 - (3*sd_l1), line_dash="dash", line_color="red", annotation_text="-3SD")
                fig1.update_layout(xaxis_title="วัน-เวลาบันทึกผล", yaxis_title="ค่าวิเคราะห์ L1", hovermode="x", height=400)
                st.plotly_chart(fig1, use_container_width=True)
                
                st.markdown("<br><hr>", unsafe_with_html=True) # ขีดเส้นแบ่งระหว่างกราฟเพื่อความชัดเจน
                
                # ----------------------------------------------------
                # กราฟที่ 2: สารควบคุมคุณภาพ Level 2 (สีแดง)
                # ----------------------------------------------------
                st.subheader("🔴 แผนภูมิควบคุมคุณภาพ Level 2")
                mean_l2 = float(test_df.loc[0, 'Mean L2']) if 'Mean L2' in test_df.columns else 200
                sd_l2 = float(test_df.loc[0, 'SD L2']) if 'SD L2' in test_df.columns else 4
                
                fig2 = go.Figure()
                if 'ผล Level 2' in test_df.columns:
                    fig2.add_trace(go.Scatter(x=test_df['Timestamp'], y=test_df['ผล Level 2'], mode='lines+markers', name='ผล QC Level 2', line=dict(color='#d62728', width=2), marker=dict(size=8)))
                
                # วาดเส้นเกณฑ์ควบคุมสำหรับ L2 (แก้ไขวงเล็บที่ปิดไม่ครบเรียบร้อยครับ)
                fig2.add_hline(y=mean_l2, line_color="green", annotation_text="Mean")
                fig2.add_hline(y=mean_l2 + (2*sd_l2), line_dash="dash", line_color="orange", annotation_text="+2SD")
                fig2.add_hline(y=mean_l2 - (2*sd_l2), line_dash="dash", line_color="orange", annotation_text="-2SD")
                fig2.add_hline(y=mean_l2 + (3*sd_l2), line_dash="dash", line_color="red", annotation_text="+3SD")
                fig2.add_hline(y=mean_l2 - (3*sd_l2), line_dash="dash", line_color="red", annotation_text="-

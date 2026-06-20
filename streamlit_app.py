import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="POCT IQC Dashboard 2026", layout="wide")
st.title("📊 ระบบ IQC Dashboard (Simple View)")

# 2. ดึงข้อมูล
SHEET_ID = "16maoziMQKJiFtn-Rkzj_ZD7SZ7MqUBRcCj8MmYuwhxM"
URL_LJ = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=LJ_Calculation"

# 3. สร้าง Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "1. กราฟและตาราง", "2. % Passing", "3. Yearly", "4. Staff", "5. Failed", "6. Raw Data", "7. Westgard"
])

with tab1:
    st.header("📈 กราฟ Levey-Jennings & ตารางสรุปรายวัน")
    try:
        df = pd.read_csv(URL_LJ)
        
        # เลือกรายการทดสอบอย่างเดียว
        selected_test = st.selectbox("🎯 เลือกรายการทดสอบ:", df['รายการทดสอบ'].unique())
        final_df = df[df['รายการทดสอบ'] == selected_test]

        if not final_df.empty:
            st.subheader(f"📅 ตารางบันทึก IQC รายวัน: {selected_test}")
            # แสดงตาราง (ตัดคอลัมน์ที่ไม่จำเป็นออกถ้าไม่มีแล้ว)
            cols = ['Timestamp', 'ผู้บันทึก', 'ผล Level 1', 'ผล Level 2', 'ผ่านเกณฑ์', 'การแก้ไข/หมายเหตุ']
            # เลือกเฉพาะคอลัมน์ที่มีอยู่จริง
            available_cols = [c for c in cols if c in final_df.columns]
            st.dataframe(final_df[available_cols].sort_values(by='Timestamp', ascending=False), use_container_width=True)
            
            # กราฟ LJ (ใช้ค่าเฉลี่ยรวมของเทสต์นั้น)
            m1 = final_df['Mean L1'].iloc[0] if 'Mean L1' in final_df.columns else final_df['ผล Level 1'].mean()
            s1 = final_df['SD L1'].iloc[0] if 'SD L1' in final_df.columns else final_df['ผล Level 1'].std()
            
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(x=final_df['Timestamp'], y=final_df['ผล Level 1'], mode='lines+markers', name='Level 1'))
            fig1.add_hline(y=m1, line_color="green", annotation_text="Mean")
            fig1.add_hline(y=m1+(3*s1), line_dash="dash", line_color="red")
            fig1.add_hline(y=m1-(3*s1), line_dash="dash", line_color="red")
            st.plotly_chart(fig1, use_container_width=True)
            
    except Exception as e:
        st.error(f"โหลดข้อมูลขัดข้อง: {e}")

# (ส่วน Tab 2-7 คงเดิม)
def load_github_csv(file_name):
    try:
        BASE_GITHUB_URL = "https://raw.githubusercontent.com/soysaena2013-creator/IQC_Dashboard_2026/main/"
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

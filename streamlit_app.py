import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="POCT IQC Dashboard 2026", layout="wide")
st.title("📊 ระบบ IQC Dashboard")

# 2. ดึงข้อมูล
SHEET_ID = "16maoziMQKJiFtn-Rkzj_ZD7SZ7MqUBRcCj8MmYuwhxM"
URL_LJ = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=LJ_Calculation"

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "1. กราฟและตารางรายวัน", "2. % Passing", "3. Yearly", "4. Staff", "5. Failed", "6. Raw Data", "7. Westgard"
])

with tab1:
    st.header("📈 กราฟและตารางสรุปผลประจำวัน")
    try:
        df = pd.read_csv(URL_LJ)
        
        # เลือกรายการตรวจ
        selected_test = st.selectbox("🎯 เลือกรายการทดสอบ:", df['รายการทดสอบ'].unique())
        final_df = df[df['รายการทดสอบ'] == selected_test]

        if not final_df.empty:
            st.subheader(f"📅 ตารางบันทึก IQC รายวัน: {selected_test}")
            # ตารางแสดงข้อมูล
            cols = ['Timestamp', 'ชื่อผู้ปฏิบัติงาน', 'ผล Level 1', 'ผล Level 2', 'สถานะ Re-run', 'สาเหตุของปัญหา', 'วิธีการแก้ไขและComment']
            available_cols = [c for c in cols if c in final_df.columns]
            st.dataframe(final_df[available_cols].sort_values(by='Timestamp', ascending=False), use_container_width=True)
            
            # ดึงค่า Mean/SD (ถ้ามี)
            m1 = final_df['Mean L1'].iloc[0] if 'Mean L1' in final_df.columns else final_df['ผล Level 1'].mean()
            s1 = final_df['SD L1'].iloc[0] if 'SD L1' in final_df.columns else final_df['ผล Level 1'].std()
            m2 = final_df['Mean L2'].iloc[0] if 'Mean L2' in final_df.columns else final_df['ผล Level 2'].mean()
            s2 = final_df['SD L2'].iloc[0] if 'SD L2' in final_df.columns else final_df['ผล Level 2'].std()

            # ฟังก์ชันสร้างกราฟที่สีคมชัดตามมาตรฐานพี่
            def draw_lj_chart(y_data, mean_val, sd_val, title, color):
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=final_df['Timestamp'], y=y_data, mode='lines+markers', name='Result', line=dict(color='#0066cc', width=3)))
                fig.add_hline(y=mean_val, line_color="green", line_width=2, annotation_text="Mean")
                fig.add_hline(y=mean_val + (3*sd_val), line_dash="dash", line_color="red", line_width=2, annotation_text="+3SD")
                fig.add_hline(y=mean_val - (3*sd_val), line_dash="dash", line_color="red", line_width=2, annotation_text="-3SD")
                fig.update_layout(title=title, height=400)
                return fig

            # กราฟแยก L1 และ L2
            st.plotly_chart(draw_lj_chart(final_df['ผล Level 1'], m1, s1, "🔵 กราฟควบคุมคุณภาพ Level 1", "#1f77b4"), use_container_width=True)
            st.plotly_chart(draw_lj_chart(final_df['ผล Level 2'], m2, s2, "🔴 กราฟควบคุมคุณภาพ Level 2", "#d62728"), use_container_width=True)
            
    except Exception as e:
        st.error(f"โหลดข้อมูลขัดข้อง: {e}")

# (ส่วน Tab 2-7 คงเดิม)
def load_github_csv(file_name):
    try:
        BASE_GITHUB_URL = "https://raw.githubusercontent.com/soysaena2013-creator/IQC_Dashboard_2026/main/"
        df = pd.read_csv(f"{BASE_GITHUB_URL}{file_name}", encoding='utf-8')
        st.dataframe(df, use_container_width=True)
    except:
        st.warning(f"⚠️ รอการอัปเดตไฟล์ {file_name}")

with tab2: load_github_csv("out_2_percentage.csv")
with tab3: load_github_csv("out_3_yearly_summary.csv")
with tab4: load_github_csv("out_4_staff_lots.csv")
with tab5: load_github_csv("out_5_failed_report.csv")
with tab6: load_github_csv("out_6_chart_data.csv")
with tab7: load_github_csv("out_7_lj_multi_rule.csv")

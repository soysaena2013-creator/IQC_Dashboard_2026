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
    st.header("📈 กราฟและตารางสรุปผล IQC")
    try:
        df = pd.read_csv(URL_LJ)
        
        # ปรับเฉพาะวันที่ (ไม่เอาเวลา)
        df['Date_only'] = pd.to_datetime(df['Timestamp']).dt.strftime('%d/%m/%Y')
        
        selected_test = st.selectbox("🎯 รายการทดสอบ:", df['รายการทดสอบ'].unique())
        final_df = df[df['รายการทดสอบ'] == selected_test].copy()

        if not final_df.empty:
            st.subheader("📋 ตารางบันทึกข้อมูล IQC")
            # แสดงคอลัมน์สำคัญตามที่ต้องการ
            cols_to_show = ['Date_only', 'สาขา', 'รายการทดสอบ', 'ผล Level 1', 'ผล Level 2', 'สถานะ Re-run', 'สาเหตุของปัญหา', 'วิธีการแก้ไขและComment', 'ชื่อผู้ปฏิบัติงาน']
            available_cols = [c for c in cols_to_show if c in final_df.columns]
            st.dataframe(final_df[available_cols].sort_values(by='Date_only', ascending=False), use_container_width=True)
            
            # ฟังก์ชันวาดกราฟ (ใช้ Date_only)
            def plot_lj(df_data, level_col, mean_col, sd_col, title):
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_data['Date_only'], y=df_data[level_col], mode='lines+markers', name='Result', line=dict(color='#1f77b4', width=3)))
                
                m = df_data[mean_col].iloc[0] if mean_col in df_data.columns else df_data[level_col].mean()
                s = df_data[sd_col].iloc[0] if sd_col in df_data.columns else df_data[level_col].std()
                
                fig.add_hline(y=m, line_color="green", line_width=3, annotation_text="Mean")
                fig.add_hline(y=m+(2*s), line_dash="dash", line_color="red", line_width=2, annotation_text="+2SD")
                fig.add_hline(y=m-(2*s), line_dash="dash", line_color="red", line_width=2, annotation_text="-2SD")
                
                fig.update_layout(title=title, height=400, template="plotly_white")
                return fig

            st.plotly_chart(plot_lj(final_df, 'ผล Level 1', 'Mean L1', 'SD L1', "🔵 กราฟ Levey-Jennings: Level 1"), use_container_width=True)
            st.plotly_chart(plot_lj(final_df, 'ผล Level 2', 'Mean L2', 'SD L2', "🔴 กราฟ Levey-Jennings: Level 2"), use_container_width=True)
            
        else:
            st.warning("ไม่พบข้อมูลในรายการที่เลือก")
            
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")

# (ส่วน Tab 2-7 คงเดิม)
def load_github_csv(file_name):
    try:
        BASE_GITHUB_URL = "https://raw.githubusercontent.com/soysaena2013-creator/IQC_Dashboard_2026/main/"
        df = pd.read_csv(f"{BASE_GITHUB_URL}{file_name}", encoding='utf-8')
        st.dataframe(df, use_container_width=True)
    except:
        st.warning(f"⚠️ กำลังรอไฟล์ {file_name} ซิงค์ข้อมูล")

with tab2: load_github_csv("out_2_percentage.csv")
with tab3: load_github_csv("out_3_yearly_summary.csv")
with tab4: load_github_csv("out_4_staff_lots.csv")
with tab5: load_github_csv("out_5_failed_report.csv")
with tab6: load_github_csv("out_6_chart_data.csv")
with tab7: load_github_csv("out_7_lj_multi_rule.csv")

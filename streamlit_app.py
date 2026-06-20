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
        
        # ปรับรูปแบบวันที่สำหรับ Filter
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        # เลือกรายการทดสอบ
        selected_test = st.selectbox("🎯 รายการทดสอบ:", df['รายการทดสอบ'].unique())
        
        # ระบบ Filter ตามช่วงเวลา
        col1, col2 = st.columns(2)
        start_date = col1.date_input("📅 เริ่มต้น", df['Timestamp'].min())
        end_date = col2.date_input("📅 สิ้นสุด", df['Timestamp'].max())
        
        # กรองข้อมูล
        mask = (df['รายการทดสอบ'] == selected_test) & (df['Timestamp'].dt.date >= start_date) & (df['Timestamp'].dt.date <= end_date)
        final_df = df[mask]

        if not final_df.empty:
            # 1. ตารางแสดงข้อมูล (ดึงตาม Header จาก Sheet)
            st.subheader("📋 ตารางบันทึกข้อมูล IQC")
            st.dataframe(final_df.sort_values(by='Timestamp', ascending=False), use_container_width=True)
            
            # 2. กราฟ LJ ที่ชัดเจน (Mean, 2SD)
            def plot_lj(df_data, level_col, mean_col, sd_col, title):
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_data['Timestamp'], y=df_data[level_col], mode='lines+markers', name='Result', line=dict(color='#1f77b4', width=3)))
                
                # เส้น Mean/SD
                m = df_data[mean_col].iloc[0]
                s = df_data[sd_col].iloc[0]
                fig.add_hline(y=m, line_color="green", line_width=3, annotation_text="Mean")
                fig.add_hline(y=m+(2*s), line_dash="dash", line_color="red", line_width=2, annotation_text="+2SD")
                fig.add_hline(y=m-(2*s), line_dash="dash", line_color="red", line_width=2, annotation_text="-2SD")
                
                fig.update_layout(title=title, height=400, template="plotly_white")
                return fig

            st.plotly_chart(plot_lj(final_df, 'ผล Level 1', 'Mean L1', 'SD L1', "🔵 กราฟ Levey-Jennings: Level 1"), use_container_width=True)
            st.plotly_chart(plot_lj(final_df, 'ผล Level 2', 'Mean L2', 'SD L2', "🔴 กราฟ Levey-Jennings: Level 2"), use_container_width=True)
            
        else:
            st.warning("ไม่พบข้อมูลในช่วงเวลาที่เลือก")
            
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")

# ... (Tab 2-7 คงเดิม)

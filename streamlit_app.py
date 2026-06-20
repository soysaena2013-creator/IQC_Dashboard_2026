import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ตั้งค่าหน้าเว็บให้เป็นแนวกว้างและสวยงาม
st.set_page_config(page_title="IQC Lab Dashboard", layout="wide")

st.title("📊 ระบบ IQC Analytics & Westgard Multi-rule Dashboard")
st.write("ข้อมูลอัปเดตอัตโนมัติจากระบบห้องปฏิบัติการ")

# ลิงก์ข้อมูลดิบจาก GitHub ของพี่
URL_LJ = https://github.com/soysaena2013-creator/IQC_Dashboard_2026/raw/refs/heads/main/out_7_lj_multi_rule.csv
URL_PERCENT = "https://raw.githubusercontent.com/soysaena2013-creator/repo/master/out_2_percentage.csv"
URL_FAILED = "https://raw.githubusercontent.com/soysaena2013-creator/repo/master/out_5_failed_report.csv"

try:
    df_lj = pd.read_csv(URL_LJ)
    df_pct = pd.read_csv(URL_PERCENT)
    df_failed = pd.read_csv(URL_FAILED)
    
    # ----------------- โซนที่ 1: สรุปภาพรวม (KPI Cards) -----------------
    st.header("📈 ภาพรวมการควบคุมคุณภาพ (IQC Overview)")
    col1, col2, col3 = st.columns(3)
    
    if not df_pct.empty:
        col1.metric("รายการตรวจที่เปิดทั้งหมด", f"{df_pct.loc[0, 'เปิดทั้งหมด']} รายการ")
        col2.metric("รายการที่ส่งทำ IQC แล้ว", f"{df_pct.loc[0, 'ทำIQC']} รายการ")
        col3.metric("ร้อยละความครอบคลุม IQC", f"{df_pct.loc[0, 'ร้อยละ']}%")

    st.markdown("---")

    # ----------------- โซนที่ 2: กราฟ Levey-Jennings & Westgard -----------------
    st.header("📉 กราฟ Levey-Jennings Control Chart")
    
    # ตรวจสอบว่ามีข้อมูล Glucose หรือรายการทดสอบไหม
    if not df_lj.empty:
        # ให้ผู้ใช้งานเลือกรายการตรวจ (เผื่ออนาคตมีหลายตัว)
        tests = df_lj['รายการทดสอบ'].unique() if 'รายการทดสอบ' in df_lj.columns else ['Glucose']
        selected_test = st.selectbox("เลือกรายการทดสอบเพื่อดูกราฟ:", tests)
        
        # กรองข้อมูลตามรายการที่เลือก
        test_df = df_lj[df_lj['รายการทดสอบ'] == selected_test].reset_index()
        
        if not test_df.empty:
            # ดึงค่า Mean และ SD (ใช้ของแถวล่าสุดมาพล็อตเส้นควบคุม)
            mean_l1 = float(test_df.loc[0, 'Mean L1']) if 'Mean L1' in test_df.columns else 100
            sd_l1 = float(test_df.loc[0, 'SD L1']) if 'SD L1' in test_df.columns else 2
            
            # สร้างกราฟ LJ ด้วย Plotly
            fig = go.Figure()
            
            # เส้นผลลัพธ์ IQC Level 1
            fig.add_trace(go.Scatter(
                x=test_df['Timestamp'], 
                y=test_df['ผล Level 1'], 
                mode='lines+markers',
                name='ผลตรวจ Level 1',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=8)
            ))
            
            # ใส่เส้นควบคุม Mean, +/-1SD, +/-2SD, +/-3SD
            colors = {
                'Mean': 'green',
                '+/-1SD': 'gray',
                '+/-2SD': 'orange',
                '+/-3SD': 'red'
            }
            
            for label, color in colors.items():
                if label == 'Mean':
                    y_val = mean_l1
                    dash = 'solid'
                elif label == '+/-1SD':
                    y_val = mean_l1 + sd_l1
                    dash = 'dash'
                    # พล็อตเส้นลบด้วย
                    fig.add_hline(y=mean_l1 - sd_l1, line_dash="dash", line_color=color)
                elif label == '+/-2SD':
                    y_val = mean_l1 + (2 * sd_l1)
                    dash = 'dash'
                    fig.add_hline(y=mean_l1 - (2 * sd_l1), line_dash="dash", line_color=color)
                elif label == '+/-3SD':
                    y_val = mean_l1 + (3 * sd_l1)
                    dash = 'dash'
                    fig.add_hline(y=mean_l1 - (3 * sd_l1), line_dash="dash", line_color=color)
                    
                fig.add_hline(y=y_val, line_dash=dash, line_color=color, annotation_text=label)
            
            fig.update_layout(
                title=f"Levey-Jennings Chart สำหรับ {selected_test} (Level 1)",
                xaxis_title="วัน/เวลา ที่บันทึกรัน",
                yaxis_title="ค่าผลตรวจ (Value)",
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # แสดงตารางสถานะกฎ Westgard ด้านล่างกราฟ
            st.subheader("📋 สถานะตารางบันทึกการวิเคราะห์ Westgard Rule")
            display_cols = [c for c in ['Timestamp', 'รายการทดสอบ', 'ผล Level 1', 'Z-Score L1', 'Westgard_Result'] if c in test_df.columns]
            st.dataframe(test_df[display_cols], use_container_width=True)

    st.markdown("---")

    # ----------------- โซนที่ 3: รายงานปัญหา IQC หลุดเกณฑ์ -----------------
    st.header("🚨 รายงานสถานะรายการที่ไม่ผ่านเกณฑ์ (Action Log)")
    if not df_failed.empty:
        st.dataframe(df_failed, use_container_width=True)
    else:
        st.success("🎉 ยินดีด้วย! ขณะนี้ไม่มีรายการทดสอบใดหลุดเกณฑ์ควบคุมคุณภาพ")

except Exception as e:
    st.error(f"ไม่สามารถโหลดข้อมูลจากระบบคลังได้ชั่วคราว: {e}")

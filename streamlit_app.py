import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ตั้งค่าหน้าเว็บแดชบอร์ดให้แสดงผลเต็มหน้าจอ
st.set_page_config(page_title="IQC Lab Dashboard", layout="wide")

st.title("📊 ระบบ IQC Analytics & Westgard Multi-rule Dashboard")
st.markdown("---")

# 📍 จุดสำคัญ: ให้พี่นำรหัสไฟล์ยาวๆ ที่คัดลอกมาจากขั้นตอนการแชร์มาวางแทนที่ข้อความด้านล่างนี้ครับ
SHEET_ID = "วางรหัสไฟล์ยาวๆของพี่ตรงนี้"
SHEET_NAME = "LJ_Calculation"

# ดึงข้อมูลจากแผ่นงานผ่านลิงก์ข้อมูลดิบ (gviz API) เพื่อป้องกันปัญหาภาษาไทยเพี้ยน
URL = f"https://docs.google.com/spreadsheets/d/16maoziMQKJiFtn-Rkzj_ZD7SZ7MqUBRcCj8MmYuwhxM/edit?usp=sharing"

try:
    # อ่านข้อมูลเข้าสู่ระบบ
    df = pd.read_csv(URL)
    
    if not df.empty and 'รายการทดสอบ' in df.columns:
        st.success("✅ เชื่อมต่อข้อมูลดิบและระบบสูตรจาก Google Sheets สำเร็จแล้วครับพี่!")
        
        # ดึงตัวเลือกรายการสิ่งส่งตรวจที่ไม่ซ้ำกัน
        tests = df['รายการทดสอบ'].dropna().unique()
        selected_test = st.selectbox("🎯 เลือกรายการทดสอบที่ต้องการเรียกดู Levey-Jennings Chart:", tests)
        
        # กรองข้อมูลเฉพาะของรายการทดสอบที่เลือก
        test_df = df[df['รายการทดสอบ'] == selected_test].reset_index(drop=True)
        
        if not test_df.empty:
            # ดึงค่ากำหนดพื้นฐานสำหรับการวาดเส้นควบคุม
            mean_l1 = float(test_df.loc[0, 'Mean L1']) if 'Mean L1' in test_df.columns else 100
            sd_l1 = float(test_df.loc[0, 'SD L1']) if 'SD L1' in test_df.columns else 2
            
            # เริ่มต้นพล็อตกราฟควบคุมคุณภาพ (Levey-Jennings)
            fig = go.Figure()
            
            # เส้นข้อมูลผลการวิเคราะห์จริง
            fig.add_trace(go.Scatter(
                x=test_df['Timestamp'], 
                y=test_df['ผล Level 1'], 
                mode='lines+markers',
                name='ผลการควบคุม Level 1',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=8)
            ))
            
            # วาดเส้นเกณฑ์ควบคุมตามเกณฑ์มาตรฐาน Westgard 
            fig.add_hline(y=mean_l1, line_color="green", line_width=2, annotation_text="Mean")
            fig.add_hline(y=mean_l1 + sd_l1, line_dash="dash", line_color="gray", annotation_text="+1SD")
            fig.add_hline(y=mean_l1 - sd_l1, line_dash="dash", line_color="gray", annotation_text="-1SD")
            fig.add_hline(y=mean_l1 + (2*sd_l1), line_dash="dash", line_color="orange", annotation_text="+2SD")
            fig.add_hline(y=mean_l1 - (2*sd_l1), line_dash="dash", line_color="orange", annotation_text="-2SD")
            fig.add_hline(y=mean_l1 + (3*sd_l1), line_dash="dash", line_color="red", line_width=1.5, annotation_text="+3SD")
            fig.add_hline(y=mean_l1 - (3*sd_l1), line_dash="dash", line_color="red", line_width=1.5, annotation_text="-3SD")
            
            fig.update_layout(
                title=f"Levey-Jennings Chart สำหรับ: {selected_test}",
                xaxis_title="วัน-เวลาบันทึกผล (Timestamp)",
                yaxis_title="ค่าผลการวิเคราะห์ (Value)",
                hovermode="x"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # แสดงตารางผลการประมวลผลกฎแล็บด้านล่าง
            st.subheader("📋 ตารางวิเคราะห์ค่าสถิติและเกณฑ์ควบคุมคุณภาพ")
            display_cols = ['Timestamp', 'สาขา', 'รายการทดสอบ', 'ผล Level 1', 'Z-Score L1', 'ผล Level 2', 'Z-Score L2', 'Westgard_Result']
            available_cols = [c for c in display_cols if c in test_df.columns]
            st.dataframe(test_df[available_cols], use_container_width=True)
        else:
            st.warning("ไม่พบข้อมูลบันทึกผลของรายการทดสอบนี้")
    else:
        st.warning("โครงสร้างตารางข้อมูลในแผ่นงานไม่ถูกต้องหรือยังไม่มีข้อมูลบันทึกเข้ามา")

except Exception as e:
    st.error(f"⚠️ เกิดปัญหาในการดึงและประมวลผลข้อมูล: {e}")

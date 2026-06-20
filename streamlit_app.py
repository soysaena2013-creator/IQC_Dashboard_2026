# ==========================================
# ข้อที่ 1: กราฟ Levey-Jennings (Real-time จาก Google Sheets แหล่งตรวจ 2 ระดับ)
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
                # ดึงค่าควบคุมของ Level 1
                mean_l1 = float(test_df.loc[0, 'Mean L1']) if 'Mean L1' in test_df.columns else 100
                sd_l1 = float(test_df.loc[0, 'SD L1']) if 'SD L1' in test_df.columns else 2
                
                # ดึงค่าควบคุมของ Level 2
                mean_l2 = float(test_df.loc[0, 'Mean L2']) if 'Mean L2' in test_df.columns else 200
                sd_l2 = float(test_df.loc[0, 'SD L2']) if 'SD L2' in test_df.columns else 4
                
                fig = go.Figure()
                
                # 🔵 1. พล็อตเส้นข้อมูลของ Level 1
                fig.add_trace(go.Scatter(
                    x=test_df['Timestamp'], 
                    y=test_df['ผล Level 1'], 
                    mode='lines+markers', 
                    name='ผล QC Level 1',
                    line=dict(color='#1f77b4', width=2),
                    marker=dict(size=8)
                ))
                
                # 🔴 2. พล็อตเส้นข้อมูลของ Level 2 เพิ่มเติมเข้ามาคู่กัน
                if 'ผล Level 2' in test_df.columns:
                    fig.add_trace(go.Scatter(
                        x=test_df['Timestamp'], 
                        y=test_df['ผล Level 2'], 
                        mode='lines+markers', 
                        name='ผล QC Level 2',
                        line=dict(color='#d62728', width=2),
                        marker=dict(size=8)
                    ))
                
                # --- วาดเส้นเกณฑ์ควบคุมมาตรฐานระดับชำนาญการ (อิงจาก Level 1 เป็นหลักบนกราฟนี้) ---
                fig.add_hline(y=mean_l1, line_color="green", annotation_text="Mean L1")
                fig.add_hline(y=mean_l1 + (2*sd_l1), line_dash="dash", line_color="orange", annotation_text="+2SD L1")
                fig.add_hline(y=mean_l1 - (2*sd_l1), line_dash="dash", line_color="orange", annotation_text="-2SD L1")
                fig.add_hline(y=mean_l1 + (3*sd_l1), line_dash="dash", line_color="red", annotation_text="+3SD L1")
                fig.add_hline(y=mean_l1 - (3*sd_l1), line_dash="dash", line_color="red", annotation_text="-3SD L1")
                
                fig.update_layout(
                    xaxis_title="วัน-เวลาบันทึกผล (Timestamp)", 
                    yaxis_title="ค่าผลการวิเคราะห์ (Value)",
                    hovermode="x"
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("กำลังรอข้อมูลบันทึกเข้าสู่ระบบ Google Sheets...")
    except Exception as e:
        st.error(f"ไม่สามารถเชื่อมต่อ Google Sheets ได้: {e}")

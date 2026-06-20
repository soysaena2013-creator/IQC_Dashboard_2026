# ส่วนของกราฟ Levey-Jennings ที่ปรับปรุงให้มีเส้น SD ครบครับ
    st.header("📈 กราฟ Levey-Jennings")

    def draw_lj_with_sd(data, col_name, title):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['ประทับเวลา'], y=data[col_name], mode='lines+markers', name=col_name))
        
        # คำนวณ Mean/SD จากข้อมูลในตาราง
        m, s = data[col_name].mean(), data[col_name].std()
        
        # เส้น Mean
        fig.add_hline(y=m, line_color="black", line_width=2, line_dash="solid", annotation_text="Mean")
        
        # เพิ่มเส้น SD +/- 1, 2, 3
        # 1SD (สีเทา), 2SD (สีส้ม), 3SD (สีแดง)
        colors = {1: "gray", 2: "orange", 3: "red"}
        for i in [1, 2, 3]:
            # เส้นบวก SD
            fig.add_hline(y=m+(i*s), line_dash="dash", line_color=colors[i], annotation_text=f"+{i}SD")
            # เส้นลบ SD
            fig.add_hline(y=m-(i*s), line_dash="dash", line_color=colors[i], annotation_text=f"-{i}SD")
            
        fig.update_layout(title=title, template="plotly_white", yaxis_title="Result")
        return fig

    # เรียกใช้ฟังก์ชันที่อัปเดตเส้น SD แล้ว
    st.plotly_chart(draw_lj_with_sd(display_df, 'ผล Level 1', 'Level 1'), use_container_width=True)
    st.plotly_chart(draw_lj_with_sd(display_df, 'ผล Level 2', 'Level 2'), use_container_width=True)

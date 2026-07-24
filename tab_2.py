import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
from generate_report_tab2 import generate_report

def go_to_step2():
    st.session_state.step = 2

def go_to_step1():
    st.session_state.form_values = {}
    st.session_state.step = 1

def render_tab2(df_information, species_table, target_col):
    if st.session_state.step == 1:
        col6, col7 = st.columns(2)
        with col6:
            st.subheader("Tuỳ chọn bộ lọc")
            None_option = pd.DataFrame({"common_character": [None], "kingdom": [None], "division": [None], "class_field": [None], "order": [None], 
                                                "family_group": [None], "family": [None], "genus": [None]})
            options = df_information[["common_character", "kingdom", "division", "class_field", "order", "family_group", "family", "genus"]]
            options = pd.concat([None_option, options], ignore_index= True)
            st.session_state.form_values["common_character"] = st.selectbox("Tên địa phương: ", options["common_character"].unique(), index = 0)
            st.session_state.form_values["kingdom"] = st.selectbox("Giới: ", options["kingdom"].unique(), index = 0)
            st.session_state.form_values["division"] = st.selectbox("Ngành: ", options["division"].unique(), index = 0)
            st.session_state.form_values["class_field"] = st.selectbox("Lớp: ", options["class_field"].unique(), index = 0)
            st.session_state.form_values["order"] = st.selectbox("Bộ: ", options["order"].unique(), index = 0)
            st.session_state.form_values["family_group"] = st.selectbox("Nhóm: ", options["family_group"].unique(), index = 0)
            st.session_state.form_values["family"] = st.selectbox("Họ: ", options["family"].unique(), index = 0)
            st.session_state.form_values["genus"] = st.selectbox("Chi: ", options["genus"].unique(), index = 0)
            st.session_state.form_values["loai_quy_hiem"] = st.selectbox("Loài quý hiếm: ", [None, "Có", "Không"], index = 0)
            if st.session_state.form_values["loai_quy_hiem"] == "Có":
                st.session_state.form_values["cac_danh_sach"] = st.multiselect("Các danh sách cụ thể: ", ["IUCN", "SDVN", "ND_84_2021", "ND_64_2019", "TT_35_2018"])
            st.button("Submit", on_click = go_to_step2)
        with col7:
            st.subheader("Thông tin các loài")
            st.metric(label = "Số lượng loài: ", value = len(species_table))
            st.session_state.selected_row_2 = st.dataframe(species_table, selection_mode='single-row',on_select='rerun', hide_index = True, key = 'df_tab2_1')
    
    if st.session_state.step == 2:
        filter_df = df_information.copy()
        filter_fields = ["common_character", "kingdom", "division", "class_field", "order", "family_group", "family", "genus"]
        for field in filter_fields:
            value = st.session_state.form_values[field]
            if value is not None:
                filter_df = filter_df[filter_df[field] == value]
        if st.session_state.form_values["loai_quy_hiem"] == "Có":
            if st.session_state.form_values["cac_danh_sach"]:
                for danh_sach in st.session_state.form_values["cac_danh_sach"]:
                    danh_sach = danh_sach.lower()
                    filter_df = filter_df[filter_df[danh_sach].notna()]
            else:
                filter_df = filter_df[filter_df[target_col].notna().any(axis = 1)]
        elif st.session_state.form_values["loai_quy_hiem"] == "Không":
            filter_df = filter_df[filter_df[target_col].isna().all(axis = 1)]
        
        col8, col9 = st.columns(2)
        with col8:
            st.subheader("Phân bố các loài:")
            map_data_2 = filter_df[(filter_df['lat'] != 0) & 
                                (filter_df['lng'] != 0)]
            st.pydeck_chart(
                pdk.Deck(
                    initial_view_state=pdk.ViewState(
                        latitude=8.6062, 
                        longitude=104.7244,
                        zoom=9
                    ),
                    layers=[
                        pdk.Layer(
                            "ScatterplotLayer",
                            data = map_data_2,
                            get_position='[lng, lat]',
                            get_color='[200, 30, 0, 160]',
                            get_radius=150,
                            pickable = True
                        )
                    ],
                    tooltip = {
                        "html": "<b>{common_character}</b><br/>sp_1: {sp_1}",
                        "style": {"color": "white"}
                    }
                ),
                use_container_width=True,
                height = 465,
                key = "map_tab2_3"
            )
        with col9:
            st.subheader("Số lượng loài đã lọc: ")
            col15, col16 = st.columns([16.5, 2])
            filter_df_table = filter_df[['common_character', 'sp_1','author','kingdom', 
                            'division', 'class_field', 'order', 'family_group', 
                            'family', 'genus', 'description', 'habit', 
                            'lifetime', 'habitat', 'distribution', 'iucn', 
                            'sdvn', 'nd_84_2021', 'nd_64_2019', 'tt_35_2018']].drop_duplicates()
            st.session_state.selected_row_2 = st.dataframe(filter_df_table, hide_index = True, selection_mode='single-row', on_select='rerun', key = 'df_tab2_2')
        
        col6, col7 = st.columns(2)
        with col6:
            st.subheader("Số lượng ghi nhận: ")
            max_year_2 = pd.Timestamp.now().year
            bar_data_2 = filter_df[(filter_df['collection_year'] >= (max_year_2 - 10)) & (filter_df['collection_year'] > 0)]
            bar_data_2 = bar_data_2.sort_values(by = 'collection_year', ascending = True)
            bar_data_2 = bar_data_2.groupby("collection_year").size().reset_index(name = 'count')
            fig_bar_2 = px.bar(bar_data_2, x = 'collection_year', y ='count')
            fig_bar_2.update_xaxes(
                tickmode="array",
                tickvals=bar_data_2["collection_year"],
                tickformat=".0f",  
                tickangle=-45,      
                title_text="Year")
            fig_bar_2.update_layout(
                plot_bgcolor="#2a003f",   
                paper_bgcolor="#0f001a"
            )
            st.plotly_chart(fig_bar_2, use_container_width=True, key = 'bar_tab2_4')
        with col7:
            st.subheader("Tỉ lệ nhóm loài: ")
            pie_data_2 = filter_df.copy()
            pie_data_2 = pie_data_2.groupby("family_group").size().reset_index(name = 'count')
            print(pie_data_2)
            fig_pie_2 = px.pie(pie_data_2, values='count', names='family_group')
            fig_pie_2.update_layout(
                plot_bgcolor="#1e1e1e",   
                paper_bgcolor="#121212"
            )
            st.plotly_chart(fig_pie_2, use_container_width=True, key = 'pie_tab2_5')
        with col15:
            st.metric(label = "",value = len(filter_df_table), label_visibility='collapsed')
        with col16:
            st.button("Reset", on_click=go_to_step1)
        if st.button("Báo cáo các loài"):
                report_2 = generate_report(filter_df_table, map_data_2, bar_data_2, pie_data_2)
                st.download_button(
                    label = "Tải báo cáo",
                    data = report_2,
                    file_name = f'Báo cáo loài theo bộ lọc.docx',
                    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        
        #Store filter_df_table in session state for tab3
        st.session_state.filter_df_table = filter_df_table
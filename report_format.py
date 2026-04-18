import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
from generate_report import generate_report

def display_form_url(base, path):
    full_url = "/".join([base, path])
    st.image(full_url)

def report_format(specific_specie_data_2, df_information):
    st.header(f"Báo cáo chi tiết {specific_specie_data_2['common_character']}")
    col8, col9 = st.columns(2)
    with col8:
        st.subheader("1. Thông tin chung về loài")
        with st.container(border = True):
            st.text(f"- Tên địa phương: {specific_specie_data_2['common_character']}")
            st.text(f"- Tên loài cấp 1: {specific_specie_data_2['sp_1']}")
            st.text(f"- Phân loại: {specific_specie_data_2['habit'] or 'Đang cập nhật'}")
            st.text(f"- Dạng sống: {specific_specie_data_2['lifetime'] or 'Đang cập nhật'}")
            st.text(f"- Tên tác giả: {specific_specie_data_2['author']}")
        st.subheader("2. Phân loại học")
        with st.container(border=True):
            st.text(f"- Giới: {specific_specie_data_2['kingdom']}")
            st.text(f"- Ngành: {specific_specie_data_2['division']}")
            st.text(f"- Lớp: {specific_specie_data_2['class_field'] }")
            st.text(f"- Bộ: {specific_specie_data_2['order']}")
            st.text(f"- Nhóm: {specific_specie_data_2['family_group']}")
            st.text(f"- Họ: {specific_specie_data_2['family']}")
            st.text(f"- Chi: {specific_specie_data_2['genus']}")
        st.subheader("3. Đặc điểm nhận dạng")
        with st.container(border = True):
            st.text(f"{specific_specie_data_2['description'] or 'Đang cập nhật'}")
    with col9:
        st.subheader("4. Tình trạng bảo tồn")
        with st.container(border = True):
            st.text(f"- Theo sách đỏ: {specific_specie_data_2['sdvn'] or 'Không'}")
            st.text(f"- IUCN: {specific_specie_data_2['sdvn'] or 'Không'}")
        st.subheader("5. Tình trạng quản lý bảo vệ")
        with st.container(border = True):    
            st.text(f"- Nghị định số 64/2019: {specific_specie_data_2['nd_64_2019'] or 'Không'}")
            st.text(f"- Nghị định số 84/2021: {specific_specie_data_2['nd_84_2021'] or 'Không'}")
            st.text(f"- Thông tư số 35/2018: {specific_specie_data_2['tt_35_2018'] or 'Không'}")
        st.subheader("6. Hình ảnh")
        image_data = df_information[['common_character', 'image', 'sp_1', 'genus']]
        image_data = image_data[((image_data['common_character'] == specific_specie_data_2['common_character']) | (specific_specie_data_2['common_character'] == "Đang cập nhật")) &
                                (image_data['genus'] == specific_specie_data_2['genus']) &
                                (image_data['sp_1'] == specific_specie_data_2['sp_1']) &
                                (image_data['image'].notna())]
        with st.container(border=True):
            col11, col12, col13 = st.columns(3)
            base = "https://muicamauapis.opengis.vn/media"
            with col11:
                if (len(image_data) >= 1):
                    display_form_url(base, image_data['image'].iloc[0])
                else:
                    st.warning("Đang cập nhật")
            with col12:
                if (len(image_data) >= 2):
                    display_form_url(base, image_data['image'].iloc[1])
            with col13:
                if (len(image_data) >= 3):
                    display_form_url(base, image_data['image'].iloc[2])
    st.markdown("---")
    col10, col14 = st.columns(2)
    with col10:  
        st.subheader("Lượng ghi nhận qua các năm")
        bar_data_3 = df_information[['collection_year', 'common_character', 'sp_1', 'genus']]
        max_year_3 = bar_data_3['collection_year'].max()
        bar_data_3 = bar_data_3[((bar_data_3['common_character'] == specific_specie_data_2['common_character']) | (specific_specie_data_2['common_character'] == "Đang cập nhật")) &
                                ((bar_data_3['sp_1'] == specific_specie_data_2['sp_1']) | (specific_specie_data_2['sp_1'] == "Đang cập nhật")) &
                                (bar_data_3['genus'] == specific_specie_data_2['genus']) &
                                (bar_data_3['collection_year'] > 0) &
                                (bar_data_3['collection_year'] >= (max_year_3 - 10)) ]
        bar_data_3 = bar_data_3.sort_values(by = 'collection_year', ascending = True)
        bar_data_3 = bar_data_3.groupby("collection_year").size().reset_index(name = 'count')
        fig_bar_3 = px.bar(bar_data_3, x = 'collection_year', y ='count')
        fig_bar_3.update_xaxes(
            tickmode="array",
            tickvals= bar_data_3["collection_year"],
            tickformat=".0f",  
            tickangle=-45,      
            title_text="Year")
        fig_bar_3.update_layout(
            plot_bgcolor="#2a003f",   
            paper_bgcolor="#0f001a"
        )
        st.plotly_chart(fig_bar_3, use_container_width=True, key= 'bar_tab3_2')
    with col14:
        st.subheader("Bảng phân bố loài")
        map_data_4 = df_information[['common_character', 'sp_1','genus', 'lat', 'lng', 'number', 'project', 
                                     'botreccat', 'collector', 'add_collector', 'collection_year',
                                     'major_area', 'minor_area', 'gazetteer', 'place', 'country']]
        map_data_4 = map_data_4[((map_data_4['common_character'] == specific_specie_data_2['common_character']) | (specific_specie_data_2['common_character'] == "Đang cập nhật")) &
                            ((map_data_4['sp_1'] == specific_specie_data_2['sp_1']) | (specific_specie_data_2['sp_1'] == "Đang cập nhật")) &
                            (map_data_4['genus'] == specific_specie_data_2['genus']) &
                            (map_data_4['lat'] != 0) &
                            (map_data_4['lng'] != 0)]
        view_state = pdk.ViewState(latitude=8.6062, longitude=104.7244, zoom=11)
        points = pdk.Layer("ScatterplotLayer", data=map_data_4,
                            get_position='[lng, lat]',
                            get_color="[255, 75, 75]",
                            get_radius=150,
                            pickable = True, 
                            id = "coordinate")
        map_display = pdk.Deck(initial_view_state = view_state, layers = [points], 
                        tooltip = {
                            "text": "Tên địa phương: {common_character}\n Sp_1: {sp_1}\n Số hiệu ghi nhận: {number}",
                            "style": {"color": "white"}
                        })
        selected_object = st.pydeck_chart(map_display, use_container_width=True, height=450, key='map_tab3_1', selection_mode = 'single-object', on_select= 'rerun')
    st.markdown("---")
    st.subheader('Thông tin ghi nhận')
    if selected_object['selection']['indices']:
        df_collection = pd.DataFrame([selected_object['selection']['objects']['coordinate'][0]])
        df_collection = df_collection[['number', 'project', 'botreccat', 'collector', 'add_collector', 'collection_year', 'major_area', 'minor_area', 'gazetteer', 'place', 'country', 'lat', 'lng']]
        st.dataframe(df_collection, hide_index=True)
    else:
        df_collection = map_data_4[['number', 'project', 'botreccat', 'collector', 'add_collector', 'collection_year', 'major_area', 'minor_area', 'gazetteer', 'place', 'country', 'lat', 'lng']]
        st.dataframe(df_collection, hide_index=True)
    if st.button("Xuất báo cáo"):
        report = generate_report(specific_specie_data_2, map_data_4, bar_data_3, image_data)
        st.download_button(
            label = "Tải báo cáo",
            data = report,
            file_name = f'Báo cáo {specific_specie_data_2["common_character"]}.docx',
            mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

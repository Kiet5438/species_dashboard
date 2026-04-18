import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import pydeck as pdk

from generate_report import generate_report
from generate_report_2 import generate_report_2
from report_format import report_format

#caching resource
@st.cache_resource
def init_connect():
    return psycopg2.connect(**st.secrets["postgres"])
#caching data
@st.cache_data
def execute_query(query):
    with init_connect() as conn:
        return pd.read_sql(query, conn)
##Lấy thông tin từ database
query_information = """
    SELECT ars.common_character, ars.sp_1, ars.author,
        atxn.kingdom, atxn.division, atxn.class_field,
        atxn.order, atxn.family_group, atxn.family,
        atxn.genus, am.lat, am.lng, ac.collection_year,
        ars.description, ars.habit, ars.lifetime, ars.habitat, 
        ars.distribution, ars.iucn, ars.iucn_version, ars.sdvn,
        ars.nd_84_2021, ars.nd_64_2019, ars.tt_35_2018, ai.image,
        ac.number, ac.project, ac.botreccat, ac.collector, ac.add_collector,
        ap.major_area, ap.minor_area, ap.gazetteer, ap.place, ap.country
    FROM apis_recordspecies ars
    LEFT JOIN apis_taxonomy atxn
    ON ars.taxonomy_id = atxn.id
    LEFT JOIN apis_map am
    ON am.record_species_id = ars.id
    LEFT JOIN apis_collection ac
    ON ac.record_species_id = ars.id
    LEFT JOIN apis_image ai
    ON ai.record_species_id = ars.id
    LEFT JOIN apis_position ap
    ON ap.id = ars.id;
"""
query_pie_chart = """
    SELECT family_group, count(ars.id) as quant
    FROM apis_recordspecies ars
    JOIN apis_map am
    ON ars.id = am.record_species_id
    JOIN apis_taxonomy atxn
    ON ars.taxonomy_id = atxn.id
    GROUP BY family_group
"""
query_bar_chart_for_all = """
    SELECT collection_year, count(record_species_id) as quant
    FROM apis_collection
    WHERE collection_year != 0
    GROUP BY collection_year
	HAVING EXTRACT(YEAR from now()) - collection_year <= 10
    ORDER BY collection_year ASC;
""" 
df_pie_chart = execute_query(query_pie_chart)
df_information = execute_query(query_information)
df_bar_chart_for_all = execute_query(query_bar_chart_for_all)
## Set up cho dashboard
st.set_page_config(page_title="Dashboard", layout="wide")
tab1, tab2, tab3 = st.tabs(["Khái quát", "Bộ lọc", "Chi tiết"])
## Khai báo các biến session state
if "selected_row_2_2" not in st.session_state:
    st.session_state.selected_row_2_2 = {"selection": {"rows": [], "columns": []}}
if "selected_row_2" not in st.session_state:
    st.session_state.selected_row_2 = {"selection": {"rows": [], "columns": []}}
if "form_values" not in st.session_state:
    st.session_state.form_values = {}
if "step" not in st.session_state:
    st.session_state.step = 1

## Khai báo callback và các hàm
def go_to_step2():
    st.session_state.step = 2

def go_to_step1():
    st.session_state.form_value = {}
    st.session_state.step = 1

## Làm sạch dữ liệu
target_col = ['sdvn', 'iucn', 'nd_64_2019', 'nd_84_2021', 'tt_35_2018']
df_information[target_col] = df_information[target_col].replace(0, None)
df_information[target_col] = df_information[target_col].replace("0", None)
df_information[target_col] = df_information[target_col].replace('', None)

target_col_2 = ['common_character', 'sp_1']
df_information[target_col_2] = df_information[target_col_2].replace("0", "Đang cập nhật")
df_information[target_col_2] = df_information[target_col_2].replace(0, "Đang cập nhật")
df_information[target_col_2] = df_information[target_col_2].replace("", "Đang cập nhật")
## Các dữ liệu dùng chung
species_data = df_information[['common_character', 'sp_1','author','kingdom', 
                                'division', 'class_field', 'order', 'family_group', 
                                'family', 'genus', 'description', 'habit', 
                                'lifetime', 'habitat', 'distribution', 'iucn', 
                                'iucn_version', 'sdvn', 'nd_84_2021', 'nd_64_2019', 'tt_35_2018']].drop_duplicates()
##Tab1
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Thông tin các loài")
        species_table = species_data[['common_character', 'sp_1','kingdom', 
                                        'division', 'class_field', 'order', 
                                        'family_group', 'family', 'genus']]
        st.metric(label = "Số lượng loài ghi nhận: ", value = len(species_table))
        selected_row = st.dataframe(species_table, hide_index = True, selection_mode='single-row', on_select='rerun', key = 'df_tab1_1')
        if selected_row['selection']['rows']:
            selected_index = selected_row['selection']['rows'][0]
            specific_specie_data = species_data.iloc[selected_index]
    with col2:
        st.subheader("Phân bố loài")
        if selected_row['selection']['rows']:
            map_data = df_information[['common_character', 'sp_1', 'lat', 'lng', 'genus']]
            map_data = map_data[((map_data['common_character'] == specific_specie_data['common_character']) | (specific_specie_data['common_character'] == "Đang cập nhật")) &
                                ((map_data['sp_1'] == specific_specie_data['sp_1']) | (specific_specie_data['sp_1'] == "Đang cập nhật")) &
                                (map_data['genus'] == specific_specie_data['genus']) &
                                (map_data['lat'] != 0) &
                                (map_data['lng'] != 0)]
            st.pydeck_chart(
                pdk.Deck(
                    initial_view_state=pdk.ViewState(
                        latitude=8.6062, 
                        longitude=104.7244,
                        zoom = 10
                    ),
                    layers=[
                        pdk.Layer(
                            "ScatterplotLayer",
                            data=map_data,
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
                height=490,
                key='map_tab1_2'
            )
        else:
            map_data_3 = df_information[['common_character', 'sp_1', 'lat', 'lng']]
            map_data_3 = map_data_3[(map_data_3['lat'] != 0) & (map_data_3['lng'] != 0)]
            st.pydeck_chart(
                pdk.Deck(
                    initial_view_state=pdk.ViewState(
                        latitude = 8.6062,
                        longitude = 104.7244,
                        zoom = 10
                    ),
                    layers = [
                        pdk.Layer(
                            "ScatterplotLayer",
                            data=map_data_3,
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
                height = 490,
                key="map_tab1_3"
            )

    col3, col4, col5 = st.columns(3)
    with col3:
        st.subheader("Tỉ lệ nhóm loài")
        fig_pie = px.pie(df_pie_chart, values='quant', names='family_group')
        fig_pie.update_layout(
            plot_bgcolor="#1e1e1e",   
            paper_bgcolor="#121212"
        )
        st.plotly_chart(fig_pie, use_container_width=True, key = 'pie_tab1_4')
    #Biểu đồ cột
    with col4:
        st.subheader("Lượng ghi nhận các loài")
        fig_all_bar = px.bar(df_bar_chart_for_all, x='collection_year', y='quant')
        fig_all_bar.update_xaxes(
            tickmode = "array",
            tickvals = df_bar_chart_for_all['collection_year'],
            tickformat = ".0f",
            tickangle=-45,      
            title_text="Year"
        )
        fig_all_bar.update_layout(
            plot_bgcolor="#0d1b2a",   
            paper_bgcolor="#000814"
        )
        st.plotly_chart(fig_all_bar, use_container_width=True, key = 'bar_tab1_5')
    with col5:
        st.subheader("Lượng ghi nhận loài được chọn")
        if selected_row['selection']['rows']:
            bar_data = df_information[['collection_year', 'common_character', 'sp_1', 'genus']]
            max_year = bar_data['collection_year'].max()
            bar_data = bar_data[((bar_data['common_character'] == specific_specie_data['common_character']) | (specific_specie_data['common_character'] == "Đang cập nhật")) &
                                ((bar_data['sp_1'] == specific_specie_data['sp_1']) | (specific_specie_data['sp_1'] == "Đang cập nhật")) &
                                (bar_data['genus'] == specific_specie_data['genus']) &
                                (bar_data['collection_year'] > 0) &
                                (bar_data['collection_year'] >= (max_year - 10)) ]
            bar_data = bar_data.sort_values(by = 'collection_year', ascending = True)
            bar_data = bar_data.groupby("collection_year").size().reset_index(name = 'count')
            fig_bar = px.bar(bar_data, x = 'collection_year', y ='count')
            fig_bar.update_xaxes(
                tickmode="array",
                tickvals=bar_data["collection_year"],
                tickformat=".0f",  
                tickangle=-45,      
                title_text="Year")
            fig_bar.update_layout(
                plot_bgcolor="#2a003f",   
                paper_bgcolor="#0f001a"
            )
            st.plotly_chart(fig_bar, use_container_width=True, key = 'bar_tab1_6')
        else:
            st.write("Hãy chọn một loài ở bảng")

with tab2:
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
            max_year_2 = filter_df['collection_year'].max()
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
                report_2 = generate_report_2(filter_df_table, map_data_2, bar_data_2, pie_data_2)
                st.download_button(
                    label = "Tải báo cáo",
                    data = report_2,
                    file_name = f'Báo cáo loài theo bộ lọc.docx',
                    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

with tab3:
    if st.session_state.selected_row_2['selection']['rows'] and st.session_state.step == 1:
        selected_index_2 = st.session_state.selected_row_2['selection']['rows'][0]
        specific_specie_data_2 = species_data.iloc[selected_index_2]
        report_format(specific_specie_data_2, df_information)
    elif st.session_state.selected_row_2['selection']['rows'] and st.session_state.step == 2:
        selected_index_2 = st.session_state.selected_row_2['selection']['rows'][0]
        specific_specie_data_2 = filter_df_table.iloc[selected_index_2]
        report_format(specific_specie_data_2, df_information)  
    else:
        selected_index = None  
        st.write("Hãy chọn 1 loài ở tab 2 để biết thông tin chi tiết")

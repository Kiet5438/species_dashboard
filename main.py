import streamlit as st
import psycopg2
import pandas as pd

from tab_1 import render_tab1
from tab_2 import render_tab2
from tab_3 import render_tab3

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
        ars.nd_84_2021, ars.nd_64_2019, ars.tt_35_2018,
        ac.number, ac.project, ac.botreccat, ac.collector, ac.add_collector,
        ap.major_area, ap.minor_area, ap.gazetteer, ap.place, ap.country
    FROM apis_recordspecies ars
    LEFT JOIN apis_taxonomy atxn
    ON ars.taxonomy_id = atxn.id
    LEFT JOIN apis_map am
    ON am.record_species_id = ars.id
    LEFT JOIN apis_collection ac
    ON ac.record_species_id = ars.id
    LEFT JOIN apis_position ap
    ON ap.id = ars.id;
"""
query_images = """
    SELECT ars.common_character, ars.sp_1, atxn.genus, ai.image
    FROM apis_image ai
    JOIN apis_recordspecies ars
    ON ai.record_species_id = ars.id
    JOIN apis_taxonomy atxn
    ON ars.taxonomy_id = atxn.id;
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
df_images = execute_query(query_images)
df_bar_chart_for_all = execute_query(query_bar_chart_for_all)
## Set up cho dashboard
st.set_page_config(page_title="Dashboard", layout="wide")
tab1, tab2, tab3 = st.tabs(["Khái quát", "Bộ lọc", "Chi tiết"])
## Khai báo các biến session state
if "selected_row_2" not in st.session_state:
    st.session_state.selected_row_2 = {"selection": {"rows": [], "columns": []}}
if "form_values" not in st.session_state:
    st.session_state.form_values = {}
if "step" not in st.session_state:
    st.session_state.step = 1
if "filter_df_table" not in st.session_state:
    st.session_state.filter_df_table = None

## Khai báo các biến session state
target_col = ['sdvn', 'iucn', 'nd_64_2019', 'nd_84_2021', 'tt_35_2018']
df_information[target_col] = df_information[target_col].replace(0, None)
df_information[target_col] = df_information[target_col].replace("0", None)
df_information[target_col] = df_information[target_col].replace('', None)

target_col_2 = ['common_character', 'sp_1']
df_information[target_col_2] = df_information[target_col_2].replace("0", "Đang cập nhật")
df_information[target_col_2] = df_information[target_col_2].replace(0, "Đang cập nhật")
df_information[target_col_2] = df_information[target_col_2].replace("", "Đang cập nhật")
df_images[target_col_2] = df_images[target_col_2].replace("0", "Đang cập nhật")
df_images[target_col_2] = df_images[target_col_2].replace(0, "Đang cập nhật")
df_images[target_col_2] = df_images[target_col_2].replace("", "Đang cập nhật")
## Các dữ liệu dùng chung
species_data = df_information[['common_character', 'sp_1','author','kingdom', 
                                'division', 'class_field', 'order', 'family_group', 
                                'family', 'genus', 'description', 'habit', 
                                'lifetime', 'habitat', 'distribution', 'iucn', 
                                'iucn_version', 'sdvn', 'nd_84_2021', 'nd_64_2019', 'tt_35_2018']].drop_duplicates()
species_table = species_data[['common_character', 'sp_1','kingdom', 
                                'division', 'class_field', 'order', 
                                'family_group', 'family', 'genus']]
##Tab1
with tab1:
    render_tab1(df_information, df_pie_chart, df_bar_chart_for_all, species_data, species_table)

with tab2:
    render_tab2(df_information, species_table, target_col)

with tab3:
    if st.session_state.selected_row_2['selection']['rows'] and st.session_state.step == 1:
        selected_index_2 = st.session_state.selected_row_2['selection']['rows'][0]
        specific_specie_data_2 = species_data.iloc[selected_index_2]
        render_tab3(specific_specie_data_2, df_information, df_images)
    elif st.session_state.selected_row_2['selection']['rows'] and st.session_state.step == 2:
        selected_index_2 = st.session_state.selected_row_2['selection']['rows'][0]
        specific_specie_data_2 = st.session_state.filter_df_table.iloc[selected_index_2]
        render_tab3(specific_specie_data_2, df_information, df_images)
    else:
        selected_index = None  
        st.write("Hãy chọn 1 loài ở tab 2 để biết thông tin chi tiết")
import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk

def render_tab1(df_information, df_pie_chart, df_bar_chart_for_all, species_data, species_table):
    #Màu sắc cho tối đa 5 loài - màu rõ ràng để dễ quan sát
    colors = ['#FF0000', '#0066FF', '#00CC00', '#FF9900', '#9933FF']
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Thông tin các loài")
        st.metric(label = "Số lượng loài ghi nhận: ", value = len(species_table))
        selected_row = st.dataframe(species_table, hide_index = True, selection_mode='multi-row', on_select='rerun', key = 'df_tab1_1')
        
        selected_species = []
        if selected_row['selection']['rows']:
            #Giới hạn tối đa 5 loài
            selected_indices = selected_row['selection']['rows'][:5]
            if len(selected_row['selection']['rows']) > 5:
                st.warning("Chỉ hiển thị 5 loài đầu tiên được chọn")
            for idx in selected_indices:
                selected_species.append(species_data.iloc[idx])
    with col2:
        st.subheader("Phân bố loài")
        if selected_species:
            #Tạo layers cho từng loài với màu khác nhau
            layers = []
            legend_html = "<div style='position: absolute; top: 10px; right: 10px; background: white; padding: 10px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.3); z-index: 1000;'>"
            
            for i, specie in enumerate(selected_species):
                map_data = df_information[['common_character', 'sp_1', 'lat', 'lng', 'genus']]
                map_data = map_data[((map_data['common_character'] == specie['common_character']) | (specie['common_character'] == "Đang cập nhật")) &
                                    ((map_data['sp_1'] == specie['sp_1']) | (specie['sp_1'] == "Đang cập nhật")) &
                                    (map_data['genus'] == specie['genus']) &
                                    (map_data['lat'] != 0) &
                                    (map_data['lng'] != 0)]
                
                if not map_data.empty:
                    #Chuyển màu hex sang RGB
                    hex_color = colors[i].lstrip('#')
                    rgb = [int(hex_color[j:j+2], 16) for j in (0, 2, 4)]
                    
                    layers.append(
                        pdk.Layer(
                            "ScatterplotLayer",
                            data=map_data,
                            get_position='[lng, lat]',
                            get_color=rgb + [160],
                            get_radius=150,
                            pickable=True,
                            id=f"species_{i}"
                        )
                    )
                    
                    #Thêm vào legend
                    legend_html += f"<div style='margin: 5px 0;'><span style='display: inline-block; width: 15px; height: 15px; background-color: {colors[i]}; margin-right: 5px;'></span>{specie['common_character']}</div>"
            
            legend_html += "</div>"
            
            st.pydeck_chart(
                pdk.Deck(
                    initial_view_state=pdk.ViewState(
                        latitude=8.6062, 
                        longitude=104.7244,
                        zoom=10
                    ),
                    layers=layers,
                    tooltip={
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

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Tỉ lệ nhóm loài")
        if selected_species:
            #Lọc theo các loài được chọn
            selected_family_groups = [sp['family_group'] for sp in selected_species]
            filtered_pie_data = df_pie_chart[df_pie_chart['family_group'].isin(selected_family_groups)]
            fig_pie = px.pie(filtered_pie_data, values='quant', names='family_group')
        else:
            fig_pie = px.pie(df_pie_chart, values='quant', names='family_group')
        
        fig_pie.update_layout(
            plot_bgcolor="#1e1e1e",   
            paper_bgcolor="#121212"
        )
        st.plotly_chart(fig_pie, use_container_width=True, key = 'pie_tab1_4')
    with col4:
        st.subheader("Lượng ghi nhận loài được chọn")
        if selected_species:
            #Tạo dữ liệu cho biểu đồ cột nhiều loài
            all_bar_data = []
            for specie in selected_species:
                bar_data = df_information[['collection_year', 'common_character', 'sp_1', 'genus']]
                max_year = pd.Timestamp.now().year
                bar_data = bar_data[((bar_data['common_character'] == specie['common_character']) | (specie['common_character'] == "Đang cập nhật")) &
                                    ((bar_data['sp_1'] == specie['sp_1']) | (specie['sp_1'] == "Đang cập nhật")) &
                                    (bar_data['genus'] == specie['genus']) &
                                    (bar_data['collection_year'] > 0) &
                                    (bar_data['collection_year'] >= (max_year - 10))]
                bar_data = bar_data.sort_values(by='collection_year', ascending=True)
                bar_data = bar_data.groupby("collection_year").size().reset_index(name='count')
                bar_data['species'] = specie['common_character']
                all_bar_data.append(bar_data)
            
            combined_bar_data = pd.concat(all_bar_data, ignore_index=True)
            fig_bar = px.bar(combined_bar_data, x='collection_year', y='count', color='species',
                            color_discrete_sequence=colors[:len(selected_species)])
            fig_bar.update_xaxes(
                tickmode="array",
                tickvals=combined_bar_data["collection_year"].unique(),
                tickformat=".0f",
                tickangle=-45,
                title_text="Year")
            fig_bar.update_layout(
                plot_bgcolor="#2a003f",
                paper_bgcolor="#0f001a",
                barmode='stack'
            )
            st.plotly_chart(fig_bar, use_container_width=True, key='bar_tab1_6')
        else:
            #Hiển thị tổng số lượng tất cả các loài khi không có loài nào được chọn
            fig_all_bar = px.bar(df_bar_chart_for_all, x='collection_year', y='quant')
            fig_all_bar.update_xaxes(
                tickmode = "array",
                tickvals = df_bar_chart_for_all['collection_year'],
                tickformat = ".0f",
                tickangle=-45,      
                title_text="Year"
            )
            fig_all_bar.update_layout(
                plot_bgcolor="#2a003f",   
                paper_bgcolor="#0f001a"
            )
            st.plotly_chart(fig_all_bar, use_container_width=True, key = 'bar_tab1_5')
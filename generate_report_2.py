import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, box
import contextily as ctx
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from io import BytesIO
import matplotlib.pyplot as plt
import os

def generate_report_2(filter_df_table:pd.DataFrame, map_data_2:pd.DataFrame, bar_data_2:pd.DataFrame, pie_data_2:pd.DataFrame):
    doc = DocxTemplate("Filter_species_template_ver2.docx")
    species = filter_df_table[['common_character', 'kingdom', 'division', 'class_field', 'order', 'family_group', 
                            'family', 'genus', 'iucn', 'sdvn', 'nd_84_2021', 'nd_64_2019', 'tt_35_2018']].to_dict("records")
    image_files = []
    with st.status("Đang tạo báo cáo...") as status2:
        status2.write("Tạo bản đồ...")
        if not map_data_2.empty:
            points_2 = gpd.GeoDataFrame(
                geometry=[Point(loc['lng'], loc['lat']) for _,loc in map_data_2.iterrows()],
                crs = "EPSG:4326").to_crs(epsg = 3857)
            buffer_for_points = 5000
            minx, miny, maxx, maxy = points_2.total_bounds
            #với min thì trừ đi buffer, max thì cộng buffer, làm như vậy để các point không bị cắt
            bbox = [minx - buffer_for_points, maxx + buffer_for_points, miny - buffer_for_points, maxy + buffer_for_points]
            #tạo nền để plot
            figure, axes = plt.subplots(figsize=(10, 10))
            points_2.plot(ax=axes, color='red', markersize=100)
            #đặt limit của x và y cho các trục
            axes.set_xlim(bbox[0], bbox[1])
            axes.set_ylim(bbox[2], bbox[3])
            #lấy nền map của OSM
            ctx.add_basemap(axes, source=ctx.providers.OpenStreetMap.Mapnik)
            axes.set_axis_off()
            plt.tight_layout()
            plt.savefig("Locations_species.png", dpi=300, bbox_inches='tight', pad_inches=0)
            image_files.append("Locations_species.png")
            locations_species = InlineImage(doc, "Locations_species.png", width = Mm(100),height = Mm(100))
            plt.close()
            #set buffer cho map tổng quan
            buffer_for_polygon = 50000
            figure, axes = plt.subplots(figsize = (10, 10))
            zoom_area_polygon = gpd.GeoDataFrame(
                geometry=[box(bbox[0], bbox[2], bbox[1], bbox[3])],
                crs="EPSG:3857"
            )
            zoom_area_polygon.plot(ax = axes, edgecolor= 'red', facecolor = 'None', linewidth= 3)
            axes.set_xlim(bbox[0] - buffer_for_polygon, bbox[1] + buffer_for_polygon)
            axes.set_ylim(bbox[2] - buffer_for_polygon, bbox[3] + buffer_for_polygon)
            ctx.add_basemap(axes, source = ctx.providers.OpenStreetMap.Mapnik)
            axes.set_axis_off()
            plt.tight_layout()
            plt.savefig("General_location.png", dpi = 300, bbox_inches = 'tight', pad_inches = 0)
            image_files.append("General_location.png")
            general_location = InlineImage(doc, "General_location.png", width = Mm(100), height = Mm(100))
            plt.close()
        else:
            locations_species = None
            general_location = None
        
        status2.write("Tạo biểu đồ cột...")
        if not bar_data_2.empty:
            year = [int(data["collection_year"]) for _,data in bar_data_2.iterrows()]
            count = [data["count"] for _,data in bar_data_2.iterrows()]
            plt.figure(figsize = (6, 6))
            plt.bar(year, count, color = 'skyblue')
            plt.xticks(ticks=year, labels=year)
            plt.tight_layout()
            plt.savefig("Quantity_through_years.png", dpi=300, transparent = True)
            image_files.append("Quantity_through_years.png")
            quantity_through_years = InlineImage(doc, "Quantity_through_years.png", width=Mm(100), height= Mm(100))
            plt.close()
        else:
            quantity_through_years = None
        
        status2.write("Tạo biểu đồ tròn...")
        if not pie_data_2.empty:
            labels = [data["family_group"] for _,data in pie_data_2.iterrows()]
            count = [data["count"] for _,data in pie_data_2.iterrows()]
            plt.figure(figsize = (6, 6))
            plt.pie(count, labels = labels, autopct= '%.1f%%', startangle=140)
            plt.tight_layout()
            plt.savefig("Species_pie_chart.png", dpi = 300, transparent = True)
            image_files.append("Species_pie_chart.png")
            species_pie_chart = InlineImage(doc, "Species_pie_chart.png", width=Mm(100), height= Mm(100))
        else:
            species_pie_chart = None

        status2.write("Tạo báo cáo...")
        context = {
            "species":species,
            "General_location": general_location, 
            "Locations_species": locations_species,
            "Quantity_through_years": quantity_through_years,
            "Species_pie_chart": species_pie_chart
        }
        doc.render(context)
        bio = BytesIO()
        doc.save(bio)
        bio.seek(0)
        status2.write("Xóa các file tạm...")
        for file_path in image_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Failed to delete: {e}")
        status2.write("Báo cáo đã được tạo!")
    return bio.getvalue()

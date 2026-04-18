import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, box
import contextily as ctx
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from io import BytesIO
import requests
from PIL import Image
from requests.exceptions import ChunkedEncodingError, ConnectionError
import matplotlib.pyplot as plt
import os

def generate_report(specific_specie_data_2:pd.Series, map_data_4:pd.DataFrame, bar_data_3:pd.DataFrame, image_data:pd.DataFrame):
    doc = DocxTemplate("General_inf_template.docx")
    specie_data = specific_specie_data_2.to_dict()
    image_files = []
    with st.status("Đang tạo báo cáo...", expanded=True) as status:
        status.write("Tạo bản đồ và các điểm...")
        points = gpd.GeoDataFrame(
                                geometry=[Point(loc['lng'], loc['lat']) for _,loc in map_data_4.iterrows()], 
                                crs = "EPSG:4326").to_crs(epsg = 3857)
        if not points.empty:
            buffer_for_points = 5000
            minx, miny, maxx, maxy = points.total_bounds
            #với min thì trừ đi buffer, max thì cộng buffer, làm như vậy để các point không bị cắt
            bbox = [minx - buffer_for_points, maxx + buffer_for_points, miny - buffer_for_points, maxy + buffer_for_points]
            #tạo nền để plot
            figure, axes = plt.subplots(figsize=(10, 10))
            points.plot(ax=axes, color='red', markersize=200)
            #đặt limit của x và y cho các trục
            axes.set_xlim(bbox[0], bbox[1])
            axes.set_ylim(bbox[2], bbox[3])
            #lấy nền map của OSM
            ctx.add_basemap(axes, source=ctx.providers.OpenStreetMap.Mapnik)
            axes.set_axis_off()
            plt.tight_layout()
            plt.savefig("Locations.png", dpi=300, bbox_inches='tight', pad_inches=0)
            image_files.append("Locations.png")
            locations = InlineImage(doc, "Locations.png", width = Mm(100),height = Mm(100))
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
            locations = None
            general_location = None
        
        status.write("Biểu đồ cột...")
        if not bar_data_3.empty:
            year = [int(data["collection_year"]) for _,data in bar_data_3.iterrows()]
            count = [data["count"] for _,data in bar_data_3.iterrows()]
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

        status.write("Hình ảnh loài...")
        base = "https://muicamauapis.opengis.vn/media"
        images = []
        for i in range(4):
            if i < len(image_data):
                image_path = image_data['image'].iloc[i]
                url = f"{base}/{image_path}"
                try: 
                    response = requests.get(url, timeout=30)
                    image_file = BytesIO(response.content)
                    with Image.open(image_file) as im:
                        clean_path = f"anh_{i}.png"
                        im.convert("RGB").save(clean_path, format="PNG")
                    images.append(InlineImage(doc, clean_path, width= Mm(60), height=Mm(60)))
                    image_files.append(clean_path)
                except (ChunkedEncodingError, ConnectionError, requests.RequestException) as e:
                    print("Lỗi kết nối")
                    images.append('')
                except Exception as e:
                    images.append('')
            else:
                images.append('')

        status.write("Tạo báo cáo...")
        context = {
            'spc':specie_data,
            "general_location": general_location, 
            "locations": locations,
            "quantity_through_years": quantity_through_years,
            "image0":images[0], "image1": images[1], "image2": images[2], "image3": images[3]
        }
        doc.render(context)
        bio = BytesIO()
        doc.save(bio)
        bio.seek(0)
        status.write("Xóa các file tạm...")
        for file_path in image_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Failed to delete: {e}")
        status.write("Báo cáo đã được tạo!")
    return bio.getvalue()

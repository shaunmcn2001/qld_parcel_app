import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from parcel_query import query_lotplans
import tempfile
import os

st.set_page_config(layout="wide")
st.title("QLD LotPlan Parcel Search")

# Sidebar input
st.sidebar.header("Enter Lot/Plan numbers")
lot_input = st.sidebar.text_area("LotPlan list (comma or newline)", height=200)
lotplans = [lp.strip().replace("/", "").upper() for lp in lot_input.replace(",", "\n").splitlines() if lp.strip()]

if st.sidebar.button("Search"):
    if not lotplans:
        st.sidebar.warning("Enter at least one LotPlan.")
    else:
        gdf = query_lotplans(lotplans)
        if gdf is None or gdf.empty:
            st.error("❌ No matching parcels found.")
        else:
            st.success(f"✅ Found {len(gdf)} matching parcels.")

            # Center map
            center = gdf.geometry.unary_union.centroid.coords[:][0][::-1]
            m = folium.Map(location=center, zoom_start=14)

            # Add parcels
            for i, row in gdf.iterrows():
                folium.GeoJson(row.geometry.__geo_interface__,
                               name=row["lotplan"],
                               tooltip=row["lotplan"],
                               popup=f"{row['lotplan']}").add_to(m)

            st_data = st_folium(m, width=1000, height=600)

            # Export section
            st.sidebar.subheader("Export Options")
            export_format = st.sidebar.selectbox("Format", ["GeoJSON", "Shapefile"])
            if st.sidebar.button("Export"):
                with tempfile.TemporaryDirectory() as tmpdir:
                    path = os.path.join(tmpdir, f"export.{export_format.lower()}")
                    if export_format == "GeoJSON":
                        gdf.to_file(path, driver="GeoJSON")
                    elif export_format == "Shapefile":
                        gdf.to_file(path, driver="ESRI Shapefile")
                    with open(path, "rb") as f:
                        st.sidebar.download_button("Download Export", f, file_name=os.path.basename(path))

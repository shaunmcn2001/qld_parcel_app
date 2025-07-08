import requests
import geopandas as gpd
from shapely.geometry import shape

def query_lotplan(lotplan):
    url = "https://spatial-gis.information.qld.gov.au/arcgis/rest/services/PlanningCadastre/LandParcelPropertyFramework/MapServer/3/query"
    params = {
        "where": f"lotplan='{lotplan}'",
        "outFields": "*",
        "returnGeometry": "true",
        "f": "geojson"
    }

    r = requests.get(url, params=params)
    if r.status_code == 200 and r.json().get("features"):
        geojson = r.json()
        features = geojson["features"]
        gdf = gpd.GeoDataFrame.from_features(features)
        gdf["lotplan"] = lotplan
        return gdf
    else:
        return None

def query_lotplans(lotplans):
    all_results = []
    for lp in lotplans:
        result = query_lotplan(lp)
        if result is not None:
            all_results.append(result)
    if all_results:
        return gpd.GeoDataFrame(pd.concat(all_results, ignore_index=True))
    return None

import h3
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon

def generate_h3_grid(center_point, radius_m, resolution=9):
    lat, lng = center_point
    center_hex = h3.latlng_to_cell(lat, lng, resolution)
    # Radiusu dinamik olaraq hex halqalarına çeviririk
    ring_count = max(1, int(radius_m / 150)) 
    k_rings = h3.grid_disk(center_hex, ring_count)
    
    hex_data = []
    for h in k_rings:
        boundary = h3.cell_to_boundary(h)
        poly = Polygon([(lng, lat) for lat, lng in boundary])
        hex_data.append({"h3_index": h, "geometry": poly})
        
    return gpd.GeoDataFrame(hex_data, crs="EPSG:4326")

def calculate_scores(hex_grid, magnets_gdf, competitors_gdf, buildings_gdf, mag_w=2.0, comp_w=1.2):
    results = []
    for idx, row in hex_grid.iterrows():
        geom = row.geometry
        
        magnet_count = sum(magnets_gdf.intersects(geom)) if not magnets_gdf.empty else 0
        competitor_count = sum(competitors_gdf.intersects(geom)) if not competitors_gdf.empty else 0
        
        pop_proxy = 0
        if not buildings_gdf.empty:
            intersecting_buildings = buildings_gdf[buildings_gdf.intersects(geom)]
            pop_proxy = len(intersecting_buildings) * 100 
            
        raw_score = (magnet_count * mag_w) - (competitor_count * comp_w)
        pop_component = min(pop_proxy / 1000.0 * 3, 3) 
        
        raw_score += pop_component
        
        results.append({
            "h3_index": row["h3_index"],
            "magnet_count": magnet_count,
            "competitor_count": competitor_count,
            "population_proxy": pop_proxy,
            "raw_score": raw_score,
            "score": max(0, min(10, raw_score))
        })
        
    df = pd.DataFrame(results)
    return hex_grid.merge(df, on="h3_index")
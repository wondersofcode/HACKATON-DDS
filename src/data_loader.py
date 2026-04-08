import osmnx as ox
import geopandas as gpd

def get_osm_data(center_point, radius, tags):
    """Fetches OSM features from a point with given tags."""
    try:
        # osmnx features_from_point expects center_point as a tuple (lat, lng)
        gdf = ox.features_from_point(center_point, tags=tags, dist=radius)
        return gdf
    except Exception as e:
        return gpd.GeoDataFrame()

def get_building_data(center_point, radius):
    """Fetches building data to calculate residential density proxy."""
    return get_osm_data(center_point, radius, tags={"building": True})
    
def generate_walk_isochrones(center_point, travel_time=5):
    """Generates walkability isochrones (Placeholder for Dijkstra logic)"""
    try:
        gdf = gpd.GeoSeries([gpd.points_from_xy([center_point[1]], [center_point[0]])[0].buffer(travel_time * 0.001)])
        return gpd.GeoDataFrame(geometry=gdf)
    except:
        return gpd.GeoDataFrame()
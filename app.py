import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.data_loader import get_osm_data, get_building_data
from src.engine import generate_h3_grid, calculate_scores
from src.ai_analyst import generate_business_report

st.set_page_config(page_title="GeoTarget AI PRO", layout="wide", page_icon="🗺️")

# --- 🔐 LOGIN PAGE (SİSTEMƏ GİRİŞ) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🗺️ GeoTarget AI Platformasına Giriş</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("""
        <div style="background-color: #1e1e1e; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
        <h3 style="text-align: center; color: white;">Hesabınıza daxil olun</h3>
        """, unsafe_allow_html=True)
        
        user = st.text_input("İstifadəçi adı (İpucu: admin)")
        pwd = st.text_input("Şifrə (İpucu: admin)", type="password")
        
        if st.button("Daxil ol 🚀", use_container_width=True):
            if user == "admin" and pwd == "admin":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("İstifadəçi adı və ya şifrə yanlışdır!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop() # Login olmadan aşağıdakı kodları oxumasın

# --- 🚀 ƏSAS TƏTBİQ ---
if "map_center" not in st.session_state:
    st.session_state.map_center = [40.4093, 49.8671] # Default Baku
if "run_analysis" not in st.session_state:
    st.session_state.run_analysis = False

st.title("🗺️ GeoTarget AI - İnteqrativ PRO Versiya")
st.markdown("Xəritədə nöqtəyə klikləyin, radiusu seçin. Sistem real-time analiz edəcək və tapılan obyektləri ikonlarla göstərəcək!")

# Məlumatları keşləyirik ki, hesablama SÜRƏTLİ olsun (Speed Optimization)
@st.cache_data(show_spinner=False)
def fetch_data(center, radius, comp_tags, mag_tags):
    competitors = get_osm_data(center, radius, comp_tags)
    magnets = get_osm_data(center, radius, mag_tags)
    buildings = get_building_data(center, radius)
    return competitors, magnets, buildings

with st.sidebar:
    st.header("⚙️ Axtarış Parametrləri")
    st.info("💡 Mərkəzi seçmək üçün sağdakı xəritəyə klikləyin!")
    
    lat = st.number_input("Enlik", value=st.session_state.map_center[0], format="%.5f")
    lng = st.number_input("Uzunluq", value=st.session_state.map_center[1], format="%.5f")
    st.session_state.map_center = [lat, lng]
    
    radius = st.slider("Axtarış Radiusu (metr)", 200, 3000, 1000, step=100)
    business_type = st.selectbox("Hədəf Biznes Növü", [
        "Kafe/Restoran", "Market/Pərakəndə", "Fitnes/İdman Zalı",
        "Aptek/Klinika", "Tədris/Kurs Mərkəzi", "Gözəllik/Xidmət"
    ])
    
    with st.expander("🛠️ Alqoritm Çəkiləri"):
        comp_weight = st.slider("Rəqiblərin Təsiri (-)", 0.0, 3.0, 1.2)
        mag_weight = st.slider("Maqnitlərin Təsiri (+)", 0.0, 3.0, 2.0)

    if st.button("Bu Nöqtəni Analiz Et 🚀", type="primary", use_container_width=True):
        st.session_state.run_analysis = True
        
    if st.button("Çıxış Et (Logout)", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# İkonların təyini
icon_map = {
    "Kafe/Restoran": "coffee",
    "Market/Pərakəndə": "shopping-cart",
    "Fitnes/İdman Zalı": "dumbbell",
    "Aptek/Klinika": "medkit",
    "Tədris/Kurs Mərkəzi": "graduation-cap",
    "Gözəllik/Xidmət": "scissors"
}

m = folium.Map(location=st.session_state.map_center, zoom_start=15, tiles="CartoDB dark_matter")

folium.Circle(
    location=st.session_state.map_center, radius=radius, color="#3498db", weight=2,
    fill=True, fill_color="#3498db", fill_opacity=0.1, tooltip="Sürətli Analiz Sahəsi"
).add_to(m)

folium.Marker(st.session_state.map_center, popup="Mərkəz", icon=folium.Icon(color="red", icon="crosshairs", prefix='fa')).add_to(m)

top5 = pd.DataFrame()
scored_grid = pd.DataFrame()

if st.session_state.run_analysis:
    center_point = (st.session_state.map_center[0], st.session_state.map_center[1])
    
    if business_type == "Kafe/Restoran": competitors_tags = {"amenity": ["cafe", "restaurant", "fast_food"]}
    elif business_type == "Market/Pərakəndə": competitors_tags = {"shop": ["supermarket", "convenience"]}
    elif business_type == "Fitnes/İdman Zalı": competitors_tags = {"leisure": ["fitness_centre", "sports_centre"]}
    elif business_type == "Aptek/Klinika": competitors_tags = {"amenity": ["pharmacy", "clinic"]}
    elif business_type == "Tədris/Kurs Mərkəzi": competitors_tags = {"amenity": ["school", "college", "language_school"]}
    else: competitors_tags = {"shop": "hairdresser"}
    
    magnets_tags = {"public_transport": "station", "highway": "bus_stop", "amenity": "university", "leisure": "park"}
    
    with st.spinner("Real-Time Data Çəkilir və Nəticələr Yığılır..."):
        competitors_gdf, magnets_gdf, buildings_gdf = fetch_data(center_point, radius, competitors_tags, magnets_tags)
        
        hex_grid = generate_h3_grid(center_point, radius, resolution=9)
        scored_grid = calculate_scores(hex_grid, magnets_gdf, competitors_gdf, buildings_gdf, mag_weight, comp_weight)
        top5 = scored_grid.sort_values(by="score", ascending=False).head(5)
        
        def get_color(score):
            if score >= 8: return "#2ecc71"
            if score >= 5: return "#f1c40f"
            return "#e74c3c"
            
        # Altıbucaqlıları xəritəyə əlavə edirik
        for idx, row in scored_grid.iterrows():
            feature_props = {"h3_index": row["h3_index"], "score": round(row["score"], 1), "magnet_count": int(row["magnet_count"]), "competitor_count": int(row["competitor_count"])}
            gj = folium.GeoJson(
                row.geometry,
                style_function=lambda x, color=get_color(row['score']): {'fillColor': color, 'color': 'white', 'weight': 1, 'fillOpacity': 0.5},
                tooltip=f"Xal: {row['score']:.1f}"
            )
            gj.data['features'][0]['properties'] = feature_props
            gj.add_to(m)

        # Rəqibləri xəritədə ikonla göstəririk
        if not competitors_gdf.empty:
            for _, row in competitors_gdf.iterrows():
                geom = row.geometry
                lat_c, lng_c = (geom.y, geom.x) if geom.geom_type == 'Point' else (geom.centroid.y, geom.centroid.x)
                folium.Marker(
                    [lat_c, lng_c], 
                    icon=folium.Icon(color="darkred", icon=icon_map[business_type], prefix='fa'),
                    tooltip=f"Rəqib Obyekt ({business_type})"
                ).add_to(m)
        
        # Maqnitləri xəritədə ikonla göstəririk
        if not magnets_gdf.empty:
            for _, row in magnets_gdf.iterrows():
                geom = row.geometry
                lat_m, lng_m = (geom.y, geom.x) if geom.geom_type == 'Point' else (geom.centroid.y, geom.centroid.x)
                folium.Marker(
                    [lat_m, lng_m], 
                    icon=folium.Icon(color="blue", icon="magnet", prefix='fa'),
                    tooltip="Trafik Maqniti (Dayanacaq, Park və s.)"
                ).add_to(m)

tab1, tab2, tab3 = st.tabs(["🗺️ İnteqrativ Xəritə", "⚖️ Ssenari Müqayisəsi", "📊 Analitika"])

with tab1:
    map_data = st_folium(m, width="100%", height=500)
    
    if map_data and map_data.get("last_clicked"):
        clicked_lat, clicked_lng = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
        if round(clicked_lat, 4) != round(st.session_state.map_center[0], 4) or round(clicked_lng, 4) != round(st.session_state.map_center[1], 4):
            st.session_state.map_center = [clicked_lat, clicked_lng]
            st.session_state.run_analysis = False
            st.rerun()

    if map_data and map_data.get("last_active_drawing"):
        props = map_data["last_active_drawing"].get("properties", {})
        if "h3_index" in props:
            st.success(f"📍 **Seçilmiş Zona: {props['h3_index']}**")
            c1, c2, c3 = st.columns(3)
            c1.metric("⭐ Xal", props["score"])
            c2.metric("🏪 Rəqiblər", props["competitor_count"])
            c3.metric("🧲 Maqnitlər", props["magnet_count"])

    if st.session_state.run_analysis and not top5.empty:
        st.markdown("### 🤖 Süni İntellektin Ümumi Rəyi")
        st.info(generate_business_report(top5.iloc[0], business_type))

with tab2:
    if not top5.empty and len(top5) >= 2:
        loc_a, loc_b = top5.iloc[0], top5.iloc[1]
        c1, c2 = st.columns(2)
        c1.success(f"**🥇 Məkan A** - Xal: {loc_a['score']:.1f}")
        c2.warning(f"**🥈 Məkan B** - Xal: {loc_b['score']:.1f}")
        
        def norm_val(val, max_val): return min(10, (val / max_val) * 10) if max_val > 0 else 0
        max_mag, max_pop, max_comp = scored_grid['magnet_count'].max() or 1, scored_grid['population_proxy'].max() or 1, scored_grid['competitor_count'].max() or 1
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=[norm_val(loc_a['magnet_count'], max_mag), 10 - norm_val(loc_a['competitor_count'], max_comp), norm_val(loc_a['population_proxy'], max_pop), loc_a['score']], theta=['Trafik', 'Rəqabətin Azlığı', 'Əhali', 'Potensial'], fill='toself', name='🥇 Məkan A', line_color='#2ecc71'))
        fig.add_trace(go.Scatterpolar(r=[norm_val(loc_b['magnet_count'], max_mag), 10 - norm_val(loc_b['competitor_count'], max_comp), norm_val(loc_b['population_proxy'], max_pop), loc_b['score']], theta=['Trafik', 'Rəqabətin Azlığı', 'Əhali', 'Potensial'], fill='toself', name='🥈 Məkan B', line_color='#f1c40f'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), margin=dict(t=30, b=30))
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    if not scored_grid.empty:
        st.markdown("### 📑 Tam Data Cədvəli")
        display_df = scored_grid.drop(columns=["geometry"]).sort_values(by="score", ascending=False)
        st.dataframe(display_df, use_container_width=True)

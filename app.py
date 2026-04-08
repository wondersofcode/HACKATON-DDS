import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.data_loader import get_osm_data, get_building_data
from src.engine import generate_h3_grid, calculate_scores
from src.ai_analyst import generate_business_report

st.set_page_config(page_title="GeoTarget AI PRO", layout="wide", page_icon="🌍")

# --- 🎨 CUSTOM CSS (ADVANCED SAAS UI FROM TEMPLATES) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Manrope:wght@600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #111318 !important;
        color: #e2e2e8 !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* GÖZƏL LANDING PAGE (HERO) DİZAYNI */
    .hero-container {
        text-align: center;
        padding: 80px 20px;
        background: radial-gradient(circle at center, rgba(195, 245, 255, 0.1) 0%, transparent 70%);
        border-radius: 20px;
        margin-bottom: 50px;
    }
    
    .hero-title {
        font-family: 'Manrope', sans-serif;
        font-size: 5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #c3f5ff 0%, #45fec9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
        line-height: 1.1;
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        color: #bac9cc;
        max-width: 800px;
        margin: 0 auto 40px auto;
        line-height: 1.6;
    }
    
    /* ÜMUMİ DÜYMƏ (BUTTON) DİZAYNI */
    div.stButton > button {
        background: #c3f5ff !important;
        color: #00363d !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.8rem 2rem !important;
        font-family: 'Manrope', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(195, 245, 255, 0.2) !important;
    }
    div.stButton > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 0 30px rgba(195, 245, 255, 0.4) !important;
    }
    
    /* XÜSUSİ 'DAXİL OL' DÜYMƏSİ (LOGIN ÜÇÜN) */
    .btn-login > button {
        background: #00e5ff !important;
    }
    
    /* KARTLARIN DİZAYNI */
    .feature-card {
        background: rgba(30, 32, 36, 0.6);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(195, 245, 255, 0.1);
        border-radius: 16px;
        padding: 30px;
        height: 100%;
        transition: all 0.3s ease;
    }
    .feature-card:hover {
        border-color: rgba(69, 254, 201, 0.3);
        box-shadow: 0 0 40px rgba(69, 254, 201, 0.05);
    }
    
    div[data-testid="metric-container"] {
        background: rgba(40, 42, 46, 0.8);
        border: 1px solid rgba(195, 245, 255, 0.1);
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    div[data-testid="metric-container"] label {
        color: #bac9cc !important;
        font-family: 'Manrope', sans-serif;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.8rem;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #45fec9 !important;
        font-family: 'Manrope', sans-serif;
        font-weight: 800;
        font-size: 2.5rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 🔐 LOGIN PAGE (İSTƏYİNƏ UYĞUN) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Sənin HTML şablonuna uyğun Login Form
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background: rgba(26, 28, 32, 0.6); backdrop-filter: blur(20px); padding: 40px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.05); box-shadow: 0 20px 40px rgba(0,0,0,0.4); text-align: center;">
            <div style="width: 60px; height: 60px; background: rgba(195, 245, 255, 0.1); border-radius: 15px; margin: 0 auto 20px auto; display: flex; align-items: center; justify-content: center; font-size: 30px;">🌍</div>
            <h2 style="font-family: 'Manrope', sans-serif; font-size: 2rem; font-weight: 800; color: #e2e2e8; margin-bottom: 5px;">Welcome Back</h2>
            <p style="color: #bac9cc; font-size: 0.9rem; margin-bottom: 30px;">Please enter your credentials to access the intelligence platform.</p>
        """, unsafe_allow_html=True)
        
        user = st.text_input("Work Email (admin)", placeholder="name@company.com")
        pwd = st.text_input("Password (admin)", type="password", placeholder="••••••••")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Sign In ➔", use_container_width=True):
            if user == "admin" and pwd == "admin":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("⚠️ Invalid credentials!")
                
        st.markdown("""
            <div style="margin-top: 30px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 20px; font-size: 0.75rem; color: #849396; text-transform: uppercase; letter-spacing: 1px;">
                Privacy • Terms • Security
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# --- 🚀 LANDING PAGE (TƏQDİMAT ÜÇÜN GET STARTED) ---
if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    # Sənin HTML şablonuna uyğun Hero Section
    st.markdown("""
    <div class="hero-container">
        <div style="display: inline-flex; align-items: center; gap: 8px; padding: 6px 16px; background: rgba(40,42,46,0.8); border: 1px solid rgba(195,245,255,0.2); border-radius: 50px; margin-bottom: 30px;">
            <div style="width: 8px; height: 8px; background: #45fec9; border-radius: 50px; box-shadow: 0 0 10px #45fec9;"></div>
            <span style="font-size: 0.75rem; font-weight: 600; color: #bac9cc; letter-spacing: 1px; text-transform: uppercase;">v2.4 Intelligence Engine Active</span>
        </div>
        <h1 class="hero-title">GeoTarget AI</h1>
        <p class="hero-subtitle">
            Data-Driven Location Intelligence. Transform spatial complexity into strategic clarity with our high-altitude analytical lens.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="feature-card">
            <div style="width: 50px; height: 50px; background: rgba(195, 245, 255, 0.1); border-radius: 12px; margin-bottom: 20px; display: flex; align-items: center; justify-content: center; font-size: 24px;">🗺️</div>
            <h3 style="font-family: 'Manrope', sans-serif; font-size: 1.5rem; font-weight: 700; color: #e2e2e8; margin-bottom: 15px;">Real-Time OSM Data</h3>
            <p style="color: #bac9cc; line-height: 1.6;">Direct integration with OpenStreetMap's global vector stream. Every node processed in milliseconds.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="feature-card" style="border-color: rgba(69, 254, 201, 0.2); box-shadow: 0 0 30px rgba(69, 254, 201, 0.05);">
            <div style="width: 50px; height: 50px; background: rgba(69, 254, 201, 0.1); border-radius: 12px; margin-bottom: 20px; display: flex; align-items: center; justify-content: center; font-size: 24px;">⬡</div>
            <h3 style="font-family: 'Manrope', sans-serif; font-size: 1.5rem; font-weight: 700; color: #e2e2e8; margin-bottom: 15px;">Uber H3 Spatial Grid</h3>
            <p style="color: #bac9cc; line-height: 1.6;">Leverage hexagonal indexing for seamless spatial aggregation. Optimize query performance at planetary scale.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="feature-card">
            <div style="width: 50px; height: 50px; background: rgba(195, 245, 255, 0.1); border-radius: 12px; margin-bottom: 20px; display: flex; align-items: center; justify-content: center; font-size: 24px;">🤖</div>
            <h3 style="font-family: 'Manrope', sans-serif; font-size: 1.5rem; font-weight: 700; color: #e2e2e8; margin-bottom: 15px;">AI-Powered Analytics</h3>
            <p style="color: #bac9cc; line-height: 1.6;">Predictive modeling that identifies site potential before the market reacts. Turn raw coordinates into strategy.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        if st.button("Launch Command Center 🚀", use_container_width=True):
            st.session_state.started = True
            st.rerun()
    st.stop()

# --- 🚀 ƏSAS TƏTBİQ (DASHBOARD) ---
if "map_center" not in st.session_state:
    st.session_state.map_center = [40.4093, 49.8671] 
if "run_analysis" not in st.session_state:
    st.session_state.run_analysis = False

st.markdown("""
<div style="display: flex; align-items: center; gap: 15px; margin-bottom: 30px; padding: 20px; background: rgba(26,28,32,0.8); border-radius: 16px; border: 1px solid rgba(195,245,255,0.1);">
    <div style="font-size: 30px;">🌍</div>
    <div>
        <h1 style="margin: 0; padding: 0; font-size: 24px; font-weight: 800; font-family: 'Manrope', sans-serif; color: #c3f5ff;">GeoTarget AI Workspace</h1>
        <p style="margin: 0; padding: 0; color: #bac9cc; font-size: 14px;">Intelligence Hub • Strategic Command</p>
    </div>
</div>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def fetch_data(center, radius, comp_tags, mag_tags):
    competitors = get_osm_data(center, radius, comp_tags)
    magnets = get_osm_data(center, radius, mag_tags)
    buildings = get_building_data(center, radius)
    return competitors, magnets, buildings

with st.sidebar:
    st.markdown("<h2 style='font-size: 14px; font-weight: 700; color: #45fec9; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 20px;'>Intelligence Hub</h2>", unsafe_allow_html=True)
    st.info("💡 Mərkəzi təyin etmək üçün xəritədə klikləyin.")
    
    lat = st.number_input("Lat (Enlik)", value=st.session_state.map_center[0], format="%.5f")
    lng = st.number_input("Long (Uzunluq)", value=st.session_state.map_center[1], format="%.5f")
    st.session_state.map_center = [lat, lng]
    
    st.markdown("---")
    radius = st.slider("Scan Radius (m)", 200, 3000, 1000, step=100)
    business_type = st.selectbox("Target Business Type", [
        "Kafe/Restoran", "Market/Pərakəndə", "Fitnes/İdman Zalı",
        "Aptek/Klinika", "Tədris/Kurs Mərkəzi", "Gözəllik/Xidmət"
    ])
    
    with st.expander("Advanced Settings"):
        comp_weight = st.slider("Competitor Weight", 0.0, 3.0, 1.2)
        mag_weight = st.slider("Traffic Magnets", 0.0, 3.0, 2.0)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Run Global Scan ⚡", type="primary", use_container_width=True):
        st.session_state.run_analysis = True
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.started = False
        st.rerun()

icon_map = {
    "Kafe/Restoran": "coffee", "Market/Pərakəndə": "shopping-cart",
    "Fitnes/İdman Zalı": "dumbbell", "Aptek/Klinika": "medkit",
    "Tədris/Kurs Mərkəzi": "graduation-cap", "Gözəllik/Xidmət": "scissors"
}

m = folium.Map(location=st.session_state.map_center, zoom_start=15, tiles="CartoDB dark_matter")

folium.Circle(
    location=st.session_state.map_center, radius=radius, color="#c3f5ff", weight=2,
    fill=True, fill_color="#c3f5ff", fill_opacity=0.1, tooltip=f"Scan Area ({radius}m)"
).add_to(m)

folium.Marker(st.session_state.map_center, popup="Target Node", icon=folium.Icon(color="black", iconColor="#45fec9", icon="crosshairs", prefix='fa')).add_to(m)

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
    
    with st.spinner("⏳ Analyzing geospatial vectors..."):
        competitors_gdf, magnets_gdf, buildings_gdf = fetch_data(center_point, radius, competitors_tags, magnets_tags)
        
        hex_grid = generate_h3_grid(center_point, radius, resolution=9)
        scored_grid = calculate_scores(hex_grid, magnets_gdf, competitors_gdf, buildings_gdf, mag_weight, comp_weight)
        top5 = scored_grid.sort_values(by="score", ascending=False).head(5)
        
        def get_color(score):
            if score >= 8: return "#45fec9" # Secondary Green from theme
            if score >= 5: return "#00daf3" # Primary Blue from theme
            return "#ffb4ab"                # Error Red from theme
            
        for idx, row in scored_grid.iterrows():
            feature_props = {"h3_index": row["h3_index"], "score": round(row["score"], 1), "magnet_count": int(row["magnet_count"]), "competitor_count": int(row["competitor_count"])}
            gj = folium.GeoJson(
                row.geometry,
                style_function=lambda x, color=get_color(row['score']): {'fillColor': color, 'color': '#111318', 'weight': 1, 'fillOpacity': 0.4},
                tooltip=f"Score: {row['score']:.1f}"
            )
            gj.data['features'][0]['properties'] = feature_props
            gj.add_to(m)

        if not competitors_gdf.empty:
            for _, row in competitors_gdf.iterrows():
                geom = row.geometry
                lat_c, lng_c = (geom.y, geom.x) if geom.geom_type == 'Point' else (geom.centroid.y, geom.centroid.x)
                obj_name = row.get("name", "Adsız Obyekt") if pd.notna(row.get("name")) else "Adsız Obyekt"
                folium.Marker(
                    [lat_c, lng_c], 
                    icon=folium.Icon(color="darkred", iconColor="white", icon=icon_map.get(business_type, "info-sign"), prefix='fa'),
                    tooltip=f"<b>{obj_name}</b>"
                ).add_to(m)
        
        if not magnets_gdf.empty:
            for _, row in magnets_gdf.iterrows():
                geom = row.geometry
                lat_m, lng_m = (geom.y, geom.x) if geom.geom_type == 'Point' else (geom.centroid.y, geom.centroid.x)
                mag_name = row.get("name", "Adsız Maqnit") if pd.notna(row.get("name")) else "Adsız Maqnit"
                folium.Marker(
                    [lat_m, lng_m], 
                    icon=folium.Icon(color="darkblue", iconColor="#00daf3", icon="magnet", prefix='fa'),
                    tooltip=f"<b>{mag_name}</b>"
                ).add_to(m)

tab1, tab2, tab3 = st.tabs(["🗺️ Interactive Map", "⚖️ Scenario Comparison", "📊 Data Analytics"])

with tab1:
    map_data = st_folium(m, width="100%", height=600, returned_objects=["last_clicked", "last_active_drawing"])
    
    if map_data and map_data.get("last_clicked"):
        clicked_lat, clicked_lng = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
        if round(clicked_lat, 4) != round(st.session_state.map_center[0], 4) or round(clicked_lng, 4) != round(st.session_state.map_center[1], 4):
            st.session_state.map_center = [clicked_lat, clicked_lng]
            st.session_state.run_analysis = False
            st.rerun()

    if map_data and map_data.get("last_active_drawing"):
        props = map_data["last_active_drawing"].get("properties", {})
        if "h3_index" in props:
            st.markdown(f"""
            <div style="background: rgba(40,42,46,0.8); border: 1px solid rgba(69,254,201,0.3); border-left: 5px solid #45fec9; padding: 20px; border-radius: 12px; margin-bottom: 20px;">
                <span style="color: #45fec9; font-family: 'Manrope'; font-size: 12px; letter-spacing: 2px; text-transform: uppercase;">Selected Node</span>
                <h3 style="margin: 5px 0 0 0; color: #e2e2e8; font-family: 'Inter';">{props['h3_index']}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Viability Score", f"{props['score']}/10")
            c2.metric("Direct Competitors", props["competitor_count"])
            c3.metric("Traffic Magnets", props["magnet_count"])

    if st.session_state.run_analysis and not top5.empty:
        st.markdown("### 🤖 AI Intelligence Insight")
        st.info(generate_business_report(top5.iloc[0], business_type))

with tab2:
    if not top5.empty and len(top5) >= 2:
        st.markdown("### ⚖️ Advanced Scenario Analysis")
        loc_a, loc_b = top5.iloc[0], top5.iloc[1]
        
        c1, c2 = st.columns(2)
        c1.markdown(f"<div style='background: rgba(69,254,201,0.1); padding:20px; border-radius:16px; border:1px solid rgba(69,254,201,0.3);'><span style='color:#45fec9; font-family:Manrope; font-weight:800; font-size:14px; text-transform:uppercase; letter-spacing:1px;'>🥇 Target Alpha</span><h1 style='color:#e2e2e8; margin:10px 0 0 0; font-size:3rem;'>{loc_a['score']:.1f}</h1></div>", unsafe_allow_html=True)
        c2.markdown(f"<div style='background: rgba(0,218,243,0.1); padding:20px; border-radius:16px; border:1px solid rgba(0,218,243,0.3);'><span style='color:#00daf3; font-family:Manrope; font-weight:800; font-size:14px; text-transform:uppercase; letter-spacing:1px;'>🥈 Target Beta</span><h1 style='color:#e2e2e8; margin:10px 0 0 0; font-size:3rem;'>{loc_b['score']:.1f}</h1></div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        def norm_val(val, max_val): return min(10, (val / max_val) * 10) if max_val > 0 else 0
        max_mag, max_pop, max_comp = scored_grid['magnet_count'].max() or 1, scored_grid['population_proxy'].max() or 1, scored_grid['competitor_count'].max() or 1
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=[norm_val(loc_a['magnet_count'], max_mag), 10 - norm_val(loc_a['competitor_count'], max_comp), norm_val(loc_a['population_proxy'], max_pop), loc_a['score']], theta=['Foot Traffic', 'Low Competition', 'Local Population', 'Overall Viability'], fill='toself', name='Alpha', line_color='#45fec9'))
        fig.add_trace(go.Scatterpolar(r=[norm_val(loc_b['magnet_count'], max_mag), 10 - norm_val(loc_b['competitor_count'], max_comp), norm_val(loc_b['population_proxy'], max_pop), loc_b['score']], theta=['Foot Traffic', 'Low Competition', 'Local Population', 'Overall Viability'], fill='toself', name='Beta', line_color='#00daf3'))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 10], gridcolor="rgba(255,255,255,0.1)"), bgcolor="rgba(0,0,0,0)"), 
            margin=dict(t=30, b=30), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#bac9cc", family="Inter")
        )
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    if not scored_grid.empty:
        st.markdown("### 📑 Hexagonal Data Matrix")
        display_df = scored_grid.drop(columns=["geometry"]).sort_values(by="score", ascending=False)
        st.dataframe(display_df, use_container_width=True)
        
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Raw Data (CSV)", csv, "geotarget_hesabat.csv", "text/csv")
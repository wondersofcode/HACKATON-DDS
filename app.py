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

# --- 🎨 CUSTOM CSS (PROFESSIONAL SAAS UI) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    #MainMenu {visibility: hidden;}
    /* header {visibility: hidden;}  <- BURA SİLİNDİ: Çünki sol paneli açan düyməni (hamburger) gizlədirdi! */
    footer {visibility: hidden;}
    
    div.stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1rem;
        font-weight: 600;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        color: white;
    }
    
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    
    .hero-box {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 60px 30px;
        border-radius: 20px;
        text-align: center;
        border: 1px solid #cbd5e1;
        margin-bottom: 40px;
        margin-top: 20px;
    }
    
    .feature-box {
        padding: 25px;
        background: white;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        height: 100%;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        text-align: center;
    }
    
    @media (prefers-color-scheme: dark) {
        div[data-testid="metric-container"], .feature-box { background-color: #1e293b; border-color: #334155; }
        .hero-box { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-color: #334155; }
    }
</style>
""", unsafe_allow_html=True)

# --- 🚀 LANDING PAGE (TƏQDİMAT ÜÇÜN GET STARTED) ---
if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    st.markdown("""
    <div class="hero-box">
        <h1 style='font-size: 3.5rem; color: #2563eb; font-weight: 800; margin-bottom: 15px;'>🌍 GeoTarget AI</h1>
        <p style='font-size: 1.5rem; color: #64748b; font-weight: 400; max-width: 800px; margin: 0 auto; line-height: 1.5;'>
            Data-Driven Location Intelligence.<br>
            <span style="font-size: 1.1rem;">Yeni biznesiniz üçün ən optimal məkanı təxminlərə görə deyil, real xəritə datalarına və süni intellektə əsasən seçin.</span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="feature-box">
            <div style="font-size: 40px; margin-bottom: 10px;">📡</div>
            <h3 style="color:#10b981; margin-top:0;">Real-Time Data</h3>
            <p style="color:#64748b;">OpenStreetMap vasitəsilə saniyələr içində rəqib obyektləri, trafik maqnitlərini və binaları canlı analiz edirik.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="feature-box">
            <div style="font-size: 40px; margin-bottom: 10px;">🛑</div>
            <h3 style="color:#f59e0b; margin-top:0;">Uber H3 Grid</h3>
            <p style="color:#64748b;">Xəritəni qabaqcıl H3 altıbucaqlılarına bölərək hər bir nöqtənin riyazi potensialını və xalını hesablayırıq.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="feature-box">
            <div style="font-size: 40px; margin-bottom: 10px;">🤖</div>
            <h3 style="color:#3b82f6; margin-top:0;">AI Analitika</h3>
            <p style="color:#64748b;">Sadəcə rəqəmlər deyil. Sistem sizə ən uyğun məkanlar üçün süni intellekt əsaslı konkret biznes rəyləri verir.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        if st.button("🚀 Platformaya Keçid (Get Started)", use_container_width=True):
            st.session_state.started = True
            st.rerun()
    st.stop()

# --- 🚀 ƏSAS TƏTBİQ (DASHBOARD) ---
if "map_center" not in st.session_state:
    st.session_state.map_center = [40.4093, 49.8671] 
if "run_analysis" not in st.session_state:
    st.session_state.run_analysis = False

st.markdown("""
<div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
    <div style="font-size: 40px;">🌍</div>
    <div>
        <h1 style="margin: 0; padding: 0; font-size: 32px; font-weight: 800; color: #2563eb;">GeoTarget AI Workspace</h1>
        <p style="margin: 0; padding: 0; color: #64748b; font-size: 15px;">Real-time OpenStreetMap Data & Uber H3 Hexagonal Analytics</p>
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
    st.markdown("<h2 style='font-size: 20px; font-weight: 700; color: #1e293b;'>⚙️ Axtarış Konfiqurasiyası</h2>", unsafe_allow_html=True)
    st.info("💡 Mərkəzi təyin etmək üçün sağdakı xəritədə klikləyin.")
    
    lat = st.number_input("📍 Enlik (Latitude)", value=st.session_state.map_center[0], format="%.5f")
    lng = st.number_input("📍 Uzunluq (Longitude)", value=st.session_state.map_center[1], format="%.5f")
    st.session_state.map_center = [lat, lng]
    
    st.markdown("---")
    radius = st.slider("📏 Axtarış Radiusu (metr)", 200, 3000, 1000, step=100)
    business_type = st.selectbox("🏢 Hədəf Biznes Növü", [
        "Kafe/Restoran", "Market/Pərakəndə", "Fitnes/İdman Zalı",
        "Aptek/Klinika", "Tədris/Kurs Mərkəzi", "Gözəllik/Xidmət"
    ])
    
    with st.expander("🎛️ Süni İntellekt Çəkiləri (Advanced)"):
        comp_weight = st.slider("Rəqiblərin Mənfi Təsiri", 0.0, 3.0, 1.2)
        mag_weight = st.slider("Trafik Maqnitlərinin Müsbət Təsiri", 0.0, 3.0, 2.0)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Analizi Başlat ⚡", type="primary", use_container_width=True):
        st.session_state.run_analysis = True
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🏠 Ana Səhifəyə Qayıt", use_container_width=True):
        st.session_state.started = False
        st.rerun()

icon_map = {
    "Kafe/Restoran": "coffee", "Market/Pərakəndə": "shopping-cart",
    "Fitnes/İdman Zalı": "dumbbell", "Aptek/Klinika": "medkit",
    "Tədris/Kurs Mərkəzi": "graduation-cap", "Gözəllik/Xidmət": "scissors"
}

m = folium.Map(location=st.session_state.map_center, zoom_start=15, tiles="CartoDB dark_matter")

folium.Circle(
    location=st.session_state.map_center, radius=radius, color="#2563eb", weight=2,
    fill=True, fill_color="#3b82f6", fill_opacity=0.15, tooltip=f"Analiz Sahəsi ({radius}m)"
).add_to(m)

folium.Marker(st.session_state.map_center, popup="Seçilmiş Mərkəz", icon=folium.Icon(color="red", icon="crosshairs", prefix='fa')).add_to(m)

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
    
    with st.spinner("⏳ Real-Time OSM Data Çəkilir və H3 Şəbəkəsi Qurulur..."):
        competitors_gdf, magnets_gdf, buildings_gdf = fetch_data(center_point, radius, competitors_tags, magnets_tags)
        
        hex_grid = generate_h3_grid(center_point, radius, resolution=9)
        scored_grid = calculate_scores(hex_grid, magnets_gdf, competitors_gdf, buildings_gdf, mag_weight, comp_weight)
        top5 = scored_grid.sort_values(by="score", ascending=False).head(5)
        
        def get_color(score):
            if score >= 8: return "#10b981" # Emerald 500
            if score >= 5: return "#f59e0b" # Amber 500
            return "#ef4444"                # Red 500
            
        for idx, row in scored_grid.iterrows():
            feature_props = {"h3_index": row["h3_index"], "score": round(row["score"], 1), "magnet_count": int(row["magnet_count"]), "competitor_count": int(row["competitor_count"])}
            gj = folium.GeoJson(
                row.geometry,
                style_function=lambda x, color=get_color(row['score']): {'fillColor': color, 'color': 'white', 'weight': 1, 'fillOpacity': 0.5},
                tooltip=f"Xal: {row['score']:.1f}"
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
                    icon=folium.Icon(color="darkred", icon=icon_map.get(business_type, "info-sign"), prefix='fa'),
                    tooltip=f"<div style='font-family:sans-serif;'><b>{obj_name}</b><br><small>Rəqib ({business_type})</small></div>"
                ).add_to(m)
        
        if not magnets_gdf.empty:
            for _, row in magnets_gdf.iterrows():
                geom = row.geometry
                lat_m, lng_m = (geom.y, geom.x) if geom.geom_type == 'Point' else (geom.centroid.y, geom.centroid.x)
                mag_name = row.get("name", "Adsız Maqnit/Dayanacaq") if pd.notna(row.get("name")) else "Adsız Maqnit/Dayanacaq"
                folium.Marker(
                    [lat_m, lng_m], 
                    icon=folium.Icon(color="blue", icon="magnet", prefix='fa'),
                    tooltip=f"<div style='font-family:sans-serif;'><b>{mag_name}</b><br><small>Trafik Maqniti</small></div>"
                ).add_to(m)

tab1, tab2, tab3 = st.tabs(["🗺️ İnteqrativ Xəritə (Map)", "⚖️ Heksagon Müqayisəsi (Compare)", "📊 Rəqəmsal Analitika (Data)"])

with tab1:
    map_data = st_folium(m, width="100%", height=550, returned_objects=["last_clicked", "last_active_drawing"])
    
    if map_data and map_data.get("last_clicked"):
        clicked_lat, clicked_lng = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
        if round(clicked_lat, 4) != round(st.session_state.map_center[0], 4) or round(clicked_lng, 4) != round(st.session_state.map_center[1], 4):
            st.session_state.map_center = [clicked_lat, clicked_lng]
            st.session_state.run_analysis = False
            st.rerun()

    if map_data and map_data.get("last_active_drawing"):
        props = map_data["last_active_drawing"].get("properties", {})
        if "h3_index" in props:
            st.markdown(f"<div style='background:#f8fafc; padding:15px; border-radius:8px; border-left:4px solid #3b82f6; margin-bottom:15px;'><b>📍 Seçilmiş H3 Zonası:</b> {props['h3_index']}</div>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("⭐ Süni İntellekt Xalı", f"{props['score']}/10")
            c2.metric("🏪 Tapılan Rəqiblər", props["competitor_count"])
            c3.metric("🧲 Trafik Maqnitləri", props["magnet_count"])

    if st.session_state.run_analysis and not top5.empty:
        st.markdown("### 🤖 Əsas Zona Üçün AI Rəyi")
        st.info(generate_business_report(top5.iloc[0], business_type))

with tab2:
    if not top5.empty and len(top5) >= 2:
        st.markdown("### ⚖️ Lider Məkanların Çoxölçülü Müqayisəsi")
        loc_a, loc_b = top5.iloc[0], top5.iloc[1]
        
        c1, c2 = st.columns(2)
        c1.markdown(f"<div style='background:#ecfdf5; padding:15px; border-radius:10px; border:1px solid #10b981;'><h3 style='color:#047857; margin:0;'>🥇 Məkan A</h3><h1 style='color:#059669; margin:0;'>{loc_a['score']:.1f}<span style='font-size:18px;'>/10</span></h1></div>", unsafe_allow_html=True)
        c2.markdown(f"<div style='background:#fffbeb; padding:15px; border-radius:10px; border:1px solid #f59e0b;'><h3 style='color:#b45309; margin:0;'>🥈 Məkan B</h3><h1 style='color:#d97706; margin:0;'>{loc_b['score']:.1f}<span style='font-size:18px;'>/10</span></h1></div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        def norm_val(val, max_val): return min(10, (val / max_val) * 10) if max_val > 0 else 0
        max_mag, max_pop, max_comp = scored_grid['magnet_count'].max() or 1, scored_grid['population_proxy'].max() or 1, scored_grid['competitor_count'].max() or 1
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=[norm_val(loc_a['magnet_count'], max_mag), 10 - norm_val(loc_a['competitor_count'], max_comp), norm_val(loc_a['population_proxy'], max_pop), loc_a['score']], theta=['Trafik (Maqnitlər)', 'Rəqabətin Azlığı', 'Əhali Sıxlığı', 'Ümumi Potensial'], fill='toself', name='🥇 Məkan A', line_color='#10b981'))
        fig.add_trace(go.Scatterpolar(r=[norm_val(loc_b['magnet_count'], max_mag), 10 - norm_val(loc_b['competitor_count'], max_comp), norm_val(loc_b['population_proxy'], max_pop), loc_b['score']], theta=['Trafik (Maqnitlər)', 'Rəqabətin Azlığı', 'Əhali Sıxlığı', 'Ümumi Potensial'], fill='toself', name='🥈 Məkan B', line_color='#f59e0b'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), margin=dict(t=30, b=30), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    if not scored_grid.empty:
        st.markdown("### 📑 Heksagonların Tam Məlumat Bazası (Database)")
        display_df = scored_grid.drop(columns=["geometry"]).sort_values(by="score", ascending=False)
        st.dataframe(display_df, use_container_width=True)
        
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Məlumatları Yüklə (CSV Formatı)", csv, "geotarget_hesabat.csv", "text/csv")
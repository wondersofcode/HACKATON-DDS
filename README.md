# Elpis AI PRO 🌍

**Elpis AI PRO**, məkana əsaslanan (location-based) qərarların qəbul edilməsi üçün qabaqcıl, AI (süni intellekt) dəstəkli geofəza (geospatial) analiz platformasıdır. Bizneslər üçün optimal yeni filial və ya mağaza yerlərini təyin etməyə, rəqiblərin sıxlığını və cəlbedici obyektləri analiz etməyə imkan yaradır.

Sistem OpenStreetMap məlumatlarını, Uber-in H3 məkan şəbəkəsini (spatial grid) və Google Gemini 3.1 Flash AI modelini istifadə edərək strateji idarəetmə mərkəzi kimi fəaliyyət göstərir.

## 🚀 Xüsusiyyətlər

- **Real-Vaxt OSM Məlumatları (Real-Time OSM Data):** OpenStreetMap vasitəsilə qlobal vektor axınlarına birbaşa inteqrasiya və hər bir nöqtənin millisaniyələr ərzində emalı.
- **Uber H3 Spatial Grid:** Qlobal miqyasda mürəkkəb geofəza sorğularını optimallaşdırmaq və datanı altıbucaqlı torlar şəklində qruplaşdırmaq üçün Uber H3 indeksləmə sistemindən istifadə.
- **Süni İntellekt Dəstəkli Analitika (AI-Powered Analytics):** Xam koordinatları strateji genişlənmə planlarına çevirmək üçün Gemini 3.1 Flash vasitəsilə ən uyğun (Top 5) yerlərin hesabatı və rəyi.
- **Ssenari Müqayisəsi və Data Analitikası:** Seçilmiş nöqtələr arasından rəqib sıxlığı və müştəri cəlb edən "Traffic Magnet" (parklar, dayanacaqlar, universitetlər və s.) mərkəzlərinə görə Uyğunluq Balı (Viability Score) hesablanması və qrafiklərlə vizuallaşdırma.
- **İnteraktiv Xəritə (Interactive Map):** Folium vasitəsilə vizuallaşdırılmış dinamik, seçilə bilən nöqtələri olan aydın interfeys.

## 🛠 Texnologiyalar

- **Frontend & UI:** Streamlit, Streamlit-Folium, Plotly
- **Backend API:** FastAPI
- **Geofəza Analitikası:** Pandas, GeoPandas, OSMnx, Shapely, H3
- **Xəritələmə:** Folium
- **Süni İntellekt (AI):** Google Generative AI (Gemini)

## 📂 Layihənin Strukturu

```text
HACKATON-DDS/
├── app.py                  # Əsas Streamlit tətbiqi və interfeys
├── fastapi_app/            # FastAPI tətbiqi və şablonları
│   ├── main.py             # FastAPI backend-i
│   └── templates/          # HTML şablonları
├── src/                    # Əsas mühərrik və məntiq
│   ├── ai_analyst.py       # Gemini AI hesablamaları və rəylər
│   ├── data_loader.py      # OSM data, rəqib və magnet yığılması
│   └── engine.py           # H3 qrid sistemi və "Score" hesablanması məntiqi
├── requirements.txt        # Asılılıqların siyahısı
└── README.md               # Layihə sənədləşdirməsi

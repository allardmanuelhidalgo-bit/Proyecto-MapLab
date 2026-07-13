import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

# 1. CONFIGURACIÓN DE LA PÁGINA Y HEADER
st.set_page_config(page_title="MapLab - Inicio", layout="wide", page_icon="📍")

# Header principal de la aplicación
st.title("📍 Proyecto MapLab")
st.subheader("Tu comparador inteligente de precios con mapa integrado")

# --- BARRA LATERAL (Simulación del estado del usuario) ---
st.sidebar.markdown("### 👤 Estado del Usuario")
# Perfil provisional (no interactivo, solo para cumplir con la vista estética)
st.sidebar.info("Modo de navegación: **Cliente Anónimo**")
st.sidebar.caption("La gestión de perfiles está deshabilitada en esta versión simplificada.")

# Ubicación simulada del usuario (por ejemplo, centro de la ciudad de interés)
st.sidebar.markdown("---")
st.sidebar.markdown("### 📍 Mi Ubicación Simulada")
user_lat = st.sidebar.number_input("Latitud actual", value=-12.0463, format="%.5f")
user_lon = st.sidebar.number_input("Longitud actual", value=-77.0427, format="%.5f")

# 2. BUSCADOR SUPERIOR DE PRODUCTOS
st.markdown("### 🔍 Buscador de Productos")
producto_buscado = st.text_input(
    label="Escribe el nombre del artículo o categoría que deseas comparar (ej: Leche, Yogurt):", 
    value="Leche"
)

# 3. CONEXIÓN CON TU BACKEND (FASTAPI)
API_URL = f"http://127.0.0.1:8000/productos/comparar"
params = {
    "nombre": producto_buscado,
    "lat": user_lat,
    "lon": user_lon,
    "limite": 10
}

if producto_buscado:
    try:
        # Petición a tu endpoint modificado en main.py
        response = requests.get(API_URL, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # --- SECCIÓN DE MÉTRICAS RÁPIDAS ---
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="🏪 Tienda más Barata", value=data["cheapest_store"])
            with col2:
                st.metric(label="💵 Precio más Bajo", value=f"S/. {data['cheapest_price']:.2f}")
            with col3:
                st.metric(label="📊 Precio Promedio en la Zona", value=f"S/. {data['average_price']:.2f}")
                
            # --- SECCIÓN DEL MAPA INTERACTIVO (FOLIUM) ---
            st.markdown("### 🗺️ Mapa de Disponibilidad y Precios")
            
            # Inicializar mapa centrado en la ubicación del usuario
            m = folium.Map(location=[user_lat, user_lon], zoom_start=14)
            
            # Marcador azul para el usuario
            folium.Marker(
                location=[user_lat, user_lon],
                popup="Tú estás aquí",
                tooltip="Mi Ubicación",
                icon=folium.Icon(color="blue", icon="user", prefix="fa")
            ).add_to(m)
            
            # Agregar las tiendas que el Backend nos devolvió
            for tienda in data["stores"]:
                # Generar el contenido del Popup usando los datos que calcula tu backend
                tendencia_icon = "🟢" if tienda["tendency"] == "baja" else ("🔴" if tienda["tendency"] == "sube" else "🟡")
                
                popup_text = f"""
                <b>{tienda['store_name']}</b><br>
                📍 Distancia: {tienda['distance_km']} km<br>
                💵 Precio Hoy: S/. {tienda['price']:.2f}<br>
                📉 Precio Anterior: S/. {tienda['previous_price'] if tienda['previous_price'] else 'N/A'}<br>
                {tendencia_icon} Tendencia: {tienda['tendency'].upper()}
                """
                
                # Definir color del PIN según el precio (Verde si es menor o igual al promedio, rojo si es caro)
                pin_color = "green" if tienda["price"] <= data["average_price"] else "red"
                
                folium.Marker(
                    location=[tienda["latitude"], tienda["longitude"]],
                    popup=folium.Popup(popup_text, max_width=300),
                    tooltip=tienda["store_name"],
                    icon=folium.Icon(color=pin_color, icon="shopping-cart", prefix="fa")
                ).add_to(m)
            
            # Renderizar mapa en Streamlit
            st_folium(m, width=1100, height=500)
            
            # --- TABLA COMPARATIVA (Opcional, debajo del mapa) ---
            st.markdown("### 📊 Tabla Comparativa de Locales")
            # Convertimos la lista de tiendas en un formato legible para st.dataframe
            tabla_datos = []
            for t in data["stores"]:
                flecha = "▼" if t["tendency"] == "baja" else ("▲" if t["tendency"] == "sube" else "■")
                tabla_datos.append({
                    "Tienda": t["store_name"],
                    "Distancia (Km)": t["distance_km"],
                    "Precio Actual": f"S/. {t['price']:.2f}",
                    "Precio Pasado": f"S/. {t['previous_price']:.2f}" if t["previous_price"] else "N/A",
                    "Tendencia": f"{flecha} {t['tendency'].upper()}"
                })
            st.dataframe(tabla_datos, use_container_width=True)
            
        elif response.status_code == 404:
            st.warning(f"🔎 {response.json()['detail']}")
        else:
            st.error("💥 Error interno en la comunicación con el servidor backend.")
            
    except requests.exceptions.ConnectionError:
        st.error("🔌 No se pudo conectar al Backend. Asegúrate de que FastAPI esté corriendo en http://127.0.0.1:8000")
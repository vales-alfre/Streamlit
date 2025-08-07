import streamlit as st
import requests
import pandas as pd
import json
from PIL import Image, ImageDraw
from io import BytesIO

API_URL = "https://u4bpgs8o43.execute-api.us-east-1.amazonaws.com/default/fnPlacaReko"

st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center;'>Detector de placas</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>Detecta placas de vehículos y dibuja su posición</h2>", unsafe_allow_html=True)

if "historial" not in st.session_state:
    st.session_state.historial = []

col1, col2 = st.columns([1, 1])

with col1:
    uploaded_file = st.file_uploader("📤 Sube una imagen", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Imagen cargada", width=300)
        image_bytes = uploaded_file.read()
        try:
            with st.spinner("🔄 Procesando imagen..."):
                response = requests.post(API_URL, data=image_bytes, headers={"Content-Type": "application/octet-stream"})
                data = response.json()

            if response.status_code != 200:
                st.error(f"❌ Error: {data.get('error', 'Error desconocido')}")
                st.stop()
            else:
                # Guardar resultado en historial
                st.session_state.historial.append(data)
                st.success(f"✅ Placa detectada: {data['placa_detectada']}")
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

with col2:
    st.subheader("📊 Resultados anteriores:")
    if st.session_state.historial:
        for i, item in enumerate(reversed(st.session_state.historial), 1):
            st.markdown(f"### 📷 Imagen #{len(st.session_state.historial) - i + 1}")
            try:
                # Descargar imagen original
                response = requests.get(item["image_url"])
                image = Image.open(BytesIO(response.content))

                # Dibujar bounding box
                draw = ImageDraw.Draw(image)
                w, h = image.size
                box = item["bounding_box"]

                left = box["Left"] * w
                top = box["Top"] * h
                right = left + box["Width"] * w
                bottom = top + box["Height"] * h

                draw.rectangle([left, top, right, bottom], outline="red", width=4)
                draw.text((left, top - 10), item["placa_detectada"], fill="red")

                # Mostrar imagen modificada
                st.image(image, caption="📍 Imagen con placa detectada", use_container_width=True)
                st.write(f"🔍 **Placa detectada:** `{item['placa_detectada']}`")
                st.markdown(f"[🔗 Ver imagen original]({item['image_url']})", unsafe_allow_html=True)
                st.markdown("---")

            except Exception as e:
                st.error(f"⚠️ Error al procesar imagen: {str(e)}")
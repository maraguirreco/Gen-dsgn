import streamlit as st
from PIL import Image, ImageDraw, ImageFilter
import random
import numpy as np

# --- Configuración de la página ---
st.set_page_config(page_title="Cala Studio - Generativo", layout="wide")

# --- Funciones Auxiliares del Motor ---

def generar_paleta(nombre_paleta):
    """Retorna una lista de colores RGB basados en un tema."""
    if nombre_paleta == "Neon Hojas (image_1.png)":
        return [
            (50, 0, 100),   # Morado oscuro (fondo)
            (150, 255, 0),  # Verde lima eléctrico
            (200, 100, 255),# Rosa/Morado vibrante
            (100, 150, 255) # Azul suave
        ]
    elif nombre_paleta == "Oceánico":
        return [(10, 30, 60), (0, 100, 150), (100, 200, 255), (255, 255, 255)]
    elif nombre_paleta == "Atardecer":
        return [(50, 10, 10), (255, 80, 80), (255, 200, 100), (100, 0, 50)]
    return [(0,0,0), (255,255,255)] # Default blanco y negro

def aplicar_grano(imagen, cantidad_grano):
    """Añade una textura granulada (ruido) a una imagen PIL."""
    if cantidad_grano <= 0:
        return imagen
    
    # Convertir PIL a numpy array
    img_array = np.array(imagen)
    
    # Generar ruido Gaussiano
    h, w, c = img_array.shape
    ruido = np.random.normal(0, cantidad_grano * 2, (h, w, c)).astype('uint8')
    
    # Sumar el ruido a la imagen original (con clipping)
    img_ruidosa_array = np.clip(img_array.astype('int16') + ruido.astype('int16'), 0, 255).astype('uint8')
    
    # Convertir de vuelta a PIL
    return Image.fromarray(img_ruidosa_array)

# --- Motor Generativo: ORGÁNICO V1 ---

def motor_organico_v1(ancho, alto, num_formas, desenfoque, paleta, grano, semilla):
    """Genera arte orgánico basado en formas difusas y ruido."""
    # Seteamos la semilla aleatoria para repetibilidad
    random.seed(semilla)
    
    colores = generar_paleta(paleta)
    fondo_rgb = colores[0]
    formas_rgb = colores[1:]
    
    # 1. Crear lienzo base
    canvas = Image.new('RGB', (ancho, alto), fondo_rgb)
    
    # 2. Crear una capa separada para dibujar las formas con transparencia (RGBA)
    capa_formas = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    dibujo = ImageDraw.Draw(capa_formas)
    
    # 3. Dibujar formas aleatorias
    for _ in range(num_formas):
        # Elegimos color aleatorio (excluyendo el fondo)
        color = random.choice(formas_rgb)
        
        # Opacidad aleatoria baja (para la estética de sombra suave)
        alfa = random.randint(30, 120) 
        
        # Geometría aleatoria para los "blobs" (manchas)
        # Hacemos elipses irregulares
        radio_max = min(ancho, alto) // 2
        radio_min = radio_max // 5
        
        r1 = random.randint(radio_min, radio_max)
        r2 = random.randint(radio_min, radio_max)
        
        x_centro = random.randint(0, ancho)
        y_centro = random.randint(0, alto)
        
        coordenadas = [
            x_centro - r1, y_centro - r2,
            x_centro + r1, y_centro + r2
        ]
        
        # Dibujar elipse con alfa
        dibujo.ellipse(coordenadas, fill=(color[0], color[1], color[2], alfa))

    # 4. Mezclar lienzo y formas (Alpha Composite)
    canvas.paste(capa_formas, (0, 0), capa_formas)
    
    # 5. Aplicar Desenfoque Gaussiano (Estética de sombras)
    if desenfoque > 0:
        canvas = canvas.filter(ImageFilter.GaussianBlur(radius=desenfoque))
        
    # 6. Aplicar Grano (Textura)
    canvas = aplicar_grano(canvas, grano)
    
    return canvas


# --- Interfaz de Usuario en Streamlit ---

st.title("👨‍🎨 Cala Generative Studio V1")
st.write("Configura tu motor generativo orgánico en la barra lateral.")

# 1. Sidebar: Selección de Motor
motor_actual = st.sidebar.selectbox("Seleccionar Motor", ["Motor Orgánico (V1)"])

# 2. Sidebar: Controles Específicos del Motor Orgánico
if motor_actual == "Motor Orgánico (V1)":
    st.sidebar.header("🎛 Controles Orgánicos")
    
    # Semilla aleatoria (importante para regenerar el mismo diseño)
    semilla = st.sidebar.number_input("Semilla Aleatoria", value=42, step=1)
    
    num_formas = st.sidebar.slider("Densidad de Formas (Sombras)", 5, 100, 25)
    desenfoque = st.sidebar.slider("Nivel de Desenfoque (Suavizado)", 5, 200, 60)
    grano = st.sidebar.slider("Textura de Grano", 0, 50, 15)
    
    paleta = st.sidebar.selectbox("Paleta de Color", [
        "Neon Hojas (image_1.png)", 
        "Oceánico", 
        "Atardecer"
    ])
    
    resolucion = st.sidebar.radio("Resolución de salida", ["Web (1200x800)", "HD (1920x1080)"])

    # Extraer ancho y alto de la resolución
    if "Web" in resolucion:
        ancho, alto = 1200, 800
    else:
        ancho, alto = 1920, 1080

    # 3. Botón de Generación y Ejecución
    if st.sidebar.button("Generar Diseño ✨"):
        # Mostramos un spinner mientras cargamos
        with st.spinner('Pintando píxeles...'):
            # LLamamos al motor
            imagen_final = motor_organico_v1(ancho, alto, num_formas, desenfoque, paleta, grano, semilla)
            
            # Mostramos el resultado
            st.image(imagen_final, caption=f"Generación Orgánica {semilla}", use_column_width=True)

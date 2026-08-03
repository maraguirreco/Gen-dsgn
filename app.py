import streamlit as st
import random

# --- Configuración de la página ---
st.set_page_config(page_title="Cala Studio - Generativo Vectorial", layout="wide")

# --- Funciones Auxiliares ---

def generar_paleta(nombre_paleta):
    """Retorna colores en formato HEX para SVG."""
    if nombre_paleta == "Neon Hojas (image_1.png)":
        return ["#320064", "#96FF00", "#C864FF", "#6496FF"] # Fondo, formas...
    elif nombre_paleta == "Oceánico":
        return ["#0A1E3C", "#006496", "#64C8FF", "#FFFFFF"]
    elif nombre_paleta == "Atardecer":
        return ["#320A0A", "#FF5050", "#FFC864", "#640032"]
    return ["#000000", "#FFFFFF"]

# --- Motor Generativo: ORGÁNICO VECTORIAL ---

def motor_organico_svg(ancho, alto, num_formas, desenfoque, paleta, grano, semilla):
    """Genera código SVG nativo con formas, blur y ruido de turbulencia."""
    random.seed(semilla)
    
    colores = generar_paleta(paleta)
    fondo_hex = colores[0]
    formas_hex = colores[1:]
    
    # 1. Configurar los filtros SVG (Blur y Ruido)
    # Convertimos la variable "grano" de Streamlit a un baseFrequency para el SVG
    frecuencia_ruido = grano / 100.0 if grano > 0 else 0
    opacidad_ruido = 0.15 if grano > 0 else 0
    
    filtros = f"""
    <defs>
        <!-- Filtro de Desenfoque -->
        <filter id="blur-filter" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="{desenfoque}" />
        </filter>
        
        <!-- Filtro de Grano (Turbulencia) -->
        <filter id="noise-filter">
            <feTurbulence type="fractalNoise" baseFrequency="{frecuencia_ruido}" numOctaves="3" result="noise" />
            <feColorMatrix type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 {opacidad_ruido} 0" in="noise" result="coloredNoise" />
        </filter>
    </defs>
    """

    # 2. Dibujar el fondo
    elementos_svg = [f'<rect width="100%" height="100%" fill="{fondo_hex}" />']
    
    # 3. Dibujar las formas abstractas dentro de un grupo con el filtro de blur aplicado
    elementos_svg.append(f'<g filter="url(#blur-filter)">')
    
    for _ in range(num_formas):
        color = random.choice(formas_hex)
        alfa = random.uniform(0.2, 0.6) # Opacidad en decimal para SVG
        
        radio_max = min(ancho, alto) // 2
        r1 = random.randint(radio_max // 5, radio_max)
        r2 = random.randint(radio_max // 5, radio_max)
        
        cx = random.randint(0, ancho)
        cy = random.randint(0, alto)
        
        # Elipse SVG
        forma = f'<ellipse cx="{cx}" cy="{cy}" rx="{r1}" ry="{r2}" fill="{color}" opacity="{alfa:.2f}" />'
        elementos_svg.append(forma)
        
    elementos_svg.append('</g>') # Cierra el grupo del blur
    
    # 4. Añadir capa de ruido por encima (si hay grano)
    if grano > 0:
        elementos_svg.append(f'<rect width="100%" height="100%" filter="url(#noise-filter)" style="mix-blend-mode: multiply;" pointer-events="none" />')

    # 5. Ensamblar el SVG final
    contenido_interno = "\n".join(elementos_svg)
    svg_final = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" width="100%" height="100%">
    {filtros}
    {contenido_interno}
    </svg>"""
    
    return svg_final

# --- Interfaz de Usuario en Streamlit ---

st.title("👨‍🎨 Cala Generative Studio V2 (Vectorial)")
st.write("Tu motor ahora genera **SVG puros**, listos para impresión infinita.")

st.sidebar.header("🎛 Controles Orgánicos (SVG)")

semilla = st.sidebar.number_input("Semilla Aleatoria", value=42, step=1)
num_formas = st.sidebar.slider("Densidad de Formas", 5, 100, 25)
desenfoque = st.sidebar.slider("Nivel de Desenfoque (SVG GaussianBlur)", 5, 200, 60)
grano = st.sidebar.slider("Textura de Grano (SVG Turbulence)", 0, 50, 15)

paleta = st.sidebar.selectbox("Paleta de Color", [
    "Neon Hojas (image_1.png)", 
    "Oceánico", 
    "Atardecer"
])

# En vectores, la resolución base solo define la proporción (aspect ratio)
proporcion = st.sidebar.radio("Proporción del lienzo", ["Horizontal (16:9)", "Cuadrado (1:1)", "Vertical (4:5)"])

if "16:9" in proporcion:
    ancho, alto = 1920, 1080
elif "1:1" in proporcion:
    ancho, alto = 1080, 1080
else:
    ancho, alto = 1080, 1350

if st.sidebar.button("Generar Diseño Vectorial ✨"):
    # Generamos el código de texto SVG
    codigo_svg = motor_organico_svg(ancho, alto, num_formas, desenfoque, paleta, grano, semilla)
    
    # Renderizamos el SVG en Streamlit de forma segura
    st.components.v1.html(codigo_svg, width=800, height=int(800 * (alto/ancho)))
    
    # Creamos un botón de descarga para el archivo .svg
    st.download_button(
        label="📥 Descargar Diseño en Alta Calidad (.SVG)",
        data=codigo_svg,
        file_name=f"cala_generativo_{semilla}.svg",
        mime="image/svg+xml"
    )

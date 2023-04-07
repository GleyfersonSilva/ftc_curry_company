import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home"
)

image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image( image, width = 120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write('# Curry Company Growth Dashboard')

st.markdown(
    """
        Growth Dashboard foi construído para acompanhar as métricas de crescimento dos entregadores e restaurantes.
        ###  Como utilizar esse Growth Dashboard?
        - Visão empresa:
            - Visão Gerencial: Métricas gerais de comportamento.
            - Visão Tática: Indicadores semanais de crescimento.
            - Visão Geográfica: Insights de Geolocalização.
        - Visão entregador:
            - Acompanhamento dos indicadores semanais de cresimento.
        - Visão restaurantes:
            - Acompanhamento dos indicadores semanais de crescimento dos restaurantes.
        ### Ask for Help
        - Time data Science no Discord:
            - @gleyferson
    """) 
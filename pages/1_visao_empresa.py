# importando as bibliotecas
import pandas as pd
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(
    page_title="Visão empresa",
    layout = "wide"
)


#==========================================================================
# FUNÇÕES
#==========================================================================

def order_metric(df1):
    colunas = ['ID', 'Order_Date']
    df_aux = df1.loc[:, colunas].groupby(['Order_Date']).count().reset_index()
    fig = px.bar(df_aux, x='Order_Date', y='ID') 
    #plotando o gráfico dentro do streamlit
    return fig

def traffic_order_share(df1):
    colunas = ['ID', 'Road_traffic_density']
    df_aux = df1.loc[:, colunas].groupby('Road_traffic_density').count().reset_index()
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    fig = px.pie(df_aux, values = 'entregas_perc', names = 'Road_traffic_density')
    return fig

def traffic_order_city(df1):
    df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
    return fig

def order_by_week(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    colunas = ['ID', 'week_of_year']
    df_aux = df1.loc[:, colunas ].groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux, x='week_of_year', y='ID')
    return fig

def order_share_by_week(df1):
    # agrupamento de pedidos por semana
    df_aux_01 = df1.loc[:, ['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()
    # agrupamento por quantiadade única de entregador por semana
    df_aux_02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby(['week_of_year']).nunique().reset_index()
    # unindo dataframes
    df_aux = pd.merge( df_aux_01, df_aux_02, how='inner')
    #realizando a divisão da quantidade de pedidos da semana pela quantidade de entregadores únicos da semana
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
    return fig

def country_maps(df1):
    colunas = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df_aux = df1.loc[:, colunas].groupby(['City', 'Road_traffic_density']).median().reset_index()
    #criando um mapa mundial e atribuindo a map
    map = folium.Map()
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                    location_info['Delivery_location_longitude']],
                    popup=location_info[['City','Road_traffic_density']]).add_to( map )
    folium_static(map, width=1024, height=600)
    return None


def clean_code(df1):
    #Filtros
    #Selecionando todas as linhas e colunas do df1 onde nas colunas Delivery_person_Age e multiple_deliveries não contenham valor 'NaN '
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ') & (df1['multiple_deliveries'] != 'NaN ') & (df1['City'] != 'NaN ') & (df1['Festival'] != 'NaN ')

    #Atribuindo ao dataframe df1 todas as linhas que foram selecionadas na ação anterior, ou seja estamos descartanto tudo que possui 'NaN ' na coluna Delivery_person_Age
    #E estamos adicionando o dataframe filtrado no df1
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas =  (df1['Weatherconditions'] != 'NaN ') & (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    # 1 - Convertendo os valores da coluna Delivery_person_Age de object para inteiro
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

    # 2 - Convertendo os valores da coluna Delivery_person_Ratings de object para float
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

    # 3 - Convertendo os valores da coluna Order_Date de object para datetime
    # Explicação: Para esta conversão, utilizamos um comando to_datetime, que está dentro da biblioteca pandas, referenciando a coluna que deve ser alterada e a máscara a aser utilizada a partir do comando format
    # Após a conversão atribuimos o valor convertido ao dataframe df1 específicando a coluna que irá receber o valor já convertido, neste caso a coluna Order_Date
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # 4 - Convertendo os valores da coluna multiple_deliveries de object para inteiro
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    # 5 - Removendo espaços (sujeiras) dentro de strings

    #Quando removemos linhas de um dataframe também removemos os index das linhas
    #Neste caso, quando removemos as linhas que continham 'NaN ' também removemos o seu index, ou seja o dataframe não inicia mais do 0 e aumentando unitariamente a té a última linha
    #ele segue os seus index anteriores, como por exemplo um dataframe de 3 linhas, linha 1 (index 0), linha 2 (index 1) e linha 3 (index 2), quando removemos a linha 2 (index 1)
    #o dataframe vai conter apenas 2 linhas porém vai manter o index anterior para cada linha, sendo linha 1 (index 0) e a nova linha 2 (index 2)
    #para que possamos fazer aplicações devemos resetar o index, passando o parametro drop=True para que o antigo index não seja mantido

    df1 = df1.reset_index(drop=True)

    #Agora sim podemos remover os espaços em branco

    #Neste comando estamos fazendo um contador, para que percorra todo o dataframe substituindo os valores com espaço pelos valores já corrigidos
    #Para realizar esta ação, utilizamos a função strip() e passamos como parâmetro o 'i' que é o contador, ou seja irá identificar a linha e passamos também a coluna que será modificada
    #Após a correção armazenamos o valor corrigido novamente na coluna, e passamos novamente os parametros de contador e coluna para que cada valor volte ao seu lugar de origem e apenas haja a correção

    # 5.1 - Removendo espaços (sujeiras) dentro da coluna ID
    #for i in range( len( df1 ) ):
    #  df1.loc[i, 'ID'] = df1.loc[i, 'ID'].strip()

    # 6 - Removendo espaços (sujeiras) dentro das colunas de forma mais eficiente

    #Explicação
    #No comando abaixo, temos um loc, que trás todas as linhas da coluna 'ID', neste caso, esse comando retorna uma Series (que é uma espécie de lista especial)
    #Quando usamos o comando '.str' acessamos a string dentro da lista, ou seja podemos acessar funções de string
    #Desta forma, podemos utilizar o comando 'strip()' que remove os espaços em branco de cada célula do nosso dataframe
    #Após removermos toda essa sujeira, atribuimos a um loc, guardando seus valores limpos em cada um dos seus respectivos locais de origem

    df1.loc[:,'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:,'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:,'Festival'] = df1.loc[:, 'Festival'].str.strip()


    #  7 - Limpando a coluna de time taken 

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split( '(min) ' )[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    # 8 - Criando o coluna semana

    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    
    return df1


#----------------------------------------Início da estrutura lógica do código--------------------

#fazendo o uploado do arquivo 
df = pd.read_csv('dataset/train.csv')

#Criando uma cópia do dataframe original para preservar os dados originais
df1 = clean_code(df)

# streamlit run visao_empresa.py
#==========================================================================
# VISÃO EMPRESA INÍCIO
#==========================================================================

#--------------------------------------------------------------------------
# SIDEBAR INÍCIO
#--------------------------------------------------------------------------

st.header('Marketplace - Visão empresa')

image_path = 'logo.png'
image = Image.open( image_path)
st.sidebar.image( image, width = 120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value = pd.datetime(2022, 4, 13),
    min_value = pd.datetime(2022, 2, 11),
    max_value = pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY' )

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('Powered by Counidade DS')

#Configuração dos filtros

#Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de densidade de tráfego
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#--------------------------------------------------------------------------
# SIDEBAR FIM
#--------------------------------------------------------------------------


#--------------------------------------------------------------------------
# LAYOUT STREAMLIT
#--------------------------------------------------------------------------

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])
       
with tab1:
    with st.container():
        #order metric
        fig = order_metric(df1)
        st.markdown('# Orders by Day')
        st.plotly_chart( fig, use_container_width = True)
    
    with st.container():  
        col1, col2 = st.columns(2)
        with col1:
            fig = traffic_order_share(df1)
            st.markdown('# Traffic Order Share')
            st.plotly_chart(fig, use_container_width = True)

        with col2:
            fig = traffic_order_city(df1)
            st.markdown('# Traffic Order City')
            st.plotly_chart(fig, use_container_width = True)
            
with tab2:
    with st.container():
        fig = order_by_week(df1)
        st.markdown('# Orders by Week')
        st.plotly_chart(fig, use_container_width = True)
    
    with st.container():
        fig = order_share_by_week(df1)
        st.markdown('# Orders Share by Week')
        st.plotly_chart(fig, use_container_width = True)
        
with tab3:
    st.markdown('# Country Maps')
    country_maps(df1)
    
    












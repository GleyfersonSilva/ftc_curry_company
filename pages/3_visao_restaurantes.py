# importando as bibliotecas
import pandas as pd
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(
    page_title="Visão restaurantes",
    layout = "wide"
)

#==========================================================================
# FUNÇÕES
#==========================================================================

def distance(df1, fig):
    if fig == False:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['distance'] = df1.loc[:, cols].apply( lambda x: 
            haversine(( x['Restaurant_latitude'], x['Restaurant_longitude']),
            ( x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        avg_distance = np.round(df1['distance'].mean(), 2)
        return avg_distance
    else:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['distance'] = df1.loc[:, cols].apply( lambda x: 
                              haversine(( x['Restaurant_latitude'], x['Restaurant_longitude']),
                              ( x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        avg_distance = df1.loc[:, ['City', 'distance']].groupby(['City']).mean().reset_index()
        fig = go.Figure( data=[go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
        return fig
            
def avg_std_time_delivery(df1, festival, operation):
    cols = ['Time_taken(min)', 'Festival']
    df_aux = df1.loc[:, cols].groupby(['Festival']).agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[(df_aux['Festival'] == festival), operation],2)
    return df_aux   

def avg_std_time_graph(df1):
    cols = ['Time_taken(min)', 'City']
    df_aux = df1.loc[:, cols].groupby(['City']).agg({ 'Time_taken(min)' : ['mean', 'std']})
    df_aux.columns = ('media','desvio_padrao')
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name = 'Control',
                    x=df_aux['City'],
                    y=df_aux['media'],
                    error_y=dict(type='data', array=df_aux['desvio_padrao'])))
    fig.update_layout(barmode='group')
    return fig

def avg_std_time_on_traffic(df1):
    cols = ['Time_taken(min)', 'City', 'Road_traffic_density']
    df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg({ 'Time_taken(min)' : ['mean', 'std']})
    df_aux.columns = ('avg_time_delivery', 'std_time_delivery')
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time_delivery',
                      color='std_time_delivery', color_continuous_scale='RdBu',
                      color_continuous_midpoint=np.average(df_aux['std_time_delivery']))
    return fig

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


#----------------------------------------Início da estrutura lógica do código-------------------


#fazendo o uploado do arquivo 
df = pd.read_csv('dataset/train.csv')

#Criando uma cópia do dataframe original para preservar os dados originais
df1 = clean_code(df)

#--------------------------------------------------------------------------
# SIDEBAR INÍCIO
#--------------------------------------------------------------------------

st.header('Marketplace - Visão entregadores')

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

weatherconditions_options = st.sidebar.multiselect(
    'Quais as condições de clima',
    ['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
       'conditions Cloudy', 'conditions Fog', 'conditions Windy'],
    default = ['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
       'conditions Cloudy', 'conditions Fog', 'conditions Windy'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('Powered by Counidade DS')

#Configuração dos filtros

#Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de densidade de tráfego
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de condição climática
linhas_selecionadas = df1['Weatherconditions'].isin(weatherconditions_options)
df1 = df1.loc[linhas_selecionadas, :]


#--------------------------------------------------------------------------
# SIDEBAR FIM
#--------------------------------------------------------------------------


#--------------------------------------------------------------------------
# LAYOUT STREAMLIT
#--------------------------------------------------------------------------


tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.markdown('## Overal Metrics')
        col1, col2, col3, col4, col5, col6 = st.columns(6,)
    #entregadores
        with col1:
            qtd = df1['Delivery_person_ID'].nunique()
            st.metric('Entregadores', qtd)
    #distância média      
        with col2:
            avg_distance = distance(df1, fig=False)
            st.metric('Distância média', avg_distance)
        
    #tmcf        
        with col3:
            df_aux = avg_std_time_delivery(df1, festival='Yes', operation='avg_time')
            st.metric('TMCF', df_aux)
           
    #vmcf
        with col4:
            df_aux = avg_std_time_delivery(df1, festival='Yes', operation='std_time')
            st.metric('VMCF', df_aux)
    #tmsf
        with col5:
            df_aux = avg_std_time_delivery(df1, festival='No', operation='avg_time')
            st.metric('TMSF', df_aux)
    #vmsf
        with col6:
            df_aux = avg_std_time_delivery(df1, festival='No', operation='std_time')
            st.metric('VMSF', df_aux)
            
    with st.container():
        st.markdown("""---""")
        st.markdown('## Medium delivery time for cities')
        col1, col2 = st.columns(2)
    #pizza   
        with col1:
            fig = distance(df1, fig=True)
            st.plotly_chart(fig, use_container_width = True)
            
     #sunburns       
        with col2:
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig, use_container_width = True)
            
    with st.container():
        st.markdown("""---""")
        st.markdown('## Time distribuition')
        col1, col2 = st.columns(2)
        
        with col1:
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig, use_container_width = True)
            
        with col2:
            cols = ['Time_taken(min)', 'City', 'Type_of_order']

            df_aux = df1.loc[:, cols].groupby(['City', 'Type_of_order']).agg({ 'Time_taken(min)' : ['mean', 'std']})

            df_aux.columns = ('media', 'desvio_padrao')

            df_aux = df_aux.reset_index()

            st.dataframe(df_aux, use_container_width = True)
            
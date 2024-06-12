import pandas as pd
import plotly.express as px
import folium
from haversine import haversine
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

# Carregar os dados
df = pd.read_csv('train.csv')

# Limpeza dos dados
df1 = df.copy()

# Limpeza das colunas de string
columns_to_strip = ['ID', 'Delivery_person_ID', 'Weatherconditions', 'Road_traffic_density',
                    'Type_of_order', 'Type_of_vehicle', 'City']

for col in columns_to_strip:
    df1[col] = df1[col].str.strip()

# Conversão da data
df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

# Remover linhas com valores nulos em colunas específicas
columns_with_nulls = ['Road_traffic_density', 'Vehicle_condition', 'Type_of_order',
                      'Type_of_vehicle', 'multiple_deliveries', 'Festival', 'City',
                      'Time_taken(min)']

df1_cleaned = df1.dropna(subset=columns_with_nulls)

# Limpar e converter colunas específicas
df1_cleaned = df1_cleaned[df1_cleaned['Delivery_person_Age'].str.strip() != 'NaN']
df1_cleaned['Delivery_person_Age'] = df1_cleaned['Delivery_person_Age'].astype(int)

df1_cleaned = df1_cleaned[df1_cleaned['Delivery_person_Ratings'].str.strip() != 'NaN']
df1_cleaned['Delivery_person_Ratings'] = df1_cleaned['Delivery_person_Ratings'].astype(float)

df1_cleaned = df1_cleaned[df1_cleaned['multiple_deliveries'].str.strip() != 'NaN']
df1_cleaned['multiple_deliveries'] = df1_cleaned['multiple_deliveries'].astype(int)

df1_cleaned = df1_cleaned[df1_cleaned['Road_traffic_density'].str.strip() != 'NaN']
df1_cleaned = df1_cleaned[df1_cleaned['City'].str.strip() != 'NaN']
df1_cleaned = df1_cleaned[df1_cleaned['Time_taken(min)'].str.strip() != 'NaN']
df1_cleaned = df1_cleaned[df1_cleaned['Festival'].str.strip() != 'NaN']

df1_cleaned['Time_taken(min)'] = df1_cleaned['Time_taken(min)'].str.replace(r'\(min\) ', '', regex=True).astype(int)

# Barra Lateral
st.header("Company's View")

image = Image.open('./cury_logo.png')
st.sidebar.image(image, use_column_width=True)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in town')
st.sidebar.markdown("""---""")

date_slider = st.sidebar.date_input(
    'Select',
    value=pd.Timestamp(2022, 2, 12),
    min_value=pd.Timestamp(2022, 2, 12),
    max_value=pd.Timestamp(2022, 4, 6),
    format="DD/MM/YYYY"
)

# Filtro de condições de trânsito
traffic_options = st.sidebar.multiselect('Traffic conditions', ['Low', 'Medium', 'High', 'Jam'], default=['Low', 'Medium', 'High','Jam'])

# Filtrar dados conforme a data e as condições de trânsito
date_slider = pd.to_datetime(date_slider)
linhas_selecionadas = df1_cleaned['Order_Date'] < date_slider
df1_cleaned = df1_cleaned.loc[linhas_selecionadas, :]

linhas_selecionadas = df1_cleaned['Road_traffic_density'].isin(traffic_options)
df1_cleaned = df1_cleaned.loc[linhas_selecionadas, :]


# Dados auxiliares para os gráficos
df_aux = df1_cleaned.groupby('Order_Date')['ID'].count().reset_index().sort_values(by='ID', ascending=False)
df_aux_traffic = df1_cleaned.groupby('Road_traffic_density')['ID'].count().reset_index()
df_city_traffic = df1_cleaned.groupby(['City', 'Road_traffic_density'])['ID'].count().reset_index()

# Adicionar verificações para garantir que os dados existem antes de acessar
high_traffic_deliveries = df_aux_traffic[df_aux_traffic['Road_traffic_density'] == 'High']['ID'].values[0] if not df_aux_traffic[df_aux_traffic['Road_traffic_density'] == 'High']['ID'].empty else 0
jam_traffic_deliveries = df_aux_traffic[df_aux_traffic['Road_traffic_density'] == 'Jam']['ID'].values[0] if not df_aux_traffic[df_aux_traffic['Road_traffic_density'] == 'Jam']['ID'].empty else 0
low_traffic_deliveries = df_aux_traffic[df_aux_traffic['Road_traffic_density'] == 'Low']['ID'].values[0] if not df_aux_traffic[df_aux_traffic['Road_traffic_density'] == 'Low']['ID'].empty else 0
medium_traffic_deliveries = df_aux_traffic[df_aux_traffic['Road_traffic_density'] == 'Medium']['ID'].values[0] if not df_aux_traffic[df_aux_traffic['Road_traffic_density'] == 'Medium']['ID'].empty else 0

# Dados para o gráfico de pizza
labels = ['High', 'Jam', 'Low', 'Medium']
values = [high_traffic_deliveries, jam_traffic_deliveries, low_traffic_deliveries, medium_traffic_deliveries]

# Layout
tab1, tab2, tab3 = st.tabs(['Managerial View', 'Tactical View', 'Geographic View'])

with tab1:
    with st.container():
        st.header('Orders per day')
        fig = px.bar(df_aux, x='Order_Date', y='ID')
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(names=labels, values=values, title='Orders by traffic conditions')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.scatter(df_city_traffic, x='City', y='Road_traffic_density', size='ID', title='Orders by traffic and city')
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.container():
        df1_cleaned['week_of_year'] = df1_cleaned['Order_Date'].dt.strftime('%U')
        df_aux_week = df1_cleaned.groupby('week_of_year')['ID'].count().reset_index()
        fig = px.line(df_aux_week, x='week_of_year', y='ID')
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        df_aux01 = df1_cleaned.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
        df_aux02 = df1_cleaned.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        df_aux_merge = pd.merge(df_aux02, df_aux01, how='inner')
        df_aux_merge['average_deliver_per_ID'] = df_aux_merge['ID'] / df_aux_merge['Delivery_person_ID']
        fig = px.line(df_aux_merge, x='week_of_year', y='average_deliver_per_ID')
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header('Geographical traffic locations')
    df_aux_grap = df1_cleaned.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude',
                                      'Delivery_location_longitude']].groupby(
        ['City', 'Road_traffic_density']).median().reset_index()
    map = folium.Map()
    for index, row in df_aux_grap.iterrows():
        popup_text = f"City: {row['City']}<br>Traffic Density: {row['Road_traffic_density']}"
        folium.Marker(
            location=[row['Delivery_location_latitude'], row['Delivery_location_longitude']],
            popup=popup_text,
            icon=folium.Icon(icon='info-sign', color='blue')
        ).add_to(map)

    # Exibe o mapa
    folium_static(map)

import pandas as pd
import plotly.express as px
import folium
from haversine import haversine
import streamlit as st
from PIL import Image
import numpy as np
import plotly.graph_objects as go
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

# Streamlit

# Barra Lateral
st.header("Restaurant's View")

image = Image.open('./cury_logo.png')
st.sidebar.image(image, use_column_width=True)

date_slider = st.sidebar.date_input(
    'Select end date',
    value=pd.Timestamp(2022, 2, 11),
    min_value=pd.Timestamp(2022, 2, 11),
    max_value=pd.Timestamp(2022, 4, 6),
    format="DD/MM/YYYY"
)

# Filtrar dados conforme a data
date_slider = pd.to_datetime(date_slider)
linhas_selecionadas = df1_cleaned['Order_Date'] < date_slider
df1_cleaned = df1_cleaned.loc[linhas_selecionadas, :]

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in town')
st.sidebar.markdown("""---""")

# Layout
tab1, tab2, tab3 = st.tabs(['section 1', 'section 2', 'section 3'])
with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            st.markdown('###### Col 1')
            delivery_unique = len(df1_cleaned['Delivery_person_ID'].unique())
            col1.metric('Unique deliveries', delivery_unique)
        with col2:
            st.markdown('###### Col 2')
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude',
                    'Restaurant_longitude']
            df1_cleaned['distance'] = df1_cleaned.loc[:, cols].apply(
                lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
            avg_distance = np.round(df1_cleaned['distance'].mean(), 2)
            col2.metric('Avg distance', avg_distance)
        with col3:
            st.markdown('###### Col 3')
            df_aux = df1_cleaned.groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']}).reset_index()
            df_aux.columns = ['Festival', 'avg_time', 'std_time']
            df_festival = df_aux[df_aux['Festival'] == 'Yes ']
            avg_time = np.round(df_festival['avg_time'].mean())
            col3.metric('Avg festival time', avg_time)
        with col4:
            st.markdown('###### Col 4')
            df_aux = df1_cleaned.groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']}).reset_index()
            df_aux.columns = ['Festival', 'avg_time', 'std_time']
            df_festival = df_aux[df_aux['Festival'] == 'Yes ']
            std_time = np.round(df_festival['std_time'].mean())
            col4.metric('Avg festival std', std_time)
        with col5:
            st.markdown('###### Col 5')
            df_aux = df1_cleaned.groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']}).reset_index()
            df_aux.columns = ['Festival', 'avg_time', 'std_time']
            df_festival = df_aux[df_aux['Festival'] == 'No ']
            avg_time = np.round(df_festival['avg_time'].mean())
            col5.metric('Avg No festival time', avg_time)
        with col6:
            st.markdown('###### Col 6')
            df_aux = df1_cleaned.groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']}).reset_index()
            df_aux.columns = ['Festival', 'avg_time', 'std_time']
            df_festival = df_aux[df_aux['Festival'] == 'No ']
            std_time = np.round(df_festival['std_time'].mean())
            col6.metric('Avg No festival std', std_time)

    with st.container():
        st.markdown("""---""")
        st.title('Average delivery distance')
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude',
                'Restaurant_longitude']
        df1_cleaned['distance'] = df1_cleaned.loc[:, cols].apply(
            lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        avg_distance = df1_cleaned.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown("""---""")
        st.title('Average delivery time')
        col1, spacer, col2 = st.columns([1, 0.1, 1])  # Adiciona um espaçamento entre as colunas

        with col1:
            st.markdown('###### Average Delivery Time by City')
            df_city_avg = df1_cleaned.groupby('City').agg({'Time_taken(min)': ['mean', 'std']}).reset_index()
            df_city_avg.columns = ['City', 'avg_time', 'std_time']
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Average Time', x=df_city_avg['City'], y=df_city_avg['avg_time'],
                                 error_y=dict(type='data', array=df_city_avg['std_time'])))
            fig.update_layout(barmode='group')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('###### Average Delivery Time by City and Traffic')
            df_city_traffic_avg = df1_cleaned.groupby(['City', 'Road_traffic_density']).agg(
                {'Time_taken(min)': ['mean', 'std']}).reset_index()
            df_city_traffic_avg.columns = ['City', 'Road_traffic_density', 'avg_time', 'std_time']
            print(df_city_traffic_avg)

            fig = px.sunburst(df_city_traffic_avg, path=['City', 'Road_traffic_density'], values='avg_time',
                              color='std_time',
                              color_continuous_scale='RdBu',
                              color_continuous_midpoint=np.average(df_city_traffic_avg['std_time']))
            st.plotly_chart(fig)




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



## streamlit

# Barra Lateral
st.header("Delivers View")

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

## Layout

with st.container():
    st.title('Overview')
    col1,col2,col3,col4 = st.columns(4)
    with col1:
        max_age = df1_cleaned.loc[:, 'Delivery_person_Age'].max()
        col1.metric("Oldest delivery driver", max_age)
    with col2:
        min_age = df1_cleaned.loc[:, 'Delivery_person_Age'].min()
        col2.metric("Youngest delivery driver", min_age)

    with col3:
        best_vehicle_cond = df1_cleaned.loc[:, 'Vehicle_condition'].max()
        col3.metric('Best Vehicle Condition', best_vehicle_cond)
    with col4:
        worst_vehicle_cond = df1_cleaned.loc[:, 'Vehicle_condition'].min()
        col4.metric('Worst Vehicle Condition', worst_vehicle_cond)

with st.container():
    st.markdown("""---""")
    st.title('Average Rates')
    col1,col2 = st.columns(2)
    with col1:
        st.markdown('Average rate by delivery drivers')
        mean_per_person = df1_cleaned.groupby('Delivery_person_ID')['Delivery_person_Ratings'].mean().reset_index()
        st.dataframe(mean_per_person)
    with col2:
        mean_traffic = df1_cleaned.groupby('Road_traffic_density')['Delivery_person_Ratings'].mean().reset_index()
        std_traffic = df1_cleaned.groupby('Road_traffic_density')['Delivery_person_Ratings'].std().reset_index()
        traffic_stats = mean_traffic.merge(std_traffic, on='Road_traffic_density')
        traffic_stats.columns = ['Road_traffic_density', 'Average_Rating', 'Standard_Deviation']
        st.markdown('Average and Standard Deviation by Traffic Condition')
        st.dataframe(traffic_stats)

        mean_weather = df1_cleaned.groupby('Weatherconditions')['Delivery_person_Ratings'].mean().reset_index()
        std_weather = df1_cleaned.groupby('Weatherconditions')['Delivery_person_Ratings'].std().reset_index()
        weather_stats = mean_weather.merge(std_weather, on='Weatherconditions')
        weather_stats.columns = ['Weatherconditions', 'Average_Rating', 'Standard_Deviation']
        st.markdown('Average and Standard Deviation by Weather Condition')
        st.dataframe(weather_stats)

with st.container():
    st.markdown("""---""")
    st.title('Top 10 fastest delivery drivers by cities')

    col1,col2,col3 = st.columns(3)
    with col1:
        st.markdown('Top 10 fastest delivery drivers Urban')
        ## 10 mais rápidos Urban
        df_aux_fastest_urban = df1_cleaned[df1_cleaned['City'] == 'Urban']
        df_aux_fastest_urban_sorted = df_aux_fastest_urban.sort_values(by='Time_taken(min)')
        df_aux_fastest_urban_unique = df_aux_fastest_urban_sorted.drop_duplicates(subset='Delivery_person_ID')
        df_top_10_urban = df_aux_fastest_urban_unique.head(10)
        final_top_10_urban = df_top_10_urban.loc[:, ['Delivery_person_ID', 'Time_taken(min)']]
        final_top_10_urban = final_top_10_urban.reset_index(drop=True)
        final_top_10_urban.index = final_top_10_urban.index + 1
        st.dataframe(final_top_10_urban)

    with col2:
        ## Mais rápidos Semi-Urban
        df_aux_fastest_semi_urban = df1_cleaned[df1_cleaned['City'] == 'Semi-Urban']
        df_aux_fastest_semi_urban_sorted = df_aux_fastest_semi_urban.sort_values(by='Time_taken(min)')
        df_aux_fastest_semi_urban_unique = df_aux_fastest_semi_urban_sorted.drop_duplicates(subset='Delivery_person_ID')
        df_top_10_semi_urban = df_aux_fastest_semi_urban_unique.head(10)
        final_top_10_semi_urban = df_top_10_semi_urban.loc[:, ['Delivery_person_ID', 'Time_taken(min)']]
        st.markdown('Top 10 fastest delivery drivers Semi-Urban')
        final_top_10_semi_urban = final_top_10_semi_urban.reset_index(drop=True)
        final_top_10_semi_urban.index = final_top_10_semi_urban.index + 1
        st.dataframe(final_top_10_semi_urban)

    with col3:
        ## 10 mais rapidos Metropolitian
        df_aux_fastest_metropolitan = df1_cleaned[df1_cleaned['City'] == 'Metropolitian']
        df_aux_fastest_metropolitan_sorted = df_aux_fastest_metropolitan.sort_values(by='Time_taken(min)')
        df_aux_fastest_metropolitan_unique = df_aux_fastest_metropolitan_sorted.drop_duplicates(
        subset='Delivery_person_ID')
        df_top_10_metropolitan = df_aux_fastest_metropolitan_unique.head(10)
        final_top_10_metropolitan = df_top_10_metropolitan.loc[:, ['Delivery_person_ID', 'Time_taken(min)']]
        st.markdown('Top 10 fastest delivery drivers Metropolitan')
        final_top_10_metropolitan = final_top_10_metropolitan.reset_index(drop=True)
        final_top_10_metropolitan.index = final_top_10_metropolitan.index + 1
        st.dataframe(final_top_10_metropolitan)








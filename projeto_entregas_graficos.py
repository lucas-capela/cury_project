#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import plotly.express as px
from IPython import get_ipython
import folium
get_ipython().system('pip install haversine')
from haversine import haversine


# In[2]:


df = pd.read_csv('train.csv')


# In[3]:


df.head()


# ##  Limpeza dos dados

# In[4]:


df1 = df.copy()


# In[5]:


df1.head()


# In[6]:


df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()


# In[7]:


df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()


# In[8]:


df1.loc[:, 'Weatherconditions'] = df1.loc[:, 'Weatherconditions'].str.strip()


# In[9]:


df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()


# In[10]:


df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip() 


# In[11]:


df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()


# In[12]:


df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()


# In[13]:


df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format= '%d-%m-%Y' )


# In[14]:


null_counts = df1.isnull().sum()
print(null_counts)


# In[15]:


# Lista de colunas com valores nulos a serem removidos
columns_with_nulls = [
    'Road_traffic_density', 'Vehicle_condition', 'Type_of_order', 
    'Type_of_vehicle', 'multiple_deliveries', 'Festival', 'City', 
    'Time_taken(min)'
]

# Remover linhas com valores nulos nas colunas especificadas
df1_cleaned = df1.dropna(subset=columns_with_nulls)


# In[16]:


df1_cleaned.head()


# In[17]:


type(df1_cleaned.loc[0, 'Delivery_person_Age'])


# In[18]:


df1_cleaned = df1_cleaned[df1_cleaned['Delivery_person_Age'].str.strip() != 'NaN']


# In[19]:


df1_cleaned['Delivery_person_Age'] = df1_cleaned['Delivery_person_Age'].astype(int)


# In[20]:


df1_cleaned = df1_cleaned[df1_cleaned['Delivery_person_Ratings'].str.strip() != 'NaN']


# In[21]:


df1_cleaned['Delivery_person_Ratings'] = df1_cleaned['Delivery_person_Ratings'].astype(float)


# In[22]:


df1_cleaned = df1_cleaned[df1_cleaned['multiple_deliveries'].str.strip() != 'NaN']


# In[23]:


df1_cleaned['multiple_deliveries'] = df1_cleaned['multiple_deliveries'].astype(int)


# In[24]:


df1_cleaned['Order_Date'] = pd.to_datetime(df1['Order_Date'], format= '%d-%m-%Y' )


# In[25]:


df1_cleaned = df1_cleaned[df1_cleaned['Road_traffic_density'].str.strip() != 'NaN']


# In[26]:


df1_cleaned = df1_cleaned[df1_cleaned['City'].str.strip() != 'NaN']


# In[27]:


df1_cleaned = df1_cleaned[df1_cleaned['Road_traffic_density'].str.strip() != 'NaN']


# In[28]:


df1_cleaned = df1_cleaned[df1_cleaned['Time_taken(min)'].str.strip() != 'NaN']


# In[29]:


df1_cleaned = df1_cleaned[df1_cleaned['Festival'].str.strip() != 'NaN']


# In[30]:


df1_cleaned['Time_taken(min)'] = df1_cleaned['Time_taken(min)'].str.replace(r'\(min\) ', '', regex=True).astype(int)


# ## Começando a parte 1 -- Quantidade de pedidos por dia.

# In[31]:


## Objetivo -  Um gráfico de barra com a quantidade de entregas no eixo Y e os dias
## no eixo X.


# In[32]:


df_aux = df1_cleaned.groupby('Order_Date')['ID'].count().reset_index().sort_values(by='ID', ascending=False)


# In[33]:


df_aux.head()


# In[34]:


px.bar(df_aux, x = 'Order_Date', y = 'ID')


# ## Começando a parte 1 -- Quantidade de pedidos por Semana.

# In[35]:


## Um gráfico de linhas com a quantidade de entregas no eixo Y e as
## semanas no eixo X. 


# In[36]:


## criando uma coluna para mostrar as semanas do ano.
df1_cleaned['week_of_year'] = df1_cleaned['Order_Date'].dt.strftime( '%U' )


# In[37]:


df1_cleaned.head()


# In[38]:


## criando uma tabela que agrupa o numero de pedidos por semanas.
df_aux_week = df1_cleaned.groupby('week_of_year')['ID'].count().reset_index()


# In[39]:


df_aux_week.head()


# In[40]:


## Plotando um gráfico de linha para visualizar a evolução do número de pedidos por semana.
px.line(df_aux_week, x= 'week_of_year', y = 'ID')


# ## Distribuição dos pedidos por tipo de tráfego

# In[41]:


## Obejetivo: Um gráfico de pizza com a porcentagem dos pedidos por cada tipo de
## tráfego.


# In[42]:


df1_cleaned.head()


# In[43]:


df_aux_traffic = df1_cleaned.groupby('Road_traffic_density')['ID'].count().reset_index()


# In[44]:


df_aux_traffic


# In[45]:


high_traffic_deliveries = df_aux_traffic[df_aux_traffic['Road_traffic_density'] == 'High']['ID'].values[0]
high_traffic_deliveries


# In[46]:


jam_traffic_deliveries = df_aux_traffic[df_aux_traffic['Road_traffic_density'] == 'Jam']['ID'].values[0]
jam_traffic_deliveries


# In[47]:


low_traffic_deliveries = df_aux_traffic[df_aux_traffic['Road_traffic_density'] == 'Low']['ID'].values[0]
low_traffic_deliveries


# In[48]:


medium_traffic_deliveries = df_aux_traffic[df_aux_traffic['Road_traffic_density'] == 'Medium']['ID'].values[0]
medium_traffic_deliveries


# In[49]:


# Dados para o gráfico de pizza
labels = ['High', 'Jam', 'Low', 'Medium']
values = [high_traffic_deliveries, jam_traffic_deliveries, low_traffic_deliveries, medium_traffic_deliveries]

# Criar o gráfico de pizza
fig = px.pie(names=labels, values=values, title='Distribuição das Entregas por Densidade de Tráfego')

# Exibir o gráfico
fig.show()


# ## Entregas por cidade e densidade de tráfego.

# In[50]:


df_city_traffic = df1_cleaned.groupby(['City','Road_traffic_density'])['ID'].count().reset_index()
df_city_traffic


# In[51]:


px.scatter(df_city_traffic, x = 'City', y = 'Road_traffic_density', size = 'ID')


# ## Quantidade de pedidos por entregador por semana.

# In[52]:


df1_cleaned.head()


# In[53]:


df_aux01 = df1_cleaned.loc[:, ['Delivery_person_ID','week_of_year']].groupby('week_of_year').nunique().reset_index()
df_aux01.head()


# In[54]:


df_aux02 = df1_cleaned.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
df_aux02.head()                           


# In[55]:


df_aux_merge = pd.merge(df_aux02, df_aux01, how = 'inner')
df_aux_merge['average_deliver_per_ID'] = df_aux_merge['ID'] / df_aux_merge['Delivery_person_ID']
df_aux_merge.head()


# In[56]:


px.line(df_aux_merge, x= 'week_of_year', y = 'average_deliver_per_ID')


# In[57]:


df_aux_grap = df1_cleaned.loc[:,['City', 'Road_traffic_density','Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City','Road_traffic_density']).median().reset_index()
df_aux_grap


# In[91]:


map = folium.Map()
for index, row in df_aux_grap.iterrows():
    popup_text = f"City: {row['City']}<br>Traffic Density: {row['Road_traffic_density']}"
    folium.Marker(
        location=[row['Delivery_location_latitude'], row['Delivery_location_longitude']],
        popup=popup_text,
        icon=folium.Icon(icon='info-sign', color='blue')
    ).add_to(map)

# Exibe o mapa
map


# ## Grafico média de idade dos entregadores por cidade.

# In[59]:


df1_cleaned.head()


# In[60]:


df_age_city = df1_cleaned.loc[:,['City','Delivery_person_Age']].groupby('City').mean().reset_index()
df_age_city


# In[61]:


fig = px.bar(df_age_city, x='City', y='Delivery_person_Age', title='Média de Idade dos Entregadores por Cidade')

# Exibir o gráfico
fig.show()


# In[62]:


df_low_jam = df1_cleaned[(df1_cleaned['Road_traffic_density'] == 'Low') | (df1_cleaned['Road_traffic_density'] == 'Jam')]
df_low_jam_aux = df_low_jam.groupby(['Road_traffic_density', 'Order_Date'])['ID'].count().reset_index()
df_low_jam_aux.head()


# In[63]:


fig = px.bar(df_low_jam_aux, x='Order_Date', y='ID', color='Road_traffic_density', barmode='group', title='Número Total de Entregas Diárias por Densidade de Tráfego (Low e Jam)')
fig.update_layout(
    width=1200,  # Largura do gráfico
    height=600   # Altura do gráfico
)
fig.show()


# In[64]:


df_rating_week = df1_cleaned.groupby('week_of_year')['Delivery_person_Ratings'].mean().reset_index().sort_values(by='week_of_year')
df_rating_week


# In[65]:


fig = px.bar(df_rating_week, x='week_of_year', y='Delivery_person_Ratings',title='avaliacoes medias das entregas por semanas.')
# Ajusta o tamanho do gráfico e a escala logarítmica
fig.update_layout(
    width=1200,  # Largura do gráfico
    height=600,  # Altura do gráfico
    yaxis=dict(type='log')
)
fig.show()


# In[66]:


df_rating_climate = df1_cleaned.groupby('Weatherconditions')['Delivery_person_Ratings'].mean().reset_index()
df_rating_climate


# In[67]:


fig = px.scatter(df_rating_climate, x='Weatherconditions', y='Delivery_person_Ratings', size='Delivery_person_Ratings', title='Média das Avaliações das Entregas por Condições Climáticas')
fig.show()


# ## Visão dos entregadores

# In[68]:


## 1. A menor e maior idade dos entregadores.
## 2. A pior e a melhor condição de veículos.
## 3. A avaliação média por entregador.
## 4. A avaliação média e o desvio padrão por tipo de tráfego.
## 5. A avaliação média e o desvio padrão por condições climáticas.
## 6. Os 10 entregadores mais rápidos por cidade.
## 7. Os 10 entregadores mais lentos por cidade.


# In[69]:


df1_cleaned.head()


# In[70]:


## 1. A menor e maior idade dos entregadores.
min_age = df1_cleaned.loc[:, 'Delivery_person_Age'].min()
max_age = df1_cleaned.loc[:, 'Delivery_person_Age'].max()
print(f'A menor idade é {min_age} e a maior é {max_age}')


# In[71]:


## 2. A pior e a melhor condição de veículos.
worst_vehicle_cond = df1_cleaned.loc[:, 'Vehicle_condition'].min()
best_vehicle_cond = df1_cleaned.loc[:, 'Vehicle_condition'].max()
print(f'A pior condição de veículo é {worst_vehicle_cond} e a melhor é {best_vehicle_cond}')


# In[72]:


## 3. A avaliação média por entregador.
mean_per_person = df1_cleaned.groupby('Delivery_person_ID')['Delivery_person_Ratings'].mean().reset_index()
mean_per_person.head()


# In[73]:


## 4. A avaliação média e o desvio padrão por tipo de tráfego.
mean_traffic = df1_cleaned.groupby('Road_traffic_density')['Delivery_person_Ratings'].mean().reset_index()
mean_traffic


# In[74]:


std_traffic = df1_cleaned.groupby('Road_traffic_density')['Delivery_person_Ratings'].std().reset_index()
std_traffic


# In[75]:


## 5. A avaliação média e o desvio padrão por condições climáticas.


# In[76]:


mean_weather = df1_cleaned.groupby('Weatherconditions')['Delivery_person_Ratings'].mean().reset_index()
mean_weather


# In[77]:


std_weather = df1_cleaned.groupby('Weatherconditions')['Delivery_person_Ratings'].std().reset_index()
std_weather


# In[78]:


## Os 10 entregadores mais rápidos por cidade.


# In[79]:


## Mais rápidos Semi-Urban
df_aux_fastest_semi_urban = df1_cleaned[df1_cleaned['City'] == 'Semi-Urban']
df_aux_fastest_semi_urban_sorted = df_aux_fastest_semi_urban.sort_values(by='Time_taken(min)')
df_aux_fastest_semi_urban_unique = df_aux_fastest_semi_urban_sorted.drop_duplicates(subset='Delivery_person_ID')
df_top_10_semi_urban = df_aux_fastest_semi_urban_unique.head(10)
df_top_10_semi_urban.loc[:, ['Delivery_person_ID' , 'Time_taken(min)']]


# In[80]:


## 10 mais rápidos Urban
df_aux_fastest_urban = df1_cleaned[df1_cleaned['City'] == 'Urban']
df_aux_fastest_urban_sorted = df_aux_fastest_urban.sort_values(by='Time_taken(min)')
df_aux_fastest_urban_unique = df_aux_fastest_urban_sorted.drop_duplicates(subset='Delivery_person_ID')
df_top_10_urban = df_aux_fastest_urban_unique.head(10)
df_top_10_urban.loc[:, ['Delivery_person_ID' , 'Time_taken(min)']]


# In[81]:


## 10 mais rapidos Metropolitian
df_aux_fastest_metropolitan = df1_cleaned[df1_cleaned['City'] == 'Metropolitian']
df_aux_fastest_metropolitan_sorted = df_aux_fastest_metropolitan.sort_values(by='Time_taken(min)')
df_aux_fastest_metropolitan_unique = df_aux_fastest_metropolitan_sorted.drop_duplicates(subset='Delivery_person_ID')
df_top_10_metropolitan = df_aux_fastest_metropolitan_unique.head(10)
df_top_10_metropolitan.loc[:, ['Delivery_person_ID' , 'Time_taken(min)']]


# In[82]:


## Concatenando os 10 mais rápidos de todas as cidades e exibindo o resultado.
df_top_10_fastest_all_cities = pd.concat([df_top_10_semi_urban, df_top_10_urban, df_top_10_metropolitan])

# Exibir o resultado final
df_top_10_fastest_all_cities.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)' ] ]


# ## A visão dos restaurantes

# In[83]:


## A quantidade de entregadores únicos.
total_unique = df1_cleaned['Delivery_person_ID'].nunique()
print(f'O número total de entregadores é {total_unique}')


# In[84]:


## A distância média dos resturantes e dos locais de entrega.
cols = ['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']
df1_cleaned['distance'] = df1_cleaned.loc[:, cols].apply(lambda x: haversine((x['Restaurant_latitude'],x['Restaurant_longitude']),(x['Delivery_location_latitude'],x['Delivery_location_longitude'] )), axis = 1 )
df1_cleaned.head()


# In[85]:


## Tempo médio e desvio padrão das entregas por cidade.
df1_cleaned.groupby('City')['Time_taken(min)'].mean()


# In[86]:


## Tempo médio e desvio padrão das entregas por cidade.
df_aux = df1_cleaned.groupby('City').agg({'Time_taken(min)' : ['mean', 'std']}).reset_index()
df_aux


# In[87]:


## Tempo médio e desvio padrão das entregas por cidade e tipo de pedido.
df_aux = df1_cleaned.groupby(['City','Type_of_order']).agg({'Time_taken(min)' : ['mean', 'std']}).reset_index()
df_aux


# In[88]:


## Tempo médio e desvio padrão das entregas por cidade e tipo de tráfego.
df_aux = df1_cleaned.groupby(['City','Road_traffic_density']).agg({'Time_taken(min)' : ['mean', 'std']}).reset_index()
df_aux


# In[89]:


## Tempo médio e desvio padrão das entregas durante festival.
df_aux = df1_cleaned.groupby('Festival').agg({'Time_taken(min)' : ['mean', 'std']}).reset_index()
df_aux


# In[ ]:





import pandas as pd
import plotly.express as px
import folium
from PIL.Image import Image
from haversine import haversine
import streamlit as st
from PIL import Image
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


df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

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


df1_cleaned['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

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

df_aux = df1_cleaned.groupby('Order_Date')['ID'].count().reset_index().sort_values(by='ID', ascending=False)

# In[33]:
df_aux.head()

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

df_city_traffic = df1_cleaned.groupby(['City','Road_traffic_density'])['ID'].count().reset_index()


# In[34]:


px.bar(df_aux, x='Order_Date', y='ID')

# ==========================
# Barra Lateral
# ==========================

st.header("Company's View")

image = Image.open('./cury_logo.png')
st.sidebar.image(image, use_column_width=True)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in town')
st.sidebar.markdown("""---""")

date_slider = st.sidebar.date_input(
    'Select',
    value=pd.Timestamp(2022, 2, 11),
    min_value=pd.Timestamp(2022, 2, 11),
    max_value=pd.Timestamp(2022, 4, 6),
    format="DD/MM/YYYY"
)
# Formatando a data para o formato DD/MM/YYYY
formatted_date = date_slider.strftime("%d/%m/%Y")
st.header(formatted_date)
st.dataframe(df1_cleaned)

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect('Traffic conditions', ['Low', 'Medium', 'High','Jam'],default='Low')

# ==========================
# Layout
# ==========================


tab1, tab2, tab3 = st.tabs(['visao gerencial', 'visao tatica', 'visao geografica'])

with tab1:
    with st.container():
        st.header('Orders per day')
        fig = px.bar(df_aux, x='Order_Date', y='ID')
        st.plotly_chart(fig, use_container_width=True)
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(names=labels, values=values, title='Orders by traffic conditions')

            # Exibir o gráfico
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.scatter(df_city_traffic, x='City', y='Road_traffic_density', size='ID',title='Orders by traffic and city')
            st.plotly_chart(fig, use_container_width=True)


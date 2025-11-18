
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout= 'centered', page_title= 'Used Cars EDA', page_icon= '🚗', initial_sidebar_state='expanded')
html_title = "<h1 style=color:white;text-align:center;> Used Cars EDA Project </h1>"
st.markdown(html_title, unsafe_allow_html= True)
st.image('https://storage.googleapis.com/kaggle-datasets-images/62920/121792/0b2d5fa44f4288eb760b7d83f9f1dfd2/dataset-cover.jpg?t=2018-10-10-16-28-48')

page = st.sidebar.radio('Page', ['Home', 'Univariate', 'Multivariate'])

df = pd.read_parquet('cleaned_df.parquet')
sample_df = df.sample(50)
if page == 'Home':
    st.header('Dataset Overview')
    st.dataframe(sample_df)

    st.header('Dataset Description')
    column_descriptions = {
    "id": "Unique identifier for each listing.",
    "url": "Full URL of the Craigslist vehicle listing.",
    "region": "Name of the Craigslist region (city/area) of the listing.",
    "region_url": "Base URL for the Craigslist region.",
    "price": "Listing price of the vehicle (USD).",
    "year": "Model year of the vehicle.",
    "manufacturer": "Car manufacturer (e.g., Toyota, Ford, BMW).",
    "model": "Vehicle model name given by the seller.",
    "condition": "Reported condition of the vehicle (e.g., good, fair, excellent).",
    "cylinders": "Number of engine cylinders, listed as text (e.g., '4 cylinders').",
    "fuel": "Fuel type (gas, diesel, electric, hybrid, etc.).",
    "odometer": "Mileage of the vehicle in miles.",
    "title_status": "Title condition (clean, salvage, rebuilt, lien, etc.).",
    "transmission": "Transmission type (automatic, manual, other).",
    "VIN": "Vehicle Identification Number, if included.",
    "drive": "Drivetrain (4wd, fwd, rwd).",
    "size": "Vehicle body size (compact, full-size, etc.).",
    "type": "Vehicle type (sedan, SUV, pickup, truck, coupe, etc.).",
    "paint_color": "Exterior color of the vehicle.",
    "image_url": "URL of the primary listing image.",
    "description": "Full text description written by the seller.",
    "county": "Mostly empty field; county name if available.",
    "state": "U.S. state where the vehicle is listed.",
    "lat": "Latitude coordinate of the listing location.",
    "long": "Longitude coordinate of the listing location.",
    "posting_date": "Date and time when the listing was posted."}

    # Create a table for descriptions
    desc_df = pd.DataFrame(list(column_descriptions.items()), columns=["Column Name", "Description"])

    # Display table
    st.subheader("📝 Column Descriptions")
    st.table(desc_df)

elif page == 'Univariate':
    tab_num, tab_cat = st.tabs(['Numerical', 'Categorical'])
    top_n = st.sidebar.slider('Top N', min_value = 1, max_value = 30, value = 5)
    # Numerical Tab
    num_cols = df.select_dtypes(include= 'number').columns.drop(['posting_year','lat','long','posting_month','posting_day','posting_weekday','posting_hour','price_per_mile','condition_score'])
    column_num = tab_num.selectbox('Column', num_cols)
    tab_num.plotly_chart(px.histogram(data_frame= df, x= column_num, title= column_num))

    # Categorical Tab
    cat_cols = df.select_dtypes(include='object').columns
    column_cat = tab_cat.selectbox('Column', cat_cols)
    chart = tab_cat.selectbox('Chart', ['Histogram', 'Pie'])

    # Top-N
    top_n_data = (
        df[column_cat]
        .value_counts()
        .head(top_n)
        .reset_index()
    )
    top_n_data.columns = [column_cat, 'count']

    if chart == 'Histogram':
        fig = px.bar(
            top_n_data,
            x=column_cat,
            y='count',
            title=f"Top {top_n} Categories for {column_cat}"
        )
        fig.update_xaxes(categoryorder='total descending')
        tab_cat.plotly_chart(fig, use_container_width=True)

    elif chart == 'Pie':
        fig = px.pie(
            top_n_data,
            names=column_cat,
            values='count',
            title=f"Top {top_n} Categories for {column_cat}"
        )
        tab_cat.plotly_chart(fig, use_container_width=True)
    
elif page == 'Multivariate':
    # Sidebar Top N
    top_n_multi = st.sidebar.slider("Top N States (by average price)", min_value=5, max_value=50, value=10)

    # Calculate top N states by average price
    state_avg_price = (
        df.groupby('state')['price']
        .mean()
        .sort_values(ascending=False)
        .head(top_n_multi)
        .reset_index()
    )
    top_states = state_avg_price['state'].tolist()

    # Dropdown to select states from Top-N
    selected_states = st.sidebar.multiselect(
        "Select States to View",
        options=top_states,
        default=top_states  # default: all top N selected
    )

    # Filter dataframe
    filtered_df = df[df['state'].isin(selected_states)]

    # Price vs State (filtered)
    st.plotly_chart(
        px.box(
            filtered_df,
            x='state',
            y='price',
            title=f"Price Variation Across Selected States",
            labels={'state':'State', 'price':'Price ($)'},
            color='state'
        ),
        use_container_width=True
    )

    # Price vs State and Manufacturer (filtered)
    state_manufacturer_price = (
        filtered_df.groupby(['state','manufacturer'])['price']
        .mean()
        .reset_index()
    )
    
    st.plotly_chart(
        px.bar(
            state_manufacturer_price,
            x='state',
            y='price',
            color='manufacturer',
            title=f"Average Price by Manufacturer in Selected States",
            labels={'state':'State', 'price':'Average Price ($)', 'manufacturer':'Manufacturer'},
            barmode='group'
        ),
        use_container_width=True
    )

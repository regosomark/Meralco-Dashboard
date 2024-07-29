import streamlit as st
import pandas as pd
from datetime import date

# Load the Excel file
file_path = 'C:/Users/MARK/Meralco History Rates/Historical MERALCO Schedule of Rates.xlsx'
df = pd.read_excel(file_path, engine='openpyxl')

# Streamlit application
st.title("Meralco History Rates")

# Initialize session state
if 'filtered_df' not in st.session_state:
    st.session_state['filtered_df'] = None
if 'selected_class' not in st.session_state:
    st.session_state['selected_class'] = None
if 'user_consumption_demand' not in st.session_state:
    st.session_state['user_consumption_demand'] = 0.0
if 'requested_dates' not in st.session_state:
    st.session_state['requested_dates'] = (date.today() - pd.Timedelta(days=365), date.today())
if 'reset' not in st.session_state:
    st.session_state['reset'] = False

# Dropdown for Customer Class
customer_classes = df['Customer Class'].unique().tolist()
if customer_classes:
    selected_class = st.selectbox(
        "Select Customer Class", 
        customer_classes, 
        index=customer_classes.index(st.session_state['selected_class']) if st.session_state['selected_class'] in customer_classes else 0
    )
    st.session_state['selected_class'] = selected_class

    # Determine the input type based on the selected class
    mapping = {
        "Residential": "Consumption",
        "General Service A": "Consumption",
        "General Service B": "Demand",
        "General Power (GP) Secondary": "Demand",
        "GP 13.8 KV and below": "Demand",
        "GP 34.5 KV": "Demand"
    }
    user_input_type = mapping.get(selected_class, "Consumption")

    # Input for consumption or demand
    user_consumption_demand = st.number_input(
        f"Enter {user_input_type} Value", 
        min_value=0.0, 
        format="%.2f", 
        value=st.session_state['user_consumption_demand']
    )
    st.session_state['user_consumption_demand'] = user_consumption_demand

    # Date range input
    requested_dates = st.date_input(
        'Select Supply Period Range',
        min_value=date(2012, 1, 1),
        max_value=date.today(),
        value=st.session_state['requested_dates']
    )
    st.session_state['requested_dates'] = requested_dates

    if len(requested_dates) == 2:
        start_date, end_date = requested_dates
        start_date = pd.Timestamp(start_date)
        end_date = pd.Timestamp(end_date) + pd.Timedelta(days=1)

        # Filter DataFrame based on inputs
        df_class = df[df['Customer Class'] == selected_class]
        df_demand = df_class[
            (df_class[f'Lower Limit {user_input_type}'] <= user_consumption_demand) &
            (df_class[f'Upper Limit {user_input_type}'] >= user_consumption_demand)
        ]
        df_demand['Supply Period'] = pd.to_datetime(df_demand['Supply Period'])
        df_period = df_demand[(df_demand['Supply Period'] >= start_date) & (df_demand['Supply Period'] < end_date)]

        if st.button("Submit"):
            st.session_state['filtered_df'] = df_period
            st.session_state['reset'] = True  # Flag to reset UI

        filtered_df = st.session_state['filtered_df']

        if filtered_df is not None and not filtered_df.empty:
            st.write("Filtered Data", filtered_df[['Customer Class', 'Customer Subclass', 'Supply Period', 'Supply Period Start', 'Supply Period End', 'Generation Charge kWh', 'Transmission Charge kWh', 'Distribution Charge kWh', 'Transmission Charge kW', 'Distribution Charge kW', 'Total per kW']])
            
            st.line_chart(
                filtered_df,
                x="Supply Period",
                y=["Distribution Charge kW", "Total per kW", "Generation Charge kWh", "Transmission Charge kWh", "Distribution Charge kWh"]
            )

            # Provide download option
            if st.download_button(
                label="Download Filtered Data",
                data=filtered_df.to_csv(index=False).encode('utf-8'),
                file_name='filtered_data.csv',
                mime='text/csv'
            ):
                st.session_state['reset'] = True  # Trigger reset after download
        else:
            st.write("")
    else:
        st.error('Please select a valid date range.')

    # Reset logic
    if st.session_state['reset']:
        st.session_state['filtered_df'] = None
        st.session_state['selected_class'] = None
        st.session_state['user_consumption_demand'] = 0.0
        st.session_state['requested_dates'] = (date.today() - pd.Timedelta(days=365), date.today())
        st.session_state['reset'] = False  # Reset flag after clearing state
else:
    st.write("")
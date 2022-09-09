import streamlit as st
from datetime import time
from utils import style
from utils import snowflake
from utils import charting

def app():

    # Initialize a variables
    container = st.container()
    all_metrics = []

    # Build out the container
    with container:

        # Read in custom CSS to style the components
        st.markdown(style.read_custom_style(), unsafe_allow_html=True)

        # Add the markdown for the page title
        st.markdown(style.page_title('analyze strava data', 'fa-chart-line'), unsafe_allow_html=True)

        # Check the session state
        if 'curr_weather_data' not in st.session_state or 'curr_activities' not in st.session_state or 'curr_activities_agg' not in st.session_state:

            # Provide a spinner to let the user know the upload take a bit of time
            with st.spinner('Please wait as the data queried in Snowflake ❄️'):

                # Go back to the database to get data an place it into session state
                snowflake.get_activities_data()

                # Set a message for the console that we are headed back to the database
                print('Querying Snowflake for activities data...')

        # Populate the dataframes from sessions values
        curr_weather_pd_df = st.session_state.curr_weather_data
        curr_activities_pd_all_df = st.session_state.curr_activities
        curr_activities_pd_agg_df = st.session_state.curr_activities_agg

        # Get the starting and ending years of our data set
        start_year = curr_activities_pd_agg_df.sort_values('ACTIVITY_YEAR')['ACTIVITY_YEAR'].iat[0]
        end_year = curr_activities_pd_agg_df.sort_values('ACTIVITY_YEAR')['ACTIVITY_YEAR'].iat[-1]

        # Define a slider which will let us slice the data by activity year
        start_year_selected, end_year_selected = st.select_slider('',options=curr_activities_pd_agg_df.ACTIVITY_YEAR.unique(),value=(start_year, end_year))

        # Filter down our dataframes to the selection of the slider
        filtered_activities_df_agg = curr_activities_pd_agg_df[curr_activities_pd_agg_df['ACTIVITY_YEAR'].between(start_year_selected, end_year_selected)]
        filtered_activities_all_df = curr_activities_pd_all_df[curr_activities_pd_all_df['ACTIVITY_YEAR'].between(start_year_selected, end_year_selected)]
        filtered_weather_df = curr_weather_pd_df[curr_weather_pd_df['ACTIVITY_YEAR'].between(start_year_selected, end_year_selected)]

        # Filter the dataframe and Get the total number of activities and Weather Observations
        total_activities = filtered_activities_df_agg['ACTIVITY_COUNT'].sum()
        total_weather_observations = filtered_weather_df['ACTIVITY_ID'].count()

        # Appending metrics to list
        all_metrics.append(style.metrics('strava data', total_activities, 'fa-person-running', '#6B6C6C', 'strava_logo_symbol.png'))
        all_metrics.append(style.metrics('weather source data', total_weather_observations, 'fa-cloud-sun', '#6B6C6C', 'weather_source_icon_logo.png'))

        # Add the markdown for the custom metrics
        st.markdown(style.custom_metric(all_metrics), unsafe_allow_html=True)

        # Add a select box to choose the chart type
        graph_type = st.selectbox('select a chart type:',('Bar Chart - Altair', 'Line Chart - Altair', 'Area Chart - Altair', 'Correlation Matrix Heatmap - Altair', 'Map Scatterplot - PyDeck', 'Bar Chart - Bokeh'))

        if (graph_type == 'Bar Chart - Altair'):

            # Build out a bar chart with the dataframe
            charting.build_bar_chart(filtered_activities_df_agg)

        elif (graph_type == 'Line Chart - Altair'):

            # Build out a bar chart with the dataframe
            charting.build_line_chart(filtered_activities_df_agg)

        elif (graph_type == 'Area Chart - Altair'):

            # Build out a bar chart with the dataframe
            charting.build_area_chart(filtered_activities_df_agg)

        elif (graph_type == 'Correlation Matrix Heatmap - Altair'):

            # Build out a bar chart with the dataframe
            charting.map_corr_matrix(filtered_weather_df, filtered_activities_all_df)

        elif (graph_type == 'Map Scatterplot - PyDeck'):

            # Build out a bar chart with the dataframe
            charting.map_with_scatterplot(filtered_activities_all_df)

        else:

            st.write(graph_type)

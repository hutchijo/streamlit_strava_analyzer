import json
import datetime
import streamlit as st
from utils import strava
from utils import style
from utils import snowflake

def app():

    # Initialize a container
    container = st.container()

    # Read in custom CSS to style the components
    container.markdown(style.read_custom_style(), unsafe_allow_html=True)

    # Initialize vasriables
    is_authenticated = False
    strava_auth = ''

    # Call the function to authenticate with Strava
    is_authenticated, strava_auth = strava.authenticate()

    if not is_authenticated:

        # Add the markdown for the page title
        container.markdown(style.page_title('get strava data', 'fa-download'), unsafe_allow_html=True)

        # Define the text for this page
        container.markdown(f'<div class="vitalorem-brand-smallest" style="padding-bottom:30px;">Before we can download data we need to connect to Strava. <br/> Please return <i class="fa-solid fa-home" style="font-size:22px;"></i> home and connect with Strava.', unsafe_allow_html=True)

    else:

        # Get the users first and last name from the data returned from Strava
        first_name = strava_auth["athlete"]["firstname"]
        last_name = strava_auth["athlete"]["lastname"]

        # Add the markdown for the page title
        container.markdown(style.page_title('download strava data', 'fa-download'), unsafe_allow_html=True)

        # Define the text for this page
        container.markdown(f'<div class="vitalorem-brand-smallest" style="padding-left:0px;padding-top:5px;padding-bottom:20px;">Welcome, {first_name} {last_name}!</div>'
        f'<div class="vitalorem-brand-smallest" style="padding-left:0px;padding-bottom:20px;">Specify the start and end dates for the activities you want to download.</div>', unsafe_allow_html=True)

        # Get the current data and tomorrow's date as well as the min time
        min_time = datetime.datetime.min.time()
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)

        # Set the date inputs with the default values
        start_date = container.date_input('Start Date:', today)
        end_date = container.date_input('End Date:', tomorrow)

        # Add the button to the page
        result = container.button('download data')

        # See if the button was clicked
        if result:

            # Convert the start and end dates into epoch values for the Strava API
            start_datetime_epoch = int(datetime.datetime.combine(start_date, min_time).timestamp())
            end_datetime_epoch = int(datetime.datetime.combine(end_date, min_time).timestamp())

            # Get strava activities
            activities_df = strava.get_activities_data(strava_auth["access_token"], start_datetime_epoch, end_datetime_epoch)

            # If the dataframe is empty display the error to the user
            if activities_df.empty:

                 # Write the status to the UI
                 st.warning('⚠️ There are no activities in this date range.')

            else:

                # Save those strava activities into the database
                snowflake.save_activities_to_snowflake(activities_df)

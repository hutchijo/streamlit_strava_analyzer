import json
import httpx
import pandas as pd
import streamlit as st
from datetime import datetime
from tabulate import tabulate

# Build out the strava authorication url
def get_strava_auth_url():

    #Initalize vasriables
    strava_authorization_url = ''

    # Define the authorization url
    strava_authorization_url = httpx.Request(
        method="GET",
        url=st.secrets.strava_config.STRAVA_AUTHORIZATION_URL,
        params={
            "client_id": st.secrets.strava_config.STRAVA_CLIENT_ID,
            "redirect_uri": st.secrets.strava_config.APP_URL,
            "response_type": "code",
            "approval_prompt": "auto",
            "scope": "activity:read_all"
        }
    )

    # Return the authorization url
    return strava_authorization_url

# Authenticate with Strava
def authenticate():

    # Initialize variables
    query_params = st.experimental_get_query_params()
    authorization_code = query_params.get("code", [None])[0]
    is_authenticated = False
    strava_auth = ''

    if authorization_code is None:
        authorization_code = query_params.get("session", [None])[0]

    # If we don't have an authorization code set up the login header
    if authorization_code is None:

        # Set the authenticated flag
        is_authenticated = False

    else:

        # Get the token using the auhtorization code
        strava_auth = exchange_authorization_code(authorization_code)

        # Set the query param for the authorization code
        st.experimental_set_query_params(session=authorization_code)

        # Set the authenticated flag
        is_authenticated = True

    # Return the strava auth
    return is_authenticated, strava_auth

# Exchange the auth code to get a token
@st.cache(show_spinner=False, suppress_st_warning=True)
def exchange_authorization_code(authorization_code):

    # Define the URL for the oauth token
    response = httpx.post(
        url="https://www.strava.com/oauth/token",
        json={
            "client_id": st.secrets.strava_config.STRAVA_CLIENT_ID,
            "client_secret": st.secrets.strava_config.STRAVA_CLIENT_SECRET,
            "code": authorization_code,
            "grant_type": "authorization_code",
        }
    )

    # Handle response errors
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError:
        st.error("Something went wrong while authenticating with Strava. Please reload and try again")
        st.experimental_set_query_params()
        st.stop()
        return

    # Convert the strava auth repsonse to JSON
    strava_auth = response.json()

    # Return the strava auth
    return strava_auth

# Define function to get your strava data
def get_activities_data(access_token, start_datetime_epoch, end_datetime_epoch):

    # Initialize variables
    per_page = 200
    page_num = 1
    max_page_num = 1000
    activities_df = pd.DataFrame()

    # Provide a spinner to let the user know that data is downloading from Strava
    with st.spinner('Please wait as the data is being downloaded from Strava 🏃'):

        # Loop through multiple pages
        while page_num < max_page_num:

            # Initialize vasriables
            uploaded_datetime = datetime.now()
            activities_url =  st.secrets.strava_config.STRAVA_ACTIVITIES_URL
            headers = {'Authorization': 'Bearer ' + access_token}
            params = {'per_page': per_page, 'page': page_num, 'after': start_datetime_epoch, 'before': end_datetime_epoch}

            # Make the Get Request for Activities
            all_activities = httpx.get(
                activities_url,
                headers=headers,
                params=params).json()

            # Create a pandas data frame from the JSON
            curr_activities_df = pd.json_normalize(all_activities)

            # See if we got any data back in this dataframe
            if curr_activities_df.empty:

                # No data was found so notifiy the user via the console
                print('No more data found - ending Strava API call on page - ' + str(page_num))

                # break out of the loop
                break

            else:

                # Concat the dataframes
                activities_df = pd.concat([activities_df, curr_activities_df], ignore_index=True)

            # Increment the counter
            page_num += 1

    # See if we have a message insetead of data with activities
    if 'message' in activities_df:

       # Clear out the auhtorization code
       authorization_code = None

       # Set the query param for the authorization code
       st.experimental_set_query_params(session=authorization_code)

       # We are not logged in so let's authenticate now
       authenticate()

    # Make sure the dataframe is not empty
    elif not activities_df.empty:

        # See if this data hasstart and end lat long data
        if 'start_latlng' in activities_df and 'end_latlng' in  activities_df:

            # Try to pull out the individual latitude and longitude for each set of coordinates
            activities_df['start_latitude'] = activities_df.apply(lambda row:  row['start_latlng'][0] if len(row['start_latlng']) > 0 else None, axis=1)
            activities_df['start_longitude'] = activities_df.apply(lambda row: row['start_latlng'][1] if len(row['start_latlng']) > 0 else None, axis=1)
            activities_df['end_latitude'] = activities_df.apply(lambda row: row['end_latlng'][0] if len(row['start_latlng']) > 0 else None, axis=1)
            activities_df['end_longitude'] = activities_df.apply(lambda row: row['end_latlng'][1] if len(row['start_latlng']) > 0 else None, axis=1)

        # See if this data has elevation data and add in default values if it doesn't
        if 'elev_low' not in activities_df and 'elev_high' not in  activities_df:

            # We didn't find elevation data so add in default values
            activities_df['elev_low'] = 0
            activities_df['elev_high'] = 0

        # Pare down the columns that are returned as we don't need all of them
        activities_df = activities_df[['id', 'name', 'start_date', 'start_date_local', 'athlete.id', 'distance', 'moving_time', 'elapsed_time', 'total_elevation_gain', 'elev_high', 'elev_low', 'type', 'sport_type','average_speed', 'average_cadence', 'average_temp', 'average_heartrate', 'max_heartrate', 'start_latitude', 'start_longitude', 'end_latitude', 'end_longitude', 'suffer_score' ]]

        # Add in a column for when this data was last uploaded
        activities_df['uploaded_datetime_original'] = pd.Series([uploaded_datetime.strftime("%Y-%m-%d %H:%M:%S") for x in range(len(activities_df.index))])

        # Write the contents of the dataframe out using Streamlit
        st.write(activities_df)

    # Return the activities dataframe
    return activities_df

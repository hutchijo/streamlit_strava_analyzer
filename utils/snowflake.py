import streamlit as st
import snowflake.connector as sf
from snowflake.snowpark.session import Session
from snowflake.snowpark.types import IntegerType, StringType, StructField, TimestampType, FloatType
from snowflake.snowpark.functions import udf, avg, count, col, lit, rank, month, year, concat, round
from snowflake.snowpark.window import Window

# Create a new Snowflake session
def create_snowflake_session():

    # Get the connection parameters from the config file
    connection_parameters = {
      "account": st.secrets.snow_config.SNOW_ACCT,
      "user": st.secrets.snow_config.SNOW_USER,
      "password": st.secrets.snow_config.SNOW_PWD,
      "role": st.secrets.snow_config.SNOW_ROLE,
      "warehouse": st.secrets.snow_config.SNOW_WH,
      "database": st.secrets.snow_config.SNOW_DB,
      "schema": st.secrets.snow_config.SNOW_SCHEMA
    }

    # Create a session which connects to Snowflake
    snow_session = Session.builder.configs(connection_parameters).create()

    # Return the Snowflake session
    return snow_session

@st.cache(show_spinner=False, suppress_st_warning=True)
def query_snowflake(curr_sql):

    # Create a new Snowflake session
    snow_session = create_snowflake_session()

    try:

        # Execute the SQL Statement
        curr_df = snow_session.sql(curr_sql)

    except:

        curr_df = None

    # Return the current dataframe
    return curr_df.to_pandas()

# Define function to save the activities to Snowflake
def save_activities_to_snowflake(activities_df):

    # Provide a spinner to let the user know the upload take a bit of time
    with st.spinner('Please wait as the data is being uploaded to Snowflake ❄️'):

        # Create a new Snowflake session
        snow_session = create_snowflake_session()

        # Create a snowpark dataframe from the pandas dataframe
        snowpark_activities_df = snow_session.create_dataframe(activities_df)

        # Using Snowpark filter down to the rows we care to preserve and properly cast fields
        snowpark_activities_df = snowpark_activities_df.select(
            col('"id"').as_('activity_id'),
            col('"name"').as_('name'),
            col('"start_date"').cast(TimestampType()).as_('start_date'),
            col('"start_date_local"').cast(TimestampType()).as_('start_date_local'),
            col('"athlete.id"').as_('athlete_id'),
            col('"distance"').as_('distance'),
            col('"moving_time"').as_('moving_time'),
            col('"elapsed_time"').as_('elapsed_time'),
            col('"total_elevation_gain"').as_('total_elevation_gain'),
            col('"elev_high"').as_('elev_high'),
            col('"elev_low"').as_('elev_low'),
            col('"average_speed"').as_('average_speed'),
            col('"average_cadence"').as_('average_cadence'),
            col('"average_temp"').as_('average_temp'),
            col('"average_heartrate"').as_('average_heartrate'),
            col('"max_heartrate"').as_('max_heartrate'),
            col('"start_latitude"').cast(FloatType()).as_('start_latitude'),
            col('"start_longitude"').cast(FloatType()).as_('start_longitude'),
            col('"end_latitude"').cast(FloatType()).as_('end_latitude'),
            col('"end_longitude"').cast(FloatType()).as_('end_longitude'),
            col('"suffer_score"').as_('suffer_score'),
            col('"sport_type"').as_('sport_type'),
            col('"uploaded_datetime_original"').cast(TimestampType()).as_('uploaded_datetime'))

        # Filter to only running activities
        snowpark_activities_df = snowpark_activities_df.filter(col('sport_type') == 'Run')

        # Write the snowpark activities dataframe to the database
        snowpark_activities_df.write.mode('append').saveAsTable('STRAVA_ACTIVITIES_RAW')

        # Call the get activities data function which will set the appropropriate sessions state
        get_activities_data()

        # Write the status to the UI
        st.success('There are ' + str(snowpark_activities_df.count()) + ' activities in this date range which have been uploaded to Snowflake ❄️')

def get_activities_data(force_reload=False):

    # If the force reload is set to true delete all of the session state values for dataframes
    if (force_reload):

        # Delete a all of the sessions state values
        del st.session_state['all_activity_data']
        del st.session_state['curr_activities_df']
        del st.session_state['curr_activities_df_agg']

    # Grab all of the activities and place this into session_state
    if 'all_activity_data' not in st.session_state:

        # Create a new Snowflake session
        snow_session = create_snowflake_session()

        # Get all of the raw activities
        all_activities_raw_df = snow_session.table('STRAVA_ACTIVITIES_RAW')

        # Place the result into the session_state
        st.session_state['all_activity_data'] = all_activities_raw_df

    # Grab the current activities and current activities aggregated into session state
    if 'curr_activities_df' not in st.session_state or 'curr_activities_df_agg' not in st.session_state:

        # Set up the window rank to get only the latest activities based on uploaded date time
        ACTIVITY_RANK = Window.partitionBy(col('ACTIVITY_ID')).orderBy(col('UPLOADED_DATETIME').desc())

        # Filter down to only the most current activities as they may have been uploaded more than once
        curr_activities_df = st.session_state.all_activity_data \
            .select('ACTIVITY_ID', 'NAME', 'START_DATE', \
            concat(year('START_DATE'), lit('-'), month('START_DATE')).as_('ACTIVITY_MONTH_YEAR'), \
            year('START_DATE').as_('ACTIVITY_YEAR'), \
            month('START_DATE').as_('ACTIVITY_MONTH'), \
            round('START_LATITUDE',3).as_('START_LATITUDE'), \
            round('START_LONGITUDE',3).as_('START_LONGITUDE'), \
            'UPLOADED_DATETIME',\
            rank().over(ACTIVITY_RANK).as_('RANKING')).filter(col('RANKING') == 1)

        # Now aggregate to the number of activities by month
        curr_activities_df_agg = curr_activities_df \
          .groupBy('ACTIVITY_MONTH_YEAR',  'ACTIVITY_YEAR', 'ACTIVITY_MONTH') \
          .agg(count('ACTIVITY_ID').alias('ACTIVITY_COUNT')) \
          .select('ACTIVITY_COUNT', 'ACTIVITY_MONTH_YEAR', 'ACTIVITY_YEAR', 'ACTIVITY_MONTH') \
          .sort('ACTIVITY_YEAR', 'ACTIVITY_MONTH')

        # Place the current activities and current activities aggregated into session state
        st.session_state['curr_activities_df'] = curr_activities_df.to_pandas()
        st.session_state['curr_activities_df_agg'] = curr_activities_df_agg.to_pandas()

    # We already have the activity data so grab it from session
    curr_activities_df = st.session_state.curr_activities_df
    curr_activities_df_agg = st.session_state.curr_activities_df_agg

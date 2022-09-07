import altair as alt
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st
from vega_datasets import data

def build_bar_chart(curr_dataframe):

    # Configure the chart with the desired settings
    configure_curr_activities_chart = alt.Chart(curr_dataframe) \
        .mark_bar() \
        .encode( \
            alt.X('ACTIVITY_MONTH_YEAR', axis=alt.Axis(title='activity month', labels=False, tickSize=0)), \
            alt.Y('ACTIVITY_COUNT', axis=alt.Axis(title='activity count')), \
            tooltip=[alt.Tooltip('ACTIVITY_MONTH_YEAR', title='activity year'), alt.Tooltip('ACTIVITY_COUNT', title='activity count')]) \
        .configure_mark( \
            opacity=1, \
            color='#fc4c02') \
        .configure_view(strokeOpacity=0) \
        .configure_axis( \
            grid=False, \
            labelFontSize=20, \
            titleFontSize=20, \
            titlePadding=10, \
            labelFont='strava_connect') \

    # Finally, use Streamlit to show the chart
    st.altair_chart(configure_curr_activities_chart, use_container_width=True)

def build_line_chart(curr_dataframe):

    # Configure the chart with the desired settings
    configure_curr_activities_chart = alt.Chart(curr_dataframe) \
        .mark_line() \
        .encode( \
            alt.X('ACTIVITY_MONTH_YEAR', axis=alt.Axis(title='activity month', labels=False, tickSize=0)), \
            alt.Y('ACTIVITY_COUNT', axis=alt.Axis(title='activity count')), \
            tooltip=[alt.Tooltip('ACTIVITY_MONTH_YEAR', title='activity year'), alt.Tooltip('ACTIVITY_COUNT', title='activity count')]) \
        .configure_mark( \
            opacity=1, \
            color='#fc4c02') \
        .configure_view(strokeOpacity=0) \
        .configure_axis( \
            grid=False, \
            labelFontSize=20, \
            titleFontSize=20, \
            titlePadding=10, \
            labelFont='strava_connect') \

    # Finally, use Streamlit to show the chart
    st.altair_chart(configure_curr_activities_chart, use_container_width=True)

def build_area_chart(curr_dataframe):

    # Configure the chart with the desired settings
    configure_curr_activities_chart = alt.Chart(curr_dataframe) \
        .mark_area(opacity=1, \
        line={'color':'#fc4c02'},\
        color=alt.Gradient(\
        gradient='linear',\
        stops=[alt.GradientStop(color='#f79e79', offset=0),\
               alt.GradientStop(color='#fc4c02', offset=1)],x1=1,x2=1,y1=1,y2=0 \
            )) \
        .encode( \
            alt.X('ACTIVITY_MONTH_YEAR', axis=alt.Axis(title='activity month', labels=False, tickSize=0)), \
            alt.Y('ACTIVITY_COUNT', axis=alt.Axis(title='activity count')), \
            tooltip=[alt.Tooltip('ACTIVITY_MONTH_YEAR', title='activity year'), alt.Tooltip('ACTIVITY_COUNT', title='activity count')]) \
        .configure_view(strokeOpacity=0) \
        .configure_axis( \
            grid=False, \
            labelFontSize=20, \
            titleFontSize=20, \
            titlePadding=10, \
            labelFont='strava_connect') \

    # Finally, use Streamlit to show the chart
    st.altair_chart(configure_curr_activities_chart, use_container_width=True)

def map_with_path():

    # We need the ability to select a single activity and then make a call back to Strava to get the map.summary_poline field
    # This field holds all of the coordinates we need - downloading it all to the database is a much larger operation
    # Once downloaded you need to use this package to decode the cordinates - https://pypi.org/project/polyline/

    # This is an example of how to use Pydeck with sample data
    trip = pd.read_json('https://raw.githubusercontent.com/uber-common/deck.gl-data/master/website/sf.trips.json')

    trip["coordinates"] = trip["waypoints"].apply(lambda f: [item["coordinates"] for item in f])
    trip.drop(["waypoints"], axis=1, inplace=True)

    layer = pdk.Layer(
        'TripsLayer',
        trip,
        get_path="coordinates",
        get_color=[252, 76, 1],
        width_min_pixels=5,
        rounded=True,
        trail_length=600
    )

    view_state = pdk.ViewState(latitude=37.7749295,longitude=-122.4194155,zoom=11,pitch=45)
    deckchart = st.pydeck_chart(pdk.Deck(initial_view_state=view_state,layers=[layer]))

def map_with_scatterplot(curr_dataframe):

    # Now aggregate to the number of activities by month
    curr_dataframe_agg = curr_dataframe \
      .groupby(['START_LATITUDE','START_LONGITUDE'])['ACTIVITY_ID'].count().reset_index(name='ACTIVITY_COUNT').sort_values(['ACTIVITY_COUNT'], ascending=False).head(10)

    # Get the most visited set of lat \ long which is how we will center the viewport
    most_visited_start_lat = curr_dataframe_agg.sort_values(['ACTIVITY_COUNT'], ascending=False)['START_LATITUDE'].iat[0]
    most_visited_start_long = curr_dataframe_agg.sort_values(['ACTIVITY_COUNT'], ascending=False)['START_LONGITUDE'].iat[0]

    # Define a layer to display on a map
    layer = pdk.Layer(
        "ScatterplotLayer",
        curr_dataframe_agg,
        pickable=True,
        opacity=0.8,
        stroked=True,
        filled=True,
        radius_scale=25,
        radius_min_pixels=1,
        radius_max_pixels=150,
        line_width_min_pixels=1,
        get_position='[START_LONGITUDE, START_LATITUDE]',
        get_radius='ACTIVITY_COUNT',
        get_fill_color=[252, 76, 1],
        get_line_color=[0, 0, 0],
    )

    # Set the viewport location to be the most travelled to starting location of an activity
    view_state = pdk.ViewState(latitude=most_visited_start_lat, longitude=most_visited_start_long, zoom=10, bearing=0, pitch=0)

    # Render the chart in streamlit
    deckchart = st.pydeck_chart(pdk.Deck(initial_view_state=view_state,layers=[layer] ,tooltip={'html': '<b>Total Activities:</b> {ACTIVITY_COUNT}','style': {'color': 'white'}}))

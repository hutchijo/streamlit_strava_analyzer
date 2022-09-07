import streamlit as st
from utils import strava
from utils import style

def app():

    # Initialize vasriables
    is_authenticated = False
    strava_auth = ''

    # Initialize a container
    container = st.container()

    # Read in custom CSS to style the components
    container.markdown(style.read_custom_style(), unsafe_allow_html=True)

    # Add the markdown for the page title
    container.markdown(style.page_title('welcome to the strava analyzer', 'fa-person-running'), unsafe_allow_html=True)

    # Define the text for this page
    container.markdown(f'<div class="vitalorem-brand-smallest" style="padding-bottom:20px;">With this Streamlit app you can connect and download your Strava data and'
    f' merge it with Snowflake Marketplace data to better understand your training trends, discover new insights and improve your overall performance.</div>', unsafe_allow_html=True)

    # Call the function to authenticate with Strava
    is_authenticated, strava_auth = strava.authenticate()

    if not is_authenticated:

        # Get the image for the button
        base64_btn_strava_connect = style.load_image_as_base64("./static/btn_strava_connect.png")

        # Get the strava authorization id
        strava_authorization_url = strava.get_strava_auth_url()

        # Define the markdown for the conect to strava page
        container.markdown(f'<div class="vitalorem-brand-smallest">Before we can download data we need to connect to Strava.  Click the \"Connect with Strava\" button to login with your Strava account and get started.</div>'
        f'<a href=\"{strava_authorization_url.url}\" target="_self">'
        f'<img alt=\"strava login\" src=\"data:image/png;base64,{base64_btn_strava_connect}\" width="220px" style="position:relative;left:-6px;padding-top:20px;padding-bottom:20px;">'
        f'</a>', unsafe_allow_html=True)

    else:

        # Get the users first and last name from the data returned from Strava
        first_name = strava_auth["athlete"]["firstname"]
        last_name = strava_auth["athlete"]["lastname"]

        # Define the markdown for the conect to strava page
        container.markdown(f'<div class="vitalorem-brand-smallest" style="padding-left:0px;padding-top:5px;padding-bottom:20px;">Welcome, {first_name} {last_name}, you are now authenticated to Strava. </div>',unsafe_allow_html=True)

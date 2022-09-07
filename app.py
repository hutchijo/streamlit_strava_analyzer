from multiapp import MultiApp
from apps import home, get_strava_data, analyze_strava_data

app = MultiApp()

# Add all your application here
app.add_app("Home", home.app, 'house-fill')
app.add_app("Get Strava Data", get_strava_data.app, 'cloud-download-fill')
app.add_app("Analyze Strava Data", analyze_strava_data.app, 'bar-chart-fill')

# The main app
app.run()

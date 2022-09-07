import streamlit as st
from utils import style
from streamlit_option_menu import option_menu

class MultiApp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, func, icon):

        self.apps.append({
            "title": title,
            "function": func,
            "icon": icon
        })

    def run(self):

        # Set up our option menu top naviation
        app_selected = option_menu(
            menu_title=None,
            options=[d['title'] for d in self.apps],
            icons=[d['icon'] for d in self.apps],
            default_index = 0,
            orientation = 'horizontal',
            styles={
                "container": {"background-color": "#444", "padding": "5!important", "margin": "10!important", "border-radius": "0rem", "min-width": "705px"},
                "icon": {"color": "white", "font-size": "20px"},
                "nav-link": {"font-size": "17px", "font-family": "Trebuchet MS",  "font-weight": "bold", "text-align": "left", "margin":"0px", "--hover-color": "#6B6C6C"},
                "nav-link-selected": {"background-color": "#FD4C00"},
            }
        )

        # Get the app selected based on the title
        app_selected = (list(filter(lambda x:x['title']==app_selected, self.apps)))[0]

        # Now run the app selected based on the function
        app_selected['function']()

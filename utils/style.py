import os
import base64

class metrics:
    def __init__(self, metric_name, metric_value, icon_name, box_color, image_name = None):
        self.metric_name = metric_name
        self.metric_value = metric_value
        self.icon_name = icon_name
        self.box_color = box_color
        self.image_name = image_name

# Convert a given file to base 64
def load_image_as_base64(image_path):

    # Read a file in as a base64
    with open(image_path, "rb") as f:
        contents = f.read()

    # Return the base 64 data
    return base64.b64encode(contents).decode("utf-8")

# Read in custom CSS file
def read_custom_style():

    # Initalize variabls
    cust_css = ''

    # Open the custom css file located in the static folder
    with open('./static/cust_strava.css') as f:
        cust_css = '<style>' + f.read() + '</style><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" crossorigin="anonymous">'

    # Return the custom CSS
    return cust_css

# Define the appearance of a custom metric
def custom_metric(all_metrics):

    # Iniitlaize vasriables
    cust_metric_markdown = '<div id="cust_container">'

    # Based on the number of metrics we have change the width percentage
    width_pct = 100 / len(all_metrics)

    # Loop through all the metrics passed in to build out the distinct metrics
    for curr_metric in all_metrics:

        # See if we have an image name
        if (curr_metric.image_name is not None):

            # Get the image for the button
            base64_image = load_image_as_base64(f"""./static/{curr_metric.image_name}""")
            image_markdown = f"""<img src="data:image/png;base64,{base64_image}" width="50">"""

        else:

            # Use the icon instread of the image
            image_markdown=f"""<i class='{curr_metric.icon_name} fa-solid'></i>"""

        # Add the details for the current metric
        cust_metric_markdown = cust_metric_markdown + f"""<div class='kpi-card' style='background-color: {curr_metric.box_color}; width: {width_pct}%'>
                <span class="metric-name">{image_markdown}&nbsp;{curr_metric.metric_name}</span>
                <span class="metric-value">{curr_metric.metric_value}</span>
            </div>"""

    # Add the closing div tag to the metric
    cust_metric_markdown + cust_metric_markdown + '</div>'

    # Return the custom metric markdown
    return cust_metric_markdown

# Define the appearance of a page title
def page_title(page_title, icon_name):

    # Add the details for the page title
    page_title_markdown = f"""<div class='vitalorem-brand-large' style='padding-bottom:2px;position:relative;top:-23px;'>
            <i class='{icon_name} fa-solid' style='font-size:22px;'></i>&nbsp;{page_title}</div>"""

    # Return the page_title markdown
    return page_title_markdown

# Define the appearance of a subpage title
def subpage_title(subpage_title):

    # Add the details for the subpage title
    subpage_title_markdown = f"""<div class='vitalorem-brand-small' style='padding-bottom:2px;'>{subpage_title}</div>"""

    # Return the subpage_title markdown
    return subpage_title_markdown

from dash import html
from dash import dcc


def about_us_layout():
    # Headshots and names in different categories
    categories = {
        "Professors": [
            {"name": "Thomas Sargent", "image_url": "assets/tom.webp", "position": "Professor of Economics at NYU", 
             "roles": "PI", "link_url": "http://www.tomsargent.com"},
            {"name": "George Hall", "image_url": "assets/george.jpeg",  "position": "Professor of Economics at Brandeis", 
             "roles": "PI", "link_url": "https://people.brandeis.edu/~ghall/"},
        ],
        "Team Members 1": [
            {"name": "Chris Liao", "image_url": "assets/chris.png",  "position": "UChicago 2024, BA Economics, MS Computer Science", 
             "roles": "Team Leader, Web App + Data", "link_url": "https://www.linkedin.com/in/chris-liao-8865b219a/"},
            {"name": "David Cho", "image_url": "assets/david.JPEG",  "position": "High School Student", 
             "roles": "Web App (Maps) + Data", "link_url": "https://github.com/davidch2020"},
            {"name": "Maria Dubasov", "image_url": "assets/maria.jpg",  "position": "William and Mary 2026, BA Economics", 
             "roles": "Web App (Maps)", "link_url": "http://www.linkedin.com/in/maria-dubasov-262aa4236"}],
        "Team Members 2": [
            {"name": "Peter Gao", "image_url": "assets/peter.jpg", "roles": "Web App (Tables)",  "position": "NYU 2024, BA Economics and Mathematics",
             "link_url": "https://www.linkedin.com/in/tianxianggao-777742236/"},
            {"name": "Jasmine Garcia", "image_url": "assets/jasmine.jpeg", "roles": "Web App (General)",  "position": "Yale 2026, BA Political Science and Economics",
             "link_url": "https://www.linkedin.com/in/jasminemg/"}],
        "Team Members 3": [
            {"name": "Liam Loughead", "image_url": "assets/liam.JPG", "roles": "Data",  "position": "High School Student",
             "link_url": "https://github.com/Snapwhiz914"},
            {"name": "John Mo", "image_url": "assets/john.png", "roles": "Web App (General)",  "position": "High School Student",
             "link_url": "https://www.linkedin.com/in/john-mo-777328233"}],
    }

    # Helper function to create a single headshot element
    def create_headshot_element(image_url, name, roles, link_url, position):
        return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        style={
                            "width": "400px",   # Adjust the width as desired
                            "height": "550px",  # Adjust the height as desired
                            "background-color": "#f1f1f1",  # Light grey background color
                            "padding": "20px",  # Add padding
                            "border": "1px solid transparent",  # Thinner border with transparent color
                        },
                        children=[
                            html.Div(
                                style={
                                    "width": "100%",
                                    "height": "70%",
                                    "background-image": f"url('{image_url}')",
                                    "background-size": "cover",
                                    "background-position": "center",
                                    "border-radius": "0%",
                                }
                            ),
                            html.Hr(style={"margin": "20px"}),  # Add horizontal line with margin
                            dcc.Link(name, className="headshot-name", href=link_url, target="_blank", style = {'fontSize':'4vh'}),
                            html.H5("Role(s): " + roles, className="headshot-name", style={"color": "black"}),
                            html.H5(position, className="headshot-name", style={"color": "black"}),
                        ],
                    )
                ],
                style={"text-align": "center", "margin-bottom": "20px"},  # Add margin
                className="headshot-element",
            ),
        ],
        style={
            "display": "inline-block",
            "width": "420px",
            "margin": "0.75in 0",
            "margin-left": "0.5in",
            "position": "relative",
        },
    )

    # Create the layout
    layout = html.Div([
        html.H1("The Team", style={"text-align": "center"}),
        html.Hr(),  # Thin line separating the categories
        
        #Professors Category
        html.H2("Professors", style={"text-align": "center"}),
        html.Div([
            create_headshot_element(person["image_url"], person["name"], person['roles'], person["link_url"], person['position'])
            for person in categories["Professors"]
        ], style={"display": "flex", "justify-content": "center"}),
        
        html.Hr(style={"height": "2px", "background-color": "black"}),  # Black line separator

        #Team Lead Category
        html.H2("Research Staff", style={"text-align": "center"}),
        html.Div([
            create_headshot_element(person["image_url"], person["name"], person['roles'], person["link_url"], person['position'])
            for person in categories["Team Members 1"]
        ], style={"display": "flex", "justify-content": "center"}),
        
        # Data Automation category
        html.Div([
            create_headshot_element(person["image_url"], person["name"], person['roles'], person["link_url"], person['position'])
            for person in categories["Team Members 2"]
        ], style={"display": "flex", "justify-content": "center"}),

        # Data Visualization category
        html.Div([
            create_headshot_element(person["image_url"], person["name"], person['roles'], person["link_url"], person['position'])
            for person in categories["Team Members 3"]
        ], style={"display": "flex", "justify-content": "center"}),

    ], className="about-us-layout")

    return layout
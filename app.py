## main app

#importing needed libraries 
import dash
from dash import html
import dash_bootstrap_components as dbc
from PIL import Image
import os

#setting the path to call datasets and images 
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
dname = dname.replace("\\", "/")
os.chdir(dname)
print(dname)
#defining the app
app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.FLATLY])

#define the variable for heroku platform
server = app.server



#creating and styling the navigation bar 
navbar = dbc.Nav([
            dbc.NavLink([
                html.Div(page["name"], className="ms-2")],
                href=page["path"],
                active="exact",
                style={'color':'white'})
                for page in dash.page_registry.values()],
            horizontal="center",
            pills=True,
            className="blue",
            style ={'backgroundColor': "#2e8bc0", 'color':'white'})

#formatting the layout of all the pages 
app.layout = dbc.Container([
    dbc.Row([


            html.Div("Wildfires monitoring system",
                         style={'fontSize':60, 'textAlign':'center', 
                                 'backgroundColor': "#eeeeee", 
                                 'color':'black',
                                 'marginBottom':5})

      ], style ={'backgroundColor': "#eeeeee"}),


    dbc.Row([
        dbc.Col([
            navbar #inserting the navbar previously created
                ],  width={'size':12}, align="center")]),
    
    html.Hr(),

    dbc.Row([
        dbc.Col([
            dash.page_container #calling the content of the pag1/pag2/pag3 
                ])
            ])
        ],fluid=True, style={'backgroundColor': "#eeeeee"}
    )

#executing the app
if __name__ == "__main__":
    app.run(debug=False,port=8050)
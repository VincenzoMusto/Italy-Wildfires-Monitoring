## main app

#importing needed libraries 
import dash
from dash import html
import dash_bootstrap_components as dbc
from PIL import Image
import os
import leafmap.foliumap as leafmap

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





m = leafmap.Map(zoom=10) #center=center, 

m.add_raster(f"static/SENTINEL2/1/2023-07-18.tiff", layer_name="Pre-fire")
# add effis_only to the map
m

# save the map as an html file
m.to_html("static/SENTINEL2/1/pre.html")



m = leafmap.Map(zoom=10) #center=center, 

m.add_raster(f"static/SENTINEL2/1/2023-07-28.tiff", layer_name="Post-fire")
# add effis_only to the map
m

# save the map as an html file
m.to_html("static/SENTINEL2/1/post.html")



m = leafmap.Map(zoom=10) #center=center, 

m.add_raster(f"static/SENTINEL2/2/2023-07-16.tiff", layer_name="Pre-fire")
# add effis_only to the map
m

# save the map as an html file
m.to_html("static/SENTINEL2/2/pre.html")


m = leafmap.Map(zoom=10) #center=center, 

m.add_raster(f"static/SENTINEL2/2/2023-07-23.tiff", layer_name="Post-fire")
# add effis_only to the map
m

# save the map as an html file
m.to_html("static/SENTINEL2/2/post.html")







m = leafmap.Map(zoom=10) #center=center, 

m.add_raster(f"static/SENTINEL2/3/2023-07-21.tiff", layer_name="Pre-fire")
# add effis_only to the map
m

# save the map as an html file
m.to_html("static/SENTINEL2/3/pre.html")


m = leafmap.Map(zoom=10) #center=center, 

m.add_raster(f"static/SENTINEL2/3/2023-07-23.tiff", layer_name="Post-fire")
# add effis_only to the map
m

# save the map as an html file
m.to_html("static/SENTINEL2/3/post.html")










m = leafmap.Map(zoom=10) #center=center, 

m.add_raster(f"static/SENTINEL2/4/2023-07-21.tiff", layer_name="Pre-fire")
# add effis_only to the map
m

# save the map as an html file
m.to_html("static/SENTINEL2/4/pre.html")


m = leafmap.Map(zoom=10) #center=center, 

m.add_raster(f"static/SENTINEL2/4/2023-07-28.tiff", layer_name="Post-fire")
# add effis_only to the map
m

# save the map as an html file
m.to_html("static/SENTINEL2/4/post.html")







m = leafmap.Map(zoom=10) #center=center, 

m.add_raster(f"static/SENTINEL2/5/2023-08-25.tiff", layer_name="Pre-fire")
# add effis_only to the map
m

# save the map as an html file
m.to_html("static/SENTINEL2/5/pre.html")


m = leafmap.Map(zoom=10) #center=center, 

m.add_raster(f"static/SENTINEL2/5/2023-08-27.tiff", layer_name="Post-fire")
# add effis_only to the map
m

# save the map as an html file
m.to_html("static/SENTINEL2/5/post.html")












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
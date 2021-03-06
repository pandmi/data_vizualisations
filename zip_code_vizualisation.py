
# import all neccesary libraries
import folium
import pandas as pd
import numpy as np
import os
import json

# passing the datas into pandas dataframe
zip_reg_raw=pd.read_csv('\\Users\\test\\Desktop\\Test_folder\\Data_file.csv')


# pivoting number of conversions from REG column and grouping them by zip codes (zip_code column)
zip_reg= zip_reg_raw[['zip_code','REG']].groupby(['zip_code'], as_index=False).sum()
# remove "de-"" prefix from zip codes
zip_reg['zip_code'] =zip_reg['zip_code'].str.replace(r'\D', '')
zip_reg['REG'] = zip_reg['REG'].replace(np.nan, 0)
# creating bins based on 4 quantiles
zip_reg['REG_bin'] = pd.qcut(zip_reg['REG'], q=4, precision=0)
# calculating percentage
zip_reg['REG_percent'] = (zip_reg['REG']/zip_reg['REG'].sum())*100

# applying filetr to the data
zip_final=zip_reg[(zip_reg.REG > 10) &(zip_reg.REG < 1000)].sort_values(by='REG', ascending=False).head(1000)



# looking into the file with german zip code datas and selecting the location where we have match with our zip_final file
# file postleitzahlen.geojson should be in the same directory where the script is running
# the easiest and most secure way is to save this file as postleitzahlen.geojson from https://github.com/yetzt/postleitzahlen/blob/master/data/postleitzahlen.geojson


with open('postleitzahlen.geojson', 'r') as jsonFile:
    data = json.load(jsonFile)
tmp = data

# remove ZIP codes not in our dataset
geozips = []
for i in range(len(tmp['features'])):
    if tmp['features'][i]['properties']['postcode'] in list(zip_final['zip_code'].unique()):
        geozips.append(tmp['features'][i])

# creating new JSON object
new_json = dict.fromkeys(['type','features'])
new_json['type'] = 'FeatureCollection'
new_json['features'] = geozips

# save JSON object as updated-file
open("updated-file.json", "w").write(
    json.dumps(new_json, sort_keys=True, indent=4, separators=(',', ': '))
)


# creating a map, figure size is importnat only if you are going to display it directly in jupyter
latitude = 51.13
longitude = 10.02
f = folium.Figure(width=1000, height=800)
germany_map = folium.Map(location=[latitude, longitude], zoom_start=5.5).add_to(f)

folium.Choropleth(
    geo_data=r'updated-file.json',
    data=zip_final,
    columns=['zip_code', 'REG'],
    key_on='feature.properties.postcode',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name= 'REG'
).add_to(germany_map)

# save the map as html - file
germany_map.save('map_vizulisation_conversions.html')

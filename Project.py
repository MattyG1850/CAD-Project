#Project Goal: use RTMA data to check for CAD in the Northeast GA/ Upstate SC area based on a CAD index developed by
#Mr Steve Nelson: If the theta-e gradient between the below locations exceeds 10 K, then there is likely a wedge front
#import all of the necessary packages first
from siphon.catalog import TDSCatalog
from datetime import datetime
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import metpy.calc as mpcalc
import metpy.plots as mpplots
import metpy.interpolate
import matplotlib.pyplot as plt
import xarray as xr
import scipy.spatial
import datetime

rtma_catalog = TDSCatalog('https://thredds-jumbo.unidata.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/catalog.xml')
rtma_data = rtma_catalog.datasets['Latest Collection for Real Time Mesoscale Analysis 2.5 km'].remote_access(use_xarray=True)
#Note: changing the two lines above will make it possible to use data other than the very latest RTMA output (archives?)

rtma_data = rtma_data.metpy.parse_cf()
#line below adds coordinates in lats and lons (were previously in x and y only)
rtma_data = rtma_data.metpy.assign_latitude_longitude(force=False)

print(rtma_data)

pres = rtma_data['Pressure_Analysis_surface'].metpy.sel().squeeze()
temp = rtma_data['Temperature_Analysis_height_above_ground'].metpy.sel().squeeze()
dewp = rtma_data['Dewpoint_temperature_Analysis_height_above_ground'].metpy.sel().squeeze()

theta_e = mpcalc.equivalent_potential_temperature(pres, temp, dewp)
theta_e = mpcalc.smooth_gaussian(theta_e, n=5)
theta_e


#We ultimately want theta-e gradients between the following airports:
GSP_lat, GSP_lon = 34.8959, -82.2172
CEU_lat, CEU_lon = 34.4020, -82.5309
GVL_lat, GVL_lon = 34.1636, -83.4881
PDK_lat, PDK_lon = 33.8768, -84.3079


df = []
dd = []
lats, lons = theta_e['latitude'].to_numpy(), theta_e['longitude'].to_numpy()
data_latlon = np.column_stack([lats.ravel(), lons.ravel()])
stations_lat = [GSP_lat, CEU_lat, GVL_lat, PDK_lat]
stations_lon = [GSP_lon, CEU_lon, GVL_lon, PDK_lon]
stations_latlon = np.column_stack([stations_lat, stations_lon])
tree = scipy.spatial.KDTree(data_latlon)
index, distance = tree.query(stations_latlon, distance_upper_bound=0.03, workers=-1)
df.append(index)
dd.append(distance)

#uncomment the lines below to see what the array outputs are
#print(df)
#print(dd)


#labeling/naming data from above arrays
GSP_ind = 0.01541369
CEU_ind = 0.00995361
GVL_ind = 0.00563323
PDK_ind = 0.00867702

GSP_dist = 1204899
CEU_dist = 1155554
GVL_dist = 1127635
PDK_dist = 1095431


#The following are the nearest neighbor coordinates for the following stations:
GSP_coord = data_latlon[GSP_dist]
CEU_coord = data_latlon[CEU_dist]
GVL_coord = data_latlon[GVL_dist]
PDK_coord = data_latlon[PDK_dist]
print(GSP_coord)
print(CEU_coord)
print(GVL_coord)
print(PDK_coord)


mag, lats, lons = theta_e.to_numpy(), theta_e['latitude'].to_numpy(), theta_e['longitude'].to_numpy()
all_data_latlon = np.column_stack([mag.ravel(), lats.ravel(), lons.ravel()])
#print(all_data_latlon)
GSP_data = all_data_latlon[GSP_dist]
CEU_data = all_data_latlon[CEU_dist]
GVL_data = all_data_latlon[GVL_dist]
PDK_data = all_data_latlon[PDK_dist]

print(GSP_data)
type(GSP_data)


#Theta-e values for the stations!
GSP_value = round(GSP_data[0], 2)
CEU_value = round(CEU_data[0], 2)
GVL_value = round(GVL_data[0], 2)
PDK_value = round(PDK_data[0], 2)

print('These are the current theta-e values for the stations in the order as shown above: (in degrees K)')
print(GSP_value,', ', CEU_value,', ', GVL_value,', and ', PDK_value)


#Theta-e gradients: (note if gradient is negative, the northernmost station has a larger value for theta-e)
GSP_to_PDK = round(GSP_value - PDK_value, 2)
CEU_to_PDK = round(CEU_value - PDK_value, 2)
GVL_to_PDK = round(GVL_value - PDK_value, 2)
GSP_to_CEU = round(GSP_value - CEU_value, 2)
GSP_to_GVL = round(GSP_value - GVL_value, 2)
CEU_to_GVL = round(CEU_value - GVL_value, 2)
GVL_to_PDK = round(GVL_value - PDK_value, 2)


def wedge_check():
    if GSP_to_PDK >= 10:
        return 'YES there is a wedge front'
    elif CEU_to_PDK >= 10:
        return 'YES there is a wedge front'
    elif GVL_to_PDK >= 10:
        return 'YES there is a wedge front'
    elif GSP_to_CEU >= 10:
        return 'YES there is a wedge front'
    elif GSP_to_GVL >= 10:
        return 'YES there is a wedge front'
    elif CEU_to_GVL >= 10:
        return 'YES there is a wedge front'
    elif GVL_to_PDK >= 10:
        return 'YES there is a wedge front'
    else:
        return 'There is not a significant wedge front in the NE Georgia/ Upstate SC area'

wedge_check()


def wedge_front_locator():
    if GSP_to_CEU >= 10:
        return 'There is a wedge front between the Greenville-Spartanburg airport and the Clemson airport'
    elif CEU_to_GVL >= 10:
        return 'There is a wedge front between the Clemson airport and the Gainesville airport'
    elif GVL_to_PDK >= 10:
        return 'There is a wedge front between the Gainesville airport and the Peachtree-DeKalb airport'
    else:
        return 'There is not a significant wedge front between the above list of stations'

wedge_front_locator()


#Plotting code below:       *note: when using Jupyter this runs automatically, but print statements may be needed to show the plot on other platforms

print("Below is an image with temperature shaded in, and equivalent potential temperature (theta-e) countoured")
plot_proj = theta_e.metpy.cartopy_crs

fig = plt.figure(figsize=(20,10))
ax = fig.add_subplot(1, 1, 1, projection=plot_proj)
ax.set_extent((-86, -81, 32, 37), crs=ccrs.PlateCarree())
ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
ax.add_feature(cfeature.STATES, linewidth=0.33)

ax.contourf(temp.metpy.x, temp.metpy.y, temp - 273.15, transform=temp.metpy.cartopy_crs, levels=np.arange(-20, 50, 4), cmap='coolwarm')
ax.contour(theta_e.metpy.x, theta_e.metpy.y, theta_e, levels=np.arange(240, 400, 4), colors='tab:olive', transform=theta_e.metpy.cartopy_crs)
plt.title(datetime.datetime.utcnow().strftime('%Y-%m-%d %HZ'))



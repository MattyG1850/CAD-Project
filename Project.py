#import all of the necessary packages first (more to add later)
from siphon.catalog import TDSCatalog
from datetime import datetime
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import metpy.calc as mpcalc
import metpy.plots as mpplots
import matplotlib.pyplot as plt

dt = datetime.utcnow()

rtma_catalog = TDSCatalog('https://thredds-jumbo.unidata.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/catalog.xml')
#rtma_catalog = TDSCatalog('https://thredds.ucar.edu/thredds/catalog/grib/NCEP/RTMA/CONUS_2p5km/latest.xml')
#rtma_data = rtma_catalog.datasets['Full Collection (Reference / Forecast Time) Dataset'].remote_access(use_xarray=True)
rtma_data = rtma_catalog.datasets['Latest Collection for Real Time Mesoscale Analysis 2.5 km'].remote_access(use_xarray=True)
rtma_data = rtma_data.metpy.parse_cf()

#print(rtma_data)

pres = rtma_data['Pressure_Analysis_surface'].metpy.sel().squeeze()
temp = rtma_data['Temperature_Analysis_height_above_ground'].metpy.sel().squeeze()
dewp = rtma_data['Dewpoint_temperature_Analysis_height_above_ground'].metpy.sel().squeeze()

#print(pres)
#print(temp)
#print(dewp)

theta_e = mpcalc.equivalent_potential_temperature(pres, temp, dewp)
theta_e = mpcalc.smooth_gaussian(theta_e, n=4)

plot_proj = theta_e.metpy.cartopy_crs

fig = plt.figure(figsize=(20,10))
ax = fig.add_subplot(1, 1, 1, projection=plot_proj)
ax.set_extent((-90, -75, 31, 40), crs=ccrs.PlateCarree())
ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.75)
ax.add_feature(cfeature.STATES, linewidth=0.33)

ax.contourf(temp.metpy.x, temp.metpy.y, temp - 273.15, transform=temp.metpy.cartopy_crs, levels=np.arange(-20, 50, 4), cmap='coolwarm')
ax.contour(theta_e.metpy.x, theta_e.metpy.y, theta_e, levels=np.arange(240, 400, 4), colors='tab:olive', transform=theta_e.metpy.cartopy_crs)
plt.title(dt.strftime('%Y-%m-%d %HZ'))



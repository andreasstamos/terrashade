# TerraShade
# Copyright (C) 2024  Andreas Stamos
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math
import datetime
import skyfield         # used for astronomic computations
import skyfield.api
import geopy.distance   # wrappes GeographicLib, an implementation of Karney algorithms for ellipsoids
import pyproj
import numpy as np

import maxdistance
import srtmcache

print("TerraShade")
print("Copyright (C) 2024  Andreas Stamos")
print("-----------")
print("Computer of the time the Sun becomes obscured by terrain (e.g. mountains)")
print("-----------")
print("You will later be asked to login with you credentials to NASA Earthdata. Please create an account if you do not have one.")
print("-----------")
print("Enter your coordinates using the WGS84 coordinate system.")
print("(If you are unsure what WGS84 is, you can likely ignore this note, as your coordinates are most likely already in this format.)")
print()

lat = float(input("Enter your latitude (in degrees, positive if north): "))
lon = float(input("Enter your longitude (in degrees, positive if east): "))

print("Below you have to enter your desired time. The time shall be in ISO format.")
print("e.g. 2024-08-12T18:00:00+03:00")

t = input("Enter the starting time for the search: ")
t = datetime.datetime.fromisoformat(t)


srtm_cache = srtmcache.SRTMCache()

elev = srtm_cache.get_elevation(lat, lon)

wgs84 = pyproj.Proj(proj="latlong", datum="WGS84")
ecef = pyproj.Proj(proj="geocent", datum="WGS84")
transformer = pyproj.Transformer.from_proj(wgs84, ecef)

# WGS84 reference ellipsoid parameters
a = 6378137.0  
f = 1 / 298.257223563
b = a * (1 - f)

def altitude(lat_p, lon_p, elev_p, lat_s, lon_s, elev_s):
    p = transformer.transform(lon_p, lat_p, elev_p, radians=False)
    s = transformer.transform(lon_s, lat_s, elev_s, radians=False)

    p, s = np.array(p), np.array(s)

    n_p = np.array((p[0] / a**2, p[1] / a**2, p[2] / b**2))
    n_p /= np.linalg.norm(n_p)

    ps = s - p
    ps /= np.linalg.norm(ps)

    return np.degrees(np.arcsin(np.dot(n_p, ps)))

     
def check(alt, az):
    maxd = math.ceil(maxdistance.maxdistance(alt, elev))

    for d in range(30,maxd,30):
        n = geopy.distance.geodesic(meters=d).destination((lat, lon), bearing = az) 
        nlat, nlon = n.latitude, n.longitude

        nelev = srtm_cache.get_elevation(nlat, nlon)

        nalt = altitude(lat, lon, elev, nlat, nlon, nelev)

        if nalt>alt: return True

    return False


ts = skyfield.api.load.timescale()
eph = skyfield.api.load("de421.bsp")

loc = eph['earth'] + skyfield.api.wgs84.latlon(lat, lon, elevation_m=elev)

sun = eph['sun']

dt = datetime.timedelta(minutes=1)

while True:
    t_s = ts.from_datetime(t)
    astrometric = loc.at(t_s).observe(sun)
    alt, az, _ = astrometric.apparent().altaz()

    if check(alt.degrees, az.degrees): break
    print("Checking: ", t) 
    t += dt

print("------------------")
print("Shadow time: ", t)

srtm_cache.close()


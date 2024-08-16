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

import scipy.optimize
import math

R = 6378137.0   # semi-major axis of WGS84 (circumscribed sphere of WGS84 reference ellipsoid)
h2 = 8000.0     # highest elevation on Earth (plus some error margin) -- Everest mountain top
margin = 0.05

def maxdistance(phi, elev):
    cosp = math.cos(math.radians(phi))

    h1 = elev
    def equation(t):
        return math.sin(t)**2 * (h2+R)**2 - cosp**2 * ((h1+R)**2 + (h2+R)**2 - 2*(h1+R)*(h2+R)*math.cos(t))

    t = scipy.optimize.root_scalar(equation, x0=0.1)
    t = t.root
    return R*t * (1+margin)


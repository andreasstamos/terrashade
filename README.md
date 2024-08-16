# TerraShade

## Computation of the time the Sun becomes obscured by terrain (e.g. mountains)

![Banner](/images/banner.png)

### Quick Start

1. If you do not have one, create an account at [NASA Earthdata](https://www.earthdata.nasa.gov/).
2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the main program:

   ```bash
   python3 main.py
   ```

4. Follow the instructions. Data will be downloaded automatically, as necessary.

### How It Works

The trajectory of the Sun is traced in time with a sampling interval of 1 minute. At each time sample, the azimuth and altitude of the Sun are computed (apparent position), according to the DE421 ephemerides published by NASA Jet Propulsion Laboratory.

Then, the line at the heading (azimuth) of the Sun (note that it is not exactly 270° but only approximately west) is considered and sampled at a 30m interval (30m = 1" = spatial accuracy of SRTM).

To determine the maximum distance from the observer within which terrain features may hide the Sun, the maximum possible height of a mountain is considered (i.e., Mount Everest with a height of 8000m, with a small error margin added). The reasoning here is that any terrain further away, in order to have an altitude angle higher than the Sun's, would have to be taller than the tallest mountain, which cannot happen.

Given that an upper bound of the distance is being searched for here (and not a precise value), the circumscribing sphere of the WGS84 reference ellipsoid is considered (this means the radius $R$ is the semi-major axis of the WGS84 ellipsoid parameters). In the following figure, $h_1$ is the elevation of the observer, $h_2$ is the elevation of the highest mountain, $\phi$ is the altitude of the Sun, and $\theta$ is the angle between the radii of the observer and the highest mountain. By applying the law of cosines for $\alpha$, and then the law of sines for $(\alpha, \theta)$ and $(h_2 + R, 90^\circ + \phi)$, it can be shown that:

```math
\frac{\cos \phi}{h_2 + R} = \frac{\sin \theta}{\sqrt{(h_1 + R)^2 + (h_2 + R)^2 - 2 (h_1 + R)(h_2 + R) \cos \theta}}
```

![Figure for the maximum distance from the observer within which terrain features may hide the Sun](/images/maxdist.svg)

This equation is numerically solved for $\theta$, which is then converted to arc distance as $d_{max} = \theta \cdot R$. On this value, a 5% margin of error is added just to be sure. The result is the maximum distance from the observer (in the heading of the Sun) which will be checked for terrain that might hide the Sun.

Then the sample points have to be computed. Their coordinates are computed as points on the WGS84 reference ellipsoid with specific distance and azimuth from the point of the observer. For this computation, the [Karney (2013)](https://doi.org/10.1007/s00190-012-0578-z) algorithms for geodesics on ellipsoids are used (Direct Problem). More specifically, the `GeographicLib` C++ implementation is used, wrapped by `geopy.distance.geodesic`.

Afterwards, the SRTM (Shuttle Radar Topographic Mission, 1" = 30m spatial accuracy, global coverage) digital elevation model (DEM), which was collected by the Space Shuttle Endeavour during the STS-99 mission, is used to find the elevation of each sample point. The data are freely provided by NASA. The elevation of the observer is also found from the DEM. (One could have instead used GPS to find this elevation with increased accuracy.)

Knowing the elevations and the coordinates of the observer and the sample point, the altitude of the sample point, as seen from the observer, has to be computed. This is defined as the angle of the line of sight of the sample point with the horizon. Firstly, the coordinates of the two points are converted from ellipsoidal coordinates (on the reference ellipsoid WGS84) to 3D Cartesian coordinates with the origin at a supposed center of the Earth (this coordinate system is usually called ECEF -- Earth-centered, Earth-fixed). The equations for the conversion can be seen [here](https://en.wikipedia.org/wiki/Geographic_coordinate_conversion#From_geodetic_to_ECEF_coordinates). The `pyproj` implementation of these equations is used. Let's call $P$ the point of the observer and $S$ the sample point. The vector $\overrightarrow{PS}$ can now be computed in Cartesian coordinates.

The vector of the horizon at $P$ is also necessary. The Cartesian equation of the ellipsoid is:

```math
\frac{x^2}{\alpha^2} + \frac{y^2}{\alpha^2} + \frac{z^2}{\beta^2} = 1
```

By taking the gradient, the (non-normalized) normal vector $\mathbf{n}$ is found to be:

```math
\mathbf{n} = \left( \frac{x}{\alpha^2}, \frac{y}{\alpha^2}, \frac{z}{\beta^2} \right)
```

The vector of the horizon is the tangent vector to the ellipsoid, which is perpendicular to the normal vector. Therefore, the angle of a vector with the horizon is complementary to the angle with the normal vector. The angle of the line of sight (this is the $\overrightarrow{PS}$) with the normal vector is:

```math
\cos^{-1} \left(\frac{\overrightarrow{PS} \cdot \mathbf{n}}{|\overrightarrow{PS}| \cdot |\mathbf{n}|}\right)
```

Therefore, the angle of the line of sight with the horizon is:

```math
\sin^{-1} \left(\frac{\overrightarrow{PS} \cdot \mathbf{n}}{|\overrightarrow{PS}| \cdot |\mathbf{n}|}\right)
```

Finally, we determine whether the terrain at the sample point obscures the Sun by checking whether the computed altitude of the terrain is higher than the Sun's altitude at that moment.

All the sample points of the line with heading of the Sun's, up to the upper distance bound calculated before, are checked, and afterwards, the next time sample is considered. This process continues until terrain is found that obscures the Sun.

---

### Experimental Validation

It was experimentally found that at a point with coordinates $(39.4729881^\circ N, 21.3201801^\circ E)$ (Football Field of Mesochora, Trikala, Greece) on 12/8/2024, the Sun was hidden by a mountain at 19:08 EEST (there could be a 1-minute error here -- or there could be not). The above procedure computed that the Sun would hide at 19:10 EEST, which is considered a reasonably accurate result.

---

© 2024 Andreas Stamos. All rights reserved.


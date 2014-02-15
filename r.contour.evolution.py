# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 22:49:47 2014

@author: Vaclav Petras
"""

import grass.script.core as gcore
from grass.script.core import run_command
from grass.script.raster import mapcalc as rmapcalc

# create contours from elevation for each year
for elevation in elevations:
    run_command('r.contour', input=elevation, output=contours, step=2)
    # extract one contour level (height)
    run_command('v.extract', input=contours, where='level=%d' % level,
                output=contours_level)
    # convert contour line to (dense enough) set of points
    run_command('v.to.points', input=contour_level,
                output=contours_level_points, dmax=1)
    # discard z coordinate (-t flag) and assign time to z (Space Time Cube)
    run_command('v.transform', flags='t', input=contours_level_points,
                output=contours_level_points_stc, zshift=year)
    contours_level_points_stcs.append(contours_level_points_stc)


# patch points of the same original height (contour level) from all years together
run_command('v.patch', input=contours_level_points_stcs,
            output=stc_surface_points)
# create a surface based on the points (in STC)
run_command('v.surf.rst', input=stc_surface_points,
            elevation=stc_surface_elevation,
            slope=stc_surface_slope,
            aspect=stc_surface_aspect)

# invert surface to have time going down the hill
rmapcalc("elev_1999_2007_contours_14_surface_inv = -elev_1999_2007_contours_14_surface")
# compute surface properties
# computing slope (surface gradient magnitude)
# and aspect (surface gradient direction projected to xy plane)
run_command('r.slope.aspect', elevation="elev_1999_2007_contours_14_surface_inv",
            slope="elev_1999_2007_contours_14_surface_slope",
            aspect="elev_1999_2007_contours_14_surface_aspect",
            format="degrees", precision="FCELL",
            dx="elev_1999_2007_contours_14_surface_dx",
            dy="elev_1999_2007_contours_14_surface_dy",
            zfactor=1.0, min_slp_allowed=0.0)
# invert slope to have higher values where slope is lower
# to avoid negative values subtract from global max instead of 0 
rmapcalc("elev_1999_2007_contours_14_surface_slope_inv = 68 - elev_1999_2007_contours_14_surface_slope")

# in GUI, add a raster flow layer
# d.rast.arrow map=elev_1999_2007_contours_14_surface_aspect arrow_color=black grid_color=none skip=3 scale=2 magnitude_map=elev_1999_2007_contours_14_surface_slope_inv

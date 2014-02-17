
#!/usr/bin/env python
#
############################################################################
#
# MODULE:       r.contour.evolution
# AUTHOR(S):    Vaclav Petras
# PURPOSE:      Outputs raster maps prepared for a Leaflet web map
#
# COPYRIGHT:    (C) 2014 by Vaclav Petras and the GRASS Development Team
#
#               This program is free software under the GNU General Public
#               License (>=v2). Read the file COPYING that comes with GRASS
#               for details.
#
#############################################################################


#%module
#% description: Outputs raster maps prepared for a Leaflet web map
#% keywords: raster
#% keywords: export
#% keywords: visualization
#% keywords: web
#%end
#%option G_OPT_R_INPUT
#% key: raster
#% label: Name(s) of input raster map(s)
#% description: Either this or strds option must be used to specify the input.
#% multiple: yes
#% required: yes
#%end
#%option
#% key: years
#% type: integer
#% label: Years
#% description: Must be same count of rasters
#% multiple: yes
#% required: yes
#%end
#%option
#% key: level
#% type: double
#% label: Contour level
#% description: Contour level where raster map with vector field will be generated
#% multiple: no
#% required: yes
#%end


# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 22:49:47 2014

@author: Vaclav Petras
"""

import os

import grass.script.core as gcore
from grass.script.core import run_command, parse_command
from grass.script.raster import mapcalc as rmapcalc

options, flags = gcore.parser()
elevations = options['raster'].split(',')
years = options['years'].split(',')
level =float(options['level'])


#def create_tmp_map_name(name):
#    return '{mod}_{pid}_{map_}_tmp'.format(mod='rcontourevolution',
#                                           pid=os.getpid(),
#                                           map_=name)

def create_tmp_map_name(name):
    return '{mod}_{map_}'.format(mod='rcontourevolution',
                                 map_=name)

contours_level_points_stcs = []

# create contours from elevation for each year
for i, elevation in enumerate(elevations):
    # create names for temporary maps
    contours = create_tmp_map_name(elevation + '_contours')
    level_str = str(level).replace('.', '_')
    contours_level = create_tmp_map_name(elevation + '_contours_level_' + level_str)
    contours_level_points = create_tmp_map_name(elevation + '_contours_level_' + level_str + '_points')
    contours_level_points_stc = create_tmp_map_name(elevation + '_contours_level_' + level_str + '_points_stc')

    run_command('r.contour', input=elevation, output=contours, step=2)
    # extract one contour level (height)
    run_command('v.extract', input=contours, where='level=%f' % level,
                output=contours_level)
    # convert contour line to (dense enough) set of points
    run_command('v.to.points', input=contours_level,
                output=contours_level_points, dmax=1)
    # discard z coordinate (-t flag) and assign time to z (Space Time Cube)
    run_command('v.transform', flags='t', input=contours_level_points,
                output=contours_level_points_stc, zshift=years[i])
    contours_level_points_stcs.append(contours_level_points_stc)

# create names for temporary maps
stc_surface_increasing_points = create_tmp_map_name('stc_surface_increasing_points')
stc_surface_increasing_elevation = create_tmp_map_name('stc_surface_increasing_elevation')
stc_surface_increasing_slope = create_tmp_map_name('stc_surface_increasing_slope')
stc_surface_increasing_aspect = create_tmp_map_name('stc_surface_increasing_aspect')
stc_surface_decreasing_elevation = create_tmp_map_name('stc_surface_decreasing_elevation')
stc_surface_decreasing_slope = create_tmp_map_name('stc_surface_decreasing_slope')
stc_surface_decreasing_aspect = create_tmp_map_name('stc_surface_decreasing_aspect')
stc_surface_decreasing_slope_inverted = create_tmp_map_name('stc_surface_decreasing_slope_inverted')

# patch points of the same original height (contour level) from all years together
run_command('v.patch', input=contours_level_points_stcs,
            output=stc_surface_increasing_points)
# create a surface based on the points (in STC)
run_command('v.surf.rst', input=stc_surface_increasing_points,
            elevation=stc_surface_increasing_elevation,
            slope=stc_surface_increasing_slope,
            aspect=stc_surface_increasing_aspect)

# invert surface to have time going down the hill
rmapcalc('%s = -%s' % (stc_surface_decreasing_elevation, stc_surface_increasing_elevation))
# compute surface properties
# computing slope (surface gradient magnitude)
# and aspect (surface gradient direction projected to xy plane)
run_command('r.slope.aspect', elevation=stc_surface_decreasing_elevation,
            slope=stc_surface_decreasing_slope,
            aspect=stc_surface_decreasing_aspect,
            format='degrees', precision='FCELL',
            zfactor=1.0, min_slp_allowed=0.0)
# invert slope to have higher values where slope is lower
# to avoid negative values subtract from global max instead of 0 
# TODO: some other "inversion" might be better
stc_surface_stats = parse_command('r.univar', map=stc_surface_decreasing_slope,
                                  flags='g')
rmapcalc('%s = %s - %s' % (stc_surface_decreasing_slope_inverted,
                           stc_surface_stats['max'],
                           stc_surface_decreasing_slope))

# in GUI, add a raster flow layer
# d.rast.arrow map=elev_1999_2007_contours_14_surface_aspect arrow_color=black grid_color=none skip=3 scale=2 magnitude_map=elev_1999_2007_contours_14_surface_slope_inv

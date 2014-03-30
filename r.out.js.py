#!/usr/bin/env python
#
############################################################################
#
# MODULE:       r.out.js
# AUTHOR(S):    Vaclav Petras
# PURPOSE:      Outputs raster map as JavaScript two dimensional array
#
# COPYRIGHT:    (C) 2014 by Vaclav Petras and the GRASS Development Team
#
#               This program is free software under the GNU General Public
#               License (>=v2). Read the file COPYING that comes with GRASS
#               for details.
#
#############################################################################


#%module
#% description: Outputs raster map as JavaScript two dimensional array
#% keywords: raster
#% keywords: export
#% keywords: visualization
#% keywords: web
#%end
#%option G_OPT_R_INPUT
#% multiple: no
#% required: yes
#%end
#%option G_OPT_F_OUTPUT
#% multiple: no
#% required: yes
#%end


# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 18:29:03 2014

@author: Vaclav Petras, <wenzeslaus gmail com>
"""

import math
import numpy
from grass.pygrass.raster import RasterRow
#
#with RasterRow('aspect') as elev:
#    for row in elev:
#        l = []
#        for cell in row:
#            l.append(str(cell))
#        print ' '.join(l)


direction = RasterRow('elev_lid_aspect')
speed = RasterRow('elev_lid_slope')

direction.open()
speed.open()

rows = []
for i, dir_row in enumerate(direction):
    speed_row = speed[i]
    vectors = []
    for j, dir_cell in enumerate(dir_row):
        speed_cell = speed_row[j]
        dx = numpy.cos(dir_cell / 180. * math.pi) * speed_cell
        dy = - numpy.sin(dir_cell / 180. * math.pi) * speed_cell
        m = speed_cell
        #dx = 5;
        #dy = 0;
        vectors.append('[' + ','.join([str(dx), str(dy), str(m)]) + ']')

    #rows.append('[' + ','.join(vectors) + ']\n')
    rows.append(vectors)

#print 'columns = ' + '[' + ','.join(rows) + ']'

ncols = len(rows[0])

columns = []
for i in range(ncols):
    column = []
    for row in rows:
        column.append(row[i])
    columns.append('[' + ','.join(column) + ']\n')

print 'columns = ' + '[' + ','.join(columns) + ']'

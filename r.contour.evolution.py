# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 22:49:47 2014

@author: Vaclav Petras
"""

# create contours from elevation for each year
r.contour input=elev_1999_1m output=elev_1999_contours step=2
# extract one contour level (height)
v.extract input=elev_1999_contours where=level=14 output=elev_1999_contours_14
# convert contour line to (dense enough) set of points
v.to.points input=elev_1999_contours_14 output=elev_1999_contours_14_points dmax=1
# discard z coordinate (-t flag) and assign time to z (Space Time Cube)
v.transform -t input=elev_1999_contours_14_points output=elev_1999_contours_14_points_stc zshift=1999
# patch points of the same original height (contour level) from all years together
v.patch input=elev_1999_contours_14_points_stc,elev_2007_contours_14_points_stc output=elev_1999_2007_contours_14_stc
# create a surface based on the points (in STC)
v.surf.bspline input=elev_1999_2007_contours_14_stc raster_output=elev_1999_2007_contours_14_surface

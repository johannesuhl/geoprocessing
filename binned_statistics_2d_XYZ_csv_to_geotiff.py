# -*- coding: utf-8 -*-
"""
Created on Fri Nov 06 13:20:58 2020

@author: Johannes Uhl, Department of Geography, University of Colorado Boulder
"""

#####################################

### the folder csv_folder contains one or more CSV files.
### each csv file contains at least 3 columns:
### lon,lat, and <target_variable>
### indstead on lon,lat any cartesian coordinate system can be used.
### proj4 string must be given in <crs_coords>
### we want to compute statistics on <target_variable> within grid cells
### given in the template geotif <template_raster>
### <template_raster> needs to be in the spatial reference system 
### as defined in the proj4 string <crs_grid>
### the script will compute the statistic defined in <statistic>
### and <statistic_str>
### the output gridded surface will be stored as LZW compressed geotiff in
### <surface_folder>

### Requirements: above python packages, GDAL's gdal_edit tool 
### (path needs to be specified in <gdal_edit>)

#####################################
import os
import pandas as pd
import scipy.stats
import geopandas as gp
from osgeo import gdal
from gdalconst import GA_ReadOnly
import subprocess
import time
import numpy as np
#####################################
   
####user parameters
target_variable = 'z'
xcoo_col,ycoo_col = 'x','y'    
statistic = np.mean
statistic_str= 'mean'    
template_raster = ''#PATH_TO_FBUY_RASTER (.tif)
csv_folder = ''# path where csv files with input (x,y,target_variable) are stored
surface_folder = ''#path where output tif files are stored
bitdepth = gdal.GDT_Int16 ## or gdal.GDT_Float32, whatever is suitable

crs_coords = '+proj=longlat +ellps=clrk66 +datum=NAD27 +no_defs' #source SRS
crs_grid = '+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23.0 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs' #target SRS

gdal_edit = r'C:\Python27\python C:\OSGeo4W\bin\gdal_edit.py'

def mode(x):
    vals,counts = np.unique(x, return_counts=True)
    index = np.argmax(counts)
    return vals[index]

def gdalNumpy2floatRaster_compressed(array,outname,template_georef_raster,x_pixels,y_pixels,px_type):

    dst_filename = outname

    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(dst_filename,x_pixels, y_pixels, 1, px_type)   
    dataset.GetRasterBand(1).WriteArray(array)                
    mapraster = gdal.Open(template_georef_raster, GA_ReadOnly)
    proj=mapraster.GetProjection() #you can get from a existing tif or import 
    dataset.SetProjection(proj)
    dataset.FlushCache()
    dataset=None                

    #set bounding coords
    ulx, xres, xskew, uly, yskew, yres  = mapraster.GetGeoTransform()
    lrx = ulx + (mapraster.RasterXSize * xres)
    lry = uly + (mapraster.RasterYSize * yres)            
    mapraster = None
                    
    gdal_cmd = gdal_edit+' -a_ullr %s %s %s %s "%s"' % (ulx,uly,lrx,lry,outname)
    print(gdal_cmd)
    response=subprocess.check_output(gdal_cmd, shell=True)
    print(response)
    
    outname_lzw=outname.replace('.tif','_lzw.tif')
    gdal_translate = r'gdal_translate %s %s -co COMPRESS=LZW' %(outname,outname_lzw)
    print(gdal_translate)
    response=subprocess.check_output(gdal_translate, shell=True)
    print(response)
    os.remove(outname)
    os.rename(outname_lzw,outname)
        

raster = gdal.Open(template_raster)
cols = raster.RasterXSize
rows = raster.RasterYSize
geotransform = raster.GetGeoTransform()
topleftX = geotransform[0]
topleftY = geotransform[3]
pixelWidth = int(abs(geotransform[1]))
pixelHeight = int(abs(geotransform[5]))
rasterrange=[[topleftX,topleftX+pixelWidth*cols],[topleftY-pixelHeight*rows,topleftY]]    
del raster

out_surface =np.zeros((cols,rows)).astype(np.float32)

counter=0
for file in os.listdir(csv_folder): 
    if not '.csv' in file:
        continue
    
    indf = pd.read_csv(csv_folder+os.sep+file)   
    if not target_variable in indf.columns:
        continue
    indf = indf.dropna(subset=[target_variable])
    indf=indf[[xcoo_col,ycoo_col,target_variable]]            
    starttime=time.time()
    counter+=1
    gpdf = gp.GeoDataFrame(indf,geometry=gp.points_from_xy(indf[xcoo_col].values, indf[ycoo_col].values))
    gpdf.crs = crs_coords
    gpdf.geometry = gpdf.geometry.to_crs(crs_grid)
    statsvals = gpdf[target_variable].values    
    curr_surface = scipy.stats.binned_statistic_2d(gpdf.geometry.x.values,gpdf.geometry.y.values,statsvals,statistic,bins=[cols,rows],range=rasterrange)        
    out_surface = np.maximum(out_surface,np.nan_to_num(curr_surface.statistic))        
    print (counter,file,time.time() - starttime)

gdalNumpy2floatRaster_compressed(np.rot90(out_surface),surface_folder+os.sep+'surface_%s_%s.tif' %(target_variable,statistic_str),template_raster,cols,rows,bitdepth)

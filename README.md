# Geoprocessing
## Selected python scripts for geoprocessing using open source geospatial resources

<img width="700" alt="java 8 and prio java 8  array review example" src="https://github.com/johannesuhl/geoprocessing/blob/main/img3.jpg">

## binned_statistics_2d_XYZ_csv_to_geotiff.py

-- Rasterization of 2d point data (x,y) with an attribute z into a grid of arbitrary cellsize and spatial reference system, using a user-specified summary statistic f(z) applied at the grid-cell level.

-- Input: CSV file holding (x,y,z) data

-- Output: A GeoTIFF containing a gridded surface, with f(z) in each grid cell.

-- f(z) can be the mean, median, count, diversity, etc.

This script generates a gridded surface in GeoTiff format, based on one or more CSV files holding marked points (i.e., [x,y,z] with x and y being geospatial coordinates and z being a variable of interest to be summarized), using scipy.stats.binned_statistic_2d() and GDAL.

Suitable for country and continental scale data processing. The output .tif will be LZW-compressed.
Each CSV file may hold the data for a geographic sub-region within the total area of interest.
However, the content of the CSV files may not overlap spatially, as f(z) is added cell-by-cell to a zero raster for each CSV file.
This strategy is very efficient, but may produce inaccurate results at "overlapping" grid cells (e.g., at the edge between two adjacebt sub-regions).
A template GeoTiff is required that dictates the target grid.

Johannes H. Uhl
University of Colorado Boulder, USA

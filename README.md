# geoprocessing
Selected python scripts for geoprocessing using open source geospatial resources

# binned_statistics_2d_XYZ_csv_to_geotiff.py
Generates a gridded surface in GeoTiff format, based on one or more CSV files holding marked points (i.e., [x,y,z] with x and y being geospatial coordinates and z being the variable to be summarized), using scipy.stats.binned_statistic_2d() and GDAL.
Suitable for country and continental scale data processing. The output .tif will be LZW-compressed.
Each CSV file may hold the data for a geographic region within the total area of interest.
A template GeoTiff is required that dictates the target grid.

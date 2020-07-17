import os

from cima.goes.tiles import LatLonRegion, generate_region_data, DatasetRegion, SatBandKey, RegionIndexes, copy_variable
from cima.goes.storage import GCS
from cima.goes import ProductBand, Product, Band
from netCDF4 import Dataset
import numpy as np

gcs = GCS()


##################
# Define SA region
##################
def get_SA_region() -> LatLonRegion:
    return LatLonRegion(
        lat_south=-53.9,
        lat_north=15.7,
        lon_west=-81.4,
        lon_east=-34.7,
    )


########################################################
# Get Google Cloud Blobs for a product at a certain time
########################################################
def get_blobs(product_band: ProductBand, year, month, day, hour):
    return gcs.one_hour_blobs(year=year, month=month, day=day, hour=hour, product_band=product_band)


def get_dataset(product_band):
    year = 2020
    month = 4
    day = 20
    hour = 15
    blob = get_blobs(product_band, year, month, day, hour).blobs[0]

    return gcs.get_dataset(blob)


def set_institutional_data(dataset):
    dataset.institution = 'Center for Oceanic and Atmospheric Research(CIMA), University of Buenos Aires (UBA) > ARGENTINA'
    dataset.creator_name = "Juan Ruiz and Paola Salio"
    dataset.creator_email = "jruiz@cima.fcen.uba.ar, salio@cima.fcen.uba.ar"
    dataset.instrument_type = "GOES R Series Advanced Baseline Imager"
    dataset.spatial_resolution = "2km at nadir"
    dataset.orbital_slot = "GOES-East"
    dataset.geospatial_lat_min = -53.9
    dataset.geospatial_lat_max = 15.7
    dataset.geospatial_lon_min = -81.4
    dataset.geospatial_lon_max = -34.7


def set_dataset_variables(dataset, info_dataset):
    dataset.summary = 'This file contains the brightness temperature of channel 13 from GOES 16 satellite, within the area of South America delimited approximately by latitude 15.7°N and 53.9°S; longitude 81.4°W and 34.7°W. To obtain the corresponding Lat-Lon grids, vectors cutting x and y are attached respectively, or you can download the file with the grids generated "SA-CMIPF-2km-75W" and "SA-CMIPF-2km-89W" in the project root directory'
    set_institutional_data(dataset)

    y_min = info_dataset.row_min
    y_max = info_dataset.row_max
    x_min = info_dataset.col_min
    x_max = info_dataset.col_max

    dataset.row_min = np.short(y_min)
    dataset.row_max = np.short(y_max)
    dataset.col_min = np.short(x_min)
    dataset.col_max = np.short(x_max)

    y_dim = y_max-y_min
    x_dim = x_max-x_min

    dataset.createDimension('cropped_y', y_dim)
    dataset.createDimension('cropped_x', x_dim)
    copy_variable(info_dataset.variables['x'], dataset)
    copy_variable(info_dataset.variables['y'], dataset)


def set_info_variables(dataset, rdata):
    copy_variable(rdata.goes_imager_projection, dataset)
    dataset.col_min = np.short(rdata.indexes.x_min)
    dataset.col_max = np.short(rdata.indexes.x_max)
    dataset.row_min = np.short(rdata.indexes.y_min)
    dataset.row_max = np.short(rdata.indexes.y_max)

    if int(rdata.sat_band_key.sat_lon) == -89:
        dataset.summary = 'This file contains the latitude - longitude grids, corresponding to the period between 07/10/2017 and 11/30/2017, where GOES16 was in the position 89.3 degrees west. The grid was cropped within the area of South America delimited approximately by latitude 15.7°N and 53.9°S; longitude 81.4°W and 34.7°W.'
    elif int(rdata.sat_band_key.sat_lon) == -75:
        dataset.summary = 'This file contains the latitude - longitude corresponding grids from 12/14/2017. GOES-16 reached 75.2 degrees west on December 11, 2017 and data flow resumed to users on December 14. The grid was cropped within the area of South America delimited approximately by latitude 15.7°N and 53.9°S; longitude 81.4°W and 34.7°W.'

    set_institutional_data(dataset)

    y_min = rdata.indexes.y_min
    y_max = rdata.indexes.y_max
    x_min = rdata.indexes.x_min
    x_max = rdata.indexes.x_max

    y_dim = y_max-y_min
    x_dim = x_max-x_min

    cropping_y = dataset.createDimension('cropped_y', y_dim)
    cropping_x = dataset.createDimension('cropped_x', x_dim)

    # create latitude axis
    new_lats = dataset.createVariable('lats', rdata.lats.dtype, ('cropped_y', 'cropped_x'))
    new_lats.standard_name = 'latitude'
    new_lats.long_name = 'latitude'
    new_lats.units = 'degrees_north'
    new_lats.axis = 'Y'
    new_lats[:,:] = rdata.lats[y_min: y_max, x_min: x_max]

    # create longitude axis
    new_lons = dataset.createVariable('lons', rdata.lons.dtype, ('cropped_y', 'cropped_x'))
    new_lons.standard_name = 'longitude'
    new_lons.long_name = 'longitude'
    new_lons.units = 'degrees_east'
    new_lons.axis = 'X'
    new_lons[:,:] = rdata.lons[y_min: y_max, x_min: x_max]

    # create x
    new_x = dataset.createVariable('x', rdata.x.dtype, ('cropped_x',))
    new_x.standard_name = 'projection_x_coordinate'
    new_x.long_name = 'GOES fixed grid projection x-coordinate'
    new_x.comments = 'Vector x of the cropping area'
    new_x.units = 'rad'
    new_x.axis = 'X'
    new_x[:] = rdata.x[x_min: x_max]

    # create y
    new_y = dataset.createVariable('y', rdata.y.dtype, ('cropped_y',))
    new_y.standard_name = 'projection_y_coordinate'
    new_y.long_name = 'GOES fixed grid projection y-coordinate'
    new_y.comments = 'Vector y of the cropping area'
    new_y.units = 'rad'
    new_y.axis = 'Y'
    new_y[:] = rdata.y[y_min: y_max]


def extract_variables(dataset, info_dataset, source_dataset):
    source_cmi = source_dataset.variables['CMI']
    cmi = dataset.createVariable('CMI', source_cmi.datatype, ('cropped_y', 'cropped_x'))
    cmi_attr = {k: source_cmi.getncattr(k) for k in source_cmi.ncattrs() if k[0] != '_'}
    cmi_attr['comments'] = f'Brightness temperature matrix of the cropping area, delimited within row_min:{info_dataset.row_min} row_max:{info_dataset.row_max}; col_min:{info_dataset.col_min}; col_max:{info_dataset.col_min} of original matrix size (approximately latitude 15.7°N and 53.9°S; longitude 81.4°W and 34.7°W.)'
    cmi.setncatts(cmi_attr)

    dataset.time_coverage_start = source_dataset.time_coverage_start
    dataset.time_coverage_end = source_dataset.time_coverage_end
    copy_variable(source_dataset.variables['goes_imager_projection'], dataset)

    dataset.variables['CMI'][:,:] = source_cmi[info_dataset.row_min:info_dataset.row_max, info_dataset.col_min:info_dataset.col_max]


def get_region_data_filename(product_band, sat_lon):
    return f'SA-{product_band.product.name}-2km-{str(int(sat_lon)).replace("-", "").replace(".", "_")}W.nc'


def save_info_netcdf(region: LatLonRegion, product_band: ProductBand) -> None:
    region_data = generate_region_data(gcs, region, [product_band])
    for k, rdata in region_data.items():
        filename = get_region_data_filename(product_band, rdata.sat_band_key.sat_lon)
        dataset = Dataset(filename, 'w', format='NETCDF4')
        try:
            dataset.dataset_name = filename
            set_info_variables(dataset, rdata)
        finally:
            dataset.close()


def get_rdata(sat_lon, product_band) -> DatasetRegion:
    filename = get_region_data_filename(product_band, sat_lon)
    info_dataset = Dataset(filename)
    imager_projection = info_dataset.variables['goes_imager_projection']
    sat_height = imager_projection.perspective_point_height
    sat_lon = imager_projection.longitude_of_projection_origin
    sat_sweep = imager_projection.sweep_angle_axis
    try:
        satBandKey = SatBandKey(
            sat_height=sat_height,
            sat_lon=sat_lon,
            sat_sweep=sat_sweep,
            x_size=info_dataset['x'].size,
            y_size=info_dataset['y'].size,
        )
        regionIndexes = RegionIndexes(
            x_min=info_dataset.col_min,
            x_max=info_dataset.col_max,
            y_min=info_dataset.row_min,
            y_max=info_dataset.row_max,
        )
        latLonRegion = LatLonRegion(
            lat_north=info_dataset.geospatial_lat_min,
            lat_south=info_dataset.geospatial_lat_max,
            lon_west=info_dataset.geospatial_lon_min,
            lon_east=info_dataset.geospatial_lon_max,
        )

        return DatasetRegion(
            sat_band_key=satBandKey,
            region=latLonRegion,
            indexes=regionIndexes,
            product_bands=[product_band],
            spatial_resolution=2.0,
            goes_imager_projection=imager_projection,
            lats=info_dataset.variables['lats'][:],
            lons=info_dataset.variables['lons'][:],
            x=info_dataset.variables['x'][:],
            y=info_dataset.variables['y'][:],
        )
    finally:
        info_dataset.close()


def save_SA_netcdf(info_dataset, source_dataset):
    filename = f'SA-{source_dataset.dataset_name}'
    new_dataset = Dataset(filename, 'w', format='NETCDF4')
    try:
        new_dataset.dataset_name = filename
        set_dataset_variables(new_dataset, info_dataset)
        extract_variables(new_dataset, info_dataset, source_dataset)
    finally:
        new_dataset.close()


def run ():
    region = get_SA_region()
    product_band = ProductBand(product=Product.CMIPF, band=Band.CLEAN_LONGWAVE_WINDOW)
    save_info_netcdf(region, product_band)

    dataset = get_dataset(product_band)
    sat_lon = dataset['goes_imager_projection'].longitude_of_projection_origin
    filename = get_region_data_filename(product_band, sat_lon)
    info_dataset = Dataset(filename)
    try:
        # rdata = get_rdata(sat_lon, product_band)
        save_SA_netcdf(info_dataset, dataset)
    finally:
        info_dataset.close()



run()
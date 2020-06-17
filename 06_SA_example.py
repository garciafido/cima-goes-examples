import os

from cima.goes.tiles import LatLonRegion, generate_region_data, DatasetRegion, SatBandKey, RegionIndexes
from cima.goes.storage import GCS
from cima.goes import ProductBand, Product, Band
from netCDF4 import Dataset

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


def set_common_variables(dataset, rdata):
    dataset.sat_height = rdata.sat_band_key.sat_height
    dataset.sat_lon = rdata.sat_band_key.sat_lon
    dataset.sat_sweep = rdata.sat_band_key.sat_sweep
    dataset.x_size = rdata.sat_band_key.x_size
    dataset.y_size = rdata.sat_band_key.y_size

    dataset.col_min = rdata.indexes.x_min
    dataset.col_max = rdata.indexes.x_max
    dataset.row_min = rdata.indexes.y_min
    dataset.row_max = rdata.indexes.y_max

    if int(rdata.sat_band_key.sat_lon) == -89:
        dataset.summary = 'This file contains the latitude - longitude grids, corresponding to the period between 07/10/2017 and 11/30/2017, where GOES16 was in the position 89.3 degrees west. The grid was cropped within the area of South America delimited approximately by latitude 15.7°N and 53.9°S; longitude 81.4°W and 34.7°W.'
    elif int(rdata.sat_band_key.sat_lon) == -75:
        dataset.summary = 'This file contains the latitude - longitude corresponding grids from 12/14/2017. GOES-16 reached 75.2 degrees west on December 11, 2017 and data flow resumed to users on December 14. The grid was cropped within the area of South America delimited approximately by latitude 15.7°N and 53.9°S; longitude 81.4°W and 34.7°W.'

    dataset.institution = 'Center for Oceanic and Atmospheric Research(CIMA), University of Buenos Aires (UBA) > ARGENTINA'
    dataset.creator_name = "Juan Ruiz and Paola Salio"
    dataset.creator_email = "jruiz@cima.fcen.uba.ar, salio@cima.fcen.uba.ar"
    dataset.instrument_type = "GOES R Series Advanced Baseline Imager"
    dataset.spatial_resolution = "2km at nadir"
    dataset.orbital_slot = "GOES-East"
    dataset.geospatial_lat_min = "-53.9"
    dataset.geospatial_lat_max = "15.7"
    dataset.geospatial_lon_min = "-81.4"
    dataset.geospatial_lon_max = "-34.7"

    dim_y = dataset.createDimension('y', rdata.lats.shape[0])
    dim_x = dataset.createDimension('x', rdata.lats.shape[1])

    cropping_y = dataset.createDimension('cropped_y', rdata.indexes.y_max-rdata.indexes.y_min)
    cropping_x = dataset.createDimension('cropped_x', rdata.indexes.x_max-rdata.indexes.x_min)

    # dim_y = dataset.createDimension('y', 2)
    # dim_x = dataset.createDimension('x', 2)

    # create latitude axis
    new_lats = dataset.createVariable('lats', rdata.lats.dtype, ('y', 'x'))
    new_lats.standard_name = 'latitude'
    new_lats.long_name = 'latitude'
    new_lats.units = 'degrees_north'
    new_lats.axis = 'Y'
    new_lats[:,:] = rdata.lats[:,:]
    # new_lats[:, :] = rdata.lats[:2, :2]

    # create longitude axis
    new_lons = dataset.createVariable('lons', rdata.lons.dtype, ('y', 'x'))
    new_lons.standard_name = 'longitude'
    new_lons.long_name = 'longitude'
    new_lons.units = 'degrees_east'
    new_lons.axis = 'X'
    new_lons[:,:] = rdata.lons[:,:]
    # new_lons[:, :] = rdata.lons[:2, :2]

    # create x
    new_x = dataset.createVariable('x', rdata.x.dtype, ('x',))
    new_x.standard_name = 'projection_x_coordinate'
    new_x.long_name = 'GOES fixed grid projection x-coordinate'
    new_x.comments = 'Vector x of the cropping area'
    new_x.units = 'rad'
    new_x.axis = 'X'
    new_x[:] = rdata.x[:]
    # new_x[:] = rdata.x[:2]

    # create y
    new_y = dataset.createVariable('y', rdata.y.dtype, ('y',))
    new_y.standard_name = 'projection_y_coordinate'
    new_y.long_name = 'GOES fixed grid projection y-coordinate'
    new_y.comments = 'Vector y of the cropping area'
    new_y.units = 'rad'
    new_y.axis = 'Y'
    new_y[:] = rdata.y[:]
    # new_y[:] = rdata.y[:2]


def extract_variables(dataset, rdata, source_dataset):
    source_cmi = source_dataset.variables['CMI']
    cmi = dataset.createVariable('CMI', source_cmi.datatype, ('cropped_y', 'cropped_x'))
    cmi_attr = {k: source_cmi.getncattr(k) for k in source_cmi.ncattrs() if k[0] != '_'}
    cmi_attr['comments'] = f'Brightness temperature matrix of the cropping area, delimited within row_min:{dataset.row_min} row_max:{dataset.row_max}; col_min:{dataset.col_min}; col_max:{dataset.col_min} of original matrix size'
    cmi.setncatts(cmi_attr)

    dataset.time_coverage_start = source_dataset.time_coverage_start
    dataset.time_coverage_end = source_dataset.time_coverage_end

    dataset.variables['CMI'][:,:] = source_cmi[rdata.indexes.y_min:rdata.indexes.y_max, rdata.indexes.x_min:rdata.indexes.x_max]

def get_region_data_filename(product_band, sat_lon):
    return f'SA-{product_band.product.name}-2km-{str(int(sat_lon)).replace("-", "").replace(".", "_")}W.nc'


def save_info_netcdf(region: LatLonRegion, product_band: ProductBand) -> None:
    region_data = generate_region_data(gcs, region, [product_band])
    for k, rdata in region_data.items():
        filename = get_region_data_filename(product_band, rdata.sat_band_key.sat_lon)
        dataset = Dataset(filename, 'w', format='NETCDF4')
        try:
            dataset.dataset_name = filename
            set_common_variables(dataset, rdata)
        finally:
            dataset.close()


def get_rdata(sat_lon, product_band) -> DatasetRegion:
    filename = get_region_data_filename(product_band, sat_lon)
    info_dataset = Dataset(filename)
    try:
        satBandKey = SatBandKey(
            sat_height=info_dataset.sat_height,
            sat_lon=info_dataset.sat_lon,
            sat_sweep=info_dataset.sat_sweep,
            x_size=info_dataset.x_size,
            y_size=info_dataset.y_size,
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
            lats=info_dataset.variables['lats'][:],
            lons=info_dataset.variables['lons'][:],
            x=info_dataset.variables['x'][:],
            y=info_dataset.variables['y'][:],
        )
    finally:
        info_dataset.close()


def save_SA_netcdf(rdata: DatasetRegion, source_dataset):
    filename = f'SA-{source_dataset.dataset_name}'
    new_dataset = Dataset(filename, 'w', format='NETCDF4')
    try:
        new_dataset.dataset_name = filename
        set_common_variables(new_dataset, rdata)
        extract_variables(new_dataset, rdata, source_dataset)
    finally:
        new_dataset.close()


def run ():
    region = get_SA_region()
    product_band = ProductBand(product=Product.CMIPF, band=Band.CLEAN_LONGWAVE_WINDOW)
    save_info_netcdf(region, product_band)

    dataset = get_dataset(product_band)
    sat_lon = dataset['goes_imager_projection'].longitude_of_projection_origin
    rdata = get_rdata(sat_lon, product_band)
    save_SA_netcdf(rdata, dataset)


run()
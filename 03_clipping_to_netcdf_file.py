from cima.goes.storage import GCS
from cima.goes.tiles import load_region_data, get_dataset_region, save_netcdf
from cima.goes.storage import NFS
from gcs_credentials import credentials
from cima.goes import ProductBand, Product, Band


# Create Google Cloud Storage object
gcs = GCS(credentials_as_dict=credentials)


def blobs():
    product_band = ProductBand(
        product=Product.CMIPF,              # Cloud and Moisture Image Product – Full Disk
        band=Band.CLEAN_LONGWAVE_WINDOW,    # 13
    )

    year = 2020
    month = 4
    day = 20
    hour = 15

    return gcs.one_hour_blobs(year=year, month=month, day=day, hour=hour, product_band=product_band).blobs


################################
# Save clippings as NETCDF files
################################

# Loads the region data previously generated
# in the example 02_generate_clipping_regions.py
region_data = load_region_data(NFS(), 'my_regions.json')

for blob in blobs():
    # Get NETCDF dataset
    dataset = gcs.get_dataset(blob)
    datetime = dataset.date_created

    # Get matrix indexes of a region
    dataset_region = get_dataset_region(dataset, region_data)

    # List variables with shape equals to lats lons
    shape = (dataset.variables['x'].size, dataset.variables['y'].size)
    variables = [x for x, v in dataset.variables.items() if shape == v.shape]

    for variable in variables:
        # Save file
        filename = f'CLIP_{variable}_{datetime}.nc'
        save_netcdf(filename, dataset, dataset_region.indexes, variable)

        # Show progress
        print(f'Region: {dataset_region.region}')
        print(f'saved as {filename}')

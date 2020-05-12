import numpy as np
from cima.goes.storage import GCS
from cima.goes.tiles import load_region_data, get_dataset_region, get_data, get_lats_lons
from cima.goes.storage import NFS
from gcs_credentials import credentials
from cima.goes import ProductBand, Product, Band
from cima.goes.img import get_image_stream, stream2pil, CLOUD_TOPS_PALETTE


# Create Google Cloud Storage object
gcs = GCS(credentials_as_dict=credentials)
nfs = NFS()


def blobs():
    product_band = ProductBand(
        product=Product.RadF,
        band=Band.RED
    )

    year = 2020
    month = 4
    day = 20
    hour = 15

    return gcs.one_hour_blobs(year=year, month=month, day=day, hour=hour, product_band=product_band).blobs


def apply_albedo(data):
    albedo = (data * np.pi * 0.3) / 663.274497
    albedo = np.clip(albedo, 0, 1)
    return np.power(albedo, 1.5)


def apply_ir(data):
    return data - 273


################################
# Save clippings as NETCDF files
################################

# Loads the region data previously generated
# in the example 02_generate_clipping_regions.py
region_data = load_region_data(nfs, 'my_regions.json')

for blob in blobs():
    # Get NETCDF dataset
    dataset = gcs.get_dataset(blob)
    datetime = dataset.date_created

    # Get matrix indexes of a region
    dataset_region = get_dataset_region(dataset, region_data)
    lats, lons = get_lats_lons(dataset, dataset_region.indexes)
    data = apply_albedo(get_data(dataset, dataset_region.indexes))

    # Get image
    format = 'png'
    image_stream = get_image_stream(
        data=data,
        lats=lats,
        lons=lons,
        format=format,
        region=dataset_region.region,
        vmin=0,
        vmax=0.7,
        cmap='gray')

    # Save image
    filename = f'CLIP_{datetime}.{format}'
    nfs.upload_stream(image_stream, filename)

    # Show progress
    print(f'Region: {dataset_region.region}, Shape: {lats.shape}')
    print(f'saved as {filename}')

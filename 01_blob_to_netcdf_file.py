###############################
# Define a GOES 16 Product Band
###############################

from cima.goes import ProductBand, Product, Band

product_band = ProductBand(
    product=Product.CMIPF,              # Cloud and Moisture Image Product – Full Disk
    band=Band.CLEAN_LONGWAVE_WINDOW,    # 13
    subproduct=None
)


######################
# Define date and time
######################

year = 2020
month = 5
day = 1
hour = 22


########################################################
# Get Google Cloud Blobs for a product at a certain time
########################################################

from cima.goes.storage import GCS

gcs = GCS()
band_blobs = gcs.one_hour_blobs(year=year, month=month, day=day, hour=hour, product_band=product_band)


###################
# Save NETCDF Files
###################

import netCDF4

print(f'Product: {product_band.product.__doc__}')
print(f'Band: {product_band.band.__doc__}')
print(f'Date: {year}-{month}-{day} at {hour} hrs.')

for blob in band_blobs.blobs:
    data = gcs.download_from_blob(blob)
    dataset = netCDF4.Dataset("in_memory_file", mode='r', memory=data)

    datetime = dataset.date_created
    with open(dataset.dataset_name, 'wb') as f:
        f.write(data)

    minute = datetime[14:16]
    print(f'    {hour}:{minute} (saved as {dataset.dataset_name})')

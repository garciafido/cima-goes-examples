###############################
# Define a GOES 16 Product Band
###############################

from cima.goes import ProductBand, Product, Band

product_band = ProductBand(
    product=Product.CMIPF,              # Cloud and Moisture Image Product – Full Disk
    band=Band.CLEAN_LONGWAVE_WINDOW,    # 13
)


######################
# Define date and time
######################

year = 2020
month = 5
day = 1
hour = 22


########################
# Get Google Cloud Blobs
########################

from cima.goes.storage import GCS
from gcs_credentials import credentials

gcs = GCS(credentials_as_dict=credentials)
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
    filename = f'Cloud_and_Moisture_{datetime}.nc'
    with open(filename, 'wb') as f:
        f.write(data)

    minute = datetime[14:16]
    print(f'    {hour}:{minute} (saved as {filename})')

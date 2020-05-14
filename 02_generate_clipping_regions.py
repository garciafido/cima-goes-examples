from cima.goes.tiles import LatLonRegion

#################
# Define a region
#################

region = LatLonRegion(
    lat_south=-45,
    lat_north=-20,
    lon_west=-75,
    lon_east=-45,
)

small_region = LatLonRegion(
    lat_south=-30,
    lat_north=-20,
    lon_west=-60,
    lon_east=-50,
)

##############################
# Define GOES 16 Product Bands
##############################

from cima.goes import ProductBand, Product, Band

product_bands = [
    ProductBand(Product.CMIPF, Band.RED),
    ProductBand(Product.CMIPF, Band.VEGGIE),
    ProductBand(Product.CMIPF, Band.BLUE),
    ProductBand(Product.CMIPF, Band.CLEAN_LONGWAVE_WINDOW),
    ProductBand(Product.RadF, Band.RED),
]

#############################
# Define Google Cloud Storage
#############################

from cima.goes.storage import GCS
from gcs_credentials import credentials

gcs = GCS(credentials_as_dict=credentials)


########################################
# Generate region data for product bands
########################################

from cima.goes.tiles import generate_region_data

# This process can take a long time
region_data = generate_region_data(gcs, small_region, product_bands)


#########################
# Save it for further use
#########################

from cima.goes.tiles import save_region_data
from cima.goes.storage import NFS

# Saving the file to the network file storage (NFS) in the current directory
save_region_data(region_data, NFS(), 'my_small_regions.json')

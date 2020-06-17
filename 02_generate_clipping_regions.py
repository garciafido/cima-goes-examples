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

test_region = LatLonRegion(
    lat_south=-30,
    lat_north=-25,
    lon_west=-60,
    lon_east=-55,
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
    # nombre proyecto = SA_
    # Este canal se baja Datos asociados. Unidades, resolucion, grid mapping...
    # Texto english
    # Variables globales, row_min row_max, col_min, col_max
    # Grilla generada (CMI)
    # x e y del recorte (dos vectores)
    # posición del satélite
    # rectangle coord
    #    indexes.x_min: indexes.x_max
    #    indexes.y_min: indexes.y_max
    # Texto english
    # Lats lons, en un archivo aparte netcdf (en vez de un json)
    # /year/month/day/....  prefijados por nombre proyecto
    ProductBand(Product.RadF, Band.RED),
]

########################################
# Generate region data for product bands
########################################

from cima.goes.storage import GCS
from cima.goes.tiles import generate_region_data

# This process can take a long time
region_data = generate_region_data(GCS(), test_region, [ProductBand(Product.CMIPF, Band.CLEAN_LONGWAVE_WINDOW)])


#########################
# Save it for further use
#########################

from cima.goes.tiles import save_region_data
from cima.goes.storage import NFS

# Saving the file to the network file storage (NFS) in the current directory
save_region_data(region_data, NFS(), 'test_regions.json')

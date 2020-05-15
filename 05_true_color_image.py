from cima.goes.storage import GCS
from cima.goes.tiles import load_region_data, get_data, get_dataset_key, get_dataset_region
from cima.goes.storage import NFS
from cima.goes import ProductBand, Product, Band
from cima.goes.img import get_true_colors, get_image_inches, apply_albedo
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


gcs = GCS()
nfs = NFS()

year = 2020
month = 4
day = 20
hour = 15


def rgb_dataset():
    blob = gcs.one_hour_blobs(
        year=year,
        month=month,
        day=day,
        hour=hour,
        product_band=ProductBand(product=Product.MCMIPC)).blobs[0]

    return gcs.get_dataset(blob)


def rgb_data(dataset):
    r_data = get_data(dataset, variable='CMI_C02')
    g_data = get_data(dataset, variable='CMI_C03')
    b_data = get_data(dataset, variable='CMI_C01')
    return get_true_colors(r_data, g_data, b_data)


def get_extent(dataset):
    geo_extent = dataset.variables['geospatial_lat_lon_extent']
    min_lon = float(geo_extent.geospatial_westbound_longitude)
    max_lon = float(geo_extent.geospatial_eastbound_longitude)
    min_lat = float(geo_extent.geospatial_southbound_latitude)
    max_lat = float(geo_extent.geospatial_northbound_latitude)

    return [min_lon, min_lat, max_lon, max_lat]


def gray_data():
    blob = gcs.one_hour_blobs(
        year=year,
        month=month,
        day=day,
        hour=hour,
        product_band=ProductBand(product=Product.RadF, band=Band.RED)).blobs[0]

    dataset = gcs.get_dataset(blob)
    return apply_albedo(get_data(dataset))


def gray_clip():
    blob = gcs.one_hour_blobs(
        year=year,
        month=month,
        day=day,
        hour=hour,
        product_band=ProductBand(product=Product.RadF, band=Band.RED)).blobs[0]

    dataset = gcs.get_dataset(blob)
    region_data = load_region_data(nfs, 'my_regions.json')
    dataset_region = get_dataset_region(dataset, region_data)
    return apply_albedo(get_data(dataset, dataset_region.indexes))


def lambert(img, geos, extent, filename):
    fig = plt.figure(frameon=False)
    image_inches = get_image_inches(img)

    # Generate an Cartopy projection
    lc = ccrs.LambertConformal(central_longitude=-97.5, standard_parallels=(38.5, 38.5))

    ax = fig.add_subplot(1, 1, 1, projection=lc)
    ax.set_extent([-135, -60, 10, 65], crs=ccrs.PlateCarree())

    ax.imshow(img, origin='upper',
              extent=extent,
              transform=geos,
              interpolation='none')
    # ax.coastlines(resolution='50m', color='black', linewidth=0.5)
    # ax.add_feature(ccrs.cartopy.feature.STATES, linewidth=0.5)
    plt.savefig(filename, format='png', dpi=image_inches.dpi, bbox_inches='tight', pad_inches=0)


def save(img, filename, **kwargs):
    fig = plt.figure(frameon=False)
    image_inches = get_image_inches(img)
    ax = fig.add_subplot(1, 1, 1)
    ax.axis('off')
    ax.imshow(img, **kwargs)
    fig.set_size_inches(image_inches.x, image_inches.y)
    plt.savefig(filename, format='png', dpi=image_inches.dpi, bbox_inches='tight', pad_inches=0)


dataset = rgb_dataset()
extent = get_extent(dataset)
sat_band_key = get_dataset_key(dataset)
geos = ccrs.Geostationary(
    central_longitude=sat_band_key.sat_lon,
    satellite_height=sat_band_key.sat_height,
    sweep_axis=sat_band_key.sat_sweep
)
lambert(rgb_data(dataset), geos, extent, f'LAMBERT_RGB.png')
# save(rgb_data(dataset), f'CLIP_RGB.png')
# save(gray_clip(), f'CLIP_GRAY.png', vmin=0, vmax=0.7, cmap='gray')
# save(gray_data(), f'ALL_GRAY.png', vmin=0, vmax=0.7, cmap='gray')

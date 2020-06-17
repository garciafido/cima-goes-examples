from cima.goes.storage import GCS
from cima.goes.tiles import load_region_data, get_data, get_lats_lons, get_dataset_region, get_dataset_key, get_tile_extent
from cima.goes.storage import NFS
from cima.goes import ProductBand, Product
from cima.goes.img import get_true_colors, get_image_inches, get_image_stream, Grid, Color
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs
from PIL import Image

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
        product_band=ProductBand(product=Product.MCMIPF)).blobs[0]

    return gcs.get_dataset(blob)


geos = None


def rgb_region_data(dataset, indexes=None):
    global geos
    r_data = get_data(dataset, indexes=indexes, variable='CMI_C02')
    g_data = get_data(dataset, indexes=indexes, variable='CMI_C03')
    b_data = get_data(dataset, indexes=indexes, variable='CMI_C01')

    sat_band_key = get_dataset_key(dataset)
    geos = ccrs.Geostationary(
        central_longitude=sat_band_key.sat_lon,
        satellite_height=sat_band_key.sat_height)

    return get_true_colors(r_data, g_data, b_data)


def save(img, filename):
    image_inches = get_image_inches(img)
    fig = plt.figure(frameon=False)
    fig.set_size_inches(image_inches.x, image_inches.y)
    ax = fig.add_subplot(1, 1, 1)
    ax.set_axis_off()
    ax.imshow(img, aspect='auto', origin='upper')
    fig.subplots_adjust(wspace=0, hspace=0, left=0, bottom=0, right=image_inches.x, top=image_inches.y)
    plt.savefig(filename, format='png', dpi=image_inches.dpi, pad_inches=0, transparent=True)


def save_image(filepath):
    dataset = rgb_dataset()
    region_data = load_region_data(nfs, 'my_regions.json')
    dataset_region = get_dataset_region(dataset, region_data)
    rgb_data = rgb_region_data(dataset, indexes=dataset_region.indexes)
    print(f'DATA SIZE: x={rgb_data.shape[1]} y={rgb_data.shape[0]}')
    save(rgb_data, filepath)


def show_image_size(filepath):
    im = Image.open(filepath)
    print(f'IMAGE SIZE: x={im.size[0]} y={im.size[1]}')


def save_images():
    dataset = rgb_dataset()
    print(dataset.spatial_resolution)
    region_data = load_region_data(nfs, 'my_regions.json')
    dataset_region = get_dataset_region(dataset, region_data)
    lats, lons = get_lats_lons(dataset, dataset_region.indexes)
    rgb_data = rgb_region_data(dataset, indexes=dataset_region.indexes)
    print(f'DATA SIZE: x={rgb_data.shape[1]} y={rgb_data.shape[0]}')

    filepath = f'ORIGINAL_REGION_RGB.png'
    # image_stream = get_image_stream(
    #     data=rgb_data,
    #     projection=None,
    #     lats=lats,
    #     lons=lons)
    # nfs.upload_stream(image_stream, filepath)
    save(rgb_data, filepath)
    show_image_size(filepath)

    filepath = f'CYLINDRICAL_REGION_RGB.png'
    image_stream = get_image_stream(
        data=rgb_data,
        lats=lats,
        lons=lons,
        region=dataset_region.region,
        draw_cultural=True,
        grid=Grid(step=5))
    nfs.upload_stream(image_stream, filepath)
    show_image_size(filepath)


save_images()

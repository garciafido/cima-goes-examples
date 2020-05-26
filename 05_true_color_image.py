from cima.goes.storage import GCS
from cima.goes.tiles import load_region_data, get_data, get_lats_lons, get_dataset_region
from cima.goes.storage import NFS
from cima.goes import ProductBand, Product
from cima.goes.img import get_true_colors, get_image_inches, get_image_stream
import matplotlib.pyplot as plt
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


def rgb_region_data(dataset, indexes=None):
    r_data = get_data(dataset, indexes=indexes, variable='CMI_C02')
    g_data = get_data(dataset, indexes=indexes, variable='CMI_C03')
    b_data = get_data(dataset, indexes=indexes, variable='CMI_C01')
    return get_true_colors(r_data, g_data, b_data)


def save(img, filename, **kwargs):
    image_inches = get_image_inches(img)
    fig = plt.figure(frameon=False, dpi=image_inches.dpi, figsize=(image_inches.x, image_inches.y))
    ax = fig.add_subplot(1, 1, 1)
    ax.axis('off')
    ax.imshow(img, **kwargs)
    plt.savefig(filename, format='png', dpi=image_inches.dpi, pad_inches=0)


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
    region_data = load_region_data(nfs, 'my_regions.json')
    dataset_region = get_dataset_region(dataset, region_data)
    rgb_data = rgb_region_data(dataset, indexes=dataset_region.indexes)
    print(f'DATA SIZE: x={rgb_data.shape[1]} y={rgb_data.shape[0]}')

    filepath = f'ORIGINAL_REGION_RGB.png'
    save(rgb_data, filepath)
    show_image_size(filepath)

    filepath = f'CYLINDRICAL_REGION_RGB.png'
    lats, lons = get_lats_lons(dataset, dataset_region.indexes)
    image_stream = get_image_stream(
        data=rgb_data,
        lats=lats,
        lons=lons)
    nfs.upload_stream(image_stream, filepath)
    show_image_size(filepath)


save_images()

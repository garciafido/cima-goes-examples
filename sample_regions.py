from cima.goes.tiles import SatBandKey, LatLonRegion, DatasetRegion, RegionIndexes

my_regions = {
    '35786023.0#-89.5#x#21696#21696': DatasetRegion(
        sat_band_key=SatBandKey(sat_height=35786023.0, sat_lon=-89.5, sat_sweep='x', x_size=21696, y_size=21696),
        region=LatLonRegion(lat_north=-20, lat_south=-45, lon_west=-75, lon_east=-45),
        indexes=RegionIndexes(x_min=12970, x_max=18725, y_min=14930, y_max=19290)),
    '35786023.0#-89.5#x#5424#5424': DatasetRegion(
        sat_band_key=SatBandKey(sat_height=35786023.0, sat_lon=-89.5, sat_sweep='x', x_size=5424, y_size=5424),
        region=LatLonRegion(lat_north=-20, lat_south=-45, lon_west=-75, lon_east=-45),
        indexes=RegionIndexes(x_min=3242, x_max=4681, y_min=3732, y_max=4822)),
    '35786023.0#-89.5#x#10848#10848': DatasetRegion(
        sat_band_key=SatBandKey(sat_height=35786023.0, sat_lon=-89.5, sat_sweep='x', x_size=10848, y_size=10848),
        region=LatLonRegion(lat_north=-20, lat_south=-45, lon_west=-75, lon_east=-45),
        indexes=RegionIndexes(x_min=6485, x_max=9362, y_min=7465, y_max=9644)),
    '35786023.0#-75.0#x#21696#21696': DatasetRegion(
        sat_band_key=SatBandKey(sat_height=35786023.0, sat_lon=-75.0, sat_sweep='x', x_size=21696, y_size=21696),
        region=LatLonRegion(lat_north=-20, lat_south=-45, lon_west=-75, lon_east=-45),
        indexes=RegionIndexes(x_min=10847, x_max=16617, y_min=15031, y_max=19322)),
    '35786023.0#-75.0#x#5424#5424': DatasetRegion(
        sat_band_key=SatBandKey(sat_height=35786023.0, sat_lon=-75.0, sat_sweep='x', x_size=5424, y_size=5424),
        region=LatLonRegion(lat_north=-20, lat_south=-45, lon_west=-75, lon_east=-45),
        indexes=RegionIndexes(x_min=2711, x_max=4154, y_min=3757, y_max=4830)),
    '35786023.0#-75.0#x#10848#10848': DatasetRegion(
        sat_band_key=SatBandKey(sat_height=35786023.0, sat_lon=-75.0, sat_sweep='x', x_size=10848, y_size=10848),
        region=LatLonRegion(lat_north=-20, lat_south=-45, lon_west=-75, lon_east=-45),
        indexes=RegionIndexes(x_min=5423, x_max=8308, y_min=7515, y_max=9661))
}

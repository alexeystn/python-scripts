# Find the most remote point
# from other countries

import shapefile
from matplotlib import pyplot as plt
from numpy import sin, cos
import numpy as np
import itertools


def lon_lat_to_xyz(p):
    def rad(deg):
        return deg * np.pi / 180
    lon = p[0]
    lat = p[1]
    x = cos(rad(lon)) * cos(rad(lat))
    y = sin(rad(lon)) * cos(rad(lat))
    z = sin(rad(lat))
    return x, y, z


def format_coordinates(pnt_ll):
    res = '{0}{1:.5f}, {2}{3:.5f}'.format('N' if pnt_ll[1] > 0 else 'S', np.abs(pnt_ll[1]),
                                          'E' if pnt_ll[0] > 0 else 'W', np.abs(pnt_ll[0]))
    return res


def chord_to_arc(dist):
    # Convert direct distance between 2 points to on-surface distance
    radius = 40e3 / 2 / np.pi
    alpha = np.arcsin(dist/2/radius)
    arc = alpha * radius * 2
    return arc


class CountryShape:
    contours_xyz = []

    def __init__(self, name):
        self.name = name
        self.__load_country(name)

    def __load_country(self, name):
        filename = 'ne_50m_admin_0_countries'
        sf = shapefile.Reader('./' + filename + '/' + filename + '.shp')
        records = sf.shapeRecords()
        shapes = sf.shapes()
        field_names = [f[0] for f in sf.fields[1:]]
        names = [r.record[field_names.index('NAME')] for r in records]
        s = shapes[names.index(name)]
        s.parts.append(len(s.points))
        contours = [s.points[i1:i2] for i1, i2 in zip(s.parts[:-1], s.parts[1:])]
        self.points_ll = np.array(list(itertools.chain.from_iterable(contours)))  # join all contours points
        self.contours_xyz = np.array([lon_lat_to_xyz(p) for p
                                      in self.points_ll])

    def distance_to_point(self, pnt_ll):
        # Distance from country border to (lon,lat) point
        pnt = lon_lat_to_xyz(pnt_ll)
        dist_array = np.sqrt(np.sum((self.contours_xyz - pnt)**2, axis=1))
        closest_point = self.points_ll[np.argmin(dist_array)]
        min_distance = min(dist_array) * 40e3 / 2 / np.pi
        return min_distance, closest_point


def get_min_dist(pnt, verbose=False):
    # Find distance to the closest country border
    global countries
    dist_list = []
    for c in countries:
        dist, closest_pnt = countries[c].distance_to_point(pnt)
        if verbose:
            print('{0:>24s}  {1:.1f}({3})km  {2}'.format(c, dist,
                                                         format_coordinates(closest_pnt),
                                                         int(chord_to_arc(dist))))
        dist_list.append(dist)
    return min(dist_list)


countries = {}


def main():

    global countries
    country_names = ['United States of America', 'Canada',
                     'Norway', 'Finland',
                     'Kazakhstan', 'Mongolia', 'China', 'Japan', 'Greenland']

    countries = {c: CountryShape(c) for c in country_names}

    # E 129.877, N 73.439

    lon_min, lon_max = 60, 160
    lat_min, lat_max = 50, 80
    lon_n, lat_n = 50, 15
    scale_step = 4

    for i in range(8):

        dist_map = np.zeros((lat_n, lon_n))  # map of distances
        lon_set = np.linspace(lon_min, lon_max, lon_n)
        lat_set = np.linspace(lat_min, lat_max, lat_n)

        for i_lat, lat in enumerate(lat_set):
            for i_lon, lon in enumerate(lon_set):
                dist_map[i_lat, i_lon] = get_min_dist((lon, lat))
        idx = np.unravel_index(np.argmax(dist_map), dist_map.shape)
        lat_optimum = lat_set[idx[0]]
        lon_optimum = lon_set[idx[1]]

        print(format_coordinates((lon_optimum, lat_optimum)))

        if 0:
            plt.imshow(dist_map, cmap='jet')
            plt.show()

        lat_range = (lat_max - lat_min) / scale_step / 2
        lon_range = (lon_max - lon_min) / scale_step / 2

        lat_min, lat_max = lat_optimum - lat_range, lat_optimum + lat_range
        lon_min, lon_max = lon_optimum - lon_range, lon_optimum + lon_range

    get_min_dist((lon_optimum, lat_optimum), verbose=True)


if __name__ == "__main__":
    main()

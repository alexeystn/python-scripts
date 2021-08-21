from numpy import *

cities = [ {'name': 'Moscow',
            'lat': 55.755771,
            'lon': 37.617657},
           {'name': 'Saint-Petersburg',
            'lat': 59.932336,
            'lon': 30.300733},
           {'name': 'Minsk',
            'lat': 53.902242, 
            'lon': 27.561843} ]

for city in cities:
    city['phi'] = city['lon'] * pi / 180
    city['theta'] = city['lat'] * pi / 180
    city['x'] = cos(city['phi']) * cos(city['theta'])
    city['y'] = sin(city['phi']) * cos(city['theta'])
    city['z'] = sin(city['theta'])

# 11 12 13
# 21 22 23
# 31 32 33

A12 = cities[1]['x'] - cities[0]['x']
A22 = cities[1]['y'] - cities[0]['y']
A32 = cities[1]['z'] - cities[0]['z']

A13 = cities[2]['x'] - cities[0]['x']
A23 = cities[2]['y'] - cities[0]['y']
A33 = cities[2]['z'] - cities[0]['z']

normal  = array([A22*A33 - A23*A32,
                 A32*A13 - A12*A33,
                 A12*A23 - A13*A22])

normal = normal / sqrt(sum(normal * normal))

x = normal[0]
y = normal[1]
z = normal[2]

r = sqrt(x*x + y*y)

phi = arctan2(y, x) 
theta = arctan2(z, r)

lon = phi / pi * 180
lat = theta / pi * 180

print('{0:.6f}, {1:.6f}'.format(lat, lon))


id1 = 0 # Moscow
id2 = 2 # Saint-Petersburg
mid_x = (cities[id1]['x'] + cities[id2]['x']) / 2
mid_y = (cities[id1]['y'] + cities[id2]['y']) / 2
mid_z = (cities[id1]['z'] + cities[id2]['z']) / 2
mid_r = sqrt(mid_x**2 + mid_y**2)
mid_phi = arctan2(mid_y, mid_x) 
mid_theta = arctan2(mid_z, mid_r)

mid_lon = mid_phi / pi * 180
mid_lat = mid_theta / pi * 180

print('{0:.6f}, {1:.6f}'.format(mid_lat, mid_lon))






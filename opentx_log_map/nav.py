import math
import csv
import requests
from io import BytesIO
from PIL import Image

lat_center = 0
lon_center = 0
resolution = 640
meters_per_pixel = 0 
zoom = 0


def read_log(filename):
    f = open(filename, 'r')
    reader = csv.reader(f)
    head = next(reader)
    log = {}
    for h in head:
        log[h] = []
    for row in reader:
        for h, v in zip(head, row):
            log[h].append(v)
    return log



def path_from_log(log):
    path = {}
    path['Lat'] = []
    path['Lon'] = []
    path['Rssi'] = []
    path['Angle'] = []
    path['Alt'] = []
    lat_prev = 0
    lon_prev = 0
    for i in range(0, len(log['GPS'])):
        lat_lon = log['GPS'][i].split(' ')
        try:
            lat = abs(float(lat_lon[0]))
            lon = abs(float(lat_lon[1]))
        except:
            pass
        else:
            if (lat > 30):
                if (lat != lat_prev) & (lat != lon_prev):
                    path['Lat'].append(lat)
                    path['Lon'].append(lon)
                    path['Rssi'].append(int(log['RSSI(dB)'][i]))
                    path['Alt'].append(float(log['Alt(m)'][i]))
                    angle = int(log['Hdg(@)'][i])/180*math.pi
                    # angle = math.atan2((lon-lon_prev)*math.cos(lat/math.pi), lat-lat_prev)
                    path['Angle'].append(angle)
                    lat_prev = lat
                    lon_prev = lon
    return path



def coords_to_pixel(lat, lon):
    x = resolution/2
    y = resolution/2
    x_coord_rel = lon - lon_center
    y_coord_rel = lat - lat_center
    x_meters = 111.3*1000 * x_coord_rel * math.cos( lat_center * math.pi / 180) #      на косинус угла, соответствующего географической широте
    y_meters = 111*1000 * y_coord_rel
    x = x + x_meters / meters_per_pixel
    y = y - y_meters / meters_per_pixel
    return x, y


def download_map(path, z):
    global lat_center, lon_center, meters_per_pixel, zoom
    f = open('key.txt')
    key = f.readline()[:-1]
    zoom = z
    lat_center = (max(path['Lat']) + min(path['Lat']))/2
    lon_center = (max(path['Lon']) + min(path['Lon']))/2
    url = 'https://maps.googleapis.com/maps/api/staticmap?'
    url += 'maptype=satellite'
    url += '&center=' + str(lat_center) + ',' + str(lon_center)
    url += '&zoom=' + str(zoom)
    url += '&size=' + str(resolution) + 'x' + str(resolution)
    url += '&key=' + key
    response = requests.get(url)
    im = Image.open(BytesIO(response.content))
    im = im.convert("RGBA")
    meters_per_pixel = 156543.03392 * math.cos(lat_center * math.pi / 180) / (2**zoom)
    return im


def rssi_to_color(rssi):
    r_max = 90
    r_min = 55
    r_mid = (r_max + r_min)/2
    if rssi < r_min:
        col = [1,0,0]
    elif rssi < r_mid:
        m = (r_mid - rssi)/(r_mid - r_min)
        col = [1,1-m,0]
    elif rssi < r_max:
        m = (r_max - rssi)/(r_max - r_mid)
        col = [m,1,0]
    else:
        col = [0,1,0]
    col_result = [int(c*255) for c in col]    
    return tuple(col_result)



def altitude_to_radius(alt):
    p_min = 2
    p_max = 5
    alt_max = 80
    alt_min = 5
    if alt < alt_min:
        return int(p_min)
    elif alt < alt_max:
        return int((alt-alt_min)/(alt_max-alt_min)*(p_max-p_min)+p_min ) 
    else:
        return p_max



def arrow_polygon(x_cnt, y_cnt, angle, rad):
    plg = [(-rad, rad), (0, -rad*1.5), (rad, rad), (0, rad/2)]
    plg_rot = [];
    for p in plg:
        x = p[0]
        y = p[1]
        x_rot = x*math.cos(angle) - y*math.sin(angle)
        y_rot = x*math.sin(angle) + y*math.cos(angle)
        plg_rot.append((x_rot + x_cnt, y_rot + y_cnt))
    return plg_rot



import shapefile
import matplotlib.pyplot as plt
import numpy as np
from numpy import sin, cos, linspace, pi

class Country_Database:
    shapes = []
    names = []
    def load(self, filename):
        sf = shapefile.Reader('./' + filename + '/' + filename + '.shp')
        records = sf.shapeRecords()
        self.shapes = sf.shapes()
        field_names = [f[0] for f in sf.fields[1:]]
        name_ind = field_names.index('NAME') 
        self.names = [r.record[name_ind] for r in records]       

    def get(self, country_name):        
        index = self.names.index(country_name)
        s = self.shapes[index]
        s.parts.append(len(s.points))
        sh = [ s.points[i1:i2] for i1, i2 in zip( s.parts[:-1], s.parts[1:])]
        return sh

def generate_globe(step, resolution):
    t = linspace(0, 2*pi, 50)
    latitudes = [zip(sin(t)*cos(lat), cos(t)*cos(lat), [sin(lat) for i in t])
                 for lat in linspace(-pi/2, pi/2, 13)]
    longitudes = [zip(cos(t)*sin(lon), cos(t)*cos(lon), sin(t))
                  for lon in linspace(-pi/2, pi/2, 13)]       
    return latitudes + longitudes

def plot_contour(contour, col):
    for cc in contour:
        pp = [[*p] for p in zip(*cc)]
        plt.plot(pp[0], pp[2], linewidth = 0.3, color = col) 



def rad(deg):
    return deg*pi/180


def country_to_globe(s):
    g = [[(sin(rad(p[0]))*cos(rad(p[1])), cos(rad(p[0]))*cos(rad(p[1])), sin(rad(p[1])))
          for p in c] for c in s]
    return g



c = Country_Database()
c.load('ne_50m_admin_0_countries')
g = generate_globe(30, 50)



plt.figure(figsize = (6,5.5))
plot_contour(g,'k')
plot_contour(country_to_globe(c.get('Japan')),'r')
plot_contour(country_to_globe(c.get('United Kingdom')),'r')
plot_contour(country_to_globe(c.get('Brazil')),'r')
plot_contour(country_to_globe(c.get('South Africa')),'r')
plot_contour(country_to_globe(c.get('Belarus')),'r')
plt.show()



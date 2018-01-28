import shapefile
import matplotlib.pyplot as plt
import numpy as np

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
        sh = []
        for i in range(len(s.parts)-1):
            p = s.points[ s.parts[i]:s.parts[i+1] ]
            for j in range(len(p)):
                p[j] = (p[j][0], p[j][1], 0)
            sh.append(p)
        return sh


def generate_globe(step, resolution):
    pi = np.pi
    g = []
    t = np.linspace(0, 2*pi, 50)
    for lat in np.linspace(-pi/2, pi/2, 13):
        x = np.sin(t)*np.cos(lat)
        y = np.cos(t)*np.cos(lat)
        z = [np.sin(lat) for i in t]
        g.append(list(zip(x,y,z)))
    for lon in np.linspace(-pi/2, pi/2, 13):
        x = np.cos(t)*np.sin(lon)
        y = np.cos(t)*np.cos(lon)
        z = np.sin(t)
        g.append(list(zip(x,y,z)))        
    return g

    
def plot_contour(contour):
    for cc in contour:
        pp = [[*p] for p in zip(*cc)]
        plt.plot(pp[0], pp[2], linewidth = 0.3, color = 'k')    


def country_to_globe(s):
    g = []
    pi = np.pi
    for c in s:
        for i in range(len(c)):
            p = c[i]
            lat = p[1]
            lon = p[0]
            x = np.sin(lon*pi/180)*np.cos(lat*pi/180)
            y = np.cos(lon*pi/180)*np.cos(lat*pi/180)
            z = np.sin(lat*pi/180)
            p = (x, y, z)
            c[i] = p 
        g.append(c)
    return g



c = Country_Database()
c.load('ne_50m_admin_0_countries')
g = generate_globe(30, 50)



plt.figure(figsize = (6,5.5))
plot_contour(g)
plot_contour(country_to_globe(c.get('Japan')))
plot_contour(country_to_globe(c.get('United Kingdom')))
plot_contour(country_to_globe(c.get('Brazil')))
plt.show()



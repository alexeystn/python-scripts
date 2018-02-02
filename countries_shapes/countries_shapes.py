import shapefile
from matplotlib import pyplot as plt
from numpy import sin, cos, linspace, pi, matmul, mean
from time import sleep


def rad(deg):
    return deg*pi/180
    
class Country_Shape:
    c = [] # contours
    c_large = [] # contours of large parts
    center = [] # lat, lon, center of large parts
    name = ''
    
    def __init__(self, name):
        self.name = name
        if name == 'Globe':
            self.__generate_globe()
        elif name == '':
            self.name = ''
        else:
            self.__load_country(name)
            self.__find_large_parts()
            self.__find_center()
            self.__project_to_sphere()
            
    def __project_to_sphere(self):
        self.c = [[(sin(rad(p[0]))*cos(rad(p[1])), -cos(rad(p[0]))*cos(rad(p[1])), sin(rad(p[1])))
                   for p in sc] for sc in self.c]
        
    def __find_large_parts(self):
        lengths = [len(cc) for cc in self.c]
        m = max(lengths)
        self.c_large = [i for i, cc in enumerate(lengths) if cc > m/2]

    def __generate_globe(self):
        g = []
        t = linspace(0, pi*2, 50) # latitudes
        g += [zip(sin(t)*cos(lat), cos(t)*cos(lat), [sin(lat) for i in t])
              for lat in linspace(-pi/2, pi/2, 13)] 
        t = linspace(-pi/2, pi/2, 50) # longitudes
        g += [zip(cos(t)*sin(lon), cos(t)*cos(lon), sin(t))
              for lon in linspace(-pi, pi, 25)]
        self.c = g

    def __load_country(self, name):
        filename = 'ne_50m_admin_0_countries'
        sf = shapefile.Reader('./' + filename + '/' + filename + '.shp')
        records = sf.shapeRecords()
        shapes = sf.shapes()
        field_names = [f[0] for f in sf.fields[1:]]
        names = [r.record[field_names.index('NAME')] for r in records]
        s = shapes[names.index(name)]
        s.parts.append(len(s.points))
        sh = [ s.points[i1:i2] for i1, i2 in zip( s.parts[:-1], s.parts[1:])]
        self.c = sh

    def __find_center(self):
        cl = [self.c[i] for i in self.c_large]
        x = [[aa[0] for aa in a] for a in cl]
        y = [[aa[1] for aa in a] for a in cl]
        xmin = min([min(xx) for xx in x])
        xmax = max([max(xx) for xx in x])
        ymin = min([min(yy) for yy in y])
        ymax = max([max(yy) for yy in y])
        x = mean([xmin,xmax])
        y = mean([ymin,ymax])
        self.center = (x, y)

    def plot(self, col, wid):
        for cc in self.c:
            pp = [[*p] for p in zip(*cc)]
            plt.plot(pp[0], pp[2], linewidth = wid, color = col) 

    def truncate(self):
        cv = []
        for cc in self.c:
            r = []
            rr = []
            for i in range(len(cc)):
                if cc[i][1] > 0:
                    if rr != []: r.append(rr);
                    rr = []
                else:
                    rr.append(cc[i])
            if rr != []:
                r.append(rr)
            cv += r
        t = linspace(0, pi*2, 50)
        cv .append(list(zip(sin(t), t*0, cos(t))))
        self.c = cv

    def limit(self):
        lim = max([max([max([abs(p[0]), abs(p[2])]) for p in cc] ) for cc in [self.c[i] for i in self.c_large]])
        return lim

    def rotate(self, angles):
        ph = rad(angles[0])
        th = rad(angles[1])
        m1 = [[cos(ph),-sin(ph),0],[sin(ph),cos(ph),0],[0,0,1]]
        m2 = [[1,0,0],[0,cos(th),sin(th)],[0,-sin(th),cos(th)]]
        m = matmul(m1, m2)
        self.c = [[ tuple(matmul(p, m)) for p in cc ] for cc in self.c]


plt.figure(figsize = (6,5.5))

if 1:
    countries = ['Russia','Australia']
    colors = ['g', 'r']
    b = []
    for country, col in zip(countries, colors):
        s = Country_Shape(country)
        c = s.center
        s.rotate(c)
        s.plot(col, 1)
        b.append(s.limit())
    b = max(b)
    plt.xlim((-b,b)) 
    plt.ylim((-b,b))
    plt.grid()
    plt.show()
    
if 0:
    g = Country_Shape('Globe')
    s = Country_Shape('Antarctica')
    c = s.center
    g.rotate(c)
    s.rotate(c)
    g.truncate()
    g.plot('k', 0.5)
    s.plot('r', 1)
    plt.show()





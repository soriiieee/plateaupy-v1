import os
import pandas as pd

import geopandas as gpd
from shapely.geometry import Polygon,Point,MultiPolygon


def make_square_polygon(bounds):
    x0,y0,x1,y1 = bounds
    return Polygon([(x0,y0),(x1,y0),(x1,y1),(x0,y1)])


    
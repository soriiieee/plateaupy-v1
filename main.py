import os
import sys
import plateaupy  
from plateaupy.plobj import plobj


class Dataset:
    city_gml_path = "/Users/sori-mac-v1/work/plateaupy/input/44204_hita-shi_2020_citygml_3_op"


# pl = plateaupy.plparser(paths=['path_to_citygml'])
ds = Dataset()
pl = plateaupy.plparser(paths=[ds.city_gml_path])

pl.loadFiles(kind =plobj.BLDG,location=50300727)
# pl.loadFiles(location=50300727)

# print(type(pl.bldg))
# print(pl.bldg[50300727],type(pl.bldg[50300727].buildings[0]))
for ii,bld in enumerate(pl.bldg[50300727].buildings):
    print(bld)
    exit()
    
# for k ,v in pl.bldg:
#     print(k)
#     print(v)
#     exit()
# # print(pl.dem)
# # print(pl.tran)

exit()


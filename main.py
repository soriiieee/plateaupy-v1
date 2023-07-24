import os
import sys
import plateaupy  
from plateaupy.plobj import plobj
from plateaupy.plcodelists import scan_codelists


from pathlib import Path
import pandas as pd
import glob
cwd = Path(__file__).parent

from shapely.geometry import Polygon,Point,MultiPolygon




class Dataset:
    ############
    city_gml_path = os.path.join(cwd,"input","44204_hita-shi_2020_citygml_3_op")
    dir_codelists = os.path.join(city_gml_path,"codelists")
    
    bldg_gml_path = os.path.join(city_gml_path , "udx" , "bldg")
    
    output_city_code = os.path.join(cwd,"output" , "info" , "city_code_name.csv")
    
    output_bldg_path = os.path.join(cwd,"output" , "bldg")
    
    
    # output_folder = os.path.join(cwd,"output" , "02_info")
    
    
    ############    
    def __init__(self):
        os.makedirs(os.path.dirname(self.output_city_code),exist_ok=True)
        os.makedirs(self.output_bldg_path,exist_ok=True)
        print("start")
        
        
    def city_code_name_lists(self):
        dicts = scan_codelists(self.dir_codelists)
        
        lists = {}
        for ii,(k,v) in enumerate(dicts["Common_localPublicAuthorities"].items()):
            lists[ii] = [k,v]

        # print(type(dicts["Common_localPublicAuthorities"]))
        df = pd.DataFrame(lists).T
        df.columns = ["ID5" , "city_name"]
        df["ID5"]  = "N" + df["ID5"]
        df.to_csv(self.output_city_code, index=False)
        print("done...[city_code_name_lists]")
    
    def search_code_from_name(self,q):
        # q(query : 市町村名)が含まれる番号をreturnで返す
        if not os.path.exists(self.output_city_code):
            self.city_code_name_lists()
        
        df = pd.read_csv(self.output_city_code)
        df = df.loc[df["city_name"].str.contains(q),:]
        df["ID5"] = df["ID5"].apply(lambda x: x.replace("N",""))
        
        if df.shape[0]==0:
            print("[Error] Not Founded ... {} please check in {}".format(q,self.output_city_code))
            exit(1)
        elif df.shape[0]==1:
            print("[OK]\n",df)
            id5 = df["ID5"].values[0]
            city_name = df["city_name"].values[0]
            return id5,city_name
        else:
            print("[OK] multi candidattes...\n",df)
            exit(1)
        
    def all_locations(self):
        # pl = plateaupy.plparser(paths=[self.city_gml_path])
        files = sorted(glob.glob("{}/*_bldg_*_op.gml".format(self.bldg_gml_path)))
        locations = [ i.split("/")[-1].split("_")[0] for i in files]
        return locations
        

ds = Dataset()
# locations = ds.all_locations()
id5,city_name = ds.search_code_from_name("日田") #もし無かったら downloadの実装

# pl = plateaupy.plparser(paths=['path_to_citygml'])
pl = plateaupy.plparser(paths=[Dataset.city_gml_path])
location = 50300727




# show Building_usage
pl.loadFiles(kind =plobj.BLDG,location=location)
print('### Building_usage in ', location)
usage = pl.codelists['Building_usage']
res = dict()
for key in list(usage.keys()):
	res[key] = 0

for bldg in list(pl.bldg.values()): #1(locationを50300727　にしている、区画)
    # print(bldg.lowerCorner , bldg.upperCorner)
    # exit()
    # print(type(bldg.buildings), len(bldg.buildings)) #<class 'list'> 10
    
    # print(pl.locations)
    # print(type(bldg))
    # exit()
    buld_info = {}
    for bl in bldg.buildings:
        
        # print(bl.id, bl.usage, self.measuredHeight, self.storeysAboveGround, self.storeysBelowGround, \
		# 	self.address, self.buildingDetails, self.extendedAttribute, self.attr)
        # print(type(bl))
        # info = bl.getBuildingInformation() 
        bl.lod0RoofEdge    
        if len(bl.lod0RoofEdge) ==1:
            geom = bl.lod0RoofEdge[0]
            poly = Polygon([(x,y) for y,x in zip(geom[:,0],geom[:,1])])
        else:
            geoms =[]
            for geom in bl.lod0RoofEdge: #複数ある場合もあるのでlistになっている
                geoms += [(x,y) for y,x in zip(geom[:,0],geom[:,1])] 
            poly = MultiPolygon(geoms)
        
        buld_info[bl.id] = [
            bl.usage, bl.measuredHeight, bl.storeysAboveGround, bl.storeysBelowGround, \
			bl.address, poly , poly.centroid.x, poly.centroid.y, 
            bl.buildingDetails["prefecture"],bl.buildingDetails["city"],
            bl.extendedAttribute
        ]

        if bl.usage is not None:
            if bl.usage in res:
                res[bl.usage] += 1
        else:
            res["461"] +=1
                
total_cnt = 0
for key, cnt in list(res.items()):
	if cnt >= 0:
		print('{} ({}) : {}'.format(key, usage[key], cnt))
	total_cnt += cnt

df = pd.DataFrame(buld_info).T
df["location"] = location
df.to_csv(os.path.join(ds.output_bldg_path,"{}-{}_loc{}_bldgs.csv".format(id5,city_name,location)))
print("{}-{}_loc{}_bldgs".format(id5,city_name,location))
print('### total :', total_cnt)
# exit()


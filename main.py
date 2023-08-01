import os
import sys

# plateau-py modules
import plateaupy  
from plateaupy.plobj import plobj
from plateaupy.plcodelists import scan_codelists


from pathlib import Path
import pandas as pd
import glob
cwd = Path(__file__).parent

import configparser
from shapely.geometry import Polygon,Point,MultiPolygon

#sorimachi make
from utils.geo import make_square_polygon
from utils.utils import file_logger

class PlateauDataset:

    def __init__(self,config_parameter,city_name):
        self.config_parameter = config_parameter
        
        # home - Plateau Data folder 
        self.city_gml_path = os.path.join(cwd,"input",self.config_parameter["plateau"]["data"])
        
        self.dir_codelists = os.path.join(self.city_gml_path,"codelists")
        
        ## output director ##
        self.output_city_code = os.path.join(cwd,"output" , "info" , "city_code_name.csv")
        self.output_bldg_path = os.path.join(cwd,"output" , "bldg")
        self.output_dem_path = os.path.join(cwd,"output" , "dem")
        os.makedirs(os.path.dirname(self.output_city_code),exist_ok=True)
        os.makedirs(self.output_bldg_path,exist_ok=True)
        os.makedirs(self.output_dem_path,exist_ok=True)
        
        ## 検索用市町村DBの整備
        if not os.path.exists(self.output_city_code):
            self.city_code_name_lists()
        
        ## city_nameでplateauデータがあるかどうかの検索
        self.search_code_from_name(city_name)
        self.pl = plateaupy.plparser(paths=[self.city_gml_path])
        
    def city_code_name_lists(self):
        '''
        city_code / name を格納しておく（検索DB）
        N01100,北海道札幌市
        '''
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
                
        df = pd.read_csv(self.output_city_code)
        df = df.loc[df["city_name"].str.contains(q),:]
        df["ID5"] = df["ID5"].apply(lambda x: x.replace("N",""))
        
        if df.shape[0]==0:
            print("[Error] Not Founded ... {} please check in {}".format(q,self.output_city_code))
            exit(1)
        elif df.shape[0]==1:
            self.city_id5 = df["ID5"].values[0]
            self.city_name = df["city_name"].values[0]
            print("[OK] -> ",self.city_id5,self.city_name )
        else:
            print("[OK] multi candidattes...\n",df)
            exit(1)
        
    def all_locations(self):
        # pl = plateaupy.plparser(paths=[self.city_gml_path])
        files = sorted(glob.glob("{}/*_bldg_*_op.gml".format(self.bldg_gml_path)))
        locations = [ i.split("/")[-1].split("_")[0] for i in files]
        return locations
    
    ### load bldg data in location ###
    def load_bldg_each_code(self,location):
        
        if not str(location) in self.all_locations():
            print("input-location (bellow...)!!!\n" , self.all_locations())
            exit(1)
        
        
        self.pl.loadFiles(kind = plobj.BLDG,location= int(location) if isinstance(location , str) else location) # show Building_usage
        
        usage = self.pl.codelists['Building_usage']
        #initialize 
        res = dict()
        area_info = dict()
        buld_info = dict()
        
        for key in list(usage.keys()):
            res[key] = 0

        for bldg in list(self.pl.bldg.values()): #1(locationを50300727　にしている、区画)
    
            meshcode = os.path.basename(bldg.filename).split("_")[0]
            y0,x0 = list(bldg.lowerCorner)[:2] #
            y1,x1 = list(bldg.upperCorner)[:2] #標高は削除
            poly_sq = make_square_polygon([x0,y0,x1,y1]) 
            area_info[meshcode] = [x0,y0,x1,y1,poly_sq,len(bldg.buildings)]
            
            # print(area_info[meshcode])
            # exit()
            
            for bl in bldg.buildings:

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
                    if bl.usage in res: res[bl.usage] += 1
                else: res["461"] +=1
                        
        total_cnt = 0
        for key, cnt in list(res.items()):
            # if cnt >= 0: print('{} ({}) : {}'.format(key, usage[key], cnt))
            total_cnt += cnt

        df = pd.DataFrame(buld_info).T.reset_index()
        df.columns = ["id","usage" , "measuredHeight","storeysAboveGround","storeysBelowGround",
                      "address", "geometry" , "centroid_x", "centroid_y",
                      "prefecture","city","extendedAttribute"]
        df["location"] = location
        df.to_csv(os.path.join(ds.output_bldg_path,"{}-{}_loc{}_bldgs.csv".format(
            self.city_id5,self.city_name,location)))

    ### load DEM data in location ###
    def load_dem_each_code(self,location):
        location = int(location) if isinstance(location , str) else location
        self.pl.loadFiles(kind = plobj.DEM,location=location) # show Building_usage
                
        dem = self.pl.dem[location] # <plateaupy.pldem.pldem object at 0x7fe5bbcb5840>
        # print(type(self.pl.dem[location]))
        # print(dem.posLists.shape) #(86224,4,3) #triangle polygon
        
        lons,lats,zs = [],[],[] 
        for point in dem.posLists:
            for j in range(3):
                lats.append(point[j][0])
                lons.append(point[j][1])
                zs.append(point[j][2])
        
        df = pd.DataFrame({"lon" : lons , "lat":lats , "Z" : zs})
        df = df.drop_duplicates(subset=['lon', 'lat'], keep='last')
        # print("after duplicates",df.shape[0])
        df.to_csv(os.path.join(ds.output_dem_path,"{}-{}_loc{}_dem.csv".format(
            self.city_id5,self.city_name,location)))
                
        ##meshには、描画用の直交座標系が組み込まれているので、緯度/経度/標高データを利用する場合、posListsでOK
        if 0:
            print(dem.meshes[0].get_center_vertices())
            print(len(dem.meshes[0].vertices) , dem.meshes[0].vertices[0])


class FloodDepthCalculator:
    
    def __init__(self,config_parameter,plateau_ds,logger=None):
        
        self.config_parameter = config_parameter
        self.pld = plateau_ds
        self.logger = logger
        
        print(self.pld)
        
        


if __name__ == "__main__":
    
    
    config_parameter = configparser.ConfigParser()
    config_parameter.read("config.ini" , encoding='utf-8')
    
    plateau_ds = PlateauDataset(config_parameter,"日田")
    flc = FloodDepthCalculator(config_parameter,plateau_ds)
    
    





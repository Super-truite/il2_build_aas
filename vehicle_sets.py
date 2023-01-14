from pylgbmimec.basic_functions.mission_class import *
from pylgbmimec.basic_functions.find_object import *
from pylgbmimec.basic_functions.modify_object import *
from pylgbmimec.basic_functions.object_creation import copy_from_mission
from pylgbmimec.basic_functions.save_mission import *
from pylgbmimec.declarations.country import *
import math
import configparser
import os 
import pandas as pd
import warnings
warnings.filterwarnings("ignore")


config = configparser.ConfigParser()
config.read('config.ini')
mission_file = config['DEFAULT']['mission_file']
mission_file_temp = config['DEFAULT']['mission_file_temp']
path_mission = config['DEFAULT']['path_mission']
settings_map = str(config['DEFAULT']['settings_map'])
vehicleset_file = config['DEFAULT']['vehicleset_file']
planesinAir = config['DEFAULT']['planesinAir']
settings_allies_team = config['DEFAULT']['settings_allies_team']
Country_ID_Allies = CountryID[settings_allies_team]
setting_tank_realistic = config['DEFAULT']['setting_tank_realistic']
complete_original_path = os.path.join(path_mission,mission_file + '.Mission')
complete_final_path = os.path.join(path_mission,mission_file_temp +'.Mission')



def vehicleToScriptModel(vehicle):
    if "\\" in vehicle:
        vehicle1 = vehicle.split("\\")[0]
        vehicle2 = vehicle.split("\\")[1]
        model = "graphics\\vehicles\{0}\{1}.mgm".format(vehicle1, vehicle2)
        script = "LuaScripts\WorldObjects\\vehicles\{0}.txt".format(vehicle2)
    else:
        model = "graphics\\vehicles\{0}\{0}.mgm".format(vehicle)
        script = "LuaScripts\WorldObjects\\vehicles\{0}.txt".format(vehicle)
    return model, script

def planeToScriptModel(plane):
    model = "graphics\\planes\{0}\{0}.mgm".format(plane)
    script = "LuaScripts\WorldObjects\\Planes\{0}.txt".format(plane)
    return model, script

def replaceAll():
    # extract plane sets
    df = pd.read_csv(vehicleset_file, sep='\t', header=0, skiprows=0, nrows=6, index_col=0)
    dict_planes = df[df.index==settings_map].to_dict('records')[0]
    # extract Allies AI tanks sets
    df = pd.read_csv(vehicleset_file, sep='\t', header=1, skiprows=8, nrows=6, index_col=0)
    df = df[["t_allies_group{0}_{1}_{2}".format(i,j,k) for i in [1,2,3] for j in [1,2,3] for k in [1,2]]]
    dict_ai_tanks_allies = df[df.index==settings_map].to_dict('records')[0]
    # extract Allies AI tanks sets
    df = pd.read_csv(vehicleset_file, sep='\t', header=1, skiprows=17, nrows=6, index_col=0)
    df = df[["t_axis_group{0}_{1}_{2}".format(i,j,k) for i in [1,2,3] for j in [1,2,3] for k in [1,2]]]
    dict_ai_tanks_axis = df[df.index==settings_map].to_dict('records')[0]
    # extract AA guns Allies
    df = pd.read_csv(vehicleset_file, sep='\t', header=1, skiprows=26, nrows=6, index_col=0)
    df = df[["AA_Allies_heavy", "AA_Allies_medium", "AA_Allies_light"]]
    dict_aa_allies = df[df.index==settings_map].to_dict('records')[0]
    # extract AA guns Axis
    df = pd.read_csv(vehicleset_file, sep='\t', header=1, skiprows=35, nrows=6, index_col=0)
    df = df[["AA_Axis_heavy", "AA_Axis_medium", "AA_Axis_light"]]
    dict_aa_axis = df[df.index==settings_map].to_dict('records')[0]
    # extract ai planes
    df = pd.read_csv(vehicleset_file, sep='\t', header=1, skiprows=44, nrows=6, index_col=0)
    df = df[["Bomber_allies", "Bomber_axis", "Allies_Plane_fighter_1", "Allies_Plane_bomber_1", "Axis_Plane_fighter_1","Axis_Plane_bomber_1"]]
    dict_AI_planes = df[df.index==settings_map].to_dict('records')[0]
    print("vehicle sets extracted")
    print('##############################################')
    print(dict_planes)


    newMission=Mission()
    readMissionFromFile(newMission, complete_original_path )

    print('############## mission parsed ################')
    print('##############################################')
    # removing unwanted planes and adjusting planes number
    all_planes = dict_planes.keys()
    unwanted_planes = []
    for plane in all_planes:
        if dict_planes[plane] == 0:
            unwanted_planes.append(plane)

    objList = findObject(newMission, Name="_LOC_Airfield_")
    for obj in objList :
        print('--------------')
        allPlanesInAirfield = newMission.ObjList[obj].PropList['Planes']
        newPlanes = []
        for planeProperty in allPlanesInAirfield:
            model = planeProperty.Value['Model'].split('\\')[-1].split('.')[0]
            if model not in unwanted_planes:
                print(model, dict_planes[model])
                planeProperty.Value['Number'] = dict_planes[model]
                if planesinAir == "False":
                    planeProperty.Value['StartInAir'] = 0
                print(planeProperty)
                newPlanes.append(planeProperty)
        newMission.ObjList[obj].PropList['Planes'] = newPlanes

    # removing unwanted tanks
    # TODO
    if setting_tank_realistic == 'True':
        '''
        for NameAirfield in ['_LOC_TankfieldAxisLight_', '_LOC_TankfieldAxisHeavy_', '_LOC_TankfieldAlliesLight_', '_LOC_TankfieldAxisHeavy_']:
            objList = findObject(newMission, Name=NameAirfield)
            for obj in objList :
                print('--------------')
                allPlanesInAirfield = newMission.ObjList[obj].PropList['Planes']
                newPlanes = []
                for planeProperty in allPlanesInAirfield:
                    model = planeProperty.Value['Model'].split('\\')[-1].split('.')[0]
                    if model not in unwanted_planes:
                        newPlanes.append(planeProperty)
                newMission.ObjList[obj].PropList['Planes'] = newPlanes
        '''
        pass

    # Replacing AI planes
    for name0 in ["Bomber_allies", "Bomber_axis", "Allies_Plane_fighter_1", "Allies_Plane_bomber_1", "Axis_Plane_fighter_1","Axis_Plane_bomber_1"]:
        AIPlanesList=findObject(newMission, Name=name0)
        if len(AIPlanesList) > 0:
            name = str(newMission.ObjList[AIPlanesList[0]].PropList['Name']).replace('"','')
            plane = dict_AI_planes[name]
            model, script = planeToScriptModel(plane)
            if name0 in ["Bomber_allies", "Allies_Plane_fighter_1", "Allies_Plane_bomber_1"]:
                modify_kv(newMission, AIPlanesList, Model=model, Script=script, Country=Country_ID_Allies)
            else:
                modify_kv(newMission, AIPlanesList, Model=model, Script=script)

    # Replacing AI tanks
    AITanksListAllies=findObject(newMission, Name="t_allies_group")
    for obj in AITanksListAllies:
        name = str(newMission.ObjList[obj].PropList['Name']).replace('"','')
        vehicle = dict_ai_tanks_allies[name]
        model, script = vehicleToScriptModel(vehicle)
        modify_kv(newMission, [obj], Model=model, Script=script, Country=Country_ID_Allies)
    AITanksListAxis=findObject(newMission, Name="t_axis_group")
    for obj in AITanksListAxis:
        name = str(newMission.ObjList[obj].PropList['Name']).replace('"','')
        print(name)
        vehicle = dict_ai_tanks_axis[name]
        model, script = vehicleToScriptModel(vehicle)
        print(model, script)
        modify_kv(newMission, [obj], Model=model, Script=script)

    # Fixing altitude of smokes/effects
    try:
        DummyEffectObjectsList = findObject(newMission, Type="Block", Name="_EFFECT_")
        dict_effect = {}
        for obj in DummyEffectObjectsList:
            name = newMission.ObjList[obj].PropList['Name']
            print(name)
            ypos = newMission.ObjList[obj].PropList['YPos']
            dict_effect[name] = ypos
        
        EffectObjectsList = findObject(newMission, Type="Effect", Name="_EFFECT_")
        print("----------------------------------------------")
        for obj in EffectObjectsList:
            name = newMission.ObjList[obj].PropList['Name']
            print(name, dict_effect)
            modify_kv(newMission, [obj], YPos=dict_effect[name])
        deleteObject(newMission, DummyEffectObjectsList)
    except:
        print("No effect blocks found")

    saveMission(newMission, complete_final_path)
    print("-------------------VEHICLE SET DONE---------------------------")

if __name__ == '__main__':
    replaceAll()
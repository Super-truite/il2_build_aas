import os 
import pandas as pd
import codecs
import shutil
import configparser
from pylgbmimec.basic_functions.mission_class import *
from pylgbmimec.basic_functions.find_object import *
from pylgbmimec.basic_functions.modify_object import *
from pylgbmimec.basic_functions.object_creation import copy_from_mission
from pylgbmimec.basic_functions.save_mission import *
from pylgbmimec.declarations.country import *

config = configparser.ConfigParser()
config.read('config.ini')
missions_paths = config['DEFAULT']['path_mission']
final_missions_paths = config['DEFAULT']['final_path_mission']
mission_file = config['DEFAULT']['mission_file']
mission_file_output = config['DEFAULT']['mission_file_output']
localization_file = config['DEFAULT']['localization_file']

localisation_eng = os.path.join(missions_paths, mission_file+'.eng')
localisation_fra = os.path.join(missions_paths, mission_file+'.fra')
localisation_ger = os.path.join(missions_paths, mission_file+'.ger')
localisation_pol = os.path.join(missions_paths, mission_file+'.pol')
localisation_rus = os.path.join(missions_paths, mission_file+'.rus')
localisation_spa = os.path.join(missions_paths, mission_file+'.spa')
localisation_final_eng = os.path.join(final_missions_paths, mission_file_output+'.eng')
localisation_final_fra = os.path.join(final_missions_paths, mission_file_output+'.fra')
localisation_final_ger = os.path.join(final_missions_paths, mission_file_output+'.ger')
localisation_final_pol = os.path.join(final_missions_paths, mission_file_output+'.pol')
localisation_final_rus = os.path.join(final_missions_paths, mission_file_output+'.rus')
localisation_final_spa = os.path.join(final_missions_paths, mission_file_output+'.spa')
mission_file_path = os.path.join(missions_paths, mission_file+'.Mission')
mission_final_file_path  = os.path.join(final_missions_paths, mission_file_output+'.Mission')


def add_localization():
    localisation_files = {"eng": localisation_eng,
                        "fra": localisation_fra,
                        "ger": localisation_ger,
                        "pol": localisation_pol,
                        "rus": localisation_rus,
                        "spa": localisation_spa}

    localisation_final_files = {"eng": localisation_final_eng,
                        "fra": localisation_final_fra,
                        "ger": localisation_final_ger,
                        "pol": localisation_final_pol,
                        "rus": localisation_final_rus,
                        "spa": localisation_final_spa}

    newMission=Mission()
    readMissionFromFile(newMission, mission_file_path)

    csv_file = localization_file
    df = pd.read_csv(csv_file, sep='\t', lineterminator='\n')

    print(df)
    keys = df["name"].values
    print(keys)
    dict_all = {}
    for language in localisation_files.keys():
        d = {}
        print(df.columns)
        try:
            values = df[language].values
        except:
            values = df[language+'\r'].values
        print(values)
        print(language)
        for i, k in enumerate(keys):
            d[k] = values[i]
        dict_all[language] = d

    dict_LOC = {}
    for name in keys:
        lines = []
        print(name)
        objects = findObject(newMission, Type="MCU_TR_Subtitle", Name=name)
        for obj in objects:
            line = newMission.ObjList[obj].PropList["SubtitleInfo"]["LCText"]
            lines.append(line)
        objects2 = findObject(newMission, Type="MCU_Icon")
        objects = findObject(newMission, Type="MCU_Deactivate", Name=name)
        for obj in objects:
            target = list(newMission.ObjList[obj].PropList["Targets"])[0]
            for obj2 in objects2:
                if int(newMission.ObjList[obj2].PropList['Index']) == target:
                    line = newMission.ObjList[obj2].PropList['LCName']
                    lines.append(line)
        objects = findObject(newMission, Type="MCU_Activate", Name=name)
        for obj in objects:
            target = list(newMission.ObjList[obj].PropList["Targets"])[0]
            for obj2 in objects2:
                if int(newMission.ObjList[obj2].PropList['Index']) == target:
                    line = newMission.ObjList[obj2].PropList['LCName']
                    lines.append(line)
        if len(lines) != 0:
            dict_LOC[name] = lines
    dict_LOC["_LOC_Name_"] = [0]
    dict_LOC["_LOC_Description_"] = [1]
    reverse_dict_LOC = {}
    for k, v in dict_LOC.items():
        for i in v:
            reverse_dict_LOC[i] = k
           
    print(dict_all[language].keys())
    for language in localisation_files.keys():
        with codecs.open(localisation_files["eng"], "r", "utf-16") as f:
            lines = f.readlines()
        newlines = []
        for l in lines:
            line_index = int(l.split(':')[0])
            if line_index in reverse_dict_LOC.keys():
                print(reverse_dict_LOC[line_index])
                newline = str(line_index) + ':' + dict_all[language][reverse_dict_LOC[line_index]] + "\n"
                newlines.append(newline)
            else:
                newlines.append(l)
        with codecs.open(localisation_final_files[language], "w", "utf-16") as f:
            f.writelines(newlines)
    #zone_left_down_axis = findObject(newMission, Name="Artillery_Zone_Axis_1")[0]
add_localization()





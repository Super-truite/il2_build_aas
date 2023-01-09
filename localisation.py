import os 
import pandas as pd
import codecs
import shutil
import configparser
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
    if not os.path.exists(final_missions_paths):
        os.makedirs(final_missions_paths)
    '''
    if mission_file != mission_file_output:
        shutil.copyfile(mission_file_path , mission_final_file_path )
    '''
    list_file = os.path.join(missions_paths, mission_file+'.list')
    list_final_file = os.path.join(final_missions_paths, mission_file_output+'.list')
    if list_file != list_final_file:
        shutil.copyfile(list_file, list_final_file)

    with open(list_final_file, "r") as f:
        s = f.read()
        s = s.replace(mission_file.lower(), mission_file_output.lower())
    with open(list_final_file, "w") as f:
        f.write(s)
            

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

    # csv_file = os.path.join(missions_paths, localization_file)
    csv_file = localization_file
    df = pd.read_csv(csv_file, sep='\t')


    keys = df["name"].values
    dict_all = {}
    for language in localisation_files.keys():
        d = {}
        values = df[language].values
        for i, k in enumerate(keys):
            d[k] = values[i]
        dict_all[language] = d

    for language in localisation_files.keys():
        with codecs.open(localisation_files["eng"], "r", "utf-16") as f:
            s = f.read()
        for k, v in dict_all[language].items():
            print(k, v)
            s = s.replace(k, v)
        with codecs.open(localisation_final_files[language], "w", "utf-16") as f:
            f.write(s)
        


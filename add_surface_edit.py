import configparser
import os
import random
import string


config = configparser.ConfigParser()
config.read('config.ini')
mission_file_output = config['DEFAULT']['mission_file_output']
path_mission = config['DEFAULT']['path_mission']
SurfaceEdit = config['DEFAULT']['SurfaceEdit']
SurfaceData = config['DEFAULT']['SurfaceData']
SurfaceTex = config['DEFAULT']['SurfaceTex']
SurfaceTini = config['DEFAULT']['SurfaceTini']


path_list_file = os.path.join(path_mission,mission_file_output + '.list')

def random_hash():
    # get random password pf length 8 with letters, digits, and symbols
    characters = string.ascii_lowercase + string.digits 
    password = ''.join(random.choice(characters) for i in range(8))
    return password

def add_surface_info():
    if SurfaceEdit == "True":
        lines = []
        with open(path_list_file, "r") as f:
            lines = f.readlines()
        with open(path_list_file, "w") as f:
            f.writelines(lines)
            f.write('filename="multiplayer\dogfight\{0}","{1}"\n'.format(SurfaceTini, random_hash()))
            f.write('filename="multiplayer\dogfight\{0}","{1}"\n'.format(SurfaceData, random_hash()))
            f.write('filename="multiplayer\dogfight\{0}","{1}"'.format(SurfaceTex, random_hash()))



        
        
        

from pylgbmimec.basic_functions.mission_class import *
from pylgbmimec.basic_functions.find_object import *
from pylgbmimec.basic_functions.modify_object import *
from pylgbmimec.basic_functions.object_creation import copy_from_mission
from pylgbmimec.basic_functions.save_mission import *
from pylgbmimec.declarations.country import *
import math
import os
import configparser
config = configparser.ConfigParser()
config.read('config.ini')

GRIDSIZE = 10000
range_artillery = {"qf45in": 6000, "fk96na": 5000, "sfh13": 8000, "bm13" : 8000, "1124bm13": 8000, "sdkfz251-szf" : 2000, "124bm13": 8000, "batterytodt": 47000, "m272":21000, "r669":10000, "r683":33000, "lefh18": 11000, "ml20": 17000, "m1gun": 15000 ,"m30": 11000,"bl55in": 14000 }
final_path_mission = config['DEFAULT']['final_path_mission']
mission_file_input = config['DEFAULT']['mission_file']
mission_file_temp = config['DEFAULT']['mission_file_temp']
mission_file_output = config['DEFAULT']['mission_file_output']
input_path_mission = os.path.join(final_path_mission,mission_file_input+".Mission")
temp_path_mission = os.path.join(final_path_mission,mission_file_temp+".Mission")
path_pkl = os.path.join(final_path_mission,"Arty_"+mission_file_output+".pkl")
final_path_mission = os.path.join(final_path_mission,mission_file_output+".Mission")

def grid_to_pos(grid, key, subkey, subsubkey,  Xmax, Z0):
    ZPos = Z0 + (grid[1]-1) * GRIDSIZE + ((key-1) % 3) * (GRIDSIZE / 3) + ((subkey-1) % 3) * (GRIDSIZE / 9) + ((subsubkey-1) % 3) * (GRIDSIZE / 27) + (GRIDSIZE / 27) / 2
    XPos = Xmax - (grid[0]-1) * GRIDSIZE - (2-math.floor((key-1) / 3)) * (GRIDSIZE / 3) - (2-math.floor((subkey-1) / 3)) * (GRIDSIZE / 9) - (2-math.floor((subsubkey-1) / 3)) * (GRIDSIZE / 27) + (GRIDSIZE / 27) / 2 
    return XPos, ZPos

def grid_coordinates_to_key(x,y):
    return y * 3 + x + 1

def pos_to_grid(XPos, ZPos, Xmax, Z0):
    grid = [math.floor((Xmax - XPos)/GRIDSIZE) + 1, math.floor((ZPos - Z0)/GRIDSIZE) + 1]
    # Computing key
    # switching from X, Z IL2 coordinates to x,y indices inside the grid
    x_inside_grid = (ZPos - Z0) - (grid[1]-1) * GRIDSIZE
    y_inside_grid = GRIDSIZE - ((Xmax - XPos) - (grid[0]-1) * GRIDSIZE)
    x_index = math.floor(x_inside_grid / (GRIDSIZE/3))
    y_index = math.floor(y_inside_grid / (GRIDSIZE/3))
    key = grid_coordinates_to_key(x_index, y_index)
    # Computing sub key
    x_inside_subgrid = x_inside_grid - x_index*GRIDSIZE/3
    y_inside_subgrid = y_inside_grid - y_index*GRIDSIZE/3
    sub_x_index = math.floor(x_inside_subgrid/(GRIDSIZE/9))
    sub_y_index = math.floor(y_inside_subgrid/(GRIDSIZE/9))
    subkey = grid_coordinates_to_key(sub_x_index, sub_y_index)
    # Computing sub sub key
    x_inside_subsubgrid = x_inside_subgrid - sub_x_index*GRIDSIZE/9
    y_inside_subsubgrid = y_inside_subgrid - sub_y_index*GRIDSIZE/9
    subsub_x_index = math.floor(x_inside_subsubgrid/(GRIDSIZE/27))
    subsub_y_index = math.floor(y_inside_subsubgrid/(GRIDSIZE/27))
    subsubkey = grid_coordinates_to_key(subsub_x_index, subsub_y_index)
    return grid, key, subkey, subsubkey

def is_inside_rectangle(XPos, ZPos, rectangle):
    X_left_down, Z_left_down = rectangle[0]
    X_right_up, Z_right_up = rectangle[1]
    if XPos > X_left_down and XPos < X_right_up:
        if ZPos > Z_left_down and ZPos < Z_right_up:
            return True
        else:
            return False
    else:
        return False

def is_in_range(X_allies_arty_leader, Z_allies_arty_leader, type_allies_arty_leader, XPos, ZPos):
        range_arty = range_artillery[type_allies_arty_leader]
        if math.sqrt((X_allies_arty_leader-XPos)**2 + (Z_allies_arty_leader-ZPos)**2) < range_arty:
            return True
        else:
            return False
    
def available_firing_positions(Max_map_X, Max_map_Z, rectangle, X_arty_leader, Z_arty_leader, type_arty_leader, Xmax, Z0):
    list_positions = []
    list_positions_coord = []
    range_grid_X, range_grid_Y = math.floor(Max_map_X / GRIDSIZE +1), math.floor(Max_map_Z / GRIDSIZE + 1)
    for i in range(1,range_grid_X+1):
        for j in range(1,range_grid_Y+1):
            for key in range(1, 10):
                for subkey in range(1, 10):
                    for subsubkey in range(1, 10):
                        XPos, ZPos = grid_to_pos([i, j], key, subkey, subsubkey,  Xmax, Z0)
                        if is_inside_rectangle(XPos, ZPos, rectangle):
                            if is_in_range(X_arty_leader, Z_arty_leader, type_arty_leader, XPos, ZPos):
                                list_positions.append((XPos, ZPos))
                                list_positions_coord.append((i, j, key, subkey, subsubkey))
    return list_positions, list_positions_coord

def attack_area_text(index_mcu, grid, key, subkey, subsubkey, artillery_index, XPos, ZPos, side):
    a = "{0}".format(grid[0])
    if grid[0] < 10:
        a ="0{0}".format(grid[0])
    b = "{0}".format(grid[1])
    if grid[1] < 10:
        b ="0{0}".format(grid[1])
    grid_txt = a + b
    MCU = '''
MCU_CMD_AttackArea
{{
    Index = {0};
    Name = "";
    Desc = "";
    Targets = [];
    Objects = [{5}];
    XPos = {6:.3f};
    YPos = 74.175;
    ZPos = {7:.3f};
    XOri = 0.00;
    YOri = 223.96;
    ZOri = 0.00;
    AttackGround = 1;
    AttackAir = 0;
    AttackGTargets = 0;
    AttackArea = 200;
    Time = 60;
    Priority = 2;
}}
MCU_TR_ServerInput
{{
    Index = {8};
    Name = "artillery_{10}_{1}_{2}_{3}_{4}";
    Desc = "";
    Targets = [{9}];
    Objects = [];
    XPos = {6:.3f};
    YPos = 102.531;
    ZPos = {7:.3f};
    XOri = 0.00;
    YOri = 0.00;
    ZOri = 0.00;
    Enabled = 1;
}}
MCU_Timer
{{
    Index = {9};
    Name = "Trigger Timer";
    Desc = "";
    Targets = [{0}];
    Objects = [];
    XPos = {6:.3f};
    YPos = 80.655;
    ZPos = {7:.3f};
    XOri = 0.00;
    YOri = 0.00;
    ZOri = 0.00;
    Time = 1;
    Random = 100;
}}
    '''.format(index_mcu,grid_txt,key,subkey,subsubkey, artillery_index,XPos,ZPos, index_mcu+1, index_mcu+2, side)
    return MCU

def add_arty():
    # reading mission file
    '''
    try:
        newMission=Mission()
        readMissionFromFile(newMission, input_path_mission)
    except:
        with open(input_path_mission, 'r') as f:
            lines = f.readlines()
        lines = lines[0:1] + ['\n'] + lines[1:]
        with open(input_path_mission, 'w') as f:
            f.writelines(lines)
        newMission=Mission()
        readMissionFromFile(newMission, input_path_mission)
    '''
    newMission=Mission()
    readMissionFromFile(newMission, input_path_mission)


    # extracting positions of artillery boundaries
    zone_left_down_allies = findObject(newMission, Name="Artillery_Zone_Allies_1")[0]
    zone_right_up_allies = findObject(newMission, Name="Artillery_Zone_Allies_2")[0]
    X_left_down_allies, Z_left_down_allies = newMission.ObjList[zone_left_down_allies].PropList['XPos'], newMission.ObjList[zone_left_down_allies].PropList['ZPos']
    X_right_up_allies, Z_right_up_allies = newMission.ObjList[zone_right_up_allies].PropList['XPos'], newMission.ObjList[zone_right_up_allies].PropList['ZPos']
    rectangle_allies = [(X_left_down_allies, Z_left_down_allies), (X_right_up_allies, Z_right_up_allies)]

    zone_left_down_axis = findObject(newMission, Name="Artillery_Zone_Axis_1")[0]
    zone_right_up_axis = findObject(newMission, Name="Artillery_Zone_Axis_2")[0]
    X_left_down_axis, Z_left_down_axis = newMission.ObjList[zone_left_down_axis].PropList['XPos'], newMission.ObjList[zone_left_down_axis].PropList['ZPos']
    X_right_up_axis, Z_right_up_axis = newMission.ObjList[zone_right_up_axis].PropList['XPos'], newMission.ObjList[zone_right_up_axis].PropList['ZPos']
    rectangle_axis = [(X_left_down_axis, Z_left_down_axis), (X_right_up_axis, Z_right_up_axis)]

    # extracting map boundaries
    map_boudaries_object = findObject(newMission, Type='Vehicle', Name="map_boundary_1")[0]
    X0, Z0 = newMission.ObjList[map_boudaries_object].PropList['XPos'], newMission.ObjList[map_boudaries_object].PropList['ZPos']
    map_boudaries_object = findObject(newMission, Type='Vehicle', Name="map_boundary_2")[0]
    Xmax, Zmax = newMission.ObjList[map_boudaries_object].PropList['XPos'], newMission.ObjList[map_boudaries_object].PropList['ZPos']
    Max_map_X, Max_map_Z = Xmax - X0, Zmax - Z0

    # extracting position, type and link  of artillery
    allies_arty_leader = findObject(newMission, Name="Lead_artillery_allies")[0]
    X_allies_arty_leader, Z_allies_arty_leader = newMission.ObjList[allies_arty_leader].PropList['XPos'], newMission.ObjList[allies_arty_leader].PropList['ZPos']
    type_allies_arty_leader = newMission.ObjList[allies_arty_leader].PropList['Script'].split('\\')[-1].split('.txt')[0]
    link_index_allies_arty_leader = newMission.ObjList[allies_arty_leader].PropList['LinkTrId']
    firing_positions_allies, list_positions_coord_allies = available_firing_positions(Max_map_X, Max_map_Z, rectangle_allies, X_allies_arty_leader, Z_allies_arty_leader, type_allies_arty_leader, Xmax, Z0)

    axis_arty_leader = findObject(newMission, Name="Lead_artillery_axis")[0]
    X_axis_arty_leader, Z_axis_arty_leader = newMission.ObjList[axis_arty_leader].PropList['XPos'], newMission.ObjList[axis_arty_leader].PropList['ZPos']
    type_axis_arty_leader = newMission.ObjList[axis_arty_leader].PropList['Script'].split('\\')[-1].split('.txt')[0]
    link_index_axis_arty_leader = newMission.ObjList[axis_arty_leader].PropList['LinkTrId']
    firing_positions_axis, list_positions_coord_axis = available_firing_positions(Max_map_X, Max_map_Z, rectangle_axis, X_axis_arty_leader, Z_axis_arty_leader, type_axis_arty_leader, Xmax, Z0)
    # saving possible targets to pkl
    import pickle
    pickle.dump((list_positions_coord_allies, list_positions_coord_axis), open(path_pkl,"wb"))
    # extraction last index in the mission file (to add new objects after)
    index_mcu = max(list(newMission.ObjList.keys()))+2

    # creating text to add new serverinputs and attack mcus to the mission 
    txt_mcus = ""
    index_mcu = max(list(newMission.ObjList.keys())) + 1
    for a in firing_positions_allies:
        XPos, ZPos = a
        grid, key, subkey, subsubkey = pos_to_grid(XPos, ZPos, Xmax, Z0)
        mcu_txt = attack_area_text(index_mcu, grid, key, subkey, subsubkey, link_index_allies_arty_leader, XPos, ZPos, "allies")
        index_mcu += 3
        txt_mcus += mcu_txt
    index_mcu += 1
    for a in firing_positions_axis:
        XPos, ZPos = a
        grid, key, subkey, subsubkey = pos_to_grid(XPos, ZPos, Xmax, Z0)
        mcu_txt = attack_area_text(index_mcu, grid, key, subkey, subsubkey, link_index_axis_arty_leader, XPos, ZPos,"axis")
        index_mcu += 3
        txt_mcus += mcu_txt

    final_txt = '''
    Group
    {{
    Name = "Artillery_logic";
    Index = {0};
    Desc = "";
    {1}
    }}
    '''.format(index_mcu+1, txt_mcus)

    # replacing the mission file
    lines = []
    with open(temp_path_mission, "r") as f:
        lines = f.readlines()
    with open(final_path_mission, "w") as f:
        lines2 = lines[:-1]
        f.writelines(lines2)
        f.write(final_txt)
        f.write('# end of file')

if __name__ == '__main__':
    add_arty()
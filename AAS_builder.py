from localisation_V2 import add_localization  
from add_artillery_to_map import add_arty
from vehicle_sets import replaceAll
from add_surface_edit import add_surface_info


# Choice of unit sets + effect altitude fix
replaceAll()

# Add Artillery system
add_arty()
# Handle Localisation
add_localization()
# add .list surface
add_surface_info()

# save TODO resave bin

"""
"D:\SteamLibrary\steamapps\common\IL-2 Sturmovik Battle of Stalingrad\bin\resaver\mission_resaver.exe"
"D:\SteamLibrary\steamapps\common\IL-2 Sturmovik Battle of Stalingrad\data\Multiplayer\Dogfight\AASL_OktyabyrskiyV2.Mission"
"D:\SteamLibrary\steamapps\common\IL-2 Sturmovik Battle of Stalingrad\data\"
MissionResaver.exe -d C:\IL2\data -f C:\IL2\data\Multiplayer\Dogfight\Mission.mission

"D:\SteamLibrary\steamapps\common\IL-2 Sturmovik Battle of Stalingrad\bin\resaver\mission_resaver.exe" - d "D:\SteamLibrary\steamapps\common\IL-2 Sturmovik Battle of Stalingrad\data" "D:\SteamLibrary\steamapps\common\IL-2 Sturmovik Battle of Stalingrad\data\Multiplayer\Dogfight\AASL_OktyabyrskiyV2.Mission"
"""
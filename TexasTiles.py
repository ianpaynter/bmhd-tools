import json


# Poly dictionary
with open("F:/USRA/FUA_Processing/files/poly_to_tile_to_pixel.json", 'r') as f:
    # Load the dictionary
    poly_dict = json.load(f)


# Dictionary of texas polygons
texas_dict = {"84005349": [
        "5349",
        "Austin",
        "USA",
        "UnitedStates"
    ],
    "84005383": [
        "5383",
        "Longmont",
        "USA",
        "UnitedStates"
    ],
    "84005399": [
        "5399",
        "Killeen",
        "USA",
        "UnitedStates"
    ],
    "84005415": [
        "5415",
        "Loveland",
        "USA",
        "UnitedStates"
    ],
    "84005431": [
        "5431",
        "Fort Collins",
        "USA",
        "UnitedStates"
    ],
    "84005447": [
        "5447",
        "Greeley",
        "USA",
        "UnitedStates"
    ],
    "84005463": [
        "5463",
        "Waco",
        "USA",
        "UnitedStates"
    ],
    "84005479": [
        "5479",
        "Cheyenne",
        "USA",
        "UnitedStates"
    ],
    "84005495": [
        "5495",
        "Wichita",
        "Falls",
        "USA"
    ],
    "84005511": [
        "5511",
        "Houston",
        "USA",
        "UnitedStates"
    ],
    "84005527": [
        "5527",
        "College",
        "Station",
        "USA"
    ],
    "84005543": [
        "5543",
        "Dallas",
        "USA",
        "UnitedStates"
    ],
    "84005559": [
        "5559",
        "Lawton",
        "USA",
        "UnitedStates"
    ],
    "84005624": [
        "5624",
        "Billings",
        "USA",
        "UnitedStates"
    ],
    "84005672": [
        "5672",
        "Port Arthur",
        "USA",
    "UnitedStates"]}
unique_tile_list = []
tile_results_dict = {}
# For each polygon ID
for poly_id in texas_dict.keys():
    place_string = f'{texas_dict[poly_id][1]}, {texas_dict[poly_id][2]}'
    # Tile list
    tile_list = []
    # For each tile in the poly dict
    for tile in poly_dict[poly_id].keys():
        if tile not in tile_results_dict.keys():
            tile_results_dict[tile] = []
        tile_results_dict[tile].append(texas_dict[poly_id][1])
        # Append to list
        tile_list.append(tile)
        if tile not in unique_tile_list:
            unique_tile_list.append(tile)
    if len(tile_list) > 1:
        print(f'{place_string} in tiles {tile_list}')
    else:
        print(f'{place_string} in tile {tile_list}')
print('============================')
print(f'{len(list(texas_dict.keys()))} cities in {len(unique_tile_list)} tiles.')
print('============================')
for tile in tile_results_dict.keys():
    print(f'Tile {tile} contains {tile_results_dict[tile]}')
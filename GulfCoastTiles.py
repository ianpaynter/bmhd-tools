import json


# Poly dictionary
with open("F:/USRA/FUA_Processing/files/tile_to_poly.json", 'r') as f:
    # Load the dictionary
    tile_dict = json.load(f)

# Poly info dictionary
with open("F:/USRA/FUA_Processing/files/poly_info.json", 'r') as f:
    # Load the dictionary
    info_dict = json.load(f)

tile_list = ['h08v05', 'h08v06', 'h09v05', 'h09v06']

for tile in tile_list:

    print(f'Tile {tile} contains:')
    for city in tile_dict[tile]:
        city_string = ''
        for component in info_dict[city][1:]:
            if component != 'UnitedStates' and component != 'MEX' and component != 'CUB':
                city_string += f'{component} '
        print(city_string)
    print('================')
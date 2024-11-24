# Script to extract model data for .mdl.json files from existing .kurodlc.json files.
# Usage:  Place in a folder with custom .kurodlc.json files and run.
#
# Requires kurodlc_lib.py, place in the same folder.
#
# GitHub eArmada8/kuro_dlc_tool

try:
    import json, glob, os, sys
    from kurodlc_lib import kuro_tables
except ModuleNotFoundError as e:
    print("Python module missing! {}".format(e.msg))
    input("Press Enter to abort.")
    raise   

def extract_kurodlc_data_to_dlc_maker_format (json_name):
    kt = kuro_tables()
    kt.read_kurodlc_json(json_name)
    dlc_data = {}
    mdl_data = {}
    costume_entries_present = False
    dlc_entries_present = False
    recipe_ids_present = False # Can be True only for Ys X entries
    shop_entries_present = False
    if 'CostumeParam' in kt.new_entries and len(kt.new_entries['CostumeParam']) > 0: # Kuro 1 / 2
        game_type = 'kuro'
        mdl_key = 'mdl_name'
        costume_table_key = 'CostumeParam'
        item_table_key = 'ItemTableData'
        char_restrict_key = 'char_restrict'
        dlc_table_key = 'DLCTableData'
        costume_entries_present = True
        if 'DLCTableData' in kt.new_entries and len(kt.new_entries['DLCTableData']) > 0:
            dlc_entries_present = True
        if 'ShopItem' in kt.new_entries and len(kt.new_entries['ShopItem']) > 0:
            shop_by_item = {}
            for i in range(len(kt.new_entries['ShopItem'])):
                if kt.new_entries['ShopItem'][i]['item_id'] in shop_by_item:
                    shop_by_item[kt.new_entries['ShopItem'][i]['item_id']].append(kt.new_entries['ShopItem'][i]['shop_id'])
                else:
                    shop_by_item[kt.new_entries['ShopItem'][i]['item_id']] = [kt.new_entries['ShopItem'][i]['shop_id']]
            shop_entries_present = True
    elif 'CostumeTable' in kt.new_entries and len(kt.new_entries['CostumeTable']) > 0: # Ys X
        game_type = 'ys_x'
        mdl_key = 'costume_model'
        costume_table_key = 'CostumeTable'
        item_table_key = 'ItemTableData'
        dlc_table_key = 'DLCTable'
        char_restrict_key = 'character_id'
        costume_entries_present = True
        if 'DLCTable' in kt.new_entries and len(kt.new_entries['DLCTable']) > 0:
            dlc_entries_present = True
        if 'ProductInfo' in kt.new_entries and len(kt.new_entries['ProductInfo']) > 0:
            recipe_by_item = {}
            item_by_recipe = {}
            shop_by_item = {}
            for i in range(len(kt.new_entries['RecipeTableData'])):
                recipe_by_item[kt.new_entries['RecipeTableData'][i]['item_id']] = kt.new_entries['RecipeTableData'][i]['recipe_id']
                item_by_recipe[kt.new_entries['RecipeTableData'][i]['recipe_id']] = kt.new_entries['RecipeTableData'][i]['item_id']
            for j in range(len(kt.new_entries['ProductInfo'])):
                if item_by_recipe[kt.new_entries['ProductInfo'][j]['recipe_id']] in shop_by_item:
                    shop_by_item[item_by_recipe[kt.new_entries['ProductInfo'][j]['recipe_id']]].append(kt.new_entries['ProductInfo'][j]['shop_id'])
                else:
                    shop_by_item[item_by_recipe[kt.new_entries['ProductInfo'][j]['recipe_id']]] = [kt.new_entries['ProductInfo'][j]['shop_id']]
            recipe_ids_present = True
            shop_entries_present = True
    if costume_entries_present == True:
        item_quantity_dict = {}
        if dlc_entries_present == True:
            dlc_dict_keys = kt.get_schema(dlc_table_key, kt.schema_dict[dlc_table_key])['keys']
            dlc_data['game_type'] = game_type
            dlc_data.update({key:kt.new_entries[dlc_table_key][0][key] for key in dlc_dict_keys
                if key in kt.new_entries[dlc_table_key][0] and not key in ['items', 'quantity']})
            dlc_data['dlc_name'] = dlc_data.pop('name')
            dlc_data['dlc_desc'] = dlc_data.pop('desc')
            dlc_data['dlc_filename'] = json_name.replace('\\','/').split('/')[-1].split('.kurodlc.json')[0]
            item_quantity_dict = {kt.new_entries[dlc_table_key][0]['items'][i]: kt.new_entries[dlc_table_key][0]['quantity'][i]
                for i in range(len(kt.new_entries[dlc_table_key][0]['items']))}
        item_dict_keys = kt.get_schema(item_table_key, kt.schema_dict[item_table_key])['keys']
        for costume in kt.new_entries[costume_table_key]:
            mdl_data[costume[mdl_key]] = {'id': costume['item_id']}
            if item_table_key in kt.new_entries and len(kt.new_entries[item_table_key]) > 0:
                matching_items = [x for x in kt.new_entries[item_table_key] if x['id'] == mdl_data[costume[mdl_key]]['id']]
                if len(matching_items) > 0: # Should be no more than 1 as 'id' is a primary key
                    mdl_data[costume[mdl_key]].update(
                        {key:matching_items[0][key] for key in item_dict_keys if key in matching_items[0]})
            mdl_data[costume[mdl_key]]['chr_restrict'] = costume[char_restrict_key] # This overrides the item version
            if mdl_data[costume[mdl_key]]['id'] in item_quantity_dict:
                mdl_data[costume[mdl_key]]['item_quantity'] = item_quantity_dict[mdl_data[costume[mdl_key]]['id']]
            else:
                mdl_data[costume[mdl_key]]['item_quantity'] = 1
            if recipe_ids_present == True and mdl_data[costume[mdl_key]]['id'] in recipe_by_item:
                mdl_data[costume[mdl_key]]['recipe_id'] = recipe_by_item[mdl_data[costume[mdl_key]]['id']]
            if shop_entries_present == True and mdl_data[costume[mdl_key]]['id'] in shop_by_item:
                mdl_data[costume[mdl_key]]['stores'] = shop_by_item[mdl_data[costume[mdl_key]]['id']]
    return(dlc_data, mdl_data)

def process_kurodlc_json (json_name, overwrite = False):
    dlc_data, mdl_data = extract_kurodlc_data_to_dlc_maker_format(json_name)
    json_path = json_name.split('.kurodlc.json')[0]
    if os.path.exists(json_path) and (os.path.isdir(json_path)) and (overwrite == False):
        if str(input(json_path + " folder exists! Overwrite? (y/N) ")).lower()[0:1] == 'y':
            overwrite = True
    if (overwrite == True) or not os.path.exists(json_path):
        if not os.path.exists(json_path):
            os.mkdir(json_path)
        for mdl in mdl_data:
            with open('{0}/{1}.mdl.json'.format(json_path, mdl), 'wb') as f:
                f.write(json.dumps(mdl_data[mdl], indent = 4).encode('utf-8'))
        with open('{0}/dlc.json'.format(json_path), 'wb') as f:
            f.write(json.dumps(dlc_data, indent = 4).encode('utf-8'))
    return

if __name__ == "__main__":
    # Set current directory
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    else:
        os.chdir(os.path.abspath(os.path.dirname(__file__)))

    # If argument given, attempt to extract from file in argument
    if len(sys.argv) > 1:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('-o', '--overwrite', help="Overwrite existing files", action="store_true")
        parser.add_argument('kurodlc_json_filename', help="Name of .kurodlc.json file to export from (required).")
        args = parser.parse_args()
        if os.path.exists(args.kurodlc_json_filename) and args.kurodlc_json_filename[-13:] == '.kurodlc.json':
            process_kurodlc_json(args.kurodlc_json_filename, overwrite = args.overwrite)
    else:
        json_files = glob.glob('*.kurodlc.json')
        for i in range(len(json_files)):
            process_kurodlc_json(json_files[i])

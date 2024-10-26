# Script to generate .kurodlc.json file interactively for making DLC tables.
# Usage:  Place in a folder with custom mdl files and run.
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

class dlc_table_maker:
    def __init__ (self):
        self.kt = kuro_tables()
        self.game_type = "" # Filled in by self.get_dlc_details()
        self.dlc_details = self.get_dlc_details()
        self.name_dict = self.get_names()
        self.models = self.get_mdl_details()
        self.model_list = list(self.models.keys())
        self.kurodlc_json = {}

    def invalid_game_type(self):
            input("Invalid game type, DLC generation failed!  Press Enter to quit.")
            raise

    def get_dlc_details (self):
        if os.path.exists('dlc.json'):
            dlc_details = self.kt.read_struct_from_json('dlc.json')
        else:
            dlc_details = {}
        while 'game_type' not in dlc_details.keys() or not dlc_details['game_type'] in ['kuro', 'ys_x']:
            raw_game_type = str(input("Game Type: [kuro, ys_x] ")).encode('utf-8').decode('utf-8').lower()[:4]
            if raw_game_type in ['kuro', 'ys_x']:
                dlc_details['game_type'] = raw_game_type
            else:
                print("Invalid entry!")
        self.game_type = dlc_details['game_type']
        while 'id' not in dlc_details.keys():
            dlc_id_raw = input("DLC ID number: ")
            try:
                dlc_details['id'] = int(dlc_id_raw)
            except ValueError:
                print("Invalid entry!")
        if 'sort_id' not in dlc_details.keys():
            dlc_details['sort_id'] = dlc_details['id']
        if 'unk0' not in dlc_details.keys():
            dlc_details['unk0'] = 0
        if 'unk1' not in dlc_details.keys():
            dlc_details['unk1'] = 0
        while 'dlc_name' not in dlc_details.keys() or dlc_details['dlc_name'] == '':
            dlc_details['dlc_name'] = str(input("DLC Name: ")).encode('utf-8').decode('utf-8')
        while 'dlc_desc' not in dlc_details.keys() or dlc_details['dlc_desc'] == '':
            dlc_details['dlc_desc'] = str(input("DLC Description: ")).encode('utf-8').decode('utf-8')
            dlc_details['dlc_desc'] = dlc_details['dlc_desc'].replace('\\n','\n') # Allow newlines
        while 'dlc_filename' not in dlc_details.keys() or dlc_details['dlc_filename'] == '':
            json_name = input("Please input name for .kurodlc.json file (e.g. \"my_mod\" for \"my_mod.kurodlc.json\") ")
            valid = '-_.[]() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            dlc_details['dlc_filename'] = ''.join([x if x in valid else '_' for x in json_name])
        if self.game_type == 'kuro':
            if 'unk_txt' not in dlc_details.keys():
                dlc_details['unk_txt'] = ''
            if 'unk2' not in dlc_details.keys():
                dlc_details['unk2'] = 0
            if 'unk3' not in dlc_details.keys():
                dlc_details['unk3'] = 1
            if 'unk4' not in dlc_details.keys():
                dlc_details['unk4'] = 0
            if 'unk_arr' not in dlc_details.keys():
                dlc_details['unk_arr'] = []
            if 'unk5' not in dlc_details.keys():
                dlc_details['unk5'] = 0
        elif self.game_type == 'ys_x':
            while 'type_desc' not in dlc_details.keys() or dlc_details['type_desc'] == '':
                dlc_details['type_desc'] = str(input("DLC Type Description (e.g. Click to Unlock): ")).encode('utf-8').decode('utf-8')
                dlc_details['type_desc'] = dlc_details['type_desc'].replace('\\n','\n') # Allow newlines
        else:
            self.invalid_game_type() # Should be impossible to get here
        self.kt.write_struct_to_json(dlc_details, 'dlc.json')
        return(dlc_details)

    #Takes NameTableData.csv from tbled
    def get_names (self):
        if os.path.exists('t_name.tbl'):
            t_name = self.kt.read_table('t_name.tbl')
            if self.game_type == 'kuro':
                name_dict = {x['model']:{'char_id': x['char_id'], 'name': x['name']}\
                    for x in t_name['NameTableData'] if x['char_id'] < 200}
            elif self.game_type == 'ys_x':
                name_dict = {x['model']:{'char_id': x['char_id'], 'name': x['name']}\
                    for x in t_name['SNameTable'] if x['char_id'] < 10}
            else:
                self.invalid_game_type()
            return(name_dict)
        else:
            input("Warning, t_name.tbl is missing, this script will likely crash! Press Enter to continue.")
            return False

    def get_items_from_jsons (self):
        items = {}
        jsons = glob.glob('*.mdl.json')
        for i in range(len(jsons)):
            mdl_details = self.kt.read_struct_from_json(jsons[i])
            if 'item_id' in mdl_details.keys():
                items[mdl_details['item_id']] = mdl_details
        return(items)

    def get_chr_id (self, mdl_name):
        try:
            if self.game_type == 'kuro':
                base_name = "_".join(mdl_name.split('.')[0].split("_")[0:1])
                if base_name[:2] == 'fc':
                    base_name = base_name[1:]
            elif self.game_type == 'ys_x':
                mdl_prefix = mdl_name.split('.')[0]
                if len(mdl_prefix) == 5 and mdl_prefix[0:2] == 'c0':
                    base_name = "c00{0}0".format(mdl_prefix[3])
            return(self.name_dict[base_name]['char_id'])
        except KeyError:
            return 0x1FFFFFFF # This number is meaningless, just used to catch errors

    def get_chr_name (self, char_id):
        try:
            return([x['name'] for x in self.name_dict.values() if x['char_id'] == char_id][0])
        except KeyError:
            return ''

    def get_mdl_details (self):
        models = sorted(list(set([x.split('.json')[0] for x in glob.glob('*.mdl*')])))
        unique_chars = list(set([self.get_chr_id(x) for x in models if self.get_chr_id(x) != 0x1FFFFFFF]))
        existing_items = self.get_items_from_jsons()
        mdl_dict = {}
        for i in range(len(models)):
            print("\nProcessing {0}...\n".format(models[i]))
            if os.path.exists(models[i] + '.json'):
                mdl_details = self.kt.read_struct_from_json(models[i] + '.json')
            else:
                mdl_details = {}
            while 'id' not in mdl_details.keys():
                print("Note: (Kuro) If you want two attachments to be grouped, give them the same item ID.")
                item_id_raw = input("Item ID number for {0}: ".format(models[i]))
                try:
                    mdl_details['id'] = int(item_id_raw)
                    if self.game_type == 'kuro':
                        if mdl_details['id'] in list(existing_items.keys()):
                            mdl_details['category'] = existing_items[mdl_details['id']]['category']
                            mdl_details['quantity'] = existing_items[mdl_details['id']]['quantity']
                            mdl_details['name'] = existing_items[mdl_details['id']]['name']
                            mdl_details['desc'] = existing_items[mdl_details['id']]['desc']
                except ValueError:
                    print("Invalid entry!")
            while 'chr_restrict' not in mdl_details.keys() or mdl_details['chr_restrict'] == 0x1FFFFFFF:
                mdl_details['chr_restrict'] = self.get_chr_id(models[i])
                if mdl_details['chr_restrict'] == 0x1FFFFFFF: #Non-costume
                    print("Item Select Character Restriction: Please choose a character for {0}: ".format(models[i]))
                    print("-1. Any character")
                    for j in range(len(unique_chars)):
                        print("{0}. {1}".format(unique_chars[j], self.get_chr_name(unique_chars[j])))
                    print("(Any number <65536 is accepted, see t_name.tbl for other options)")
                    chr_id_raw = input("Character restriction for {0}: ".format(models[i]))
                    try:
                        if int(chr_id_raw) == -1:
                            mdl_details['chr_restrict'] = 0xFFFF
                        else:
                            if int(chr_id_raw) < 0x10000:
                                mdl_details['chr_restrict'] = int(chr_id_raw)
                            else:
                                print("Invalid entry!")
                    except ValueError:
                        print("Invalid entry!")
            if self.game_type == 'kuro':
                while 'category' not in mdl_details.keys() or mdl_details['category'] not in [17,18,19,24]:
                    print("Item type: [17=costume, 18=hair color, 19=accessory, 24=Xipha cover, leave blank for 17]")
                    item_type_raw = input("Item type for {0}: ".format(models[i]))
                    if item_type_raw == '':
                        print("No entry given, setting item type to default of 17.")
                        mdl_details['category'] = 17
                    else:
                        try:
                            mdl_details['category'] = int(item_type_raw)
                            if mdl_details['category'] not in [17,18,19,24]:
                                print("Invalid entry!")
                        except ValueError:
                            print("Invalid entry!")
                if 'subcategory' not in mdl_details.keys() or mdl_details['subcategory'] not in [15,17]:
                    mdl_details['subcategory'] = {17:15, 18:15, 19:15, 24:17}[mdl_details['category']]
                while 'attach_name' not in mdl_details.keys()\
                        or (mdl_details['attach_name'] == '' and mdl_details['category'] == 19):
                    if mdl_details['category'] == 19:
                        mdl_details['attach_name'] = str(input("Attach point for {0}: (e.g. Head_Point - check model .json file for valid options)  ".format(models[i]))).encode('utf-8').decode('utf-8')
                    else:
                        mdl_details['attach_name'] = ''
                if 'attach_txt1' not in mdl_details.keys():
                    mdl_details['attach_txt1'] = {17:'', 18:'', 19:'hold', 24:''}[mdl_details['category']]
            elif self.game_type == 'ys_x':
                if 'type' not in mdl_details.keys() or mdl_details['type'] == '':
                    # Costume only
                    mdl_details['type'] = {1:12, 2:13}[mdl_details['chr_restrict']]
                    # hopefully will expand to attachments later
            else:
                self.invalid_game_type() #probably ok to pass here, but this is for script debugging
            while 'name' not in mdl_details.keys() or mdl_details['name'] == '':
                mdl_details['name'] = str(input("Item Name for {0}: ".format(models[i]))).encode('utf-8').decode('utf-8')
            while 'desc' not in mdl_details.keys() or mdl_details['desc'] == '':
                mdl_details['desc'] = str(input("Item Description for {0}: ".format(models[i]))).encode('utf-8').decode('utf-8')
                mdl_details['desc'] = mdl_details['desc'].replace('\\n','\n') # Allow newlines
            if self.game_type == 'ys_x':
                while 'short_desc' not in mdl_details.keys() or mdl_details['short_desc'] == '':
                    mdl_details['short_desc'] = str(input("Item Short Description for {0}: ".format(models[i]))).encode('utf-8').decode('utf-8')
            while 'item_quantity' not in mdl_details.keys():
                item_quant_raw = input("How many should be included in the DLC? [Leave blank for 1] ".format(models[i]))
                if item_quant_raw == '':
                    mdl_details['item_quantity'] = 1
                else:
                    try:
                        mdl_details['item_quantity'] = min(max(int(item_quant_raw),1),99)
                    except ValueError:
                        print("Invalid entry!")
            while 'stores' not in mdl_details.keys():
                store_opt_raw = input("Would you like to add this item to a store? (y/N) ")
                store_opt = store_opt_raw[0].lower() if len(store_opt_raw) > 0 else 'N'
                if store_opt == 'y':
                    if os.path.exists('t_shop.tbl') or os.path.exists('t_shop.tbl.original'):
                        if os.path.exists('t_shop.tbl'):
                            shop_info = self.kt.read_table('t_shop.tbl')['ShopInfo']
                        else:
                            shop_info = self.kt.read_table('t_shop.tbl.original')['ShopInfo']
                        valid_stores = [x['id'] for x in shop_info]
                        need_list = input("Would you like a list of stores? (y/N) ")[0].lower()
                        if need_list == 'y':
                            for j in range(len(shop_info)):
                                print("{0}. {1}".format(shop_info[j]['id'], shop_info[j]['shop_name']))
                                if (j+1) % 25 == 0:
                                    input("Press Enter to continue...")
                    else:
                        print("t_shop.tbl unavailable, cannot display shop names.")
                    raw_input = input("What stores should have this item? (Separate ID numbers by spaces) ")
                    stores = sorted(list(set([int(x) for x in raw_input.split() if x.isnumeric()])))
                    if len(stores) > 0:
                        mdl_details['stores'] = stores
                    else:
                        print("Invalid input, please enter store IDs separated by spaces! e.g. 20 21 22")
                else:
                    mdl_details['stores'] = []
            if self.game_type == 'ys_x' and len(mdl_details['stores']) > 0:
                while 'recipe_id' not in mdl_details.keys():
                    recipe_id_raw = input("Recipe ID number - required for Ys X stores: ")
                    try:
                        mdl_details['recipe_id'] = int(recipe_id_raw)
                    except ValueError:
                        print("Invalid entry!")
            if self.game_type == 'kuro':
                if 'flags' not in mdl_details.keys():
                    mdl_details['flags'] = ''
                if 'unk_txt' not in mdl_details.keys():
                    mdl_details['unk_txt'] = {17:'1', 18:'1', 19:'', 24:'1'}[mdl_details['category']]
                if 'unk0' not in mdl_details.keys() or mdl_details['unk0'] == '':
                    mdl_details['unk0'] = 0
                if 'unk1' not in mdl_details.keys() or mdl_details['unk1'] == '':
                    mdl_details['unk1'] = 0
                if 'unk2' not in mdl_details.keys() or mdl_details['unk2'] == '':
                    mdl_details['unk2'] = 0
                if 'unk3' not in mdl_details.keys() or mdl_details['unk3'] == '':
                    mdl_details['unk3'] = 0
                if 'unk4' not in mdl_details.keys() or mdl_details['unk4'] == '':
                    mdl_details['unk4'] = 0
                if 'eff1_id' not in mdl_details.keys() or mdl_details['eff1_id'] == '':
                    mdl_details['eff1_id'] = 0
                if 'eff1_0' not in mdl_details.keys() or mdl_details['eff1_0'] == '':
                    mdl_details['eff1_0'] = 0
                if 'eff1_1' not in mdl_details.keys() or mdl_details['eff1_1'] == '':
                    mdl_details['eff1_1'] = 0
                if 'eff1_2' not in mdl_details.keys() or mdl_details['eff1_2'] == '':
                    mdl_details['eff1_2'] = 0
                if 'eff2_id' not in mdl_details.keys() or mdl_details['eff2_id'] == '':
                    mdl_details['eff2_id'] = 0
                if 'eff2_0' not in mdl_details.keys() or mdl_details['eff2_0'] == '':
                    mdl_details['eff2_0'] = 0
                if 'eff2_1' not in mdl_details.keys() or mdl_details['eff2_1'] == '':
                    mdl_details['eff2_1'] = 0
                if 'eff2_2' not in mdl_details.keys() or mdl_details['eff2_2'] == '':
                    mdl_details['eff2_2'] = 0
                if 'eff3_id' not in mdl_details.keys() or mdl_details['eff3_id'] == '':
                    mdl_details['eff3_id'] = 0
                if 'eff3_0' not in mdl_details.keys() or mdl_details['eff3_0'] == '':
                    mdl_details['eff3_0'] = 0
                if 'eff3_1' not in mdl_details.keys() or mdl_details['eff3_1'] == '':
                    mdl_details['eff3_1'] = 0
                if 'eff3_2' not in mdl_details.keys() or mdl_details['eff3_2'] == '':
                    mdl_details['eff3_2'] = 0
                if 'eff4_id' not in mdl_details.keys() or mdl_details['eff4_id'] == '':
                    mdl_details['eff4_id'] = 0
                if 'eff4_0' not in mdl_details.keys() or mdl_details['eff4_0'] == '':
                    mdl_details['eff4_0'] = 0
                if 'eff4_1' not in mdl_details.keys() or mdl_details['eff4_1'] == '':
                    mdl_details['eff4_1'] = 0
                if 'eff4_2' not in mdl_details.keys() or mdl_details['eff4_2'] == '':
                    mdl_details['eff4_2'] = 0
                if 'eff5_id' not in mdl_details.keys() or mdl_details['eff5_id'] == '':
                    mdl_details['eff5_id'] = 0
                if 'eff5_0' not in mdl_details.keys() or mdl_details['eff5_0'] == '':
                    mdl_details['eff5_0'] = 0
                if 'eff5_1' not in mdl_details.keys() or mdl_details['eff5_1'] == '':
                    mdl_details['eff5_1'] = 0
                if 'eff5_2' not in mdl_details.keys() or mdl_details['eff5_2'] == '':
                    mdl_details['eff5_2'] = 0
                if 'unk5' not in mdl_details.keys() or mdl_details['unk5'] == '':
                    mdl_details['unk5'] = 0
                if 'hp' not in mdl_details.keys() or mdl_details['hp'] == '':
                    mdl_details['hp'] = 0
                if 'ep' not in mdl_details.keys() or mdl_details['ep'] == '':
                    mdl_details['ep'] = 0
                if 'patk' not in mdl_details.keys() or mdl_details['patk'] == '':
                    mdl_details['patk'] = 0
                if 'pdef' not in mdl_details.keys() or mdl_details['pdef'] == '':
                    mdl_details['pdef'] = 0
                if 'matk' not in mdl_details.keys() or mdl_details['matk'] == '':
                    mdl_details['matk'] = 0
                if 'mdef' not in mdl_details.keys() or mdl_details['mdef'] == '':
                    mdl_details['mdef'] = 0
                if 'str' not in mdl_details.keys() or mdl_details['str'] == '':
                    mdl_details['str'] = 0
                if 'def' not in mdl_details.keys() or mdl_details['def'] == '':
                    mdl_details['def'] = 0
                if 'ats' not in mdl_details.keys() or mdl_details['ats'] == '':
                    mdl_details['ats'] = 0
                if 'adf' not in mdl_details.keys() or mdl_details['adf'] == '':
                    mdl_details['adf'] = 0
                if 'agl' not in mdl_details.keys() or mdl_details['agl'] == '':
                    mdl_details['agl'] = 0
                if 'dex' not in mdl_details.keys() or mdl_details['dex'] == '':
                    mdl_details['dex'] = 0
                if 'hit' not in mdl_details.keys() or mdl_details['hit'] == '':
                    mdl_details['hit'] = 0
                if 'eva' not in mdl_details.keys() or mdl_details['eva'] == '':
                    mdl_details['eva'] = 0
                if 'meva' not in mdl_details.keys() or mdl_details['meva'] == '':
                    mdl_details['meva'] = 0
                if 'crit' not in mdl_details.keys() or mdl_details['crit'] == '':
                    mdl_details['crit'] = 0
                if 'spd' not in mdl_details.keys() or mdl_details['spd'] == '':
                    mdl_details['spd'] = 0
                if 'mov' not in mdl_details.keys() or mdl_details['mov'] == '':
                    mdl_details['mov'] = 0
                if 'stack_size' not in mdl_details.keys() or mdl_details['stack_size'] == '':
                    mdl_details['stack_size'] = {17:1, 18:1, 19:8, 24:1}[mdl_details['category']]
                if 'price' not in mdl_details.keys() or mdl_details['price'] == '':
                    mdl_details['price'] = 100
                if 'anim' not in mdl_details.keys():
                    mdl_details['anim'] = ''
                if 'unk6' not in mdl_details.keys() or mdl_details['unk6'] == '':
                    mdl_details['unk6'] = 0
                if 'unk7' not in mdl_details.keys() or mdl_details['unk7'] == '':
                    mdl_details['unk7'] = 0
                if 'unk8' not in mdl_details.keys() or mdl_details['unk8'] == '':
                    mdl_details['unk8'] = 0
                if 'unk9' not in mdl_details.keys() or mdl_details['unk9'] == '':
                    mdl_details['unk9'] = 0
                if 'attach_unk0' not in mdl_details.keys() or mdl_details['attach_unk0'] == '':
                    mdl_details['attach_unk0'] = 0
                if 'attach_txt0' not in mdl_details.keys():
                    mdl_details['attach_txt0'] = ''
                if 'attach_unk1' not in mdl_details.keys() or mdl_details['attach_unk1'] == '':
                    mdl_details['attach_unk1'] = 0
                if 'attach_unk2' not in mdl_details.keys() or mdl_details['attach_unk2'] == '':
                    mdl_details['attach_unk2'] = 0
                if 'attach_txt2' not in mdl_details.keys():
                    mdl_details['attach_txt2'] = ''
            elif self.game_type == 'ys_x':
                if 'icon' not in mdl_details.keys() or mdl_details['icon'] == '':
                    mdl_details['icon'] = {12:370, 13:370}[mdl_details['type']]
                if 'unk0' not in mdl_details.keys() or mdl_details['unk0'] == '':
                    mdl_details['unk0'] = 0
                if 'unk1' not in mdl_details.keys() or mdl_details['unk1'] == '':
                    mdl_details['unk1'] = 0
                if 'unk2' not in mdl_details.keys() or mdl_details['unk2'] == '':
                    mdl_details['unk2'] = 0 # May need to set to 1 or a random number?
                if 'unk3' not in mdl_details.keys() or mdl_details['unk3'] == '':
                    mdl_details['unk3'] = 4
                if 'unk4' not in mdl_details.keys() or mdl_details['unk4'] == '':
                    mdl_details['unk4'] = 43
                if 'unk5' not in mdl_details.keys() or mdl_details['unk5'] == '':
                    mdl_details['unk5'] = 0
                if 'unk6' not in mdl_details.keys() or mdl_details['unk6'] == '':
                    mdl_details['unk6'] = 0
                if 'unk7' not in mdl_details.keys() or mdl_details['unk7'] == '':
                    mdl_details['unk7'] = 0 # May need to set to 10x for Adol and 20x for Karja?
                if 'unk8' not in mdl_details.keys() or mdl_details['unk8'] == '':
                    mdl_details['unk8'] = 1 # Might also be 0
                if 'unk9' not in mdl_details.keys() or mdl_details['unk9'] == '':
                    mdl_details['unk9'] = 0
                if 'obtain_type' not in mdl_details.keys():
                    mdl_details['obtain_type'] = ''
                if 'obtain_amount' not in mdl_details.keys() or mdl_details['obtain_amount'] == '':
                    mdl_details['obtain_amount'] = 0
                if 'unk10' not in mdl_details.keys() or mdl_details['unk10'] == '':
                    mdl_details['unk10'] = 0 # Might need to be some number >50000 or >50702??
                if 'hp' not in mdl_details.keys() or mdl_details['hp'] == '':
                    mdl_details['hp'] = 0
                if 'str' not in mdl_details.keys() or mdl_details['str'] == '':
                    mdl_details['str'] = 0
                if 'break' not in mdl_details.keys() or mdl_details['break'] == '':
                    mdl_details['break'] = 0
                if 'def' not in mdl_details.keys() or mdl_details['def'] == '':
                    mdl_details['def'] = 0
                if 'vit' not in mdl_details.keys() or mdl_details['vit'] == '':
                    mdl_details['vit'] = 0
                if 'luck' not in mdl_details.keys() or mdl_details['luck'] == '':
                    mdl_details['luck'] = 0
                if 'crit' not in mdl_details.keys() or mdl_details['crit'] == '':
                    mdl_details['crit'] = 0
                if 'eva' not in mdl_details.keys() or mdl_details['eva'] == '':
                    mdl_details['eva'] = 0
                if 'dmg' not in mdl_details.keys() or mdl_details['dmg'] == '':
                    mdl_details['dmg'] = 0
                if 'dmg_received' not in mdl_details.keys() or mdl_details['dmg_received'] == '':
                    mdl_details['dmg_received'] = 0
                if 'eff1_id' not in mdl_details.keys() or mdl_details['eff1_id'] == '':
                    mdl_details['eff1_id'] = 0
                if 'eff1_0' not in mdl_details.keys() or mdl_details['eff1_0'] == '':
                    mdl_details['eff1_0'] = 0
                if 'eff2_id' not in mdl_details.keys() or mdl_details['eff2_id'] == '':
                    mdl_details['eff2_id'] = 0
                if 'eff2_0' not in mdl_details.keys() or mdl_details['eff2_0'] == '':
                    mdl_details['eff2_0'] = 0
                if 'eff3_id' not in mdl_details.keys() or mdl_details['eff3_id'] == '':
                    mdl_details['eff3_id'] = 0
                if 'eff3_0' not in mdl_details.keys() or mdl_details['eff3_0'] == '':
                    mdl_details['eff3_0'] = 0
                if 'eff4_id' not in mdl_details.keys() or mdl_details['eff4_id'] == '':
                    mdl_details['eff4_id'] = 0
                if 'eff4_0' not in mdl_details.keys() or mdl_details['eff4_0'] == '':
                    mdl_details['eff4_0'] = 0
                if 'unk_txt' not in mdl_details.keys():
                    mdl_details['unk_txt'] = ''
                if 'unk11' not in mdl_details.keys() or mdl_details['unk11'] == '':
                    mdl_details['unk11'] = 0
                if 'unk12' not in mdl_details.keys() or mdl_details['unk12'] == '':
                    mdl_details['unk12'] = 0
                if 'unused0' not in mdl_details.keys() or mdl_details['unused0'] == '':
                    mdl_details['unused0'] = 0
                if 'unused1' not in mdl_details.keys() or mdl_details['unused1'] == '':
                    mdl_details['unused1'] = 0
                if 'unused2' not in mdl_details.keys() or mdl_details['unused2'] == '':
                    mdl_details['unused2'] = 0
                if 'unused3' not in mdl_details.keys() or mdl_details['unused3'] == '':
                    mdl_details['unused3'] = 0
                if 'unused4' not in mdl_details.keys() or mdl_details['unused4'] == '':
                    mdl_details['unused4'] = 0
                if 'unused5' not in mdl_details.keys() or mdl_details['unused5'] == '':
                    mdl_details['unused5'] = 0
            else:
                self.invalid_game_type() #probably ok to pass here, but this is for script debugging
            mdl_dict[models[i]] = mdl_details
            if mdl_details['id'] not in list(existing_items.keys()):
                existing_items[mdl_details['id']] = mdl_details
            self.kt.write_struct_to_json(mdl_details, models[i] + '.json')
        return(mdl_dict)

    def make_item_entry (self, mdl_name):
        mdl_data = self.models[mdl_name]
        if self.game_type == 'kuro':
            return({"id": mdl_data['id'], "chr_restrict": mdl_data['chr_restrict'], "flags": mdl_data['flags'],\
                "unk_txt": mdl_data['unk_txt'], "category": mdl_data['category'], "subcategory": mdl_data['subcategory'],\
                "unk0": mdl_data['unk0'], "unk1": mdl_data['unk1'], "unk2": mdl_data['unk2'], "unk3": mdl_data['unk3'],\
                "unk4": mdl_data['unk4'], "eff1_id": mdl_data['eff1_id'], "eff1_0": mdl_data['eff1_0'],\
                "eff1_1": mdl_data['eff1_1'], "eff1_2": mdl_data['eff1_2'], "eff2_id": mdl_data['eff2_id'],\
                "eff2_0": mdl_data['eff2_0'], "eff2_1": mdl_data['eff2_1'], "eff2_2": mdl_data['eff2_2'],\
                "eff3_id": mdl_data['eff3_id'], "eff3_0": mdl_data['eff3_0'], "eff3_1": mdl_data['eff3_1'],\
                "eff3_2": mdl_data['eff3_2'], "eff4_id": mdl_data['eff4_id'], "eff4_0": mdl_data['eff4_0'],\
                "eff4_1": mdl_data['eff4_1'], "eff4_2": mdl_data['eff4_2'], "eff5_id": mdl_data['eff5_id'],\
                "eff5_0": mdl_data['eff5_0'], "eff5_1": mdl_data['eff5_1'], "eff5_2": mdl_data['eff5_2'],\
                "unk5": mdl_data['unk5'], "hp": mdl_data['hp'], "ep": mdl_data['ep'], "patk": mdl_data['patk'],\
                "pdef": mdl_data['pdef'], "matk": mdl_data['matk'], "mdef": mdl_data['mdef'], "str": mdl_data['str'],\
                "def": mdl_data['def'], "ats": mdl_data['ats'], "adf": mdl_data['adf'], "agl": mdl_data['agl'],\
                "dex": mdl_data['dex'], "hit": mdl_data['hit'], "eva": mdl_data['eva'], "meva": mdl_data['meva'],\
                "crit": mdl_data['crit'], "spd": mdl_data['spd'], "mov": mdl_data['mov'],\
                "stack_size": mdl_data['stack_size'], "price": mdl_data['price'], "anim": mdl_data['anim'],\
                "name": mdl_data['name'], "desc": mdl_data['desc'], "unk6": mdl_data['unk6'], "unk7": mdl_data['unk7'],\
                "unk8": mdl_data['unk8'], "unk9": mdl_data['unk9']})
        elif self.game_type == 'ys_x':
            return({'id': mdl_data['id'], 'icon': mdl_data['icon'], 'name': mdl_data['name'], 'short_desc': mdl_data['short_desc'],\
                'desc': mdl_data['desc'], 'unk0': mdl_data['unk0'], 'type': mdl_data['type'], 'unk1': mdl_data['unk1'],
                'unk2': mdl_data['unk2'], 'unused0': mdl_data['unused0'], 'unused1': mdl_data['unused1'],\
                'unused2': mdl_data['unused2'], 'unk3': mdl_data['unk3'], 'unk4': mdl_data['unk4'], 'unk5': mdl_data['unk5'],\
                'unk6': mdl_data['unk6'], 'unk7': mdl_data['unk7'], 'unk8': mdl_data['unk8'], 'unk9': mdl_data['unk9'],\
                'unused3': mdl_data['unused3'], 'unused4': mdl_data['unused4'], 'unused5': mdl_data['unused5'],\
                'obtain_type': mdl_data['obtain_type'], 'obtain_amount': mdl_data['obtain_amount'], 'unk10': mdl_data['unk10'],\
                'hp': mdl_data['hp'], 'str': mdl_data['str'], 'break': mdl_data['break'], 'def': mdl_data['def'],\
                'vit': mdl_data['vit'], 'luck': mdl_data['luck'], 'crit': mdl_data['crit'], 'eva': mdl_data['eva'],\
                'dmg': mdl_data['dmg'], 'dmg_received': mdl_data['dmg_received'], 'eff1_id': mdl_data['eff1_id'],\
                'eff1_0': mdl_data['eff1_0'], 'eff2_id': mdl_data['eff2_id'], 'eff2_0': mdl_data['eff2_0'],\
                'eff3_id': mdl_data['eff3_id'], 'eff3_0': mdl_data['eff3_0'], 'eff4_id': mdl_data['eff4_id'],\
                'eff4_0': mdl_data['eff4_0'], 'unk_txt': mdl_data['unk_txt'], 'unk11': mdl_data['unk11'], 'unk12': mdl_data['unk12']})
        else:
            self.invalid_game_type() #probably ok to pass here, but this is for script debugging

    def make_costume_entry (self, mdl_name):
        mdl_data = self.models[mdl_name]
        if self.game_type == 'kuro':
            return({"char_restrict": mdl_data['chr_restrict'], "type": {17:0, 18:2, 19:1, 24:3}[mdl_data['category']],\
                "item_id": mdl_data['id'], "unk0": mdl_data['attach_unk0'], "unk_txt0": mdl_data['attach_txt0'],\
                "mdl_name": mdl_name.lower().split('.mdl')[0], "unk1": mdl_data['attach_unk1'], "unk2": mdl_data['attach_unk2'], "attach_name": mdl_data['attach_name'], "unk_txt1": mdl_data['attach_txt1'], "unk_txt2": mdl_data['attach_txt2']})
        elif self.game_type == 'ys_x':
            # Is there a scenario where this will not be valid?
            assert mdl_data['chr_restrict'] in [x['char_id'] for x in self.name_dict.values()]
            base_model = [x for x in dlc_table_maker.name_dict
                if dlc_table_maker.name_dict[x]['char_id'] == mdl_data['chr_restrict']][0]
            return({'character_id': mdl_data['chr_restrict'], 'item_id': mdl_data['id'],
                'base_model': base_model, 'costume_model': mdl_name.lower().split('.mdl')[0]})
        else:
            self.invalid_game_type() #probably ok to pass here, but this is for script debugging

    def make_dlc_entry (self):
        items = [x['id'] for x in self.models.values()]
        quant = [x['item_quantity'] for x in self.models.values()]
        if self.game_type == 'kuro':
            return({"id": self.dlc_details['id'], "sort_id": self.dlc_details['sort_id'], "items": items,\
                "unk0": self.dlc_details['unk0'], "quantity": quant, "unk1": self.dlc_details['unk1'],\
                "name": self.dlc_details['dlc_name'], "desc": self.dlc_details['dlc_desc'],\
                "unk_txt": self.dlc_details['unk_txt'], "unk2": self.dlc_details['unk2'],\
                "unk3": self.dlc_details['unk3'], "unk4": self.dlc_details['unk4'],\
                "unk_arr": self.dlc_details['unk_arr'], "unk5": self.dlc_details['unk5']})
        elif self.game_type == 'ys_x':
            return({'id': self.dlc_details['id'], 'sort_id': self.dlc_details['sort_id'],\
                'items': items, 'unk0': self.dlc_details['unk0'], 'quantity': quant,\
                'unk1': self.dlc_details['unk1'], 'name': self.dlc_details['dlc_name'],\
                'type_desc': self.dlc_details['type_desc'], 'desc': self.dlc_details['dlc_desc']})
        else:
            self.invalid_game_type() #probably ok to pass here, but this is for script debugging

    def make_shop_entries (self, mdl_name):
        mdl_data = self.models[mdl_name]
        shop_entries = []
        if self.game_type == 'kuro':
            for i in range(len(mdl_data['stores'])):
                shop_entries.append({"shop_id": mdl_data['stores'][i], "item_id": mdl_data['id'],\
                    "unknown": 1, "start_scena_flags": [], "empty1": 0, "end_scena_flags": [], "int2": 0})
        elif self.game_type == 'ys_x':
            for i in range(len(mdl_data['stores'])):
                shop_entries.append({"recipe_id": mdl_data['recipe_id'], "shop_id": mdl_data['stores'][i],\
                    "max_quantity": -1, "int2":0, "arr0": [], "int3": 0, "arr1": [], "int4": 0,\
                    "arr2": [], "int5": 0, "int6": -1, "int7": -1, "int8": -1, "int9": 0,\
                    "unk_txt0": "", "unk_txt1": ""})
        else:
            self.invalid_game_type() #probably ok to pass here, but this is for script debugging
        return(shop_entries)

    def make_recipe_entries (self, mdl_name):
        mdl_data = self.models[mdl_name]
        recipe_entries = []
        if self.game_type == 'kuro':
            pass # Not used for Kuro
        elif self.game_type == 'ys_x':
            recipe_entries.append({"recipe_id": mdl_data['recipe_id'], "unk0": 0,\
                "item_id": mdl_data['id'], "mat1_id": 2051, "mat1_quant": 0, "mat2_id": 0,\
                "mat2_quant": 0, "mat3_id": 0, "mat3_quant": 0, "mat4_id": 0, "mat4_quant": 0,\
                "mat5_id": 0, "mat5_quant": 0, "mat6_id": 0, "mat6_quant": 0})
        else:
            self.invalid_game_type() #probably ok to pass here, but this is for script debugging
        return(recipe_entries)

    def make_item_tbl_data (self):
        self.kurodlc_json['ItemTableData'] = []
        for i in range(len(self.model_list)):
            self.kurodlc_json['ItemTableData'].append(self.make_item_entry(self.model_list[i]))
        return

    def make_costume_tbl_data (self):
        subtable_header = {'kuro': 'CostumeParam', 'ys_x': 'CostumeTable'}[self.game_type]
        self.kurodlc_json[subtable_header] = []
        for i in range(len(self.model_list)):
            self.kurodlc_json[subtable_header].append(self.make_costume_entry(self.model_list[i]))
        return

    def make_dlc_tbl_data (self):
        subtable_header = {'kuro': 'DLCTableData', 'ys_x': 'DLCTable'}[self.game_type]
        self.kurodlc_json[subtable_header] = [self.make_dlc_entry()]
        return

    def make_shop_tbl_data (self):
        subtable_header = {'kuro': 'ShopItem', 'ys_x': 'ProductInfo'}[self.game_type]
        self.kurodlc_json[subtable_header] = []
        for i in range(len(self.model_list)):
            self.kurodlc_json[subtable_header].extend(self.make_shop_entries(self.model_list[i]))
        return

    def make_recipe_tbl_data (self):
        subtable_header = {'ys_x': 'RecipeTableData'}[self.game_type]
        self.kurodlc_json[subtable_header] = []
        for i in range(len(self.model_list)):
            self.kurodlc_json[subtable_header].extend(self.make_recipe_entries(self.model_list[i]))
        return

if __name__ == "__main__":
    # Set current directory
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    dlc_table_maker = dlc_table_maker()
    dlc_table_maker.make_costume_tbl_data()
    dlc_table_maker.make_dlc_tbl_data()
    dlc_table_maker.make_item_tbl_data()
    if dlc_table_maker.game_type == 'ys_x':
        dlc_table_maker.make_recipe_tbl_data()
    dlc_table_maker.make_shop_tbl_data()
    dlc_table_maker.kt.write_struct_to_json(dlc_table_maker.kurodlc_json,\
        dlc_table_maker.dlc_details['dlc_filename'] + '.kurodlc.json')
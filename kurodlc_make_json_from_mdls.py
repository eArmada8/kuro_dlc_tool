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
        self.dlc_details = self.get_dlc_details()
        self.name_dict = self.get_names()
        self.models = self.get_mdl_details()
        self.model_list = list(self.models.keys())
        self.kurodlc_json = {}

    def get_dlc_details (self):
        if os.path.exists('dlc.json'):
            with open('dlc.json', 'r') as f:
                dlc_details = json.loads(f.read())
        else:
            dlc_details = {}
        while 'id' not in dlc_details.keys():
            dlc_id_raw = input("DLC ID number: ")
            try:
                dlc_details['id'] = int(dlc_id_raw)
            except ValueError:
                print("Invalid entry!")
        while 'sort_id' not in dlc_details.keys():
            dlc_details['sort_id'] = dlc_details['id']
        while 'unk0' not in dlc_details.keys():
            dlc_details['unk0'] = 0
        while 'unk1' not in dlc_details.keys():
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
        while 'unk_txt' not in dlc_details.keys():
            dlc_details['unk_txt'] = ''
        while 'unk2' not in dlc_details.keys():
            dlc_details['unk2'] = 0
        while 'unk3' not in dlc_details.keys():
            dlc_details['unk3'] = 1
        while 'unk4' not in dlc_details.keys():
            dlc_details['unk4'] = 0
        while 'unk_arr' not in dlc_details.keys():
            dlc_details['unk_arr'] = []
        while 'unk5' not in dlc_details.keys():
            dlc_details['unk5'] = 0
        with open('dlc.json', "wb") as f:
            f.write(json.dumps(dlc_details, indent=4).encode("utf-8"))
        return(dlc_details)

    #Takes NameTableData.csv from tbled
    def get_names (self):
        if os.path.exists('t_name.tbl'):
            t_name = self.kt.read_table('t_name.tbl')
            name_dict = {x['model']:{'char_id': x['char_id'], 'name': x['name']}\
                for x in t_name['NameTableData'] if x['char_id'] < 200}
            return(name_dict)
        else:
            return False

    def get_items_from_jsons (self):
        items = {}
        jsons = glob.glob('*.mdl.json')
        for i in range(len(jsons)):
            with open(jsons[i], 'r') as f:
                mdl_details = json.loads(f.read())
            if 'item_id' in mdl_details.keys():
                items[mdl_details['item_id']] = mdl_details
        return(items)

    def get_chr_id (self, mdl_name):
        try:
            base_name = "_".join(mdl_name.split('.')[0].split("_")[0:1])
            if base_name[:2] == 'fc':
                base_name = base_name[1:]
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
                with open(models[i] + '.json', 'r') as f:
                    mdl_details = json.loads(f.read())
            else:
                mdl_details = {}
            while 'id' not in mdl_details.keys():
                print("Note: If you want two attachments to be grouped, give them the same item ID.")
                item_id_raw = input("Item ID number for {0}: ".format(models[i]))
                try:
                    mdl_details['id'] = int(item_id_raw)
                    if mdl_details['id'] in list(existing_items.keys()):
                        mdl_details['category'] = existing_items[mdl_details['id']]['category']
                        mdl_details['quantity'] = existing_items[mdl_details['id']]['quantity']
                        mdl_details['name'] = existing_items[mdl_details['id']]['name']
                        mdl_details['desc'] = existing_items[mdl_details['id']]['desc']
                except ValueError:
                    print("Invalid entry!")
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
            while 'subcategory' not in mdl_details.keys() or mdl_details['subcategory'] not in [15,17]:
                mdl_details['subcategory'] = {17:15, 18:15, 19:15, 24:17}[mdl_details['category']]
            while 'attach_name' not in mdl_details.keys()\
                    or (mdl_details['attach_name'] == '' and mdl_details['category'] == 19):
                if mdl_details['category'] == 19:
                    mdl_details['attach_name'] = str(input("Attach point for {0}: (e.g. Head_Point - check model .json file for valid options)  ".format(models[i]))).encode('utf-8').decode('utf-8')
                else:
                    mdl_details['attach_name'] = ''
            while 'attach_txt1' not in mdl_details.keys():
                mdl_details['attach_txt1'] = {17:'', 18:'', 19:'hold', 24:''}[mdl_details['category']]
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
            while 'name' not in mdl_details.keys() or mdl_details['name'] == '':
                mdl_details['name'] = str(input("Item Name for {0}: ".format(models[i]))).encode('utf-8').decode('utf-8')
            while 'desc' not in mdl_details.keys() or mdl_details['desc'] == '':
                mdl_details['desc'] = str(input("Item Description for {0}: ".format(models[i]))).encode('utf-8').decode('utf-8')
                mdl_details['desc'] = mdl_details['desc'].replace('\\n','\n') # Allow newlines
            while 'item_quantity' not in mdl_details.keys():
                item_quant_raw = input("How many should be included in the DLC? [Leave blank for 1] ".format(models[i]))
                if item_quant_raw == '':
                    mdl_details['item_quantity'] = 1
                else:
                    try:
                        mdl_details['item_quantity'] = min(max(int(item_quant_raw),1),99)
                    except ValueError:
                        print("Invalid entry!")
            while 'flags' not in mdl_details.keys():
                mdl_details['flags'] = ''
            while 'unk_txt' not in mdl_details.keys() or mdl_details['unk_txt'] == '':
                mdl_details['unk_txt'] = {17:'1', 18:'1', 19:'', 24:'1'}[mdl_details['category']]
            while 'unk0' not in mdl_details.keys() or mdl_details['unk0'] == '':
                mdl_details['unk0'] = 0
            while 'unk1' not in mdl_details.keys() or mdl_details['unk1'] == '':
                mdl_details['unk1'] = 0
            while 'unk2' not in mdl_details.keys() or mdl_details['unk2'] == '':
                mdl_details['unk2'] = 0
            while 'unk3' not in mdl_details.keys() or mdl_details['unk3'] == '':
                mdl_details['unk3'] = 0
            while 'unk4' not in mdl_details.keys() or mdl_details['unk4'] == '':
                mdl_details['unk4'] = 0
            while 'eff1_id' not in mdl_details.keys() or mdl_details['eff1_id'] == '':
                mdl_details['eff1_id'] = 0
            while 'eff1_0' not in mdl_details.keys() or mdl_details['eff1_0'] == '':
                mdl_details['eff1_0'] = 0
            while 'eff1_1' not in mdl_details.keys() or mdl_details['eff1_1'] == '':
                mdl_details['eff1_1'] = 0
            while 'eff1_2' not in mdl_details.keys() or mdl_details['eff1_2'] == '':
                mdl_details['eff1_2'] = 0
            while 'eff2_id' not in mdl_details.keys() or mdl_details['eff2_id'] == '':
                mdl_details['eff2_id'] = 0
            while 'eff2_0' not in mdl_details.keys() or mdl_details['eff2_0'] == '':
                mdl_details['eff2_0'] = 0
            while 'eff2_1' not in mdl_details.keys() or mdl_details['eff2_1'] == '':
                mdl_details['eff2_1'] = 0
            while 'eff2_2' not in mdl_details.keys() or mdl_details['eff2_2'] == '':
                mdl_details['eff2_2'] = 0
            while 'eff3_id' not in mdl_details.keys() or mdl_details['eff3_id'] == '':
                mdl_details['eff3_id'] = 0
            while 'eff3_0' not in mdl_details.keys() or mdl_details['eff3_0'] == '':
                mdl_details['eff3_0'] = 0
            while 'eff3_1' not in mdl_details.keys() or mdl_details['eff3_1'] == '':
                mdl_details['eff3_1'] = 0
            while 'eff3_2' not in mdl_details.keys() or mdl_details['eff3_2'] == '':
                mdl_details['eff3_2'] = 0
            while 'eff4_id' not in mdl_details.keys() or mdl_details['eff4_id'] == '':
                mdl_details['eff4_id'] = 0
            while 'eff4_0' not in mdl_details.keys() or mdl_details['eff4_0'] == '':
                mdl_details['eff4_0'] = 0
            while 'eff4_1' not in mdl_details.keys() or mdl_details['eff4_1'] == '':
                mdl_details['eff4_1'] = 0
            while 'eff4_2' not in mdl_details.keys() or mdl_details['eff4_2'] == '':
                mdl_details['eff4_2'] = 0
            while 'eff5_id' not in mdl_details.keys() or mdl_details['eff5_id'] == '':
                mdl_details['eff5_id'] = 0
            while 'eff5_0' not in mdl_details.keys() or mdl_details['eff5_0'] == '':
                mdl_details['eff5_0'] = 0
            while 'eff5_1' not in mdl_details.keys() or mdl_details['eff5_1'] == '':
                mdl_details['eff5_1'] = 0
            while 'eff5_2' not in mdl_details.keys() or mdl_details['eff5_2'] == '':
                mdl_details['eff5_2'] = 0
            while 'unk5' not in mdl_details.keys() or mdl_details['unk5'] == '':
                mdl_details['unk5'] = 0
            while 'hp' not in mdl_details.keys() or mdl_details['hp'] == '':
                mdl_details['hp'] = 0
            while 'ep' not in mdl_details.keys() or mdl_details['ep'] == '':
                mdl_details['ep'] = 0
            while 'patk' not in mdl_details.keys() or mdl_details['patk'] == '':
                mdl_details['patk'] = 0
            while 'pdef' not in mdl_details.keys() or mdl_details['pdef'] == '':
                mdl_details['pdef'] = 0
            while 'matk' not in mdl_details.keys() or mdl_details['matk'] == '':
                mdl_details['matk'] = 0
            while 'mdef' not in mdl_details.keys() or mdl_details['mdef'] == '':
                mdl_details['mdef'] = 0
            while 'str' not in mdl_details.keys() or mdl_details['str'] == '':
                mdl_details['str'] = 0
            while 'def' not in mdl_details.keys() or mdl_details['def'] == '':
                mdl_details['def'] = 0
            while 'ats' not in mdl_details.keys() or mdl_details['ats'] == '':
                mdl_details['ats'] = 0
            while 'adf' not in mdl_details.keys() or mdl_details['adf'] == '':
                mdl_details['adf'] = 0
            while 'agl' not in mdl_details.keys() or mdl_details['agl'] == '':
                mdl_details['agl'] = 0
            while 'dex' not in mdl_details.keys() or mdl_details['dex'] == '':
                mdl_details['dex'] = 0
            while 'hit' not in mdl_details.keys() or mdl_details['hit'] == '':
                mdl_details['hit'] = 0
            while 'eva' not in mdl_details.keys() or mdl_details['eva'] == '':
                mdl_details['eva'] = 0
            while 'meva' not in mdl_details.keys() or mdl_details['meva'] == '':
                mdl_details['meva'] = 0
            while 'crit' not in mdl_details.keys() or mdl_details['crit'] == '':
                mdl_details['crit'] = 0
            while 'spd' not in mdl_details.keys() or mdl_details['spd'] == '':
                mdl_details['spd'] = 0
            while 'mov' not in mdl_details.keys() or mdl_details['mov'] == '':
                mdl_details['mov'] = 0
            while 'stack_size' not in mdl_details.keys() or mdl_details['stack_size'] == '':
                mdl_details['stack_size'] = {17:1, 18:1, 19:8, 24:1}[mdl_details['category']]
            while 'price' not in mdl_details.keys() or mdl_details['price'] == '':
                mdl_details['price'] = 100
            while 'anim' not in mdl_details.keys():
                mdl_details['anim'] = ''
            while 'unk6' not in mdl_details.keys() or mdl_details['unk6'] == '':
                mdl_details['unk6'] = 0
            while 'unk7' not in mdl_details.keys() or mdl_details['unk7'] == '':
                mdl_details['unk7'] = 0
            while 'unk8' not in mdl_details.keys() or mdl_details['unk8'] == '':
                mdl_details['unk8'] = 0
            while 'unk9' not in mdl_details.keys() or mdl_details['unk9'] == '':
                mdl_details['unk9'] = 0
            while 'attach_unk0' not in mdl_details.keys() or mdl_details['attach_unk0'] == '':
                mdl_details['attach_unk0'] = 0
            while 'attach_txt0' not in mdl_details.keys():
                mdl_details['attach_txt0'] = ''
            while 'attach_unk1' not in mdl_details.keys() or mdl_details['attach_unk1'] == '':
                mdl_details['attach_unk1'] = 0
            while 'attach_unk2' not in mdl_details.keys() or mdl_details['attach_unk2'] == '':
                mdl_details['attach_unk2'] = 0
            while 'attach_txt2' not in mdl_details.keys():
                mdl_details['attach_txt2'] = ''
            mdl_dict[models[i]] = mdl_details
            if mdl_details['id'] not in list(existing_items.keys()):
                existing_items[mdl_details['id']] = mdl_details
            with open(models[i] + '.json', "wb") as f:
                f.write(json.dumps(mdl_details, indent=4).encode("utf-8"))
        return(mdl_dict)

    def make_item_entry (self, mdl_name):
        mdl_data = self.models[mdl_name]
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

    def make_costume_entry (self, mdl_name):
        mdl_data = self.models[mdl_name]
        return({"char_restrict": mdl_data['chr_restrict'], "type": {17:0, 18:2, 19:1, 24:3}[mdl_data['category']],\
            "item_id": mdl_data['id'], "unk0": mdl_data['attach_unk0'], "unk_txt0": mdl_data['attach_txt0'],\
            "mdl_name": mdl_name.lower().split('.mdl')[0], "unk1": mdl_data['attach_unk1'], "unk2": mdl_data['attach_unk2'], "attach_name": mdl_data['attach_name'], "unk_txt1": mdl_data['attach_txt1'], "unk_txt2": mdl_data['attach_txt2']})

    def make_dlc_entry (self):
        items = [x['id'] for x in self.models.values()]
        quant = [x['item_quantity'] for x in self.models.values()]
        return({"id": self.dlc_details['id'], "sort_id": self.dlc_details['sort_id'], "items": items,\
            "unk0": self.dlc_details['unk0'], "quantity": quant, "unk1": self.dlc_details['unk1'],\
            "name": self.dlc_details['dlc_name'], "desc": self.dlc_details['dlc_desc'],\
            "unk_txt": self.dlc_details['unk_txt'], "unk2": self.dlc_details['unk2'],\
            "unk3": self.dlc_details['unk3'], "unk4": self.dlc_details['unk4'],\
            "unk_arr": self.dlc_details['unk_arr'], "unk5": self.dlc_details['unk5']})

    def make_item_tbl_data (self):
        self.kurodlc_json['ItemTableData'] = []
        for i in range(len(self.model_list)):
            if self.models[self.model_list[i]]['id'] not in self.kurodlc_json['ItemTableData']:
                self.kurodlc_json['ItemTableData'].append(self.make_item_entry(self.model_list[i]))
        return

    def make_costume_tbl_data (self):
        self.kurodlc_json['CostumeParam'] = []
        for i in range(len(self.model_list)):
            if self.models[self.model_list[i]]['id'] not in self.kurodlc_json['CostumeParam']:
                self.kurodlc_json['CostumeParam'].append(self.make_costume_entry(self.model_list[i]))
        return

    def make_dlc_tbl_data (self):
        self.kurodlc_json['DLCTableData'] = [self.make_dlc_entry()]
        return

if __name__ == "__main__":
    # Set current directory
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    dlc_table_maker = dlc_table_maker()
    dlc_table_maker.make_costume_tbl_data()
    dlc_table_maker.make_dlc_tbl_data()
    dlc_table_maker.make_item_tbl_data()
    dlc_table_maker.kt.write_struct_to_json(dlc_table_maker.kurodlc_json,\
        dlc_table_maker.dlc_details['dlc_filename'] + '.kurodlc.json')
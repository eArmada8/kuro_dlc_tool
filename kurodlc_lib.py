# Library to read and write to kuro dlc tables.
# Usage:  Place in the same folder as the kuro dlc scripts.
#
# GitHub eArmada8/kuro_dlc_tool

try:
    import json, struct, shutil, glob, os, sys
except ModuleNotFoundError as e:
    print("Python module missing! {}".format(e.msg))
    input("Press Enter to abort.")
    raise   

class kuro_tables:
    def __init__(self):
        self.schema_dict = {}
        self.crc_dict = {}
        self.data2_start_offset = 0
        self.data2_buffer = b''
        self.new_entries = {}
        self.init_schemas()

    def init_schemas(self):
        tables = glob.glob('*.tbl.original') + [x for x in glob.glob('*.tbl') if not os.path.exists(x+'.original')]
        for table_name in tables:
            with open(table_name, 'rb') as f:
                magic = f.read(4)
                if magic == b'#TBL':
                    num_sections, = struct.unpack("<I", f.read(4))
                    for i in range(num_sections):
                        header = {}
                        header['name'] = f.read(64).replace(b'\x00',b'').decode('utf-8')
                        header['crc'], header['start_offset'], header['entry_length'],\
                            header['num_entries'] = struct.unpack("<4I", f.read(16))
                        if not header['name'] in self.crc_dict:
                            self.crc_dict[header['name']] = header['crc']
                        self.schema_dict[header['name']] = header['entry_length']
        return

    def get_schema(self, name, entry_length):
        self.schema_dict[name] = entry_length
        if name == 'DLCTableData' and entry_length == 88: # Kuro 1
            self.schema_dict[name] = entry_length
            return({'schema': "<2IQ2IQ2I3Q2HIQ2I", 'sch_len': 88,\
                'keys': ['id', 'sort_id', 'items', 'unk0', 'quantity',\
                    'unk1', 'name', 'desc', 'unk_txt', 'unk2', 'unk3',\
                    'unk4', 'unk_arr', 'unk5'],\
                'values': 'nnanantttnnnan', 'primary_key': 'id'})
        if name == 'DLCTableData' and entry_length == 64: # Kuro 2
            self.schema_dict[name] = entry_length
            return({'schema': "<2IQ2IQ2I3Q", 'sch_len': 64,\
                'keys': ['id', 'sort_id', 'items', 'unk0', 'quantity',\
                    'unk1', 'name', 'desc', 'unk_txt'],\
                'values': 'nnananttt', 'primary_key': 'id'})
        if name == 'DLCTable' and entry_length == 64: # Ys X
            self.schema_dict[name] = entry_length
            return({'schema': "<2IQ2IQ2I3Q", 'sch_len': 64,\
                'keys': ['id', 'sort_id', 'items', 'unk0', 'quantity',\
                    'unk1', 'name', 'type_desc', 'desc'],\
                'values': 'nnananttt', 'primary_key': 'id'})
        elif name == 'ItemTableData' and entry_length == 248: # Kuro 1 / 2
            return({'schema': "<2I2Q2BIHI2f20If20I3Q4I", 'sch_len': 248,\
                'keys': ['id','chr_restrict','flags','unk_txt','category','subcategory',\
                    'unk0','unk1','unk2','unk3','unk4','eff1_id','eff1_0','eff1_1','eff1_2',\
                    'eff2_id','eff2_0','eff2_1','eff2_2','eff3_id','eff3_0','eff3_1','eff3_2',\
                    'eff4_id','eff4_0','eff4_1','eff4_2','eff5_id','eff5_0','eff5_1','eff5_2',\
                    'unk5','hp','ep','patk','pdef','matk','mdef','str','def','ats','adf','agl',\
                    'dex','hit','eva','meva','crit','spd','mov','stack_size','price','anim',\
                    'name','desc','unk6','unk7','unk8','unk9'],\
                'values': 'nnttnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnntttnnnn',\
                'primary_key': 'id'})
        elif name == 'ItemTableData' and entry_length == 176: # Ys X
            return({'schema': "<2I3QI2hI3I4BI2B3HQfI10iIfIfIfIfQ2I", 'sch_len': 176,\
                'keys': ['id','icon','name','short_desc','desc','unk0','type','unk1','unk2',\
                'unused0','unused1','unused2',\
                'unk3','unk4','unk5','unk6','unk7','unk8','unk9','unused3','unused4','unused5',\
                'obtain_type','obtain_amount','unk10', 'hp','str','break',\
                'def','vit','luck','crit','eva','dmg','dmg_received',\
                'eff1_id','eff1_0','eff2_id','eff2_0','eff3_id','eff3_0','eff4_id','eff4_0',\
                'unk_txt','unk11','unk12'],\
                'values': 'nntttnnnnnnnnnnnnnnnnntnnnnnnnnnnnnnnnnnnnntnn',\
                'primary_key': 'id'})
        elif name == 'ItemKindParam2' and entry_length == 16: # Kuro 1 / 2
            return({'schema': "<2Q", 'sch_len': 16,\
                'keys': ['id', 'value'],\
                'values': 'nt', 'primary_key': 'id'})
        elif name == 'QuartzParam' and entry_length == 28: # Kuro 1 / 2
            return({'schema': "<8H8BI", 'sch_len': 28,\
                'keys': ['id', 'cost_e', 'cost_wa', 'cost_f', 'cost_wi', 'cost_t', 'cost_s', 'cost_m',\
                    'quant_e', 'quant_wa', 'quant_f', 'quant_wi', 'quant_t', 'quant_s', 'quant_m', 'unk0', 'unk1'],\
                'values': 'nnnnnnnnnnnnnnnnn', 'primary_key': 'id'})
        elif name == 'ItemTabType' and entry_length == 12: # Kuro 1 / 2
            return({'schema': "<3I", 'sch_len': 12,\
                'keys': ['id', 'int1', 'int2'],\
                'values': 'nnn', 'primary_key': 'id'})
        elif name == 'CostumeParam' and entry_length == 56: # Kuro 1 / 2
            return({'schema': "<4H2Q2I3Q", 'sch_len': 56,\
                'keys': ['char_restrict', 'type', 'item_id', 'unk0', 'unk_txt0', 'mdl_name',\
                    'unk1', 'unk2', 'attach_name', 'unk_txt1', 'unk_txt2'],\
                'values': 'nnnnttnnttt'})
        elif name == 'CostumeAttachOffset' and entry_length == 56: # Kuro 1 / 2
            return({'schema': "<2IQ10f", 'sch_len': 56,\
                'keys': ['char_id', 'unk0', 'mdl_name', 't0', 't1', 't2', 'r0', 'r1', 'r2',\
                    's0', 's1', 's2', 'unk1'],\
                'values': 'nntnnnnnnnnnn'})
        elif name == 'CostumeTable' and entry_length == 24: # Ys X
            return({'schema': "<2I2Q", 'sch_len': 24,\
                'keys': ['character_id', 'item_id', 'base_model', 'costume_model'],\
                'values': 'nntt'})
        elif name == 'CostumeAttachTable' and entry_length == 80: # Ys X
            return({'schema': "<2I2i8Q", 'sch_len': 80,\
                'keys': ['character_id', 'unk0', 'item_id', 'unk1', 'base_model',\
                'equip_model', 'attach_point', 'unk_text0', 'unk_text1',
                'unk_text2', 'unk_text3', 'unk_text4'],\
                'values': 'nnnntttttttt'})
        elif name == 'CostumeMaterialTable' and entry_length == 24: # Ys X
            return({'schema': "<2I2Q", 'sch_len': 24,\
                'keys': ['character_id', 'item_id', 'base_model', 'equip_model'],\
                'values': 'nntt'})
        elif name == 'CostumeUIFaceTable' and entry_length == 48: # Ys X
            return({'schema': "<Ii2IQ2IQ2I", 'sch_len': 48,\
                'keys': ['character_id', 'unk0', 'unk1', 'unk2', 'unk_array0',\
                'unk3', 'unk_array1', 'unk4'],\
                'values': 'nnnnanan'})
        elif name == 'NameTableData' and entry_length == 88: # Kuro 1
            return({'schema': "<11Q", 'sch_len': 88,\
                'keys': ['char_id', 'name', 'model', 'face', 'texture',\
                    'unk0', 'unk_txt0', 'unk_txt1', 'unk1', 'unk_txt2', 'unk_txt3'],\
                'values': 'nttttnttntt'})
        elif name == 'NameTableData' and entry_length == 104: # Kuro 2
            return({'schema': "<13Q", 'sch_len': 104,\
                'keys': ['char_id', 'name', 'model', 'face', 'texture',\
                    'unk0', 'unk_txt0', 'unk1', 'unk_txt1', 'unk2', 'unk_txt2',\
                    'unk_txt3', 'unk_txt4'],\
                'values': 'nttttntntnttt'})
        elif name == 'SNameTable' and entry_length == 96: # Ys X
            return({'schema': "<2I9QiIQ", 'sch_len': 96,\
                'keys': ['char_id', 'unk0', 'name', 'unk1', 'unk2',\
                    'model', 'ani', 'face', 'unk_model0', 'unk_model1', 'unk_model2',\
                    'unk3', 'unk4', 'unk_txt'],\
                'values': 'nntnnttttttnnt'})
        elif name == 'ShopInfo' and entry_length == 80: # Kuro 1 / 2
            return({'schema': "<4Q2H7f4I", 'sch_len': 80,\
                'keys': ['id', 'shop_name', 'long1', 'flag', 'empty', 'short1',\
                    'float1', 'float2', 'float3', 'float4', 'float5', 'float6',\
                    'float7', 'int1', 'int2', 'int3', 'int4'],\
                'values': 'ntntnnnnnnnnnnnnn'})
        elif name == 'ShopItem' and entry_length == 40: # Kuro 1 / 2
            return({'schema': "<2HIQ2IQ2I", 'sch_len': 40,\
                'keys': ['shop_id', 'item_id', 'unknown', 'start_scena_flags',\
                    'empty1', 'end_scena_flags', 'int2'],\
                'values': 'nnnbnbn'})
        elif name == 'ShopTypeDesc' and entry_length == 24: # Kuro 1 / 2
            return({'schema': "<2Q8B", 'sch_len': 24,\
                'keys': ['id', 'flag', 'byte1', 'byte2', 'byte3', 'byte4', 'byte5',\
                    'byte6', 'byte7', 'byte8'],\
                'values': 'ntnnnnnnnn'})
        elif name == 'ShopConv' and entry_length == 36: # Kuro 1 / 2
            return({'schema': "<I8f", 'sch_len': 36,\
                'keys': ['id', 'float1', 'float2', 'float3', 'float4', 'float5',\
                    'float6', 'float7', 'float8'],\
                'values': 'nnnnnnnnn'})
        elif name == 'TradeItem' and entry_length == 52: # Kuro 1 / 2
            return({'schema': "<13I", 'sch_len': 52,\
                'keys': ['item_id', 'trade_item_id1', 'quant1', 'trade_item_id2',\
                    'quant2', 'trade_item_id3', 'quant3', 'trade_item_id4', 'quant4',\
                    'trade_item_id5', 'quant5', 'trade_item_id6', 'quant6'],\
                'values': 'nnnnnnnnnnnnn'})
        elif name == 'ShopInfo' and entry_length == 32: # Ys X
            return({'schema': "<2I3Q", 'sch_len': 32,\
                'keys': ['id', 'unk0', 'shop_name', 'unk_txt1', 'unk_txt2'],\
                'values': 'nnttt'})
        elif name == 'ProductInfo' and entry_length == 96: # Ys X
            return({'schema': "<2I2iQ2IQ2IQ2I4i2Q", 'sch_len': 96,\
                'keys': ['recipe_id', 'shop_id', 'max_quantity', 'int2', 'arr0',\
                'int3', 'arr1', 'int4', 'arr2', 'int5', 'int6', 'int7', 'int8',\
                'int9', 'unk_txt0', 'unk_txt1'],\
                'values': 'nnnnananannnnntt'})
        elif name == 'ShopNameInfo' and entry_length == 24: # Ys X
            return({'schema': "<2I2Q", 'sch_len': 24,\
                'keys': ['unk0', 'unk1', 'unk_txt0', 'unk_txt1'],\
                'values': 'nntt'})
        elif name == 'RecipeTableData' and entry_length == 60: # Ys X
            return({'schema': "<15I", 'sch_len': 60,\
                'keys': ['recipe_id', 'unk0', 'item_id', 'mat1_id', 'mat1_quant',\
                'mat2_id', 'mat2_quant', 'mat3_id', 'mat3_quant', 'mat4_id', 'mat4_quant',\
                'mat5_id', 'mat5_quant', 'mat6_id', 'mat6_quant'],\
                'values': 'nnnnnnnnnnnnnnn'})
        else:
            return({})

    def read_struct_from_json(self, filename, raise_on_fail = True):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                return(json.loads(f.read()))
            except json.JSONDecodeError as e:
                print("Decoding error when trying to read JSON file {0}!\r\n".format(filename))
                print("{0} at line {1} column {2} (character {3})\r\n".format(e.msg, e.lineno, e.colno, e.pos))
                if raise_on_fail == True:
                    input("Press Enter to abort.")
                    raise
                else:
                    return(False)

    def write_struct_to_json(self, struct, filename):
        with open(filename, "wb") as f:
            f.write(json.dumps(struct, indent=4).encode("utf-8"))
        return

    # Schema must already be loaded by reading the original tables
    def validate_kurodlc_entries(self, json_data, json_name):
        for key in [x for x in json_data if len(json_data[x]) > 0]:
            if key in self.schema_dict:
                schema = self.get_schema(key, self.schema_dict[key])
                if not all([list(json_data[key][i].keys()) == schema['keys']\
                        for i in range(len(json_data[key]))]):
                    print("Validation of {0} failed, schema in {1} is incorrect!".format(json_name, key))
                    if [all([x in schema['keys'] for x in list(json_data[key][i].keys())]) for i in range(len(json_data[key]))]:
                        print("Keys present but out-of-order, attempting correction.")
                        for i in range(len(json_data[key])):
                            if not list(json_data[key][i].keys()) == schema['keys']:
                                json_data[key][i] = {x:json_data[key][i][x] for x in schema['keys']}
                    else:
                        input("Invalid or missing keys, auto-correction not possible.")
                        raise
                pass_value_validation = True
                problem_keys = []
                for i in range(len(schema['values'])):
                    if schema['values'][i] == 'n':
                        if not all([isinstance(json_data[key][j][schema['keys'][i]], int)\
                                or isinstance(json_data[key][j][schema['keys'][i]], float) for j in range(len(json_data[key]))]):
                            problem_keys.append(schema['keys'][i])
                            pass_value_validation = False
                    elif schema['values'][i] == 'a':
                        if not all([isinstance(json_data[key][j][schema['keys'][i]], list)\
                                and all([isinstance(k, int) for k in json_data[key][j][schema['keys'][i]]])\
                                for j in range(len(json_data[key]))]):
                            problem_keys.append(schema['keys'][i])
                            pass_value_validation = False
                    elif schema['values'][i] == 't':
                        if not all([isinstance(json_data[key][j][schema['keys'][i]], str) for j in range(len(json_data[key]))]):
                            problem_keys.append(schema['keys'][i])
                            pass_value_validation = False
                if pass_value_validation == False:
                    input("Validation of {0} failed, values {1} in {2} do not match the schema!".format(json_name, problem_keys, key))
                    raise
            else:
                input("Validation of {0} in {1} failed, schema not found! (tbl file missing)".format(key, json_name))
                raise
        return(json_data)

    def read_kurodlc_json(self, json_name):
        if os.path.exists(json_name):
            json_data = self.read_struct_from_json(json_name)
            self.validate_kurodlc_entries(json_data, json_name)
            for key in json_data:
                if key in self.new_entries:
                    self.new_entries[key].extend(json_data[key])
                else:
                    self.new_entries[key] = json_data[key]
        return

    def read_all_kurodlc_jsons(self):
        kurodlc_jsons = sorted(glob.glob('*.kurodlc.json'))
        for i in range(len(kurodlc_jsons)):
            self.read_kurodlc_json(kurodlc_jsons[i])
        return

    def update_table_with_kurodlc(self, table):
        for key in table:
            if key in self.new_entries:
                table[key].extend(self.new_entries[key])
                #For tables with primary keys, cull old entries by primary key if new one supercedes them
                schema = self.get_schema(key, self.schema_dict[key])
                if 'primary_key' in schema:
                    primary_key = schema['primary_key']
                    table[key] = list({table[key][i][primary_key]:table[key][i] for i in range(len(table[key]))}.values())
        return(table)

    def read_table(self, table_name):
        def read_array(offset, numvalues): #u32
            arr = []
            f.seek(offset)
            if numvalues > 0:
                arr.extend(list(struct.unpack("<{}I".format(numvalues), f.read(numvalues*4))))
            return(arr)
        def read_short_array(offset, numvalues): #u16
            arr = []
            f.seek(offset)
            if numvalues > 0:
                arr.extend(list(struct.unpack("<{}H".format(numvalues), f.read(numvalues*2))))
            return(arr)
        def read_null_term_str(offset):
            f.seek(offset)
            bstr = f.read(1)
            while bstr[-1] != 0:
                bstr += f.read(1)
            return(bstr[:-1].decode('utf-8'))
        def decode_row(raw_data, keys, values):
            i = 0
            assert len(keys) == len(values)
            decoded_data = {}
            for j in range(len(values)):
                if values[j] == 'n':
                    decoded_data[keys[j]] = raw_data[i]
                    i += 1
                elif values[j] == 'a':
                    decoded_data[keys[j]] = read_array(raw_data[i], raw_data[i+1])
                    i += 2
                elif values[j] == 'b':
                    decoded_data[keys[j]] = read_short_array(raw_data[i], raw_data[i+1])
                    i += 2
                elif values[j] == 't':
                    decoded_data[keys[j]] = read_null_term_str(raw_data[i])
                    i += 1
            return(decoded_data)
        with open(table_name, 'rb') as f:
            magic = f.read(4)
            if magic == b'#TBL':
                num_sections, = struct.unpack("<I", f.read(4))
                headers = []
                for i in range(num_sections):
                    header = {}
                    header['name'] = f.read(64).replace(b'\x00',b'').decode('utf-8')
                    header['crc'], header['start_offset'], header['entry_length'],\
                        header['num_entries'] = struct.unpack("<4I", f.read(16))
                    headers.append(header)
                    if not header['name'] in self.crc_dict:
                        self.crc_dict[header['name']] = header['crc']
                tbl_data = {}
                for i in range(num_sections):
                    f.seek(headers[i]['start_offset'])
                    schema = self.get_schema(headers[i]['name'], headers[i]['entry_length'])
                    if schema == {}:
                        continue
                    raw_data = [struct.unpack(schema['schema'], f.read(schema['sch_len'])) for j in range(headers[i]['num_entries'])]
                    tbl_data[headers[i]['name']] = [decode_row(x, schema['keys'], schema['values']) for x in raw_data]
                return(tbl_data)
        return False # Failed to read table properly

    def write_table(self, table_name):
        def write_array(data_list): #u32
            self.data2_buffer += struct.pack("<{}I".format(len(data_list)), *data_list)
        def write_short_array(data_list): #u16
            self.data2_buffer += struct.pack("<{}H".format(len(data_list)), *data_list)
        def write_null_term_str(string):
            self.data2_buffer += string.encode('utf-8') + b'\x00'
        def return_64_len_str(string):
            assert len(string) <= 64
            return(string.encode('utf-8') + b'\x00'*(64-len(string)))
        def encode_row(raw_data, schema_table):
            encoded_data = []
            for key in raw_data:
                if isinstance(raw_data[key], str):
                    data_offset = len(self.data2_buffer)
                    write_null_term_str(raw_data[key])
                    encoded_data.append(data_offset + self.data2_start_offset)
                elif isinstance(raw_data[key], list):
                    data_type = schema_table['values'][schema_table['keys'].index(key)]
                    if data_type == 'a':
                        #32-bit alignment
                        while len(self.data2_buffer) % 4 > 0:
                            self.data2_buffer += b'\x00'
                        data_offset = len(self.data2_buffer)
                        write_array(raw_data[key])
                    elif data_type == 'b':
                        #16-bit alignment
                        while len(self.data2_buffer) % 2 > 0:
                            self.data2_buffer += b'\x00'
                        data_offset = len(self.data2_buffer)
                        write_short_array(raw_data[key])
                    else:
                        input("Error, data type \"{}\" is not an array as expected, press Enter to quit!")
                        raise
                    encoded_data.extend([data_offset + self.data2_start_offset, len(raw_data[key])])
                else:
                    encoded_data.append(raw_data[key])
            return(encoded_data)
        if os.path.exists(table_name) and not os.path.exists(table_name+'.original'):
            shutil.copy2(table_name, table_name+'.original')
        table = self.read_table(table_name+'.original')
        table = self.update_table_with_kurodlc(table)
        new_table = b'#TBL' + struct.pack("<I", len(table))
        offset = 8 + len(table) * 80
        for key in table:
            new_table += return_64_len_str(key) + struct.pack("<4I", self.crc_dict[key], offset,\
                self.schema_dict[key], len(table[key]))
            offset += self.schema_dict[key] *  len(table[key])
        #Need 32-bit alignment here?  Or per table?
        #Will ignore for now, t_costume/t_dlc/t_item are all naturally aligned
        self.data2_start_offset = offset
        self.data2_buffer = b''
        for key in table:
            schema_table = self.get_schema(key, self.schema_dict[key])
            new_table += b''.join([struct.pack(schema_table['schema'],\
                *encode_row(x, schema_table)) for x in table[key]])
        assert self.data2_start_offset == len(new_table)
        new_table += self.data2_buffer
        with open(table_name, 'wb') as f:
            f.write(new_table)
        return

if __name__ == "__main__":
    pass
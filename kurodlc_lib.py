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
        tables = [x+'.original' if os.path.exists(x+'.original') else x for x in glob.glob('*.tbl')]
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
        if name == 'DLCTableData' and entry_length == 88:
            self.schema_dict[name] = entry_length
            return({'schema': "<2IQ2IQ2I3Q2HIQ2I", 'sch_len': 88,\
                'keys': ['id', 'sort_id', 'items', 'unk0', 'quantity',\
                    'unk1', 'name', 'desc', 'unk_txt', 'unk2', 'unk3',\
                    'unk4', 'unk_arr', 'unk5'],\
                'values': 'nnanantttnnnan'})
        elif name == 'ItemTableData' and entry_length == 248:
            return({'schema': "<2I2Q2BIHI2f20If20I3Q4I", 'sch_len': 248,\
                'keys': ['id','chr_restrict','flags','unk_txt','category','subcategory',\
                    'unk0','unk1','unk2','unk3','unk4','eff1_id','eff1_0','eff1_1','eff1_2',\
                    'eff2_id','eff2_0','eff2_1','eff2_2','eff3_id','eff3_0','eff3_1','eff3_2',\
                    'eff4_id','eff4_0','eff4_1','eff4_2','eff5_id','eff5_0','eff5_1','eff5_2',\
                    'unk5','hp','ep','patk','pdef','matk','mdef','str','def','ats','adf','agl',\
                    'dex','hit','eva','meva','crit','spd','mov','stack_size','price','anim',\
                    'name','desc','unk6','unk7','unk8','unk9'],\
                'values': 'nnttnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnntttnnnn'})
        elif name == 'ItemKindParam2' and entry_length == 16:
            return({'schema': "<2Q", 'sch_len': 16,\
                'keys': ['id', 'value'],\
                'values': 'nt'})
        elif name == 'QuartzParam' and entry_length == 28:
            return({'schema': "<8H8BI", 'sch_len': 28,\
                'keys': ['id', 'cost_e', 'cost_wa', 'cost_f', 'cost_wi', 'cost_t', 'cost_s', 'cost_m',\
                    'quant_e', 'quant_wa', 'quant_f', 'quant_wi', 'quant_t', 'quant_s', 'quant_m', 'unk0', 'unk1'],\
                'values': 'nnnnnnnnnnnnnnnnn'})
        elif name == 'CostumeParam' and entry_length == 56:
            return({'schema': "<4H2Q2I3Q", 'sch_len': 56,\
                'keys': ['char_restrict', 'type', 'item_id', 'unk0', 'unk_txt0', 'mdl_name',\
                    'unk1', 'unk2', 'attach_name', 'unk_txt1', 'unk_txt2'],\
                'values': 'nnnnttnnttt'})
        elif name == 'CostumeAttachOffset' and entry_length == 56:
            return({'schema': "<2IQ10f", 'sch_len': 56,\
                'keys': ['char_id', 'unk0', 'mdl_name', 't0', 't1', 't2', 'r0', 'r1', 'r2',\
                    's0', 's1', 's2', 'unk1'],\
                'values': 'nntnnnnnnnnnn'})
        elif name == 'NameTableData' and entry_length == 88:
            return({'schema': "<11Q", 'sch_len': 88,\
                'keys': ['char_id', 'name', 'texture', 'face', 'model',\
                    'unk0', 'unk_txt0', 'unk_txt1', 'unk1', 'unk_txt2', 'unk_txt3'],\
                'values': 'nttttnttntt'})
        else:
            return({})

    def read_struct_from_json(self, filename, raise_on_fail = True):
        with open(filename, 'r') as f:
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
        for key in json_data:
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
                for i in range(len(schema['values'])):
                    if schema['values'][i] == 'n':
                        if not all([isinstance(json_data[key][j][schema['keys'][i]], int)\
                                or isinstance(json_data[key][j][schema['keys'][i]], float) for j in range(len(json_data[key]))]):
                            pass_value_validation = False
                    elif schema['values'][i] == 'a':
                        if not all([isinstance(json_data[key][j][schema['keys'][i]], list)\
                                and all([isinstance(k, int) for k in json_data[key][j][schema['keys'][i]]])\
                                for j in range(len(json_data[key]))]):
                            pass_value_validation = False
                    elif schema['values'][i] == 't':
                        if not all([isinstance(json_data[key][j][schema['keys'][i]], str) for j in range(len(json_data[key]))]):
                            pass_value_validation = False
                if pass_value_validation == False:
                    input("Validation of {0} failed, one or more values in {1} do not match the schema!".format(json_name, key))
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
        kurodlc_jsons = glob.glob('*.kurodlc.json')
        for i in range(len(kurodlc_jsons)):
            self.read_kurodlc_json(kurodlc_jsons[i])
        return

    def update_table_with_kurodlc(self, table):
        for key in table:
            if key in self.new_entries:
                table[key].extend(self.new_entries[key])
        return(table)

    def read_table(self, table_name):
        def read_array(offset, numvalues): #u32 only for now
            arr = []
            f.seek(offset)
            if numvalues > 0:
                arr.extend(list(struct.unpack("<{}I".format(numvalues), f.read(numvalues*4))))
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
        def write_array(data_list): #u32 only for now
            self.data2_buffer += struct.pack("<{}I".format(len(data_list)), *data_list)
        def write_null_term_str(string):
            self.data2_buffer += string.encode('utf-8') + b'\x00'
        def return_64_len_str(string):
            assert len(string) <= 64
            return(string.encode('utf-8') + b'\x00'*(64-len(string)))
        def encode_row(raw_data):
            encoded_data = []
            for key in raw_data:
                if isinstance(raw_data[key], str):
                    data_offset = len(self.data2_buffer)
                    write_null_term_str(raw_data[key])
                    encoded_data.append(data_offset + self.data2_start_offset)
                elif isinstance(raw_data[key], list):
                    #32-bit alignment
                    while len(self.data2_buffer) % 4 > 0:
                        self.data2_buffer += b'\x00'
                    data_offset = len(self.data2_buffer)
                    write_array(raw_data[key])
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
            schema = self.get_schema(key, self.schema_dict[key])['schema']
            new_table += b''.join([struct.pack(schema, *encode_row(x)) for x in table[key]])
        assert self.data2_start_offset == len(new_table)
        new_table += self.data2_buffer
        with open(table_name, 'wb') as f:
            f.write(new_table)
        return

if __name__ == "__main__":
    pass
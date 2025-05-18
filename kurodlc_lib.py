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
        self.schemas = {}
        self.schema_dict = {}
        self.crc_dict = {}
        self.data2_start_offset = 0
        self.data2_buffer = b''
        self.new_entries = {}
        self.new_entries_sources = {}
        self.init_schemas()

    def init_schemas(self):
        if os.path.exists('kurodlc_schema.json'):
            kurodlc_schema = json.loads(open('kurodlc_schema.json','rb').read())
            self.schemas = {(x['table_header'],x['schema_length']):x['schema'] for x in kurodlc_schema}
        else:
            print("kurodlc_schema.json is missing!  This tool will not be able to read tables.")
            input("Press Enter to continue.")
        tables = glob.glob('**/*.tbl.original', recursive = True) \
            + [x for x in glob.glob('**/*.tbl', recursive = True) if not os.path.exists(x+'.original')]
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
        if (name, entry_length) in self.schemas:
            return self.schemas[(name, entry_length)]
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
                if len(schema) > 0:
                    if not all([list(json_data[key][i].keys()) == schema['keys']\
                            for i in range(len(json_data[key]))]):
                        if [all([x in schema['keys'] for x in list(json_data[key][i].keys())]) for i in range(len(json_data[key]))]:
                            for i in range(len(json_data[key])):
                                if not list(json_data[key][i].keys()) == schema['keys']:
                                    json_data[key][i] = {x:json_data[key][i][x] for x in schema['keys']}
                        else:
                            print("Validation of {0} failed, schema in {1} is incorrect!".format(json_name, key))
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
                        elif schema['values'][i] in ['a', 'b']:
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
                    input("Validation of {0} in {1} skipped, schema not found! (tbl file not supported)".format(key, json_name))
                    raise
            else:
                input("Validation of {0} in {1} failed, schema not found! (tbl file is missing)".format(key, json_name))
                raise
        return(json_data)

    def detect_duplicate_entries(self, json_data, json_name):
        for key in [x for x in json_data if len(json_data[x]) > 0]:
            if key in self.schema_dict:
                schema = self.get_schema(key, self.schema_dict[key])
                if 'primary_key' in schema and isinstance(schema['primary_key'], list):
                    schema['new_primary_key'] = "_".join(schema['primary_key'])
                    for i in range(len(json_data[key])):
                        json_data[key][i][schema['new_primary_key']] =\
                            tuple(json_data[key][i][j] for j in schema['primary_key'] if j in json_data[key][i])
                # Search for duplicates and report them
                if key in self.new_entries:
                    if 'primary_key' in schema:
                        primary_key = schema['new_primary_key'] if 'new_primary_key' in schema else schema['primary_key']
                        prior_id_values = [x[primary_key] for x in self.new_entries[key]]
                        duplicates = [x for x in json_data[key] if x[primary_key] in prior_id_values]
                        if len(duplicates) > 0:
                            for i in range(len(duplicates)):
                                matches = []
                                for j in range(len(self.new_entries_sources[key+'_primary_key'])):
                                    matches.extend([self.new_entries_sources[key+'_primary_key'][j][x[primary_key]]
                                        for x in self.new_entries[key]
                                        if x[primary_key] in self.new_entries_sources[key+'_primary_key'][j]
                                        and x[primary_key] == duplicates[i][primary_key]])
                            print("Duplicates found in {0} [\"{1}\"]!  This entry: {2}\nconflicts with {3}".format(
                                json_name, key, duplicates[i][primary_key], matches))
                            input("Press Enter to Continue.")
                    if 'unique_values' in schema and len(schema['unique_values']) > 0:
                        for i in range(len(schema['unique_values'])):
                            key_tag = key + '_' + schema['unique_values'][i]
                            prior_values = [x[schema['unique_values'][i]] for x in self.new_entries[key]]
                            duplicates = [x for x in json_data[key] if x[schema['unique_values'][i]] in prior_values]
                            if len(duplicates) > 0:
                                for i in range(len(duplicates)):
                                    matches = []
                                    for j in range(len(self.new_entries_sources[key_tag])):
                                        matches.extend([self.new_entries_sources[key_tag][j][x[schema['unique_values'][i]]]
                                            for x in self.new_entries[key]
                                            if x[schema['unique_values'][i]] in self.new_entries_sources[key_tag][j]
                                            and x[schema['unique_values'][i]] == duplicates[i][schema['unique_values'][i]]])
                                    print("Duplicates found in {0} [\"{1}\"]!  This entry: {2}\nconflicts with {3}".format(
                                        json_name, key, duplicates[i][schema['unique_values'][i]], matches))
                                input("Press Enter to Continue.")
                # Insert the primary keys and unique values into self.new_entries_sources so they can be referenced in future calls
                if 'primary_key' in schema:
                    primary_key = schema['new_primary_key'] if 'new_primary_key' in schema else schema['primary_key']
                    if key+'_primary_key' in self.new_entries_sources:
                        self.new_entries_sources[key+'_primary_key'].extend([{x[primary_key]:json_name}
                            for x in json_data[key]])
                    else:
                        self.new_entries_sources[key+'_primary_key'] = [{x[primary_key]:json_name}
                            for x in json_data[key]]
                if 'unique_values' in schema and len(schema['unique_values']) > 0:
                    for i in range(len(schema['unique_values'])):
                        key_tag = key + '_' + schema['unique_values'][i]
                        if key_tag in self.new_entries_sources:
                            self.new_entries_sources[key_tag].extend([{x[schema['unique_values'][i]]:json_name} for x in json_data[key]])
                        else:
                            self.new_entries_sources[key_tag] = [{x[schema['unique_values'][i]]:json_name} for x in json_data[key]]
        return

    def read_kurodlc_json(self, json_name):
        if os.path.exists(json_name):
            json_data = self.read_struct_from_json(json_name)
            self.validate_kurodlc_entries(json_data, json_name)
            self.detect_duplicate_entries(json_data, json_name)
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
                if 'primary_key' in schema and isinstance(schema['primary_key'], list):
                    schema['new_primary_key'] = "_".join(schema['primary_key'])
                    for i in range(len(table[key])):
                        table[key][i][schema['new_primary_key']] =\
                            tuple(table[key][i][j] for j in schema['primary_key'] if j in table[key][i])
                if 'primary_key' in schema:
                    primary_key = schema['new_primary_key'] if 'new_primary_key' in schema else schema['primary_key']
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
                if 'new_primary_key' in schema_table and key == schema_table['new_primary_key']:
                    continue # Do not encode the temporary tuple used to identify unique rows
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
# GitHub eArmada8/kuro_dlc_tool

import json, glob, os, sys

def add_element(schema, element_name, element_type):
    if element_type == 'u32':
        aa = ('I', 4, 'n')
    elif element_type == 's32':
        aa = ('i', 4, 'n')
    elif element_type == 'f32':
        aa = ('f', 4, 'n')
    elif element_type == 'u16':
        aa = ('H', 2, 'n')
    elif element_type == 's16':
        aa = ('h', 2, 'n')
    elif element_type == 'u8':
        aa = ('B', 1, 'n')
    elif element_type == 's8':
        aa = ('b', 1, 'n')
    elif element_type == 's8':
        aa = ('b', 1, 'n')
    elif element_type == 'arr_u32':
        aa = ('QI', 12, 'a')
    elif element_type == 'arr_u16':
        aa = ('QI', 12, 'b')
    elif element_type == 'ptr_str_utf8':
        aa = ('Q', 8, 't')
    elif isinstance(element_type, dict):
        for i in range(element_type['repeat']):
            for key in element_type['type']:
                new_name = "{0}_{1}_{2}".format(element_name, i, key)
                schema = add_element(schema, new_name, element_type['type'][key])
    elif element_type[0] == 'd':
        for i in range(int(element_type[1:])):
            new_name = "{0}_{1}".format(element_name, i)
            schema = add_element(schema, new_name, 'u8')
    else:
        print("Panic!  {} missing.".format(element_type))
    if not (isinstance(element_type, dict) or element_type[0] == 'd'): #skip in recursive loops
        schema['schema'] += aa[0]
        schema['sch_len'] += aa[1]
        schema['keys'].append(element_name)
        schema['values'] += aa[2]
    return(schema)

def condense_schema(schema_code):
    new_schema = "<"
    type_ = ''
    counter = 1
    for i in range(1, len(schema_code)):
        if schema_code[i] == type_:
            counter += 1
        else:
            if not type_ == '':
                new_schema += "{0}{1}".format('' if counter == 1 else counter, type_)
            counter = 1
            type_ = schema_code[i]
    new_schema += "{0}{1}".format(counter, type_)
    return(new_schema)

def create_new_schema(tbl_tool_schema, schema_name):
    t_schema = tbl_tool_schema['schema']
    schema = {"schema": "<", "sch_len": 0, "keys": [], "values": "", "primary_key": ""}
    for key in t_schema:
        schema = add_element(schema, key, t_schema[key])
    schema['schema'] = condense_schema(schema['schema'])
    return({'info_comment': '', 'table_header': schema_name, 'schema_length': schema['sch_len'], 'schema': schema})

if __name__ == "__main__":
    # Set current directory
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    else:
        os.chdir(os.path.abspath(os.path.dirname(__file__)))

    tbls = [os.path.basename(x).split('.json')[0] for x in glob.glob('*.json') if 'new_schemas' not in x]
    schemas = [create_new_schema(json.loads(open('{}.json'.format(x),'rb').read()), x) for x in tbls]
    open('new_schemas.json','wb').write(json.dumps(schemas, indent = 4).encode('utf-8'))
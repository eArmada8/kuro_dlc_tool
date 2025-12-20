# Script with functions to manipulate a P3A archive.
#
# GitHub eArmada8/kuro_dlc_tool

try:
    import struct, math, io, json, os, sys, glob
    import lz4.block, zstandard, xxhash
except ModuleNotFoundError as e:
    print("Python module missing! {}".format(e.msg))
    input("Press Enter to abort.")
    raise   

class p3a_class:
    def __init__ (self):
        self.f = None

    def read_entry (self, version):
        entry = {}
        entry['name'] = self.f.read(0x100).split(b'\x00')[0].decode('utf-8')
        entry['cmp_type'], entry['cmp_size'], entry['unc_size'], entry['offset']\
            = struct.unpack("<4Q", self.f.read(32))
        entry['cmp_hash'], = list(struct.unpack("Q", self.f.read(8)))
        if version >= 1200:
            entry['unc_hash'], = list(struct.unpack("Q", self.f.read(8)))
        return(entry)

    def read_dict (self):
        magic = self.f.read(8)
        if magic == b'P3ADICT\x00':
            dict_size, = struct.unpack("<Q", self.f.read(8))
            return(self.f.read(dict_size))
        else:
            return b''

    def read_p3a_toc (self):
        self.f.seek(0)
        magic = self.f.read(8)
        if magic == b'PH3ARCV\x00':
            header = {}
            header['flags'], header['version'], header['num_files'], header['p3a_hash']\
                = struct.unpack("<2I2Q", self.f.read(24))
            if header['version'] >= 1200:
                header['p3a_hash_2'], header['ext_header_size'], header['entry_size']\
                    = struct.unpack("<Q2I", self.f.read(16))
            entries = [self.read_entry(header['version']) for i in range(header['num_files'])]
            if header['flags'] & 1 == 1:
                p3a_dict = zstandard.ZstdCompressionDict(self.read_dict())
            else:
                p3a_dict = None
            return(header, entries, p3a_dict)
        else:
            input("Not P3A! Press Enter to continue")
            return []

    def read_file (self, entry, p3a_dict):
        self.f.seek(entry['offset'])
        cmp_data = self.f.read(entry['cmp_size'])
        if not xxhash.xxh64_intdigest(cmp_data) == entry['cmp_hash']:
            input("{} is corrupt, skipping.  Press Enter to continue.".format(entry['name']))
            return(b'')
        if entry['cmp_type'] == 0:
            unc_data = cmp_data
        elif entry['cmp_type'] == 1:
            unc_data = lz4.block.decompress(cmp_data, entry['unc_size'])
        elif entry['cmp_type'] == 2:
            decompressor = zstandard.ZstdDecompressor()
            unc_data = decompressor.decompress(cmp_data)
        elif entry['cmp_type'] == 3:
            decompressor = zstandard.ZstdDecompressor(dict_data = p3a_dict)
            unc_data = decompressor.decompress(cmp_data)
        else:
            input("{0} is unknown compression (type {1}), skipping.  Press Enter to continue.".format(entry['name'],
                entry['cmp_type']))
            unc_data = b''
        if len(unc_data) > 0 and 'unc_hash' in entry:
            if not xxhash.xxh64_intdigest(unc_data) == entry['unc_hash']:
                input("{} is corrupt, skipping.  Press Enter to continue.".format(entry['name']))
                return(b'')
        return(unc_data)

    # assigned_paths are specific names for each file, and are optional.
    # The key should match the file in file_list, and the value is the new name.
    # For example, if '/path/to/file1' is in file_list, then assigned_path could have
    # a key:value of '/path/to/file1':'/different/path/to/file2', and '/path/to/file1'
    # will be stored in the p3a as '/different/path/to/file2'.
    def p3a_pack_files (self, file_list, assigned_paths = {}, cmp_type = 1, p3a_ver = 1100):
        def return_256_len_str(string):
            assert len(string) <= 256
            return(string.encode('utf-8') + b'\x00'*(256-len(string)))
        p3a_flags = 0
        header_length = ({1100: 32, 1200: 48}[p3a_ver]
            + {1100: 296, 1200: 304}[p3a_ver] * len(file_list))
        file_data = []
        if cmp_type == 2:
            zstd_compressor = zstandard.ZstdCompressor(level = 12, write_checksum = True)
        if cmp_type == 3:
            p3a_flags = p3a_flags | 1
            dict_size = 112640
            print("Generating dictionary...")
            samples = [open(file, 'rb').read() for file in file_list]
            zdict = zstandard.train_dictionary(dict_size, samples)
            header_length += len(zdict.as_bytes()) + 16
            zstd_compressor = zstandard.ZstdCompressor(level = 12, dict_data = zdict, write_checksum = True)
        header_length = math.ceil(header_length / 64) * 64
        print("Compressing files...")
        with io.BytesIO() as f:
            toc = []
            for i in range(len(file_list)):
                with open(file_list[i], 'rb') as f2:
                    unc_data = f2.read()
                if cmp_type == 0:
                    cmp_data = unc_data
                elif cmp_type == 1:
                    cmp_data = lz4.block.compress(unc_data, mode = 'high_compression', store_size=False)
                elif cmp_type in [2,3]:
                    cmp_data = zstd_compressor.compress(unc_data)
                if file_list[i] in assigned_paths:
                    file_path = assigned_paths[file_list[i]]
                    file_path = "".join([x if x not in ":*?<>|" else "_" for x in file_path]) #Sanitize
                else:
                    file_path = file_list[i]
                file_entry = {'name': file_path, 'cmp_type': cmp_type, 'cmp_size': len(cmp_data),
                    'unc_size': len(unc_data), 'offset': f.tell() + header_length,
                    'cmp_hash': xxhash.xxh64_intdigest(cmp_data), 'unc_hash': xxhash.xxh64_intdigest(unc_data)}
                f.write(cmp_data)
                file_data.append(file_entry)
                if i < len(file_list) - 1:
                    while f.tell() % 64 > 0: #64-byte alignment
                        f.write(b'\x00')
            f.seek(0)
            file_block = f.read()
        header = b'PH3ARCV\x00' + struct.pack("<2IQ", p3a_flags, p3a_ver, len(file_list))
        header += struct.pack("<Q", xxhash.xxh64_intdigest(header))
        if p3a_ver >= 1200:
            ext_header = struct.pack("<2I", 16, {1200: 304}[p3a_ver])
            header += struct.pack("<Q", xxhash.xxh64_intdigest(ext_header)) + ext_header
        for i in range(len(file_data)):
            file_entry_block = return_256_len_str(file_data[i]['name'].lower()) # All file names in P3A are lower case
            file_entry_block += struct.pack("<5Q", file_data[i]['cmp_type'], file_data[i]['cmp_size'],
                file_data[i]['unc_size'], file_data[i]['offset'], file_data[i]['cmp_hash'])
            if p3a_ver >= 1200:
                file_entry_block += struct.pack("<Q", file_data[i]['unc_hash'])
            header += file_entry_block
        if cmp_type == 3:
            header += b'P3ADICT\x00' + struct.pack("<Q", len(zdict.as_bytes())) + zdict.as_bytes()
        if len(header) % 64 > 0: #64-byte alignment
            header += b''.join([b'\x00']*(64-(len(header) % 64)))
        return(header + file_block)

    def extract_all_files (self, p3a_archive, output_dir = None, overwrite = False):
        with open(p3a_archive,'rb') as self.f:
            headers, entries, p3a_dict = self.read_p3a_toc()
            if output_dir == None:
                output_dir = p3a_archive[:-4]
            for i in range(len(entries)):
                file_data = self.read_file(entries[i], p3a_dict)
                if len(file_data) > 0:
                    overwrite_files = overwrite
                    if os.path.exists(output_dir + '/' + entries[i]['name']) and (overwrite == False):
                        if str(input(output_dir + '/' + entries[i]['name'] + " exists! Overwrite? (y/N) ")).lower()[0:1] == 'y':
                            overwrite_files = True
                    if not os.path.exists(output_dir + '/' + entries[i]['name']) or overwrite_files == True:
                        if not os.path.exists(output_dir + '/' + os.path.dirname(entries[i]['name'])):
                            os.makedirs(output_dir + '/' + os.path.dirname(entries[i]['name']))
                        with open(output_dir + '/' + entries[i]['name'], 'wb') as f2:
                            f2.write(file_data)
        return

    # if output_name is None, then the name of the folder will be used.
    def pack_folder (self, folder_name, output_name = None, overwrite = False, cmp_type = 1, p3a_ver = 1100):
        if output_name == None:
            p3a_name = folder_name + '.p3a'
        else:
            p3a_name = "".join([x if x not in "\\/:*?<>|" else "_" for x in output_name]) #Sanitize
            if not p3a_name.lower()[-4:] == '.p3a':
                p3a_name = p3a_name + '.p3a'
        if os.path.exists(p3a_name) and overwrite == False:
            if str(input(p3a_name + " exists! Overwrite? (y/N) ")).lower()[0:1] == 'y':
                overwrite = True
        if (overwrite == True) or not os.path.exists(p3a_name):
            file_list = [x.replace('\\','/') for x in glob.glob('**/*',root_dir=folder_name,recursive=True)
                if not os.path.isdir(folder_name+'/'+x)]
            assigned_paths = {folder_name+'/'+x:x for x in file_list}
            p3a_data = self.p3a_pack_files (list(assigned_paths.keys()), assigned_paths,
                cmp_type = cmp_type, p3a_ver = p3a_ver)
            with open(p3a_name, 'wb') as f:
                f.write(p3a_data)
        return

if __name__ == "__main__":
    pass
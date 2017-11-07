import unittest
import csv
import logging
import os
import hmac
import hashlib
import sys
import json
import difflib
from datetime import datetime
from epsig2_gui import epsig2
p_reset = "\x08"*8

class Preferences: 

    def __init__(self): 
        preference_filename = 'preferences.dat'
        self.data = dict()
        
        if os.path.isfile(preference_filename): 
            self.readfile(preference_filename)
        else: 
            self.path_to_binimage = '\\\Justice.qld.gov.au\\Data\\OLGR-TECHSERV\\BINIMAGE'
            self.mid_list = [ '00', '01', '05', '07', '09', '12', '17']
            self.cache_filename = 'qcas_df_cache_file.json'
            self.valid_bin_types = VALID_BIN_TYPE = ['BLNK','PS32','SHA1']
            self.epsig_log_file = 'G:\\OLGR-TECHSERV\\MISC\\BINIMAGE\\qcas\\log\\epsig.log'
            
            # default values
            self.data = { 'path_to_binimage' : self.path_to_binimage,
                          'mid_list' : self.mid_list,
                          'cache_filename' : self.cache_filename,
                          'valid_bin_types' : self.valid_bin_types,
                          'epsig_log_file' : self.epsig_log_file,
                          'previous_TSLfile' : "qcas_2017_09_v02.tsl", 
                          'TSLfile' : "qcas_2017_10_v01.tsl", 
                          'PSLfile' : "qcas_2017_10_v03.psl", 
                          'nextMonth_PSLfile': "qcas_2017_11_v01.psl", 
                          'MSLfile' : "qcas_2017_10_v01.msl",
                          'nextMonth_MSLfile' : "qcas_2017_11_v01.msl",
                        }
            self.writefile(preference_filename)
            
    def readfile(self, filename): 
        with open(filename, 'r') as jsonfile: 
            data = json.load(jsonfile)
            # data file preferences
            self.path_to_binimage = data['path_to_binimage']
            self.mid_list = data['mid_list']
            self.cache_filename = data['cache_filename']
            self.valid_bin_types = data['valid_bin_types']
            self.previous_TSLfile = data['previous_TSLfile']
            self.epsig_log_file = data['epsig_log_file']
            
            # Datafiles 
            self.TSLfile = data['TSLfile']
            self.PSLfile = data['PSLfile']
            self.nextMonth_PSLfile = data['nextMonth_PSLfile']
            self.MSLfile = data['MSLfile']
            self.nextMonth_MSLfile = data['nextMonth_MSLfile']
            
    def toJSON(self): 
        return (json.dumps(self, default=lambda o: o.__dict__, sort_keys = True, indent=4))
    
    def writefile(self, fname): 
        with open(fname, 'w') as outfile: 
            json.dump(self.data, outfile,sort_keys=False, indent=4, separators=(',', ': '))
        
class CacheFile: 

    def __init__(self, fname): 
        self.cache_file = fname
        self.cache_dict = self.importCacheFile()
                
    def importCacheFile(self):
        if os.path.isfile(self.cache_file): 
            # Verify Cache Integrity
            #cache_file_sigs_filename = self.cache_file[:-4] + ".sigs"
            #if self.verifyCacheIntegrity(cache_file_sigs_filename): 
            with open(self.cache_file,'r') as json_cachefile: 
                cache_data = json.load(json_cachefile)
            #else: 
            #    logging.warning("**** WARNING **** File Cache integrity issue: " +
            #           " Cannot Verify signature")
            #    logging.info("Generating new File Cache file:" + self.cache_file)
            #    cache_data = {} # return empty cache
        else:
            logging.info(self.cache_file + 
                " cannot be found. Generating default file...")
            with open(self.cache_file, 'w+') as json_cachefile:
                # write empty json file
                json.dump({}, 
                    json_cachefile, 
                    sort_keys=True, 
                    indent=4, 
                    separators=(',', ': '))
                print('Run script again, empty cache file created')
                sys.exit(0)
        
        return(cache_data)

    def checkCacheFilename(self, filename, seed_input, alg_input): # alg_input
        # For filename_seed, concatenate to form unique string. 
        if filename in self.cache_dict.keys(): # a hit?
            data = self.cache_dict.get(filename) # now a list
            for item in data:
                # Check if Seed and Algorithm matches. 
                if item['seed'] == seed_input and item['alg'] == alg_input: 
                    verified_time = item['verify'] 
                    return(str(item['hash'])) # return Hash result
        else:
            return 0
    
    def verifyCacheIntegrity(self, cache_location_sigs): 
        if os.path.isfile(cache_location_sigs): # Sigs file exist?
            with open(cache_location_sigs, 'r') as sigs_file: 
                cache_sigs_data = json.load(sigs_file)
                hashm = cache_sigs_data['cachefile_hash']
                #fname = cache_sigs_data['filename']
                
                generated_hash = QCASTestClient.dohash_sha256(self.cache_file, 8192)
                if hashm == generated_hash: 
                    return True
                else: 
                    return False     
        else: 
            # advise user
            logging.warning("\n**** WARNING **** Generating new Cache Sigs file\n") 
            self.signCacheFile() # Generate Cache Sigs file
        
    def signCacheFile(self):
        sigsCacheFile = self.cache_file[:-4] + "sigs" # .json file renaming to .sigs file
        h = QCASTestClient.dohash_sha256(self.cache_file, 8192) # requires file name as input
        
        with open(sigsCacheFile,'w') as sigs_file:    
            timestamp = datetime.now()
            sigs_dict = { 'cachefile_hash' : h,
                          'filename': self.cache_file,
                          'last_generated_by_user' : getpass.getuser(),
                          'date': str(timestamp.strftime("%Y-%m-%d %H:%M"))
                        }
            
            json.dump(sigs_dict,
                      sigs_file,
                      sort_keys=True,
                      indent=4,
                      separators=(',', ': '))
        
    def updateCacheFile(self):
        if os.path.isfile(self.cache_file):
            with open(self.cache_file, 'w') as json_cachefile:
                json.dump(self.cache_dict,
                          json_cachefile,
                          sort_keys=True,
                          indent=4,
                          separators=(',', ': '))
            
        # self.signCacheFile() # Sign Cache
    
class PSLfile:
    # helper class for PSL file
    def __init__(self, line):
        my_preferences = Preferences()
        fields = str(line).split(',')
        input_line = line.strip(',') # remove trailing comma
        
        self.game_name = fields[0].strip() # strip spaces
        # print(len(self.game_name))
        assert(len(self.game_name) < 31)
       
        self.manufacturer = fields[1]
        assert(self.manufacturer in my_preferences.mid_list)
        
        self.year = int(fields[2])
        valid_year = list(range(2017,9999))
        assert(len(fields[2]) == 4)
        assert(self.year in valid_year)
        
        self.month = int(fields[3])
        valid_months = list(range(1,13))
        assert(self.month in valid_months)
        
        assert(len(fields[4]) == 10)
        self.ssan = int(fields[4].strip())

        # included_cols = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35]
        included_cols_v2 = list(range(5,36))
        self.hash_list = list(fields[i] for i in included_cols_v2)
        assert(len(self.hash_list) == 31)
        
        self.psl_entry_str = self.toString()
        if self.psl_entry_str != input_line:
            self.identifyDifference(self.psl_entry_str, input_line)
        
        assert(self.psl_entry_str == input_line)
        
    def toString(self): 
        self.psl_entry_str = "%(game_name)-30s,%(mid)02d,%(year)4s,%(month)02d,%(ssan)010d," % {'game_name': self.game_name, 'mid': int(self.manufacturer), 'year': self.year, 'month': int(self.month), 'ssan': int(self.ssan)}
        for hash_item in self.hash_list: 
            self.psl_entry_str += hash_item + ","
        return self.psl_entry_str.strip(',')
        
    def identifyDifference(self, str1, str2): 
        cases = [(str1, str2)] 
        for a,b in cases:     
            print('{} => {}'.format(a,b))  
            for i,s in enumerate(difflib.ndiff(a, b)):
                if s[0]==' ': continue
                elif s[0]=='-':
                    print(u'Delete "{}" from position {}'.format(s[-1],i))
                elif s[0]=='+':
                    print(u'Add "{}" to position {}'.format(s[-1],i))    
            print()

class MSLfile:
    # helper class for MSL file
    def __init__(self, line):
        fields = str(line).split(',')
        
        self.year = int(fields[0])
        valid_year = list(range(2017,9999))
        assert(self.year in valid_year) # verify year field is 2017-9999
       
        self.month = int(fields[1])
        valid_months = list(range(1,13))
        assert(self.month in valid_months) # verify months fields is 1-12
        
        included_cols = list(range(2, 33))
        self.seed_list = list(fields[i] for i in included_cols)
        assert(len(self.seed_list) == 31) # verify 31 seeds
        for seed in self.seed_list: 
            assert(len(seed) == 8)  # verify each seed has 8 characters
        
class TSLfile:
    # helper class for TSL file
    def __init__(self, line):
        my_preferences = Preferences()
        
        fields = str(line).split(',')
        self.mid = fields[0]
        assert(self.mid in my_preferences.mid_list)
        
        assert(len(fields[1]) == 10)
        self.ssan = int(fields[1])
        
        self.game_name = fields[2].strip()
        assert(len(self.game_name) < 61)
        
        self.bin_file = fields[3].strip()
        assert(len(self.bin_file) < 21)
        
        self.bin_type = fields[4].strip()
        assert(self.bin_type in my_preferences.valid_bin_types)
        
        
# Derived unittest.TestCase class used for unittest testing. 
class QCASTestClient(unittest.TestCase):
    # common test behaviours
    
    def setUp(self):
        # Read from JSON file
        # Global Vars, Paths, and QCAS datafile names
        self.my_preferences = Preferences() 
        
        ###############################################
        ## Files to Verify
        ## Modify the following files only
        ## 
        ## TSL files 
        self.previous_TSLfile = self.my_preferences.previous_TSLfile
        self.TSLfile = self.my_preferences.TSLfile
        ## PSL files (hashes)
        self.PSLfile = self.my_preferences.PSLfile
        self.nextMonth_PSLfile = self.my_preferences.nextMonth_PSLfile
        ## MSL files (seeds)
        self.MSLfile = self.my_preferences.MSLfile
        self.nextMonth_MSLfile = self.my_preferences.nextMonth_MSLfile
        ##
        ###############################################
        self.next_month = {'month': '', 'year':''} 
        self.this_month = {
            'month': datetime.now().month,
            'year': datetime.now().year
        }
        
        if self.this_month['month'] == 12:
            self.next_month = {
                'month': 1,
                'year': int(self.this_month['year']) + 1
            } # new year
        else: 
            self.next_month = {
                'month': int(self.this_month['month']) + 1,
                'year': self.this_month['year']
            }

    def is_new_month(self, file1, file2):
        # new month is when file 2 version is equal to v1 and is less than file1 version. 
        if int(self.get_filename_month(file2)) == 1 and int(self.get_filename_month(file1)) == 1:
            return True
        else:
            return False

    def is_new_year(self, file):
        if int(self.get_filename_month(file)) == 12:
            return True
        else:
            return False

    def check_game_name(self, game_name):
        if len(game_name) > 1:
            return True
        else:
            return False

    def check_manufacturer(self, manufacturer):
        output = ''
            
        if len(manufacturer) < 2:
            temp_manufacturer = "0" + manufacturer
        else:
            temp_manufacturer = manufacturer

        if temp_manufacturer in set(self.my_preferences.mid_list):
            output =  True
        else:
            output = False

        return output
    
    def check_file_format(self, file, file_format):
        item_list = list()
        
        # test PSL file format
        if file_format == 'PSL':
            with open(file, 'r') as psl:
                psl_entries = csv.reader(psl, delimiter=',')
                try:
                    for row in psl_entries:
                        item_list.append(PSLfile(",".join(row)))

                except csv.Error as e:
                    sys.exit('file %s, line %d: %s' % (file, psl_entries.line_num, e))

        # test MSL file format
        elif file_format == 'MSL':           
            with open(file, 'r') as msl:
                msl_entries = csv.reader(msl, delimiter=',')
                try:
                    for item in msl_entries:
                        item_list.append(MSLfile(",".join(item)))

                except csv.Error as e:
                    sys.exit('file %s, line %d: %s' % (file, msl_entries.line_num, e))

        # test TSL file format
        elif file_format == 'TSL':
            with open(file, 'r') as tsl:
                tsl_entries = csv.reader(tsl, delimiter=',')
                try:
                    for item in tsl_entries:
                        item_list.append(TSLfile(",".join(item)))
                except csv.Error as e: 
                    sys.exit('file %s, line %d: %s' % (file, tsl_entries.line_num, e))

        return item_list

    def check_year_field(self, year):
        today = datetime.now()

        if year == today.year or year == today.year + 1:
            return True
        else:
            return False

    def check_month_field(self, month):
        today = datetime.now()
        if month == today.month or today.month + 1 :
            return True
        else:
            return False

    def check_hash_list(self, hash_list):
        # To do:
        # Generate hash using MSL file, and compare result in hash_list
        # must equal
        
        return False

    def get_filename_version(self, filename):
        file_version = ''

        #strip file suffix:
        fields = filename.split('_')
        file_version = fields[3][1:-4] # remove suffix i.e. .psl/.msl/.tsl, and 'v' char

        return file_version

    def get_filename_month(self, filename):
        fields = filename.split('_')
        
        return fields[2]

    def get_filename_year(self, filename):
        fields = filename.split('_')
        
        return fields[1]

    def check_valid_binimage_type(self, binimage_type):
        output = ''
        if binimage_type in self.my_preferences.valid_bin_types:
            output = True
        else:
            output = False
        return output

    def check_unique_field(self, field_str, tslfile_list, flag='SSAN'):
        # Confirm that only a single entry exists. 
        count = 0
        duplicate_entries = list()
        
        for tsl_entry in tslfile_list:
            if flag == 'SSAN': 
                if field_str == tsl_entry.ssan: 
                    count += 1
            elif flag == 'BIN_FILE':
                if field_str == '0201230':
                    pass
                else: 
                    if field_str == tsl_entry.bin_file:
                        count += 1

                    if count > 1:
                        duplicate_entries.append(field_str.strip())
            else:
                print("unknown flag type")
                sys.exit(1)

        if count == 1:
            return True
        else:
            print("Not Unique, counted : " + str(count) + " ,".join(duplicate_entries))
            if '0201230' in duplicate_entries: # handle this duplicate entry
                return True
            else:
                return False

    def get_newgames_to_be_added(self): 
        game_list_to_be_added = list()
        tsl_difference = set()

        with open(self.TSLfile, 'r') as file1:
            with open(self.previous_TSLfile, 'r') as file2:
                tsl_difference = set(file1).difference(file2)
        
        self.assertTrue(len(tsl_difference) > 0) # TSL files must be contain a new game? 
        # print("\nNew Games added: \n" + "".join(list(tsl_difference)))
  
        # Differences are the new games to be added. 
        for game in list(tsl_difference): # Single Line
            game_list_to_be_added.append(TSLfile(game)) # Generate TSL object
        
        return game_list_to_be_added
    
    # input:    total path to BLNK file, MID and optional blocksize
    # output:   blnk hash result using seed. 
    def dobnk(self, blnk_file, seed, mid, blocksize=65534):
        psl_cache_file = CacheFile(self.my_preferences.cache_filename) # use a Cachefile - all defaults
        oh = "0000000000000000000000000000000000000000"

        with open(blnk_file, 'r') as file:         # Read BNK file
            field_names = ['fname', 'type', 'blah']
            reader = csv.DictReader(file, delimiter=' ', fieldnames=field_names)
            # print(self.getQCAS_Expected_output(seed))
        
            for row in reader: 
                if row['type'].upper() == 'SHA1':
                    complete_path_to_file = os.path.join(self.my_preferences.path_to_binimage,self.getMID_Directory(mid), str(row['fname']))    
                    cachedhit = psl_cache_file.checkCacheFilename(complete_path_to_file, self.getQCAS_Expected_output(seed), row['type'].upper()) 
        
                    if cachedhit:
                        localhash = cachedhit # use cached data
                    else: 
                        new_cache_list = list()
                        localhash = self.dohash_hmacsha1(complete_path_to_file, self.getQCAS_Expected_output(seed), blocksize) 
                    
                        # create cache object
                        cache_object = { 
                            'seed': self.getQCAS_Expected_output(seed), 
                            'alg': row['type'].upper(), 
                            'verify':'0', 
                            'hash': localhash 
                        }        
                        
                        cache_entry_list = psl_cache_file.cache_dict.get(complete_path_to_file) # Should return a list. 
                        
                        if cache_entry_list :   # File Entry Exists, append to list
                            cache_entry_list.append(cache_object) # print this
                            psl_cache_file.cache_dict[complete_path_to_file] = cache_entry_list
                        else:                   # No File Entry Exits generate new list entry in cache_dict
                            new_cache_list.append(cache_object)
                            psl_cache_file.cache_dict[complete_path_to_file] = new_cache_list # keep unique
                                                        
                        psl_cache_file.updateCacheFile() # Update file cache
    
                    if localhash == 0:
                        break
                        
                    oh = hex(int(oh,16) ^ int(str(localhash), 16)) # XOR

                else: 
                    print(row['type'] + "  - Not processing any other file other than SHA1!")
                    sys.exit(1)    
        return oh
             
    # input: file to be hashed using sha256()
    # output: hexdigest of input file    
    def dohash_sha256(self, fname, chunksize=8192): 
        m = hashlib.sha256()         

        # Read in chunksize blocks at a time
        with open(fname, 'rb') as f:
            while True:
                block = f.read(chunksize)
                if not block: break
                m.update(block)    

        return m.hexdigest()
        
    # input: file to be hashed using hmac-sha1
    # output: hexdigest of input file    
    def dohash_hmacsha1(self, fname, seed='00', chunksize=8192):
        key = bytes.fromhex(seed)
        m = hmac.new(key, digestmod = hashlib.sha1) # change this if you want other hashing types for HMAC, e.g. hashlib.md5
        done = 0
        size = os.path.getsize(fname)
        # Read in chunksize blocks at a time
        with open(fname, 'rb') as f:
            #print("\nHashing: " + os.path.basename(fname) + "\tSeed:" + seed + "\t", end="")
            while True:
                block = f.read(chunksize)
                done += chunksize
                sys.stdout.write("%7d" % (done*100/size) + "%" + p_reset)
                if not block: break
                m.update(block)      
        return m.hexdigest()
        
    def get_bin_type(self, bin_type):
        if bin_type.startswith('BLNK'):
            return "BNK"
        elif bin_type.startswith('SHA1'): 
            return "BIN"
        elif bin_type.startswith('CR32'): 
            return "BIN"
        else: 
            assert(bin_type in my_preferences.VALID_BIN_TYPE)
    
    # input:    string representation for Manufacturer ID
    # output:   MID directory name to be used in BINIMAGE 
    def getMID_Directory(self, mid):
        manufacturer = ''   
        if (mid == '00'): manufacturer = 'ARI'
        elif (mid == '01'): manufacturer = 'IGT'
        elif (mid == '05'): manufacturer = 'PAC'
        elif (mid == '07'): manufacturer = 'VID'
        elif (mid == '09'): manufacturer = 'KONAMI'
        elif (mid == '12'): manufacturer = 'AGT'
        elif (mid == '17'): manufacturer = 'VGT'
        else:
            assert(mid in my_preferences.MID_LIST)
            
        return manufacturer
    
    # input:    string
    # output:   QCAS Expected output, i.e. 8 characters reversed
    def getQCAS_Expected_output(self, text):
        tmpstr = text[:8] # Returns from the beginning to position 8 of uppercase text
        return "".join(reversed([tmpstr[i:i+2] for i in range(0, len(tmpstr), 2)]))     
    
    # input: psl entry string, filename
    # output: Does PSL entry string exist in filename. 
    def verify_psl_entry_exist(self, psl_entry_str, file):
        with open(file, 'r') as psl_file: 
            reader = psl_file.readlines()
            for line in reader: 
                if psl_entry_str.rstrip(',') == str(line).strip(): 
                    return True
                else: 
                    pass
            return False # end of file return false
    
    # input: epsig command_str as represented in the log
    # output: none, function verifies the fields used in command string
    def verify_epsig_command_used(self, command_str): 
        command_str = command_str.lstrip()
        self.assertTrue(command_str.startswith("D:\OLGR-TECHSERV\MISC\BINIMAGE\qcas\epsigQCAS3_5.exe"))

        fields = command_str.split(' ')
        # assert(len(fields) == 5)
        
        command = fields[0]
        self.assertTrue(command == "D:\OLGR-TECHSERV\MISC\BINIMAGE\qcas\epsigQCAS3_5.exe")
        
        path = fields[1]
        self.assertTrue(path == "d:\OLGR-TECHSERV\BINIMAGE\*.*")
        
        msl = fields[2]
        msl_list = [self.MSLfile, self.nextMonth_MSLfile]
        self.assertTrue(any(msl in x for x in msl_list)) 
        
        tsl = fields[3]
        tsl_list = [self.TSLfile, self.previous_TSLfile]
        self.assertTrue(any(tsl in x for x in tsl_list))
        
        psl = fields[4]
        self.assertTrue(psl in [self.PSLfile, self.nextMonth_PSLfile])

    # input:    complete path to blnk file, TSL game object to for blnk file
    # output:   list containing two (2) PSL entries (text) for two months for the TSL game object
    def generate_PSL_entry(self, blnk_file, TSL_object):
        psl_entry = ''
        psl_entry_list = list()
       
        msl_file_list = [self.MSLfile, self.nextMonth_MSLfile]
    
        for msl_file in msl_file_list: # Check both months
            msl = self.check_file_format(msl_file, 'MSL')
            
            self.assertEqual(len(msl), 1)
            seed_list = msl[0].seed_list # expect one list

            psl_entry = "%(game_name)-30s,%(mid)02d,%(year)4s,%(month)02d,%(ssan)010d," % {'game_name': TSL_object.game_name, 'mid': int(TSL_object.mid), 'year': msl[0].year, 'month': msl[0].month, 'ssan': TSL_object.ssan}

            for seed in seed_list: 
                # def dobnk(self, fname, seed, mid, blocksize:65534)
                h = self.dobnk(blnk_file, seed, TSL_object.mid, blocksize=65534)
            
                tmpStr = str(h).lstrip('0X').zfill(40) # forces 40 characters with starting 0 characters. 
                tmpStr = str(h).lstrip('0x').zfill(40)
            
                psl_entry += self.getQCAS_Expected_output(tmpStr).upper() + ","
            
            psl_entry_list.append(psl_entry)
                    
        return psl_entry_list
        
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s- %(message)s')
    logging.debug('Start of unittesting for qcas datafiles.py')
    unittest.main()

    
    

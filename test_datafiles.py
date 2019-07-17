import unittest
import csv
import logging
import os
import hmac
import hashlib
import sys
import json
import difflib
import pickle
import getpass
import operator
import random
import time
from io import StringIO

from datetime import datetime, timedelta
from time import sleep

p_reset = "\x08"*8
CHECK_ONE_FILE_ONLY_FLG = "ONE_MONTH_ONLY"

DEFAULT_DATA = { 'path_to_binimage' : 'G:\\OLGR-TECHSERV\\BINIMAGE',
                  'mid_list' : [ '00', '01', '05', '07', '09', '12', '17'],
                  'valid_bin_types' : ['BLNK','PS32','SHA1'], #
                  'epsig_log_file' : 'G:\\OLGR-TECHSERV\\MISC\\BINIMAGE\\qcas\\log\\epsig.log',# 
                  'previous_TSLfile' : "qcas_2017_09_v02.tsl", 
                  'TSLfile' : "qcas_2017_10_v01.tsl", 
                  'PSLfile' : "qcas_2017_10_v03.psl", 
                  'nextMonth_PSLfile': "qcas_2017_11_v01.psl", 
                  'previousMonth_PSLfile' : "qcas_2018_12_v03.psl",
                  'MSLfile' : "qcas_2017_10_v01.msl",
                  'nextMonth_MSLfile' : "qcas_2017_11_v01.msl",
                  'write_new_games_to_file': "new_games.json",
                  'skip_lengthy_validations': "true",
                  'percent_changed_acceptable' : 0.10,
                  'verbose_mode': "true",
                  'number_of_random_games': 4,
                  'one_month_mode': "false"
                }

   
                
def skipping_PSL_comparison_tests(): 
    my_preferences = Preferences()    
    if my_preferences.data['one_month_mode'].upper() == "TRUE": 
        return True
    else:
        return False

def binimage_path_exists(): 
    my_preferences = Preferences()
    return os.path.isdir(my_preferences.data['path_to_binimage'])        

# Class for Preferences.dat file     
class Preferences: 

    def __init__(self): 
        preference_filename = 'preferences.dat'
        self.data = dict()

        self.psl_file_list = list()
        self.msl_file_list = list()
        self.tsl_file_list = list() 
        
        if os.path.isfile(preference_filename): 
            self.readfile(preference_filename)
            if self.verifydata() == False: # verify preferences file read
                self.data = DEFAULT_DATA # generate defaults
                self.writefile(preference_filename)
        else:            
            # default values
            self.data = DEFAULT_DATA
            self.writefile(preference_filename)
            
    def readfile(self, filename): 
        with open(filename, 'r') as jsonfile: 
            self.data = json.load(jsonfile)

            
    def scan_datafiles(self): 
        df_list = dict([(f, None) for f in os.listdir(".")])

        for file in df_list: 
            if file.upper().endswith('.PSL'):
                self.psl_file_list.append(file)
            elif file.upper().endswith('.MSL'): 
                self.msl_file_list.append(file)
            elif file.upper().endswith('.TSL'): 
                self.tsl_file_list.append(file)
            else: 
                pass # don't care about other files

        # expect two files 
        assert(len(self.psl_file_list) == 2) 
        # 'PSLfile' : "qcas_2017_10_v03.psl", 
        # 'nextMonth_PSLfile': "qcas_2017_11_v01.psl",    
    
        ordered_psl_file = self.identify_datafiles(self.psl_file_list)

        if self.data['verbose_mode'] == "TRUE": 
            logging.getLogger().debug("Sorted PSL file: " + ",".join(ordered_psl_file))
    
    def identify_datafiles(self, datafile): 
        # Verify Year 
        if QCASTestClient.get_filename_year(datafile[0]) == QCASTestClient.get_filename_year(datafile[1]): 
            # Same Year: Verify Month
            if QCASTestClient.get_filename_month(filename=datafile[0]) ==  QCASTestClient.get_filename_month(filename=datafile[1]): 
                # Same Year & Month, Verify Version
                if QCASTestClient.get_filename_version(filename=datafile[0]) < QCASTestClient.get_filename_version(filename=datafile[1]): 
                    return [datafile[0], datafile[1]]
                else: 
                    return [datafile[1], datafile[0]]
            elif QCASTestClient.get_filename_month(filename=datafile[0]) <  QCASTestClient.get_filename_month(filename=datafile[1]): 
                return [datafile[0], datafile[1]]
            else: 
                return [datafile[1], datafile[0]]
                
        elif QCASTestClient.get_filename_year(filename=datafile[0]) < QCASTestClient.get_filename_year(filename=datafile[1]): 
            return [datafile[0], datafile[1]]
        else: 
            return [datafile[1], datafile[0]]
            
    def toJSON(self): 
        return (json.dumps(self, default=lambda o: o.__dict__, sort_keys = True, indent=4))
    
    def writefile(self, fname):       
        with open(fname, 'w') as outfile: 
            json.dump(self.data, outfile,sort_keys=True, indent=4, separators=(',', ': '))    
    
    def getData(self): 
        return self.data
        
    def verifydata(self): 
        if self.data['path_to_binimage'] != None and \
            self.data['mid_list'] != None and \
            self.data['valid_bin_types'] != None and \
            self.data['epsig_log_file'] != None and \
            self.data['previous_TSLfile'] != None and \
            self.data['TSLfile'] != None and \
            self.data['PSLfile'] != None and \
            self.data['nextMonth_PSLfile'] != None and \
            self.data['previousMonth_PSLfile'] != None and \
            self.data['MSLfile'] != None and \
            self.data['nextMonth_MSLfile'] != None and \
            self.data['skip_lengthy_validations'] != None and \
            self.data['percent_changed_acceptable'] != None and \
            self.data['verbose_mode'] != None and \
            self.data['number_of_random_games'] != None and \
            self.data['one_month_mode'] != None : 

            # do nothing
            return True
            
        else:            
            print("Error reading file from disk, recreating all preferences from Default") 
            return False
                  
class CacheMemory: 

    def __init__(self):
        self.cache_dict = {} 

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
    
    def toJSON(self): 
        return (json.dumps(self, default=lambda o: o.__dict__, sort_keys = True, indent=4))

class CacheFile:

    def __init__(self, fname): 
        if os.path.isfile(fname): 
            self.cache_file = fname
            self.sigsCacheFile = self.cache_file[:-4] + "sigs" # .json file renaming to .sigs file
            # no File Cache
            # self.cache_dict = self.importCacheFile()
            self.cache_dict = {} 
                    
    def importCacheFile(self):
        cache_data = {} 

        if os.path.isfile(self.cache_file): 
            # Verify Cache Integrity
            cache_file_sigs_filename = self.cache_file[:-4] + ".sigs"
            
            if self.verifyCacheIntegrity(cache_file_sigs_filename): 
                with open(self.cache_file,'r') as json_cachefile: 
                    cache_data = json.load(json_cachefile)
            else: 
                logging.warning("**** WARNING **** File Cache integrity issue: " +
                       " Cannot Verify signature")
                logging.info("Generating new File Cache file:" + self.cache_file)
                cache_data = {} # return empty cache
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
                logging.getLogger().warning('Run script again, empty cache file created')
                self.signCacheFile()
                sys.exit(0)
        
        self.signCacheFile()

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
        hashm = {}
        
        if os.path.isfile(cache_location_sigs): # Sigs file exist?
            with open(cache_location_sigs, 'rb') as sigs_file: 
                cache_sigs_data = json.load(sigs_file)
                hashm = cache_sigs_data['cachefile_hash']
                #fname = cache_sigs_data['filename']
        else: 
            # advise user
            logging.warning("\n**** WARNING **** Generating new Cache Sigs file\n") 
            self.signCacheFile() # Generate Cache Sigs file
            
        generated_hash = QCASTestClient.dohash_sha256(self.cache_file, 8192)
        
        if hashm == generated_hash: 
            return True
        else: 
            return False     
        
        
    def signCacheFile(self):
        h = QCASTestClient.dohash_sha256(self.cache_file, 8192) # requires file name as input
        
        with open(self.sigsCacheFile,'w+') as sigs_file:    
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
            with open(self.cache_file, 'w+') as json_cachefile:
                json.dump(self.cache_dict,
                          json_cachefile,
                          sort_keys=True,
                          indent=4,
                          separators=(',', ': '))

# PSLEntry with only one hash (random)
class PSLEntry_OneHash: 
    # helper class for PSL file
    def __init__(self, line):
        my_preferences = Preferences()
        fields = str(line).split(',')
            
        self.game_name = fields[0].strip() # strip spaces
        assert(len(self.game_name) < 31)
       
        self.manufacturer = fields[1]
        assert(self.manufacturer in my_preferences.data['mid_list'])
        
        self.year = int(fields[2])
        valid_year = list(range(2017,9999))
        assert(len(fields[2]) == 4)
        assert(self.year in valid_year)
        
        self.month = int(fields[3])
        valid_months = list(range(1,13))
        assert(self.month in valid_months)
        
        assert(len(fields[4].strip()) == 10)
        self.ssan = int(fields[4].strip())

        self.hash = fields[5].strip()       
        
    def toString(self): 
        self.psl_entry_str = "%(game_name)-30s,%(mid)02d,%(year)4s,%(month)02d,%(ssan)010d,%(hash)08s" % {'game_name': self.game_name, 'mid': int(self.manufacturer), 'year': self.year, 'month': int(self.month), 'ssan': int(self.ssan), 'hash': self.hash}

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
    
    def toJSON(self): 
        return (json.dumps(self, default=lambda o: o.__dict__, sort_keys = True, indent=4))
                          
class PSLfile:
    # helper class for PSL file
    def __init__(self, line):
        my_preferences = Preferences()
        fields = str(line).split(',')
        input_line = str(line).strip(',') # remove trailing comma

        self.game_name = fields[0].strip() # strip spaces
        
        assert(len(self.game_name) < 31)
       
        self.manufacturer = fields[1]
        assert(self.manufacturer in my_preferences.data['mid_list'])
        
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
    
    def toJSON(self): 
        return (json.dumps(self, default=lambda o: o.__dict__, sort_keys = True, indent=4))
        
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
        assert(self.mid in my_preferences.data['mid_list'])
        
        assert(len(fields[1]) == 10)
        self.ssan = int(fields[1])
        
        self.game_name = fields[2].strip()
        assert(len(self.game_name) < 61)
        
        self.bin_file = fields[3].strip()
        assert(len(self.bin_file) < 21)
        
        self.bin_type = fields[4].strip()
        assert(self.bin_type in my_preferences.data['valid_bin_types'])
    
    def toJSON(self): 
        return (json.dumps(self, default=lambda o: o.__dict__, sort_keys = True, indent=4))

    def toJSON_oneline(self): 
        return (json.dumps(self, default=lambda o: o.__dict__, sort_keys = True))
        
# Derived unittest.TestCase class used for unittest testing. 
class QCASTestClient(unittest.TestCase):
    # common test behaviours
    
    def setUp(self):                  
        # Read from JSON file
        # Global Vars, Paths, and QCAS datafile names
        self.my_preferences = Preferences() 
        self.verbose_mode = self.my_preferences.data['verbose_mode'] == "TRUE"
        
        self.psl_cache_file = CacheMemory() ## Use a cache memory, clear after each test
        # self.psl_cache_file = CacheFile(self.my_preferences.cache_filename) # use a Cachefile - all defaults

        ###############################################
        ## Files to Verify
        ## Modify the following files only
        ## 
        ## TSL files 
        ## PSL files (hashes)        
        ## MSL files (seeds)        
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

    def tearDown(self): 
        err_msg = ""  
        self.my_preferences = None
            
    def generate_seed_list_for_test(self): 
        seedlist = list() 
        for i in range(1, self.my_preferences.data['number_of_random_games']): 
            random_seed_idx =  random.randint(0,30) # Choose a random day for the month
            seedlist.append(random_seed_idx)
        
        return seedlist
        
    # input: num : number
    # output: s : string formatted i.e. 01-09
    def format_twoDigit(self, num):
        if num < 10:
            return("0" + str(num))
        else:
            return str(num)
        
        
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
        if len(game_name) > 1 and len(game_name) < 31:
            return True
        else:
            return False

    def check_manufacturer(self, manufacturer):
        output = ''
            
        if len(manufacturer) < 2:
            temp_manufacturer = "0" + manufacturer
        else:
            temp_manufacturer = manufacturer

        if temp_manufacturer in set(self.my_preferences.data['mid_list']):
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

    def check_hash_list_size(self, hash_list):
       
        if len(hash_list) == 31:
           return True 
        else:
           return False
    
    def check_hash_list(self, msl_file, hash_list): 
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
        if binimage_type in self.my_preferences.data['valid_bin_types']:
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
                logging.getLogger().error("unknown flag type")
                sys.exit(1)

        if count == 1:
            return True
        else:
            logging.getLogger().debug("Not Unique, counted : " + str(count) + " ,".join(duplicate_entries))
            if '0201230' in duplicate_entries: # handle this duplicate entry
                return True
            else:
                return False

    def get_oldgames_to_be_removed(self): 
        tsl_difference_games_removed = set()
        game_list_to_be_removed = list()

        with open(self.my_preferences.data['previous_TSLfile'], 'r') as file1: 
            with open(self.my_preferences.data['TSLfile'], 'r') as file2: 
                tsl_difference_games_removed = set(file1).difference(file2)        
        
        for game in list(game_list_to_be_removed): # Single Line
            game_list_to_be_removed.append(TSLfile(game)) # Generate TSL object        
        
        return game_list_to_be_removed
    
    def get_newgames_to_be_added(self): 
        game_list_to_be_added = list()
        tsl_difference_games_added = set()

        with open(self.my_preferences.data['TSLfile'], 'r') as file1:
            with open(self.my_preferences.data['previous_TSLfile'], 'r') as file2:
                tsl_difference_games_added = set(file1).difference(file2)
        
        self.assertTrue(len(tsl_difference_games_added) > 0, msg="TSL file has no new games") # TSL files must contain a new game? 
  
        # Differences are the new games to be added. 
        for game in list(tsl_difference_games_added): # Single Line
            game_list_to_be_added.append(TSLfile(game)) # Generate TSL object
        
        # sort by game name then by manufacturer, manufaturer is sorted by MID (i.e. numbers with ARI = 00, IGT= 01, etc)
        tsl_game_list_sorted = sorted(game_list_to_be_added, key=lambda game_list_to_be_added: (game_list_to_be_added.game_name))
        tsl_game_list_sorted = sorted(tsl_game_list_sorted, key=lambda tsl_game_list_sorted: (tsl_game_list_sorted.mid))
        
        self.save_game_list_to_disk(tsl_game_list_sorted)  # write file to disk. 
        
        return tsl_game_list_sorted
    
    # input: tsl object game list
    # output: none
    # writes to file new games
    def save_game_list_to_disk(self, tsl_game_list): 
        timestamp = str(datetime.now())
        # month = datetime.now().strftime("%B")
        
        today = datetime.now()
        this_month = today
        next_month = today + timedelta(days=31) 

        with open(self.my_preferences.data['write_new_games_to_file'], 'w+') as file: 
            file.writelines("==== Generated by: " + getpass.getuser() + "; Timestamp: " + timestamp + " ====\n")
            file.writelines("\nTo Whom it may concern,\n\n")
            file.writelines("Please find attached the MSL/PSL files for " 
                + this_month.strftime("%B %Y") + " and " + next_month.strftime("%B %Y") + "\n")
            file.writelines("\nAdditions:")
            mid = ""
            for game in tsl_game_list: 
                if mid != game.mid: 
                    mid = game.mid
                    file.writelines("\n\n" + self.get_manufacturer_name(game.mid) + "\n")
                
                # str1 = str("\n%(man)15s\t%(game_name)40s\tSSAN: %(ssan)-10s" %
                str1 = str("\n%(game_name)40s\tSSAN: %(ssan)-10s" %
                {  # 'man' : self.get_manufacturer_name(game.mid),
                    'game_name' : game.game_name,
                    'ssan': str(game.ssan)
                })
                file.writelines(str1)
                        
            file.writelines("\nRemovals: \n\n")
            file.writelines("Please acknowledge the receipt of the attached MSL/PSL files via a return email within the next two (2) business days.\n")
            file.writelines("<REMOVE>NOTE: VERIFY THAT THIS EMAIL CONTAINS ALL CORRECT TO: ADDRESSES PRIOR TO SENDING. <REMOVE>")

    def get_manufacturer_name(self, s): 
        if s == '00': 
            return "Aristocrat"
        elif s == '01': 
            return "IGT"
        elif s == '05': 
            return "Aruze"
        elif s == '07': 
            return "Bally/SG Gaming"
        elif s == '09':
            return "Konami"
        elif s == '12': 
            return "AGT"
        elif s == '17':
            return "QGS"
        else: 
            return "Unknown Manufacturer: " + s
    
    # input:    total path to BLNK file, MID and optional blocksize
    # output:   blnk hash result using seed. 
    def dobnk(self, blnk_file, seed, s_index, mid, blocksize=65534):
        oh = "0000000000000000000000000000000000000000"

        with open(blnk_file, 'r') as file:         # Read BNK file
            field_names = ['fname', 'type', 'blah']
            
            data = file.read()
            data = data.replace('\x00','') # remove null characters in file
            
            reader = csv.DictReader(StringIO(data), delimiter=' ', fieldnames=field_names)
        
            for row in reader: 
                if row['type'].upper() == 'SHA1': # To handle CR32, 0A4R, 0A4F
                    complete_path_to_file = os.path.join(self.my_preferences.data['path_to_binimage'],self.getMID_Directory(mid), str(row['fname']))    
                    cachedhit = self.psl_cache_file.checkCacheFilename(complete_path_to_file, self.getQCAS_Expected_output(seed), row['type'].upper()) 
        
                    if cachedhit:
                        localhash = cachedhit # use cached data
                    else: 
                        new_cache_list = list()
                        localhash = self.dohash_hmacsha1(complete_path_to_file, s_index, self.getQCAS_Expected_output(seed), blocksize) 
                    
                        # create cache object
                        cache_object = { 
                            'seed': self.getQCAS_Expected_output(seed), 
                            'alg': row['type'].upper(), 
                            'verify':'0', 
                            'hash': localhash 
                        }        
                        
                        cache_entry_list = self.psl_cache_file.cache_dict.get(complete_path_to_file) # Should return a list. 
                        
                        if cache_entry_list :   # File Entry Exists, append to list
                            cache_entry_list.append(cache_object) # print this
                            self.psl_cache_file.cache_dict[complete_path_to_file] = cache_entry_list
                        else:        
                            # No File Entry Exits generate new list entry in cache_dict
                            new_cache_list.append(cache_object)
                            self.psl_cache_file.cache_dict[complete_path_to_file] = new_cache_list # keep unique
                                                                                
                    if localhash == 0:
                        break
                      
                    oh = hex(int(oh,16) ^ int(str(localhash), 16)) # XOR

                else: 
                    self.assertEqual(row['type'], "SHA1", msg=row['type'] + "  - Not processing these Hash Types: CR32, 0A4R, 0A4F. Only supports .BNK files with SHA1: " + blnk_file)
                           
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
    def dohash_hmacsha1(self, fname, seed_index, seed='00', chunksize=32768):
        key = bytes.fromhex(seed)
        m = hmac.new(key, digestmod = hashlib.sha1) # change this if you want other hashing types for HMAC, e.g. hashlib.md5
        done = 0
        size = os.path.getsize(fname)
        # Read in chunksize blocks at a time
        with open(fname, 'rb') as f:            
            print("\nHashing: %(file_name)-40s\tSeed[%(s_index)2s]: %(seed)8s [in MSLfile as: %(reversed)8s]\t" % \
                {   'file_name' : os.path.basename(fname)[:40], # truncate 40 chars only
                    's_index': seed_index+1, 
                    'seed': seed,
                    'reversed': self.getQCAS_Expected_output(seed)
                }, end="")
            
            while True:
                block = f.read(chunksize)
                if done >= size: 
                    done = size
                else: 
                    done += chunksize
                if not block: break
                m.update(block)      
                
                # percentage %
                if self.my_preferences.data['verbose_mode'] == "TRUE": 
                    if (done*100/size) < 100: 
                        sys.stdout.write("%7d" % (done*100/size) + "%" + p_reset)
                    else:
                        sys.stdout.write("%7d" % 100 + "%" + p_reset)
                            
        return m.hexdigest()
        
    def get_bin_type(self, bin_type):
        if bin_type.startswith('BLNK'):
            return "BNK"
        elif bin_type.startswith('SHA1'): 
            return "BIN"
        elif bin_type.startswith('CR32'): 
            return "BIN"
        elif bin_type.startswith('PS32'):
            return "BIN"
        else: 
            assert(bin_type in self.my_preferences.data['valid_bin_types'])
    
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
        elif (mid == '17'): manufacturer = 'QGS'
        else:
            assert(mid in self.my_preferences.data['mid_list'])
            
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
    # Z:\OLGR-TECHSERV\MISC\BINIMAGE\qcas\epsigQCAS3_5.exe z:\OLGR-TECHSERV\BINIMAGE\*.* qcas_2018_08_v01.msl qcas_2018_07_v02.tsl qcas_2018_08_v01.psl 
    def verify_epsig_command_used(self, command_str): 
        command_str = command_str.lstrip()[2:] # strip drive
        
        self.assertTrue(command_str.startswith("\OLGR-TECHSERV\MISC\BINIMAGE\qcas\epsigQCAS3_5.exe"))

        fields = command_str.split(' ')
        # assert(len(fields) == 5)
        
        command = fields[0].strip()
        self.assertTrue(command == "\OLGR-TECHSERV\MISC\BINIMAGE\qcas\epsigQCAS3_5.exe")
        
        path = fields[1].strip()
        self.assertTrue(path[2:] == "\OLGR-TECHSERV\BINIMAGE\*.*")
        
        msl = fields[2].strip()
        msl_list = [self.my_preferences.data['MSLfile'], self.my_preferences.data['nextMonth_MSLfile']]
        self.assertTrue(any(msl in x for x in msl_list)) 
        
        tsl = fields[3].strip()
        tsl_list = [self.my_preferences.data['TSLfile'], self.my_preferences.data['previous_TSLfile']]
        self.assertTrue(any(tsl in x for x in tsl_list))
        
        psl = fields[4].strip()
        
        # remove paths
        head, psl_tail = os.path.split(self.my_preferences.data['PSLfile'])
        head, psl_tail2 = os.path.split(self.my_preferences.data['nextMonth_PSLfile'])

        self.assertTrue(psl in [psl_tail, psl_tail2])

    # input:    complete path to blnk file, TSL game object to for blnk file
    # output:   list containing two (2) PSL entries (text) for two months for the TSL game object
    def generate_PSL_entry(self, blnk_file, TSL_object):
        psl_entry = ''
        psl_entry_list = list()

        if skipping_PSL_comparison_tests(): 
            msl_file_list = [self.my_preferences.data['MSLfile']]
        else: 
            msl_file_list = [self.my_preferences.data['MSLfile'], self.my_preferences.data['nextMonth_MSLfile']]
    
        for msl_file in msl_file_list: # Check both months
            msl = self.check_file_format(msl_file, 'MSL')
            
            self.assertEqual(len(msl), 1)
            seed_list = msl[0].seed_list # expect one list

            psl_entry = "%(game_name)-30s,%(mid)02d,%(year)4s,%(month)02d,%(ssan)010d," % {'game_name': TSL_object.game_name[:30], 'mid': int(TSL_object.mid), 'year': msl[0].year, 'month': msl[0].month, 'ssan': TSL_object.ssan}

            for seed in seed_list: 
                # def dobnk(self, fname, seed, mid, blocksize:65534)
                # test if BIN LINK FILE 
                h = ""
                if blnk_file.upper().endswith(".BNK"): # Process BNK file
                    h = self.dobnk(blnk_file, seed, seed_list.index(seed), TSL_object.mid, blocksize=65535)
                else: # PROCESS everything else as HMAC-SHA1 files
                    h = self.dohash_hmacsha1(blnk_file, seed_list.index(seed), self.getQCAS_Expected_output(seed)) 
                  
                tmpStr = str(h).lstrip('0X').zfill(40) # forces 40 characters with starting 0 characters. 
                tmpStr = str(h).lstrip('0x').zfill(40)
            
                psl_entry += self.getQCAS_Expected_output(tmpStr).upper() + ","
            
            psl_entry_list.append(psl_entry.rstrip(','))
        
        # self.psl_cache_file.signCacheFile()
        
        return psl_entry_list
    
    def generate_PSL_entry_one_seed(self, blnk_file, TSL_object, seed, random_seed_idx):
        psl_entry = ''
        psl_entry_list = list()
    
        msl = self.check_file_format(self.my_preferences.data['MSLfile'], 'MSL')
        
        psl_entry = "%(game_name)-30s,%(mid)02d,%(year)4s,%(month)02d,%(ssan)010d," % {'game_name': TSL_object.game_name[:30], 'mid': int(TSL_object.mid), 'year': msl[0].year, 'month': msl[0].month, 'ssan': TSL_object.ssan}

        # def dobnk(self, fname, seed, mid, blocksize:65534)
        h = self.dobnk(blnk_file, seed, random_seed_idx, TSL_object.mid, blocksize=65535)

        tmpStr = str(h).lstrip('0X').zfill(40) # forces 40 characters with starting 0 characters. 
        tmpStr = str(h).lstrip('0x').zfill(40)
    
        psl_entry += self.getQCAS_Expected_output(tmpStr).upper() + ","
                
        return psl_entry
    
    # Confirm whether this game can be processed by this script.
    # Returns: Boolean
    # Input: TSL game object
    def check_game_type(self, tsl_entry_object): 
        rv = None

        if tsl_entry_object.bin_type == 'BLNK':  # Check only BLNK files 

            # Check the contents of the BLNK file to make sure that 
            # 0A4R, 0A4F types are handled. 

            blnk_file = os.path.join(self.my_preferences.data['path_to_binimage'], 
                self.getMID_Directory(tsl_entry_object.mid), 
                tsl_entry_object.bin_file.strip() + "." + self.get_bin_type(tsl_entry_object.bin_type))

            # inspect the bin file
            with open(blnk_file, 'r') as file:         # Read BNK file
                field_names = ['fname', 'type', 'blah']
                reader = csv.DictReader(file, delimiter=' ', fieldnames=field_names)

                for row in reader: 
                    if row['type'].upper() == 'SHA1': # To handle CR32, 0A4R, 0A4F
                        rv = True
                    else: 
                        rv = False # Everything other than SHA1 in BLNK files are invalid. 

        else: 
            rv = False

        return rv
       
if __name__ == '__main__':
    unittest.main()

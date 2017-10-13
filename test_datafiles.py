import unittest
import csv
import logging
from datetime import datetime

VALID_BIN_TYPE = ['BLNK','PS32','SHA1']

class PSLfile:
    # helper class for PSL file
    def __init__(self, line):
        fields = str(line).split(',')
        self.game_name = fields[0]
        self.manufacturer = fields[1]
        self.year = int(fields[2])
        self.month = int(fields[3])
        self.ssan = int(fields[4])

        included_cols = [5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35]
        self.hash_list = list(fields[i] for i in included_cols)
        assert(len(self.hash_list) == 31)

        #count = 0
        #for item in self.hash_list:
        #    print("Count: " + str(count) + " Hash: " + str(item))
        #    count += 1

class MSLfile:
    # helper class for MSL file
    def __init__(self, line):
        fields = str(line).split(',')
        self.year = int(fields[0])
        self.month = int(fields[1])

        included_cols = [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32]
        self.seed_list = list(fields[i] for i in included_cols)

        #count = 1
        #for item in self.seed_list:
        #    print("Day: " + str(count) + " Seed item: " + str(item))
        #    count += 1
            
        assert(len(self.seed_list) == 31)
        
class TSLfile:
    # helper class for TSL file
    def __init__(self, line):
        fields = str(line).split(',')
        self.mid = int(fields[0])
        self.ssan = int(fields[1])
        self.game_name = fields[2]
        self.bin_file = fields[3]
        self.bin_type = fields[4]

        
# Derived unittest.TestCase class used for unittest testing. 
class QCASTestClient(unittest.TestCase):
    # common test behaviours
    
    def setUp(self):
        # Files to Verify
        self.previous_TSLfile = "qcas_2017_09_v02.tsl"
        self.TSLfile = "qcas_2017_10_v01.tsl"

        self.PSLfile = "qcas_2017_10_v03.psl"
        self.MSLfile = "qcas_2017_11_v01.msl"

        self.nextMonth_PSLfile = "qcas_2017_11_v01.psl"
        self.nextMonth_MSLfile = "qcas_2017_12_v01.msl"
        
        self.manufacturer_id_list = [ '00', '01', '05', '07', '09', '12', '17']
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
        #print("manufacturer is: " + manufacturer)
            
        if len(manufacturer) < 2:
            temp_manufacturer = "0" + manufacturer
        else:
            temp_manufacturer = manufacturer

        if temp_manufacturer in set(self.manufacturer_id_list):
            output =  True
        else:
            output = False

        #print("temp_manufacturer is: " + temp_manufacturer)

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
        logging.debug("Year input: " + str(year), " Today.year is: " + str(today.year))

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
        
        return True

    def get_filename_version(self, filename):
        file_version = ''
        #self.PSLfile = "qcas_2016_05_v03.psl"
        #self.MSLfile = "qcas_2016_06_v01.msl"
        #self.TSLfile = "qcas_2016_06_v01.tsl"

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
        if binimage_type in VALID_BIN_TYPE:
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


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s- %(message)s')
    logging.debug('Start of unittesting for qcas datafiles.py')
    unittest.main()

import unittest
import csv
import logging
from datetime import datetime

class PSLfile:
    # helper class for PSL file
    def __init__(self, line):
        fields = str(line).split(',')
        self.game_name = fields[0]
        self.manufacturer = fields[1]
        self.year = fields[2]
        self.month = fields[3]
        self.ssan = fields[4]

        included_cols = [5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35]
        self.hash_list = list(i for i in included_cols)

class MSLfile:
    # helper class for MSL file
    def __init__(self, line):
        fields = str(line).split(',')
        self.year = fields[0]
        self.month = fields[1]

        included_cols = [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33]
        self.seed_list = list(i for i in included_cols)

# Derived unittest.TestCase class used for unittest testing. 
class QCASTestClient(unittest.TestCase):
    # common test behaviours
    
    def setUp(self):
        # Files to Verify
        self.PSLfile = "qcas_2016_05_v03.psl"
        self.MSLfile = "qcas_2016_06_v01.msl"
        self.TSLfile = "qcas_2016_06_v01.tsl"

        
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
                for row in psl_entries:
                    item_list.append(PSLfile(row))
        # test MSL file format
        elif file_format == 'MSL':
            with open(file, 'r') as msl:
                msl_entries = csv.reader(msl, delimiter=',')
                for row in msl_entries: 
                    item_list = MSLfile(row) # only 1 row in MSL file. 

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
        
        return True

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s- %(message)s')
    logging.debug('Start of unittesting for qcas datafiles.py')
    unittest.main()

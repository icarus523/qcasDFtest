import os
import csv
import random

from test_datafiles import QCASTestClient, PSLfile, TSLfile, MSLfile
from epsig2_gui import epsig2

MID_LIST = [ '00', '01', '05', '07', '09', '12', '17']
PATH_TO_BINIMAGE = 'C:\\Users\\aceretjr\\Documents\\dev\\qcas-Datafiles-Unittest\\binimage'

class test_chk01_checklist(QCASTestClient):
   
    def test_Generated_PSL_files_Differ(self):
        same = set()
        
        with open(self.PSLfile, 'r') as file1:
            with open(self.nextMonth_PSLfile, 'r') as file2:
                same = set(file1).intersection(file2)
   
        self.assertFalse(len(same) > 0)
                
    def test_new_games_to_be_added_are_in_PSL_files(self):
        game_list_to_be_added = self.get_newgames_to_be_added()
            
        # Find these games in the both PSL files
        psl_file_list = [self.PSLfile, self.nextMonth_PSLfile] 
        verified_game = list()
        
        for psl_file in psl_file_list: 
            psl_entries_list = self.check_file_format(psl_file, 'PSL')       
            
            for game in game_list_to_be_added:      #TSL entries
                for psl_entry in psl_entries_list: 
                    if game.ssan == psl_entry.ssan: # TSL entry SSAN == PSL entry SSAN
                        verified_game.append(game)  # List of TSL entries that have been verified. 
                        
            psl_difference = list(set(verified_game).intersection(set(game_list_to_be_added))) # TSL lists
                
            self.assertTrue(set(verified_game).intersection(set(game_list_to_be_added))) # For each PSL file does verified_game match game_list_to_be_added? 
    
    def test_TSL_entries_exist_in_PSL_files(self):        
        # Read TSL entry
        # Generate PSL entry with seeds
        # Find that this PSL entry exits in PSL file. 
        psl_object_list = list()
        
        TSL_game_list_to_be_added = self.get_newgames_to_be_added()
        both_MSL_seed_list_file = [self.MSLfile , self.nextMonth_MSLfile] 
        count = 0
        for MSL_file in both_MSL_seed_list_file: 
            for game in TSL_game_list_to_be_added: 
                psl_entry_string = self.generate_PSL_entries(MSL_file, game) 
                # print("\n" + psl_entry_string)
                # PSLfile.identifyDifference(psl_entry_string, 
                # test the psl_entry to be formatted as an PSL object
                psl_entry_object = PSLfile(psl_entry_string) 
                
                self.assertTrue(len(psl_entry_object.game_name) < 31)
                self.assertTrue(psl_entry_object.manufacturer in MID_LIST)
                
                valid_year = list(range(2017,9999))
                self.assertTrue(psl_entry_object.year in valid_year)
                
                valid_months = list(range(1,13))
                self.assertTrue(psl_entry_object.month in valid_months)
            
                #valid_ssan = list (range(150000, 999999999))
                self.assertTrue(psl_entry_object.ssan < 999999999 and psl_entry_object.ssan > 150000)
                
                self.assertTrue(len(psl_entry_object.hash_list) == 31)
                
                # verify that PSL object fields matches is the the PSLfiles  
                psl_files_list = [self.PSLfile, self.nextMonth_PSLfile] 
                for psl_file in psl_files_list:
                    with open(psl_file, 'r') as file: 
                        if psl_entry_object.toString().strip(',') in file.read(): 
                            # print(psl_entry_object.toString() + "\t found!")
                            count+=1
        
            # print("Length of new_psl_entries_list: " + str(len(TSL_game_list_to_be_added)) + " Identified Entries: " + str(count))
        #assert(count == len(TSL_game_list_to_be_added))
    
    def test_Games_removed_from_PSL_files(self): 
        # generate a list of games removed. 
        # Difference from previous month PSL and this Months PSL files (multiple). 
        print("test - Games removed from PSL files")
    
    def test_One_new_game_to_be_added_in_PSL_files(self):
        new_games_to_be_added = self.get_newgames_to_be_added()   # TSL object list
        random_tsl_entry = random.choice(new_games_to_be_added) 
        blnk_file = os.path.join(PATH_TO_BINIMAGE, self.getMID_Directory(random_tsl_entry.mid), random_tsl_entry.bin_file.strip() + "." + self.get_bin_type(random_tsl_entry.bin_type))

        psl_entry_list = list()
        msl  = self.check_file_format(self.MSLfile, 'MSL')
        seed_list = msl[0].seed_list
        
        for seed in seed_list: 
            # def dobnk(self, fname, seed, mid, blocksize:65534)
            h = self.dobnk(blnk_file, seed, random_tsl_entry.mid, blocksize=65534)
            
            tmpStr = str(h).lstrip('0X').zfill(40) # forces 40 characters with starting 0 characters. 
            tmpStr = str(h).lstrip('0x').zfill(40)
            
            
            print(self.getQCAS_Expected_output(tmpStr))
            #psl_entry_string = self.generate_PSL_entries(mslfile, random_tsl_entry) 
            #psl_entry_list.append(psl_entry_string)
            
        #self.assertEqual(len(psl_entry_list), 2) # one PSL entry for each month
        
        #for psl_entry in psl_entry_list:
        #    print(psl_entry)
        
        #self.assertTrue(self.verify_psl_entry_exist(psl_entry_list[0], self.PSLfile))
        #self.assertTrue(self.verify_psl_entry_exist(psl_entry_list[1], self.nextMonth_PSLfile))
        
    def test_One_old_game_to_be_added_in_PSL_files(self): 
        print("test - one old game to be added in PSL files")
    
    def test_Epsig_Log_file(self): 
        #log_file = "G:\\OLGR-TECHSERV\\MISC\\BINIMAGE\\qcas\\log\\epsig.log"
        log_file = "C:\\Users\\aceretjr\\Documents\\dev\\qcas-Datafiles-Unittest\\logs\\epsig.log"
        
        # EPSIG.EXE Version 3.5 Copyright The State of Queensland 1999-2015
        # Started at   Thu Oct 19 13:41:14 2017
        # D:\OLGR-TECHSERV\MISC\BINIMAGE\qcas\epsigQCAS3_5.exe d:\OLGR-TECHSERV\BINIMAGE\*.* qcas_2017_11_v01.msl qcas_2017_10_v02.tsl qcas_2017_11_v02.psl 
        # Allocating buffer 262144 bytes
    
        with open(log_file, 'r') as file: 
            epsig_log = file.read()
            paragraphs = epsig_log.split('\n\n')
            
            
            data = paragraphs[len(paragraphs)-1].split('\n') # get last paragraph from list. 
            data = list(filter(None, data)) # remove empty lists            
                        
            header = data[0]
            #print("header: " + header) 
            time_stamp_start = data[1]
            #print("time_stamp_start: " + time_stamp_start)
            command = data[2]
            #print("command: " + command)
            allocating_buffer = data[3]
            #print("allocating_buffer: " + allocating_buffer)

            if len(data) > 4: 
                time_stamp_end = data[4]
                #print("time_stamp_end: " + time_stamp_end) 
                footer_status = data[5]
                #print("footer_status: " + footer_status)
                
                # The latest run Epsig error file is correct.(Ref WI01)      
                assert(footer_status == " with EXIT_SUCCESS")
                       
            assert(len(data) == 4 or len(data) == 6) # +1 is required here because of the expected blank line. 
            # Ensure that the parameters of the epsig.exe call appear correct, the dates and start and finish time of processing appear reasonable.         
            self.verify_epsig_command_used(command)
            
            
    def test_PSL_size_is_reasonable(self): 
        psl_files = [self.PSLfile, self.nextMonth_PSLfile] 
        for psl_file in psl_files: 
            size_in_bytes = os.stat(psl_file)
            
            # Verify that the size of the PSL files is reasonable. (The size range generally grows a few Kilobytes per run) and is approximately 1055KB as at July 2013.
            self.assertTrue(size_in_bytes.st_size > 1055000)
    
    def test_MSL_size_is_reasonable(self): 
        msl_files = [self.MSLfile, self.nextMonth_MSLfile] 
        for msl_file in msl_files: 
            size_in_bytes = os.stat(msl_file)
            
        # Verify that the size of the MSL files is reasonable. (The size should not change and is 1KB)
        self.assertTrue(size_in_bytes.st_size < 1024)
    
    def test_PSL_content(self): 
        # Verify the content of ach PSL including that they refer to the correct month, year and contains hash data for all manufactures. 
        # This can be done by ensuring all active Manufacturers have entries represented by their Machine ID, in the second column of the file. E.g AGT’s is ‘12’.
        psl_files = [self.PSLfile, self.nextMonth_PSLfile] 
        for psl_file in psl_files:        
            psl_entry_object_list = self.check_file_format(psl_file, 'PSL') # Parse the file and validate MSL content

            psl_file_num_lines = sum(1 for line in open(psl_file))
            
            self.assertTrue(len(psl_entry_object_list) == psl_file_num_lines) # Check the number of lines equal
            
    def test_MSL_content(self): 
        # Verify the content of any MSL including that they refers to the correct month, year and contains seed data for each day
        msl_files = [self.MSLfile, self.nextMonth_MSLfile] 
        for msl_file in msl_files: 
            msl_entry_object_list = self.check_file_format(msl_file, 'MSL') # Parse the file and validate MSL content
        
        self.assertTrue(len(msl_entry_object_list) == 1) # 1 Entry

import os
import csv

from test_datafiles import QCASTestClient, PSLfile, TSLfile

MID_LIST = [ '00', '01', '05', '07', '09', '12', '17']

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
            #for tslitem in psl_difference: 
            #    print("Verified added games in " + psl_file + " is: " + tslitem.game_name)
                
            self.assertTrue(set(verified_game).intersection(set(game_list_to_be_added)))
    
    def test_TSL_entries_exist_in_PSL_files(self):        
        # Read TSL entry
        # Generate PSL entry with seeds
        # Find that this PSL entry exits in PSL file. 
        
        TSL_game_list_to_be_added = self.get_newgames_to_be_added()
        both_MSL_seed_list_file = [self.MSLfile, self.nextMonth_MSLfile] 
        psl_list_for_each_month = list()
        for MSL_file in both_MSL_seed_list_file: 
            new_psl_entries_list = self.generate_PSL_entries(MSL_file, TSL_game_list_to_be_added) 
            psl_list_for_each_month.append(new_psl_entries_list) # should return two lists for two games 
            
        # print("Size of PSL entries generated: " + str(len(new_psl_entries_list)))
        
        # test the psl_entry to be formatted as an PSL object
        for month in psl_list_for_each_month:
            for psl_entry in new_psl_entries_list: 
                print(psl_entry)
                psl_entry_object = PSLfile(psl_entry) 
                
                assert(len(psl_entry_object.game_name) < 31)
                assert(psl_entry_object.manufacturer in MID_LIST)
                
                valid_year = list(range(2017,9999))
                assert(psl_entry_object.year in valid_year)
                
                valid_months = list(range(1,13))
                assert(psl_entry_object.month in valid_months)
            
                #valid_ssan = list (range(150000, 999999999))
                #print(psl_entry_object.ssan in valid_ssan)
                
                assert(len(psl_entry_object.hash_list) == 31)
        
        # verify that PSL object fields matches is the the PSLfiles 
        #psl_files_list = [self.PSLfile, self.nextMonth_PSLfile] 
        #count = 0
        #for psl_entry in new_psl_entries_list: 
        #   for psl_file in psl_files_list:
        #        if self.verify_psl_entry_exist(psl_entry, psl_file): 
        #            count+=1
        
        #print("Length of new_psl_entries_list: " + str(len(new_psl_entries_list)) + " Identified Entries: " + str(count))
        #assert(count == len(new_psl_entries_list))
        # print("PSL entries generated: " + ', '.join(new_psl_entries_list))

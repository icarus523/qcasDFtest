import os
import unittest
from test_datafiles import QCASTestClient, PSLfile, CHECK_ONE_FILE_ONLY_FLG, skipping_PSL_comparison_tests

class test_PSLfile_content(QCASTestClient): 

    def test_psl_size_is_reasonable(self): 
        if skipping_PSL_comparison_tests() == True: 
            psl_files = [self.PSLfile] 
        else: 
            psl_files = [self.PSLfile, self.nextMonth_PSLfile] 
            
        for psl_file in psl_files: 
            size_in_bytes = os.stat(psl_file).st_size # filesize
            
            # Verify that the size of the PSL files is reasonable. 
            # (The size range generally grows a few Kilobytes per run) and 
            # is approximately 1055KB as at July 2013.
            self.assertTrue(size_in_bytes > 1055000)
    
    @unittest.skipIf(skipping_PSL_comparison_tests(), "Single PSL Validation only") 
    def test_psl_size_reduction(self):
        PSLfile_size_in_bytes = os.stat(self.PSLfile).st_size # filesize
        nextMonth_PSLfile_size_in_bytes = os.stat(self.nextMonth_PSLfile).st_size # filesize
        
        # +/-10% of the current PSL size is acceptable. 
        acceptable_size = float(PSLfile_size_in_bytes) * self.my_preferences.percent_changed_acceptable # 0.10
        
        warning_string_upper = "expected: " + str(float(PSLfile_size_in_bytes) + acceptable_size) + " bytes, calculated: " + str(nextMonth_PSLfile_size_in_bytes)
        warning_string_lower = "expected: " + str(float(PSLfile_size_in_bytes) - acceptable_size) + " bytes, calculated: " + str(nextMonth_PSLfile_size_in_bytes)
        
        # VS request: 10.	The reduction of size of the PSL file from its previous version is not highlighted / checked.
        self.assertTrue(nextMonth_PSLfile_size_in_bytes < (float(PSLfile_size_in_bytes) + acceptable_size), warning_string_upper) 
        self.assertTrue(nextMonth_PSLfile_size_in_bytes > (float(PSLfile_size_in_bytes) - acceptable_size), warning_string_lower)  
        
    
    def test_PSL_content_can_be_parsed(self):
        if skipping_PSL_comparison_tests() == True: 
            pslfile_list = [self.PSLfile] 
        else: 
            pslfile_list = [self.PSLfile, self.nextMonth_PSLfile] 
            
        for pslfile in pslfile_list: 
            # Check for PSL File Format by Instantiating an object of PSL type
            game_list = self.check_file_format(pslfile, 'PSL')

            for game in game_list:
                # Check for PSL manufacturer field
                self.assertTrue(self.check_manufacturer(game.manufacturer))

                # Check for PSL Game name field
                self.assertTrue(self.check_game_name(game.game_name))

                # Check for PSL year field
                self.assertTrue(self.check_year_field(game.year))
                
                # Check for PSL month field
                self.assertTrue(self.check_month_field(game.month))

                # Check Hash List size 
                self.assertTrue(self.check_hash_list_size(game.hash_list))
                
                # TODO: Check Hashlist for each day of the month, with the seed. 

            with open(pslfile) as f:
                psl_file_num_lines = len(f.readlines()) # read number of lines in text file
        
            self.assertTrue(len(game_list) == psl_file_num_lines) # Check the number of lines equal


    def test_Read_PSL_file_from_disk(self):
        self.assertTrue(os.path.isfile(self.PSLfile))
        
        if not skipping_PSL_comparison_tests():
            self.assertTrue(os.path.isfile(self.nextMonth_PSLfile))
    
    # Verify that valid MIDs have PSL entries. 
    def test_valid_MIDs_have_PSL_entries(self): 
        verified_manufacturer = list()
        pslfile_list = list() 
        
        if skipping_PSL_comparison_tests() == True: 
            pslfile_list = [self.PSLfile] 
        else: 
            pslfile_list = [self.PSLfile, self.nextMonth_PSLfile] 
        
        for pslfile in pslfile_list: 
            # Check for PSL File Format by Instantiating an object of PSL type
            game_list = self.check_file_format(pslfile, 'PSL')
            
            for game in game_list:
                if game.manufacturer in self.my_preferences.mid_list:
                    verified_manufacturer.append(game.manufacturer)
            
            sorted_verified_mid = list() # need to sort list in this way
            for mid in sorted(list(set(verified_manufacturer))): 
                sorted_verified_mid.append(mid)
            
            #if sorted_verified_mid.sort() == self.manufacturer_id_list.sort(): 
            #   print("verified_manufacturer.sort(): " + ",".join(sorted_verified_mid))
            #   print("self.manufacturer_id_list.sort(): " + ",".join(self.manufacturer_id_list))
            
            self.assertEqual(sorted_verified_mid, self.my_preferences.mid_list)
                  
    
    def test_date_field_in_PSL_entry_equals_date_field_in_filename(self): 
        pslfile_list = list() 
        if skipping_PSL_comparison_tests() == True: 
            pslfile_list = [self.PSLfile] 
        else: 
            pslfile_list = [self.PSLfile, self.nextMonth_PSLfile] 
            
        psl_field_month = ''
        psl_field_year = ''
        
        for pslfile in pslfile_list: 
            first_line = True # reset flag for each pslfile
            game_list = self.check_file_format(pslfile, 'PSL')
            
            for game in game_list: 
                if first_line: # first entry, save current year & month
                    psl_field_month = game.month
                    psl_field_year = game.year
                    first_line = False
                
                # validate the month/year field in each PSL entry are the same.
                self.assertEqual(game.month, psl_field_month)
                self.assertEqual(game.year, psl_field_year)

                # Check Month PSL field matches filename
                self.assertEqual(int(game.month), int(self.get_filename_month(pslfile)))
                
                # Check Year PSL field matches filename
                self.assertEqual(int(game.year), int(self.get_filename_year(pslfile)))
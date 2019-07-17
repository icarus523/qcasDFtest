import os
import unittest
import logging
import sys
from test_datafiles import QCASTestClient, PSLfile, skipping_PSL_comparison_tests

class test_PSLfile_content(QCASTestClient): 

    def test_psl_size_is_reasonable(self): 
        if self.verbose_mode: 
            logging.getLogger().info("Testing PSL file is reasonable")    
        
        if skipping_PSL_comparison_tests() == True: 
            psl_files = [self.my_preferences.data['PSLfile']] 
        else: 
            psl_files = [self.my_preferences.data['PSLfile'], self.my_preferences.data['nextMonth_PSLfile']] 
            
        for psl_file in psl_files: 
            size_in_bytes = os.stat(psl_file).st_size # filesize
            
            # Verify that the size of the PSL files is reasonable. 
            # (The size range generally grows a few Kilobytes per run) and 
            # is approximately 1055KB as at July 2013.
            err_msg = "PSL file size has unexpectedly decreased in size: < 1055KB"
            self.assertTrue(size_in_bytes > 1055000, msg=err_msg)
    
    @unittest.skipIf(skipping_PSL_comparison_tests(), "Single PSL Validation only") 
    def test_psl_size_reduction(self):
        if self.verbose_mode: 
            logging.getLogger().info("Testing PSL file size reduction is reasonable") 
            
        PSLfile_size_in_bytes = os.stat(self.my_preferences.data['PSLfile']).st_size # filesize
        nextMonth_PSLfile_size_in_bytes = os.stat(self.my_preferences.data['nextMonth_PSLfile']).st_size # filesize
        
        # +/-10% of the current PSL size is acceptable. 
        acceptable_size = float(PSLfile_size_in_bytes) * self.my_preferences.data['percent_changed_acceptable'] # 0.10
        logging.getLogger().info("Testing PSL files sizes +/- " + str(self.my_preferences.data['percent_changed_acceptable']*100) + "%")    

        warning_string_upper = "expected: " + str(float(PSLfile_size_in_bytes) + acceptable_size) + " bytes, calculated: " + str(nextMonth_PSLfile_size_in_bytes)
        warning_string_lower = "expected: " + str(float(PSLfile_size_in_bytes) - acceptable_size) + " bytes, calculated: " + str(nextMonth_PSLfile_size_in_bytes)
        
        # VS request: 10.	The reduction of size of the PSL file from its previous version is not highlighted / checked.
        self.assertTrue(nextMonth_PSLfile_size_in_bytes < (float(PSLfile_size_in_bytes) + acceptable_size), warning_string_upper) 
        self.assertTrue(nextMonth_PSLfile_size_in_bytes > (float(PSLfile_size_in_bytes) - acceptable_size), warning_string_lower)  
        
    
    def test_PSL_content_can_be_parsed(self):
        if skipping_PSL_comparison_tests() == True: 
            pslfile_list = [self.my_preferences.data['PSLfile']] 
        else: 
            pslfile_list = [self.my_preferences.data['PSLfile'], self.my_preferences.data['nextMonth_PSLfile']] 
        
        if self.verbose_mode: 
            logging.getLogger().info("Testing PSL files can be parsed: " + ",".join(pslfile_list))    
            
        for pslfile in pslfile_list: 
            # Check for PSL File Format by Instantiating an object of PSL type
            game_list = self.check_file_format(pslfile, 'PSL')

            for game in game_list:
                # Check for PSL manufacturer field
                err_msg = "PSL entry has invalid MID entry: " + str(game.manufacturer)
                self.assertTrue(self.check_manufacturer(game.manufacturer), msg=err_msg)

                # Check for PSL Game name field
                err_msg = "PSL entry has invalid gamename field: " + str(game.game_name)
                self.assertTrue(self.check_game_name(game.game_name), msg=err_msg)

                # Check for PSL year field
                err_msg = "PSL entry has invalid Year field: " + str(game.year)
                self.assertTrue(self.check_year_field(game.year))
                
                # Check for PSL month field
                err_msg = "PSL entry has invalid Month field: " + str(game.month)
                self.assertTrue(self.check_month_field(game.month), msg=err_msg)

                # Check Hash List size 
                err_msg = "PSL entry has invalid Hash size"
                self.assertTrue(self.check_hash_list_size(game.hash_list), msg=err_msg)
                
                # TODO: Check Hashlist for each day of the month, with the seed. 

            psl_file_num_lines = ''
            with open(pslfile) as f:
                psl_file_num_lines = len(f.readlines()) # read number of lines in text file
        
            err_msg = "Unexpected game list size difference: Check PSL files" 
            self.assertTrue(len(game_list) == psl_file_num_lines, msg=err_msg) # Check the number of lines equal


    def test_Read_PSL_file_from_disk(self):
        logging.getLogger().info("Testing PSL files read from disk")    

        self.assertTrue(os.path.isfile(self.my_preferences.data['PSLfile']))
        
        if not skipping_PSL_comparison_tests():
            self.assertTrue(os.path.isfile(self.my_preferences.data['nextMonth_PSLfile']))


    # Verify that valid MIDs have PSL entries. 
    def test_valid_MIDs_have_PSL_entries(self): 
        if self.verbose_mode: 
            logging.getLogger().info("Testing PSL files contains all expected MIDs")    
        
        verified_manufacturer = list()
        pslfile_list = list() 
        
        if skipping_PSL_comparison_tests() == True: 
            pslfile_list = [self.my_preferences.data['PSLfile']] 
        else: 
            pslfile_list = [self.my_preferences.data['PSLfile'], self.my_preferences.data['nextMonth_PSLfile']] 
        
        for pslfile in pslfile_list: 
            # Check for PSL File Format by Instantiating an object of PSL type
            game_list = self.check_file_format(pslfile, 'PSL')
            
            for game in game_list:
                if game.manufacturer in self.my_preferences.data['mid_list']:
                    verified_manufacturer.append(game.manufacturer)
            
            sorted_verified_mid = list() # need to sort list in this way
            for mid in sorted(list(set(verified_manufacturer))): 
                sorted_verified_mid.append(mid)
            
            #if sorted_verified_mid.sort() == self.manufacturer_id_list.sort(): 
            #   print("verified_manufacturer.sort(): " + ",".join(sorted_verified_mid))
            #   print("self.manufacturer_id_list.sort(): " + ",".join(self.manufacturer_id_list))
            
            err_msg = "Missing MID in PSL files. Check PSL file" 
            self.assertEqual(sorted_verified_mid, self.my_preferences.data['mid_list'], msg=err_msg)
                  
    
    def test_date_field_in_PSL_entry_equals_date_field_in_filename(self): 
        if self.verbose_mode: 
            logging.getLogger().info("Testing PSL Date Fields matches Filename Date")    
            
        pslfile_list = list() 
        if skipping_PSL_comparison_tests() == True: 
            pslfile_list = [self.my_preferences.data['PSLfile']] 
        else: 
            pslfile_list = [self.my_preferences.data['PSLfile'], self.my_preferences.data['nextMonth_PSLfile']] 
            
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
                self.assertEqual(game.month, psl_field_month, msg="Invalid PSL Months")
                self.assertEqual(game.year, psl_field_year, msg="Invalid PSL Year")

                # Check Month PSL field matches filename
                self.assertEqual(int(game.month), int(self.get_filename_month(pslfile)), msg="Invalid PSL Month")
                
                # Check Year PSL field matches filename
                self.assertEqual(int(game.year), int(self.get_filename_year(pslfile)), msg="Invalid PSL Year")
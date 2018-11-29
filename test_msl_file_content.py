import os
import csv
import logging
from test_datafiles import QCASTestClient, PSLfile, TSLfile, MSLfile, skipping_PSL_comparison_tests

class test_MSL_files(QCASTestClient):

    # Verify that the size of the MSL files is reasonable. 
    # (The size should not change and is 1KB)
    def test_MSL_size_is_reasonable(self): 
        if self.my_preferences.data['verbose_mode'] == "true": 
            logging.getLogger().info("Testing MSL file size remains reasonable (1KB)")    
        
        msl_files = list() 
        
        if skipping_PSL_comparison_tests():
            msl_files = [self.my_preferences.data['MSLfile']] 
        else:            
            msl_files = [self.my_preferences.data['MSLfile'], self.my_preferences.data['nextMonth_MSLfile']] 
        
        for msl_file in msl_files: 
            size_in_bytes = os.stat(msl_file)
        
            err_msg = "Unexpected MSL file size increase (>1KB)"
            self.assertTrue(size_in_bytes.st_size < 1024, msg=err_msg)

    # Verify the content of any MSL including that they refers to the correct month, year 
    # and contains seed data for each day
    def test_MSL_content_can_be_parsed(self): 
        if self.my_preferences.data['verbose_mode'] == "true": 
            logging.getLogger().info("Testing MSL content can be parsed")    
        
        msl_files = list() 
        msl_entry_object_list = list() 
        
        if skipping_PSL_comparison_tests(): 
            msl_files = [self.my_preferences.data['MSLfile']] 
        else:
            msl_files = [self.my_preferences.data['MSLfile'], self.my_preferences.data['nextMonth_MSLfile']] 

        for msl_file in msl_files: 
            msl_entry_object_list = self.check_file_format(msl_file, 'MSL') # Parse the file and validate MSL content
        
        err_msg = "Expected only one (1) entry for MSL file, got " + str(len(msl_entry_object_list))
        self.assertTrue(len(msl_entry_object_list) == 1, msg=err_msg) 

    # MSL file should always be one row
    def test_MSL_file_one_row(self):
        if self.my_preferences.data['verbose_mode'] == "true": 
            logging.getLogger().info("Testing MSL file only has one entry")    
    
        msl_files = list() 
        
        if skipping_PSL_comparison_tests(): 
            msl_files = [self.my_preferences.data['MSLfile']] 
        else:            
            msl_files = [self.my_preferences.data['MSLfile'], self.my_preferences.data['nextMonth_MSLfile']] 
        
        for msl_file in msl_files:
            with open(msl_file, 'r') as msl:
                err_msg = "Expected only one (1) entry for MSL file"                
                self.assertEqual(sum(1 for _ in msl), 1, msg=err_msg) # count the number of rows
                
    # General Test to make sure MSL files can be read from disk
    def test_Read_MSL_file_from_disk(self):
        if self.my_preferences.data['verbose_mode'] == "true": 
            logging.getLogger().info("Testing MSL files can be read from disk")    
        
        err_msg = "Cannot read MSL file, check paths to: " + self.my_preferences.data['MSLfile']
        self.assertTrue(os.path.isfile(self.my_preferences.data['MSLfile']), msg=err_msg)
        
        if not skipping_PSL_comparison_tests():
            err_msg = "Cannot read MSL file, check paths to: " + self.my_preferences.data['MSLfile']
            self.assertTrue(os.path.isfile(self.my_preferences.data['nextMonth_MSLfile']), msg=err_msg)
            
    def test_MSL_fields_sanity_checks(self):
        if self.my_preferences.data['verbose_mode'] == "true": 
            logging.getLogger().info("Testing MSL content passes sanity checks")    
        
        mslfile_list = list() 
        
        if skipping_PSL_comparison_tests():
            mslfile_list = [self.my_preferences.data['MSLfile']] 
        else:            
            mslfile_list = [self.my_preferences.data['MSLfile'], self.my_preferences.data['nextMonth_MSLfile']] 
            
        for mslfile in mslfile_list: 
            # Check for MSL file format
            msl_file_list = self.check_file_format(mslfile, 'MSL')

            # Test the year is this month's or next
            err_msg = "MSL Month field is incorrect"
            self.assertTrue(self.check_month_field(msl_file_list[0].month), msg=err_msg)

            # Test the year is this year's or next.
            err_msg = "MSL Year field is incorrect"
            self.assertTrue(self.check_year_field(msl_file_list[0].year), msg=err_msg)

            # Test the number of seeds equal 31
            err_msg = "Number of seeds is invalid"
            self.assertEqual(len(msl_file_list[0].seed_list), 31, msg=err_msg)


        
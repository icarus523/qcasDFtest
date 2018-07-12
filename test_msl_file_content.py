import os
import csv
from test_datafiles import QCASTestClient, PSLfile, TSLfile, MSLfile

class test_MSL_files(QCASTestClient):

    # Verify that the size of the MSL files is reasonable. 
    # (The size should not change and is 1KB)
    def test_MSL_size_is_reasonable(self): 
        msl_files = [self.MSLfile, self.nextMonth_MSLfile] 
        for msl_file in msl_files: 
            size_in_bytes = os.stat(msl_file)
        
        self.assertTrue(size_in_bytes.st_size < 1024)

    # Verify the content of any MSL including that they refers to the correct month, year 
    # and contains seed data for each day
    def test_MSL_content_can_be_parsed(self): 
        msl_files = [self.MSLfile, self.nextMonth_MSLfile] 
        for msl_file in msl_files: 
            msl_entry_object_list = self.check_file_format(msl_file, 'MSL') # Parse the file and validate MSL content
        
        self.assertTrue(len(msl_entry_object_list) == 1) # 1 Entry

    # MSL file should always be one row
    def test_MSL_file_one_row(self):
        msl_files = [self.MSLfile, self.nextMonth_MSLfile]
        for msl_file in msl_files:
            with open(msl_file, 'r') as msl:
                self.assertEqual(sum(1 for _ in msl), 1) # count the number of rows
                
    # General Test to make sure MSL files can be read from disk
    def test_Read_MSL_file_from_disk(self):
        self.assertTrue(os.path.isfile(self.MSLfile))
        self.assertTrue(os.path.isfile(self.nextMonth_MSLfile))

    def test_MSL_fields_sanity_checks(self):
        mslfile_list = [self.MSLfile, self.nextMonth_MSLfile]

        for mslfile in mslfile_list: 
            # Check for MSL file format
            msl_file_list = self.check_file_format(mslfile, 'MSL')

            # Test the year is this month's or next
            self.assertTrue(self.check_month_field(msl_file_list[0].month))

            # Test the year is this year's or next.
            self.assertTrue(self.check_year_field(msl_file_list[0].year))

            # Test the number of seeds equal 31
            self.assertEqual(len(msl_file_list[0].seed_list), 31)


        
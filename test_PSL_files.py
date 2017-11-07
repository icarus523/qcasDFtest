import os
import csv
from test_datafiles import QCASTestClient, PSLfile, TSLfile, MSLfile

class test_PSL_files(QCASTestClient):

    def test_PSL_size_is_reasonable(self): 
        psl_files = [self.PSLfile, self.nextMonth_PSLfile] 
        for psl_file in psl_files: 
            size_in_bytes = os.stat(psl_file)
            
            # Verify that the size of the PSL files is reasonable. 
            # (The size range generally grows a few Kilobytes per run) and 
            # is approximately 1055KB as at July 2013.
            self.assertTrue(size_in_bytes.st_size > 1055000)
    
    def test_PSL_content(self): 
        # Verify the content of each PSL entry: that they refer to the correct month, 
        # year and contains hash data for all manufactures. 
        # This can be done by ensuring all active Manufacturers have entries represented 
        # by their Machine ID, in the second column of the file. E.g AGT’s is ‘12’.
        psl_files = [self.PSLfile, self.nextMonth_PSLfile] 
        
        for psl_file in psl_files:        
            psl_entry_object_list = self.check_file_format(psl_file, 'PSL') # Parse the file and validate PSL content

            with open(psl_file) as f:
                psl_file_num_lines = len(f.readlines()) # read number of lines in text file
            
            self.assertTrue(len(psl_entry_object_list) == psl_file_num_lines) # Check the number of lines equal
            

import os
from test_datafiles import QCASTestClient, PSLfile

class test_general_file_format(QCASTestClient):
   
    def test_Read_TSL_file_from_disk(self):
        self.assertTrue(os.path.isfile(self.TSLfile))
        self.assertTrue(os.path.isfile(self.previous_TSLfile)) # this is mandatory even if your only checkling one month
        
    def test_TSL_content_can_be_parsed(self):
        # only one TSL file
        tslfile_list = self.check_file_format(self.TSLfile, 'TSL')

        for tsl_entry in tslfile_list:
            # Check for TSL manufacturer field
            self.assertTrue(self.check_manufacturer(str(tsl_entry.mid)))

            # Check SSAN is unique
            self.assertTrue(self.check_unique_field(tsl_entry.ssan, tslfile_list, flag='SSAN'))

            # Check BNK Type is valid
            self.assertTrue(self.check_valid_binimage_type(tsl_entry.bin_type))

            # Check BNK File name is unique
            # @unittest.skipIf(tsl_entry.binfile == '0101230', "Duplicate entry exist for this game")
            #self.assertTrue(self.check_unique_field(tsl_entry.bin_file, tslfile_list, flag='BIN_FILE'), 
            #    msg=tsl_entry.bin_file + " is not unique!")

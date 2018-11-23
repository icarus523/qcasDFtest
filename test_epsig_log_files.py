import os
import csv
import unittest
from test_datafiles import QCASTestClient, PSLfile, TSLfile, MSLfile, Preferences, skipping_PSL_comparison_tests
from datetime import datetime, date

NUMBER_OF_VALID_DAYS_SINCE_START_OF_LOG = 60
NUMBER_OF_VALID_DAYS_SINCE_END_OF_LOG = 60

VALID_EPSIG_VERSION = '3.5'
#LOG_FILE = "G:\\OLGR-TECHSERV\\MISC\\BINIMAGE\\qcas\\log\\epsig.log"
#LOG_FILE = "C:\\Users\\aceretjr\\Documents\\dev\\qcas-Datafiles-Unittest\\logs\\epsig.log"
#LOG_FILE = '/Users/james/Documents/dev/python/qcasDFtest/epsig.log'

class EpsigLogFile(): 

    def __init__(self, data):    
        assert(len(data) == 6) # this should be 5
    
        self.header = data[0] 
        self.version_number = self.header.split(' ')[2] # 3.5

        self.time_stamp_start_str = data[1]
        self.command_str = data[2]
        self.allocating_buffer = data[3]
        self.time_stamp_end = data[4]
        self.footer_status = data[5]                
        

    def is_complete(self): 
        if self.time_stamp_start_str.strip() and self.time_stamp_end.strip() and \
            self.footer_status == " with EXIT_SUCCESS": 
            
            return True
        else:
            return False
    
    def toString(self): 
        self.epsig_log_entry_str = "\n\n%(header)s\n%(time_stamp_start_str)s\n%(command_str)s\n%(allocating_buffer)s\n%(time_stamp_end)s\n%(footer_status)s" % \
            {   'header': self.header, 
                'version_number': str(self.version_number), 
                'time_stamp_start_str': self.time_stamp_start_str, 
                'command_str': self.command_str, 
                'allocating_buffer': self.allocating_buffer, 
                'time_stamp_end': self.time_stamp_end, 
                'footer_status' : self.footer_status
            }

        return self.epsig_log_entry_str.strip()


 
class test_epsig_log_files(QCASTestClient):

    def get_psl_file_from_cmd_str(self, s): 
        psl_file = s.split(' ')[5]
        self.assertTrue(psl_file.endswith(".psl")) 
        return psl_file
    
    def last_four_logs_success_exit(): 
        today = datetime.now()
        my_preferences = Preferences()
        last_four_logs_ok = False
        
        with open(my_preferences.epsig_log_file, 'r') as file: 
            epsig_log = file.read()
            paragraphs = epsig_log.split('\n\n')
            
            log_blocks = list() 
            
            # Get Last 4 paragraphs (end of file) with EXIT_SUCCESS
            for i in list(range(1,5)): 
                data = paragraphs[len(paragraphs)-i].split('\n') 
                data = list(filter(None, data)) # remove empty lists    
                log_entry = EpsigLogFile(data)
                log_blocks.append(log_entry)
                
            current_month_list = list() 
            next_month_list = list() 
            
            for log_file in log_blocks:
                if not log_file.is_complete(): 
                    last_four_logs_ok = False
                    break
                else: 
                    last_four_logs_ok = True
                        
        return last_four_logs_ok
    
    def test_Read_Epsig_log_file_from_disk(self):
        self.assertTrue(os.path.isfile(self.my_preferences.epsig_log_file), 
        	msg=self.my_preferences.epsig_log_file + ": File not found")
        
    @unittest.skipIf(skipping_PSL_comparison_tests() == True, "Single PSL Validation only") 
    # @unittest.skipIf(last_four_logs_success_exit() == False, "Skipping PSL version inc tests: Last 4 entries did not complete!")        
    def test_epsig_log_file_last_four_entries_are_valid_for_psl_versions(self): 
        # EPSIG.EXE Version 3.5 Copyright The State of Queensland 1999-2015
        # Started at   Fri Oct 06 08:41:37 2017
        # D:\OLGR-TECHSERV\MISC\BINIMAGE\qcas\epsigQCAS3_5.exe d:\OLGR-TECHSERV\BINIMAGE\*.* qcas_2017_11_v01.msl qcas_2017_10_v02.tsl qcas_2017_11_v02.psl 
        # Allocating buffer 262144 bytes
        # Finished at Mon Oct 09 13:18:15 2017
        # with EXIT_SUCCESS   

        today = datetime.now()

        with open(self.my_preferences.epsig_log_file, 'r') as file: 
            epsig_log = file.read()
            paragraphs = epsig_log.split('\n\n')
            
            log_blocks = list() 
            
            # Get Last 4 paragraphs (end of file) with EXIT_SUCCESS
            for i in list(range(1,5)): 
                data = paragraphs[len(paragraphs)-i].split('\n') 
                data = list(filter(None, data)) # remove empty lists    
                log_entry = EpsigLogFile(data)
                log_blocks.append(log_entry)
                
            # data = paragraphs[len(paragraphs)-1].split('\n') # get last paragraph from list. 

            #data = list(filter(None, data)) # remove empty lists            
            #log_file = EpsigLogFile(data)
            current_month_list = list() 
            next_month_list = list() 
            
            for log_file in log_blocks:
                # Verify EPSIG version number. 
                self.assertEqual(log_file.version_number, VALID_EPSIG_VERSION, 
                    msg="EPSIG version not equal to: " + VALID_EPSIG_VERSION)
                
                # The dates and start and finish time of processing appear reasonable
                # Valid Start Date: Assume within 7 days from current date
                time_stamp_start_obj = datetime.strptime(log_file.time_stamp_start_str[13:], "%a %b %d %H:%M:%S %Y")
                time_delta = today - time_stamp_start_obj
                self.assertTrue(time_delta.days < NUMBER_OF_VALID_DAYS_SINCE_START_OF_LOG, 
                    msg="Number of days since last epsig log started is greater than " + str(NUMBER_OF_VALID_DAYS_SINCE_START_OF_LOG)) # less than NUMBER_OF_VALID_DAYS_SINCE_START_OF_LOG days

                if log_file.is_complete(): 
                    time_stamp_end_obj = datetime.strptime(log_file.time_stamp_end[13:], "%a %b %d %H:%M:%S %Y")
                    time_delta = today - time_stamp_end_obj

                    self.assertTrue(time_delta.days < NUMBER_OF_VALID_DAYS_SINCE_START_OF_LOG, 
                        msg="Number of days since last epsig log started is greater than " + str(NUMBER_OF_VALID_DAYS_SINCE_START_OF_LOG)) # less than NUMBER_OF_VALID_DAYS_SINCE_START_OF_LOG days
                    
                    # The latest run Epsig error file is correct.(Ref WI01)      
                    self.assertEqual(log_file.footer_status, " with EXIT_SUCCESS", 
                        msg="Epsig Log file did not end with 'EXIT_SUCCESS")
                else: 
                    if self.my_preferences.verbose_mode == "true": 
                        print("#### WARNING: Entry in EPSIG log indicates it has not finished. ####")

                # Need to Verify PSL files used in the last 4 Entries are correct
                psl_files = list()
                psl_files.append(self.get_psl_file_from_cmd_str(log_file.command_str))
                for psl in psl_files: 
                    if len(current_month_list) == 0:  
                        current_month_list.append(psl) 
                    else: 
                        if current_month_list[0][10:12] == psl[10:12]: # month fields is the same
                            current_month_list.append(psl) 
                        else:
                            next_month_list.append(psl)
            
            # Sort to make sure that filenames are in order
            current_month_list.sort()
            next_month_list.sort()
            
            self.assertTrue(int(current_month_list[1][14:16]) == (int(current_month_list[0][14:16]) + 1), "Second PSL version is not incremented by 1")
            self.assertTrue(int(next_month_list[1][14:16]) == (int(next_month_list[0][14:16]) + 1), "Second PSL version is not incremented by 1")
    
    @unittest.skipIf(skipping_PSL_comparison_tests(), "Single PSL Validation only")     
    def test_epsig_log_file_last_two_entries_command_str_is_valid(self): 
        today = datetime.now()
        
        with open(self.my_preferences.epsig_log_file, 'r') as file: 
            epsig_log = file.read()
            paragraphs = epsig_log.split('\n\n')

            last_log_entry = paragraphs[len(paragraphs)-1].split('\n')              # get last paragraph from list. 
            second_last_log_entry = paragraphs[len(paragraphs)-2].split('\n')       # 2nd last
            
            logs = [last_log_entry, second_last_log_entry]
            for log in logs: 
                data = list(filter(None, log)) # remove empty lists    
                epsig_entry = EpsigLogFile(data)
                
                # Verify EPSIG version number. 
                self.assertEqual(epsig_entry.version_number, VALID_EPSIG_VERSION, 
                    msg="EPSIG version not equal to: " + VALID_EPSIG_VERSION)
                
                # The dates and start and finish time of processing appear reasonable
                # Valid Start Date: Assume within 7 days from current date
                time_stamp_start_obj = datetime.strptime(epsig_entry.time_stamp_start_str[13:], "%a %b %d %H:%M:%S %Y")
                time_delta = today - time_stamp_start_obj
                
                self.assertTrue(time_delta.days < NUMBER_OF_VALID_DAYS_SINCE_START_OF_LOG, 
                    msg="Number of days since last epsig log started is greater than " 
                        + str(NUMBER_OF_VALID_DAYS_SINCE_START_OF_LOG)) # less than NUMBER_OF_VALID_DAYS_SINCE_START_OF_LOG days
                    
                if epsig_entry.is_complete(): 
                    time_stamp_end_obj = datetime.strptime(epsig_entry.time_stamp_end[13:], "%a %b %d %H:%M:%S %Y")
                    time_delta_end = today - time_stamp_end_obj
                    
                    self.assertTrue(time_delta_end.days < NUMBER_OF_VALID_DAYS_SINCE_END_OF_LOG, 
                        msg="Number of days since last epsig log ended is greater than " 
                            + str(NUMBER_OF_VALID_DAYS_SINCE_END_OF_LOG))

                    
                    # The latest run Epsig error file is correct.(Ref WI01)      
                    self.assertEqual(epsig_entry.footer_status, " with EXIT_SUCCESS", 
                            msg="Epsig Log file did not end with 'EXIT_SUCCESS")
                
                self.assertTrue(epsig_entry.is_complete())

                # Ensure that the parameters of the epsig.exe call appear correct, ...         
                self.verify_epsig_command_used(epsig_entry.command_str)
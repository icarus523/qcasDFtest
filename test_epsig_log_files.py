import os
import csv
from test_datafiles import QCASTestClient, PSLfile, TSLfile, MSLfile
from datetime import datetime, date

NUMBER_OF_VALID_DAYS_SINCE_START_OF_LOG = 60
VALID_EPSIG_VERSION = '3.5'
#LOG_FILE = "G:\\OLGR-TECHSERV\\MISC\\BINIMAGE\\qcas\\log\\epsig.log"
#LOG_FILE = "C:\\Users\\aceretjr\\Documents\\dev\\qcas-Datafiles-Unittest\\logs\\epsig.log"
#LOG_FILE = '/Users/james/Documents/dev/python/qcasDFtest/epsig.log'

class EpsigLogFile(): 
    def __init__(self, data): 
        self.header = data[0] 
        self.version_number = self.header.split(' ')[2]
        
        self.time_stamp_start_str = data[1]
        self.command = data[2]
        self.allocating_buffer = data[3]
        self.time_stamp_end = data[4]
        self.footer_status = data[5]                

        assert(len(data) == 6) # this should be 5

class test_epsig_log_files(QCASTestClient):

    def test_log_file_exist(self):
        self.assertTrue(os.path.isfile(self.my_preferences.epsig_log_file))

    def test_Epsig_Log_file(self): 
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
        
            data = paragraphs[len(paragraphs)-1].split('\n') # get last paragraph from list. 
            data = list(filter(None, data)) # remove empty lists            
            log_file = EpsigLogFile(data)
            
            # Verify EPSIG version number. 
            self.assertEqual(log_file.version_number, VALID_EPSIG_VERSION)
            
            # The dates and start and finish time of processing appear reasonable
            # Valid Start Date: Assume within 7 days from current date
            time_stamp_start_obj = datetime.strptime(log_file.time_stamp_start_str[13:], "%a %b %d %H:%M:%S %Y")
            time_delta = today - time_stamp_start_obj
            print("Number of days since last epsig log started: " + str(time_delta.days))
            self.assertTrue(time_delta.days < NUMBER_OF_VALID_DAYS_SINCE_START_OF_LOG) # less than NUMBER_OF_VALID_DAYS_SINCE_START_OF_LOG days

            if len(data) > 4: 
                time_stamp_end_obj = datetime.strptime(log_file.time_stamp_end[13:], "%a %b %d %H:%M:%S %Y")
                time_delta = today - time_stamp_end_obj
                print("Number of days since last epsig log ended: " + str(time_delta.days))
                self.assertTrue(time_delta.days < NUMBER_OF_VALID_DAYS_SINCE_START_OF_LOG) # less than NUMBER_OF_VALID_DAYS_SINCE_START_OF_LOG days
                
                # The latest run Epsig error file is correct.(Ref WI01)      
                self.assertEqual(log_file.footer_status, " with EXIT_SUCCESS")
            else: 
                print("#### WARNING: Last entry in EPSIG log indicates it has not finished. ####")
                
            # Ensure that the parameters of the epsig.exe call appear correct, ...         
            self.verify_epsig_command_used(log_file.command)
        

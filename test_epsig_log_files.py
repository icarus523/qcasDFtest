import os
import csv
from test_datafiles import QCASTestClient, PSLfile, TSLfile, MSLfile

class test_epsig_log_files(QCASTestClient):

    def test_Epsig_Log_file(self): 
            #log_file = "G:\\OLGR-TECHSERV\\MISC\\BINIMAGE\\qcas\\log\\epsig.log"
            # log_file = "C:\\Users\\aceretjr\\Documents\\dev\\qcas-Datafiles-Unittest\\logs\\epsig.log"
            log_file = '/Users/james/Documents/dev/python/qcasDFtest/epsig.log'
            
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
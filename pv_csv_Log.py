#!/usr/bin/python

# ------------------------------------------------
# Persistence of vision log writer
# John Watson  4/1/2017
# ------------------------------------------------

import time
import os.path
import csv

experimentdesignation = "No designation"

subjectname  = "No subject"
imagetopaint = "No image"
ratemode = "Slice by slice"
framerate = 0
result = "no result"

logfile = "/media/usb/pv_log.csv"

def instance(Experimentdesignation,Subjectname,Imagetopaint,Ratemode,Framerate):
    global experimentdesignation,subjectname,imagetopaint,ratemode,framerate
    
    experimentdesignation = Experimentdesignation
    subjectname = Subjectname
    imagetopaint = Imagetopaint
    ratemode = Ratemode
    framerate = Framerate 

def instanceresult(Result):
    global result
    
    result = Result
    writelog()

def writelog():
    if os.path.isfile(logfile):
        f = open(logfile,"a")
        writelogline(f)
    else:
        f = open(logfile,"a")
        writeloghead(f)
        writelogline(f)
    f.close

def writeloghead(f):
    writer = csv.writer(f,quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(('Experiment','Date','Subject','Image','Mode','Rate','Result'))


def writelogline(f):
    dt = time.localtime(time.time())
    dateandtime = '%d/%d/%d %d:%d:%d' % (dt[2], dt[1], dt[0], dt[3], dt[4],dt[5])

    writer = csv.writer(f,quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow((experimentdesignation,dateandtime,subjectname,imagetopaint,ratemode,framerate,result))
        


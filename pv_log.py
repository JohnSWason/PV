#!/usr/bin/python

# ------------------------------------------------
# Persistence of vision GPIO button
# John Watson  4/1/2017
# ------------------------------------------------

import time
import os.path


#logfile = "pv_log.txt"
logfile = "/media/usb/pv_log.txt"

if os.path.isfile(logfile):
    logexists = 1
else:
    logexists = 0


def logstart(ilogfile,Experimentdesignation):
    global logfile

    logfile = ilogfile

    print "log exists ", logexists
    if logexists == 0:
        f = open(logfile,"a+")
        DOSwrite(f,"Persistence of Vision experiment log\n")
        DOSwrite(f,"Note: Unless the PI is connected to the internet and has set its internal clock,\n")
        DOSwrite(f,"the date and time will be relative to some random value of time set when the pi booted.\n\n")
    else:
        f = open(logfile,"a")

    print "Persistence of Vision experiment starting ", time.asctime(time.localtime(time.time()))

    DOSwrite(f,"\n\nPersistence of Vision experiment starting %s\n" % time.asctime( time.localtime(time.time())) ) 
    DOSwrite(f,"Experiment designation %s\n" % Experimentdesignation)
    f.close

def logfiles(cnt,files):
    f = open(logfile,"a+")
    DOSwrite(f,"\tFound %i files \n" % cnt)
    for fi in files:
        DOSwrite(f,"\t%s \n" % fi)
    f.close

def logpaint(delay, speed,imagetopaint, Experimentdesignation, Subjectname, RateMode):
    f = open(logfile,"a+")
    f.write("\n\tPainting:")
    f.write("\n\tExperiment:\t%s"  % Experimentdesignation)
    f.write("\n\tTime:\t\t%s"  % str(time.asctime(time.localtime(time.time()))))
    f.write("\n\tSubject:\t%s" % Subjectname)
    f.write("\n\tImage:\t\t%s" % imagetopaint)
    f.write("\n\tRate mode:\t%s" % RateMode)
    f.write("\n\tSpeed:\t\t%s" % speed)
    #DOSwrite(f,"\n\n\tPainting\n"  + "\tTime \t" + str(time.asctime(time.localtime(time.time()))) + "\n\tImage\t" + str(name) + "\n\tspeed\t" + str(speed))
    # print "\tPainting\n"  + "\tTime \t" + str(time.asctime(time.localtime(time.time()))) + "\n\tImage\t" + str(name) + "\n\tspeed\t" + str(speed)
    f.close
    
    print("\tExperiment:\t%s"  % Experimentdesignation)
    print("\tTime:\t\t%s"  % str(time.asctime(time.localtime(time.time()))))
    print("\tSubject:\t%s" % Subjectname)
    print("\tImage:\t\t%s" % imagetopaint)
    print("\tRate mode:\t%s" % RateMode)
    print("\tSpeed:\t\t%s" % speed)    
    
def logresult(result):
    f = open(logfile,"a+")
    f.write("\n\tResult:\t\t%s"  % result)
    f.close

def DOSwrite(f, text):
    t2 = text.replace('\n', '\n')
    #t2 = text.replace('\n', '\r\n')
    f.write(t2)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#title           : pv_menu.py
#description     : display an interactive menu of images
#author          : John Watson
#date            : 8/2/2017
#version         : 0.1
#usage           : import pv_menu
#notes           : call pv_menu_initialise to create the menu at any
#                : time the image list changes
#                : call pv_menu_show to when ready to show an image
#                :  use call: speed, imagename = pv_menu_show(imagenames)
#python_version  :
#=======================================================================

# Import the modules needed to run the script.
import sys, os, termios, fcntl
import strandtest

imagenames = ()
delay = 0.0005      # the delay to slow down the paint speed
topspeed = 1000     # the maximum speed entry gives a range 0 to 1000. 1000 = maximum speed, zero = slowest speed
maxdelay = .001     # The maximum amount of delay. The slowest possible paint aspeed
selectedspeed = 0   # User selected framerate
Experimentdesignation = "No designation"
Subjectname = "No subject"
RateMode = "Slice by slice"          # default rate mode is slice by slice

# =======================
#     MENUS FUNCTIONS
# =======================
# Call this function to initialise the menu
def pv_menu_initialise(ispeed, iimagenames, experimentdesignation):
    global selectedspeed, imagenames, Experimentdesignation

    selectedspeed = ispeed
    imagenames = iimagenames
    Experimentdesignation = experimentdesignation

# Call this function to show the menu
# returns a speed and a imagenames index
def pv_menu_show():
    global selectedspeed, Subjectname, RateMode

    print_menu(selectedspeed, False)

    while True:  
#        choice = raw_input("Select option: ")    ## Get first choice
        print 'Select >>> ',
        choice = myGetch()                       ## Dont have to press enter

        if choice=='1':
            os.system('clear')
            return delay,selectedspeed, 0, Experimentdesignation, Subjectname, RateMode
        elif choice=='2':
            os.system('clear')
            return delay, selectedspeed, 1, Experimentdesignation, Subjectname, RateMode
        elif choice=='3':
            os.system('clear')
            return delay, selectedspeed, 2, Experimentdesignation, Subjectname, RateMode
        elif choice=='4':
            os.system('clear')
            return delay, selectedspeed, 3, Experimentdesignation, Subjectname, RateMode
        elif choice=='5':
            os.system('clear')
            return delay, selectedspeed, 4, Experimentdesignation, Subjectname, RateMode
        elif choice=='6':
            os.system('clear')
            return delay, selectedspeed, 5, Experimentdesignation, Subjectname, RateMode
        elif choice.lower()=='s':
            subjectname = raw_input('Subject name: ')
            Subjectname = subjectname
            print_menu(selectedspeed, False)
        elif choice.lower()=='r':
            if RateMode == 'Slice by slice':
                RateMode = "Whole image"
            else:
                RateMode = 'Slice by slice'
            print_menu(selectedspeed, False)
        elif choice.lower()=='f':
            selectedspeed = setspeed()
        elif choice.lower()=='t':
            strandtest.runtest()
            print_menu(selectedspeed, False)
        elif choice.lower()=='q':
            os.system('clear')
            print 'By from Pi  Persistence of Vision'
            sys.exit(1)
        elif choice.lower()=='o':
            os.system('clear')
            os.system("shutdown -h now")
        else:
            print_menu(selectedspeed, True)

def setspeed():
    global delay

    os.system('clear')
    print 27 * "-" , "Persistence of Vision" , 27 * "-"
    while True:
        Selected = raw_input("\tSpeed (0-1000) >> ")
        if Selected.isdigit():
            if int(Selected) <= topspeed: 
                delay = maxdelay*(1-(int(Selected)/topspeed))
                print_menu(Selected,False)
                return int(Selected)

def exit():
    sys.exit()
    
def print_menu(speed, invalidmessage = False):    
    os.system('clear')
    
    imagecount = len(imagenames)
    
    print("Python %s.%s.%s" % sys.version_info[:3])

    print 27 * "-" , "Persistence of Vision" , 27 * "-"
    print 'Experiment designation:',Experimentdesignation

    if imagecount >= 7:
        print "Number of allowed images exeeded", imagecount - 6, "images not shown"
        
    if invalidmessage:
        print "Invalid option selected. Try again:"
    #    elif:
    #    print "Select option:"
    
    if imagecount >= 1:
        print "\t1. Show", imagenames[0]
    if imagecount >= 2:
        print "\t2. Show", imagenames[1]
    if imagecount >= 3:
        print "\t3. Show", imagenames[2]
    if imagecount >= 4:
        print "\t4. Show", imagenames[3]
    if imagecount >= 5:
        print "\t5. Show", imagenames[4]
    if imagecount >= 6:
        print "\t6. Show", imagenames[5]

    print ''
    print "\tS. Subject name, currently =", Subjectname
    print "\tF. Frame rate, currently =", speed
    print "\tR. Rate mode, currently =", RateMode
    print "\tT. Test connected strip of LEDs"
    print "\tQ. Quit"
    print "\tO. Turn of the Pi"
    print 76 * "-"


# Get a charcter from the keyboard
def myGetch():
    fd = sys.stdin.fileno()
    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)

    oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)


    try:        
        while 1:
            try:
                c = sys.stdin.read(1)
                break
            except IOError: pass
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)

    return c



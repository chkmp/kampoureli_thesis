#!/usr/bin/python
# -*- coding: UTF-8 -*-


import os
import pydicom
import glob
import shutil
import time
from datetime import datetime, date
import subprocess
from pathlib import Path

# NOTE: run this sript from admin terminal

# f1 - return path to source directory
# where all the incoming DICOMs are arriving to
def getsourcedir():
    # user input CISC number and have script grab data to reconstruct this path
    ciscnumber = input("Enter the participant's CISC number (e.g. CISC2171)\n")
    ciscnumber = ciscnumber.strip(" ").upper()
    date = time.strftime("%Y%m%d")  # get date with no delimiter for directory name
    # Reconstruct source directory name using ciscnumber and date
    sourcedir = f"/mnt/d/RTMRI/{date}.{ciscnumber}.{ciscnumber}"#alex-rename this to /mnt/d/RTMRI/ instead of c
    if os.path.exists(sourcedir) == True:  # SANITY check the source dir exists
        return sourcedir, ciscnumber
    else:
        print("Source directory doesn't exist:", sourcedir)



# f2 - ask user for the required target directory and return the path
def whichtargetdir(sourcedir):
    targets = ["RAI","CLEAN"]
    print("Available targets: \n", targets)
    target = input("Which target directory do you require?\n")
    target = target.strip(" ").upper()
    if target not in targets:
        print("Target you entered is not in list. Try again.")
        return

    else: 
        targetpath = os.path.join(sourcedir, 'nf_attention', target ) 
        print('TARGETPATH', targetpath)
        if os.path.exists(targetpath) == False:
            os.mkdir(targetpath)
            print("Target path OK:", targetpath)
            return targetpath
        if os.path.exists(targetpath) == True:
            return targetpath




def movedicom(src, dest):
    """
    Funtion to move files from source to destination, with error handling
    """
    
    # NOTE : DIOMS are 1,907kb
    go = True # allows the while loop to run 
    chmod = False # Change to true once permissions have been liberalized on file

    attempt = 0 

    #print("Attempting to move:", src, "\nto:", dest)
    incident = f"Attempting to move: {src} \nto: {dest}"
    #writetofileoutfile, incident)

    
    while go: # try to copy file infinitely - may need to account for a situation where this needs to be skipped 
        try:
            shutil.move(src, dest)
            #print("Success!\n")
            #writetofileoutfile, "Success!")
            go = False # break out the while loop, and therefore function
        except PermissionError:
            print("PermissionError raised when attempting to move:", src)
            #writetofileoutfile, str("PermissionError raised when attempting to move:", src))
            attempt += 1 # log the number of attempts 
            print("Attempt number #{}".format(attempt))
            #writetofileoutfile, str("Attempt number #{}".format(attempt)))

def path_for_nifti(targetpath):
    """
    Convert DICOMs to NIFTIs. Only when Ctrl+c is pressed.
    """
    #writetofileoutfile, f"Converting NIFTIs in {targetpath}")

    niftibase = os.path.split(targetpath)[0]
    print('NIFTIBASE', niftibase)
    niftipath = os.path.join(niftibase, 'nifti')
    print('NIFTIPATH', niftipath)
    print('TARGETPATH', targetpath)

    if os.path.exists(niftipath) == False:
            os.mkdir(niftipath)
            print("niftipath OK:", niftipath)
            return niftipath
    elif os.path.exists(niftipath) == True:
            return niftipath   

    '''print('TARGETPATHHH', targetpath)
    subprocess.run(["dcm2niix", targetpath], capture_output=True)
    
    print("\nDICOMs converted. Check inside:", targetpath)
    return
    '''
def dcm_to_nifti(targetpath, niftipath):

    target = os.path.split(targetpath)[1]
    if target == "RAI":
        subprocess.run(["dcm2niix","-o", niftipath, targetpath], capture_output=True)
        
        print("\nDICOMs converted. Check inside:", niftipath)
        return

# f3 - Reading the headers of all DICOMS in source directory
def readheaders(sourcedir,ciscnumber, targetpath, waittime):
    #outfile = initcsv(targetdir) # initialize csv
    target = os.path.split(targetpath)[1]
    print(target)
    RUNLIST = ["RUN01", "RUN02", "RUN03", "RUN04", "RUN05", "RUN06"]

    while True:  # Infinetely looop
        try:
            alldcms = [ f for f in os.listdir(sourcedir) if f.endswith(".dcm") ]  # grab list of all dicoms in source directory
            if len(alldcms) == 0:
                incident = 'No files arrived with the .dcm extension. Waiting for {}s'.format(waittime)
                print(incident)
                #writetofileoutfile, incident)
                time.sleep(waittime)  # in case no new files have arrived

            else:
                for f in alldcms:
                    fullf = os.path.join(sourcedir, f)
                    #print('Before reading DICOM header, checking file size stability of:', f)
                    

                    dcm = pydicom.dcmread(os.path.join(sourcedir, f))
                    sd = dcm.SeriesDescription
                    it = dcm.ImageType
                    inn = dcm.InstanceNumber
                

                    #print(sd)
                    print(it)
                    print(inn)

                    
                    shortf = f #removed renaming 16.05
                   
                    
                    DICOMLIST= ["RUN01" , "RUN02", "RUN03", "RUN04"]

                    if target == "RAI":
                        if sd == 'MPRAGE':
                            src = fullf
                            dest = os.path.join(targetpath, shortf)  # Join to make full path so identically named files are overwritten, thus avoiding error
                            movedicom(src, dest)
                            dicomnumber=str(inn).zfill(6)
                            #print(dicomnumber)
                            dicom_chopped= shortf[:-10]
                            print('dicom_chopped', dicom_chopped)
                            dicom_new = os.path.join(targetpath, ciscnumber+ '_' + dicom_chopped + dicomnumber +'.dcm')  
                            print('dicom_new', dicom_new)
                            print('fullf',dest)
                            os.rename(dest, dicom_new)
                            #need to remove the conversion for this to work

                    elif target == "CLEAN":
                        if sd not in DICOMLIST:
                            src = fullf
                            dest = os.path.join(targetpath, shortf)
                            movedicom(src, dest)         

        except KeyboardInterrupt:  # I.E. press control-C
            # print(os.listdir(targetdir))
            if target == "RAI" :

                # Only do this next block if 208 files 
                # If 208 files hav been moves, length of alldcms_new should be 208 
                alldcms_new = sorted([ f for f in os.listdir(targetpath) if f.endswith(".dcm") ])

                
                for f, i in zip(alldcms_new, range(len(alldcms_new))):  
                    #print('f', f)
                    fullf = os.path.join(targetpath, f)
                    print(fullf)
                    
                    number= int(i)+1  
                    dicomnumber = str(number).zfill(4)  
                    dicom_chopped= f[:-8]  
                    dicom_renamed = os.path.join(dicom_chopped + dicomnumber +'.dcm')  
                    #print('dicom_renamed',dicom_renamed)
                    
                
                    ciscnumber= dicom_renamed.split("_")[0]
                    #print('ciscnumber', ciscnumber)
                    
                    session = dicom_renamed.split("_")[1]
                    session = str(session).zfill(4)
                    scanning = dicom_renamed.split("_")[2]
                    scanning= scanning[-4:]
                    dicom_number = dicom_renamed.split("_")[3]
                    dicom_number= dicom_number[-8:]
                    dicom_renamed_tbv = os.path.join(targetpath, ciscnumber+' -' + scanning + '-' + session + '-' + dicom_number)
                    print('dest',dicom_renamed_tbv)
            
                    print('source',fullf)
                    
                    os.rename(fullf, dicom_renamed_tbv)

                    


                    
                    
                    
                break
            else:  # if target is not rai or rfi, don't need to convert to nifti
                break
               


########################## Set Time Parameters ##########################


waittime = 0.1 # Set time to wait while no files with .dcm extension are found 

########################## RUN ##########################

sourcedir, ciscnumber = getsourcedir()
#studydir = studydir(sourcedir)
targetdir = whichtargetdir(sourcedir)
readheaders(sourcedir, ciscnumber, targetdir, waittime)
niftidir= path_for_nifti(targetdir)
dcm_to_nifti(targetdir, niftidir)

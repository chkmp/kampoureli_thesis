
#!/usr/bin/python

from psychopy import visual, monitors, core, event, gui
from psychopy.hardware import keyboard
from datetime import datetime
from csv import DictWriter
import os 
import glob
import pandas as pd #for importing the MW questions
import pyglet

"""
Script generate thought-probes at the end of resting state block and record responses
Instructions -> Fixation cross -> ESQs -> Fixation Cross -> ESQs 
"""

######GUI##########################################################

# Create a dialog box to collect participant information
dlg = gui.Dlg(title="Participant Information")
dlg.addField('subject')
dlg.addField('session', choices=['1', '2', '3', '4'])
dlg.addField('run', choices=['1', '2', '3', '4'])
dlg.addField('group', choices=['male-indoor', 'male-outdoor', 'female-indoor', 'female-outdoor'])

participant_info = dlg.show()

# convert participant_info[0] to an integer
sub_num_int = int(participant_info[0])
sub_ses_int = int(participant_info[1])
sub_run_int = int(participant_info[2])
# format the integer as a zero-padded two-digit string
sub_num = f"sub-{sub_num_int:02d}"
ses_num = f"ses-{sub_ses_int:02d}"
run_num = f"run-{sub_run_int:02d}"
# If the user clicks "Cancel", exit the script
if not dlg.OK:
    core.quit()

# Extract participant info from dictionary
subject = participant_info[0]
session = participant_info[1]
run = participant_info[2]
group = participant_info[3]


def repopath():
    """Get path to repository"""
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def init_csv(outputpath):
    """
    Initialize csv file
    """
    header = str('question_number' + ',' + 'block' + ','
    + 'dimension' + ',' + 'response' + ',' + 'rt_clock' + ',' + 'global_clock' + ',' + 'real_time')

    with open(outputpath, 'w') as f:
        f.write(header)
        f.write('\n')


def thought_probe(df, outfilepath, globalclock, blockname):
    """
    Input: Experience sampling dataframe
    Present thought probes seqentially with a sliding response scale.
    Responses should be returned and passed to _csv_writer 
    """
    lKey= 'r'
    rKey = 'y'
    mKey = 'b'

    # create rating scale for user to rate thought probes.
    ratingScale = visual.RatingScale(win, low=0, high=10, markerStart=5.0,precision=10, 
    leftKeys=lKey, rightKeys=rKey, acceptKeys=mKey, scale = None, labels = None, acceptPreText = 'Press key', tickMarks = [1,10])

    # create text stimulus for thought probe presentation. 
    QuestionText = visual.TextStim(win, color = [-1,-1,-1], alignHoriz = 'center', alignVert= 'top', pos =(0.0, 0.3))
    # create text stimuli for low and high scale responses. 
    Scale_low = visual.TextStim(win, pos= (-0.5,-0.5), color ='black')
    Scale_high = visual.TextStim(win, pos =(0.6, -0.5), color ='black')

    # shuffle dataframe rows to randomly present questions
    df = df.sample(frac=1)

    # Loop through each question 
    for idx in range(len(df)):
        # Save time 
        rtclock = core.Clock()
        firsttime = rtclock.getTime()

        # extract relevent question information
        dimension = df.loc[idx].dimension
        question = df.loc[idx].question
        scale_low = df.loc[idx].scale_low
        scale_high = df.loc[idx].scale_high

        ratingScale.noResponse = True

        # section for keyboard handling. 
        key = pyglet.window.key
        keyState = key.KeyStateHandler()
        win.winHandle.activate() # to resolve mouse click issue. 
        win.winHandle.push_handlers(keyState)
        pos = ratingScale.markerStart
        inc = 0.1 
  
        # while there is no response from user, present thought probe and scale.
        while ratingScale.noResponse:

            # use 1 and 2 keys to move left and right along scale. 
            if keyState[key.R] is True: # Here is where you can change the key mappings - needs to be uppercase to work 
                pos -= inc
            elif keyState[key.Y] is True:
                pos += inc
            if pos > 10: 
                pos = 10
            elif pos < 1:
                pos = 1
            ratingScale.setMarkerPos(pos)


            # set text of probe and responses 
            QuestionText.setText(question)
            Scale_low.setText(scale_low)
            Scale_high.setText(scale_high)

            # draw text stimuli and rating scale
            QuestionText.draw()
            ratingScale.draw() 
            Scale_low.draw()
            Scale_high.draw()

            # store response using getRating function
            response = ratingScale.getRating()
            win.flip()

        # reset marker to middle of scale each time probe is presented. 
        ratingScale.setMarkerPos((0.5))
        
        # for each probe, write to row 
        # call _csv_writer
        resptime = rtclock.getTime() # get time once repsonse entered
        _csv_writer(outfilepath, dimension, response, globalclock, blockname, trialnum=idx, rt_clock=resptime)
         # reset clock 


def _csv_writer(outfilepath, dimension, response, globalclock, blockname, trialnum,  rt_clock):
    """Function to append to csv file with response"""

    RealTime = str(datetime.now().time())[:-3] # remove the last three digits to match the format of the Graphic Update Printed time

    # line to write
    writeline = str(f"{trialnum}, {blockname}, {dimension}, {response}, {rt_clock}, {globalclock.getTime()}, {RealTime}\n")
    with open(outfilepath, 'a') as f:
        f.write(writeline)

def task_esq_instructions():
    # List of instructions
    # Each entry in list corresponds to a seperate slide 
    # TODO: Adapt to button box
    instruction_list = ["You will now be asked to rate several statements about the ongoing thoughts you experienced during the previous neurofeedback block. \nPress THE MIDDLE BUTTON to continue.",
    "To rate these statements, hold THE LEFT MOST BUTTON to move the marker left along the slider and hold THE RIGHT MOST BUTTON to move the marker right along the slider.\n\nWhen you are happy with your selection, please press THE MIDDLE BUTTON to move on to the next statement."
    ,"Press THE MIDDLE BUTTON to start."]

    # Loop over instructions list, presenting each string as a seperate slide
    for idx,message in enumerate(instruction_list):
        idx = idx+1
        instruct = visual.TextStim(win, message, color = (1.0, 1.0, 1.0))
        instruct.draw()
        win.flip()
        if idx == len(instruction_list): # if last instruction slide, require '1' press to start the experiment 
            event.waitKeys(keyList=['b'])
        else:
            event.waitKeys()

def rest_esq_instructions():
    # List of instructions
    # Each entry in list corresponds to a seperate slide 
    # TODO: Adapt to button box
    instruction_list = ["You will now be asked to rate several statements about the ongoing thoughts you experienced during the previous scan. \n\nPress the middle button to move on.",
    "To rate these statements, hold the left button to move the marker left along the slider and hold the right button to move the marker right along the slider.\n\nWhen you are happy with your selection, please press the middle button to move on to the next statement. \n\nPress the middle button to start."]

    # Loop over instructions list, presenting each string as a seperate slide
    for idx,message in enumerate(instruction_list):
        idx = idx+1
        instruct = visual.TextStim(win, message, color = (1.0, 1.0, 1.0))
        instruct.draw()
        win.flip()
        if idx == len(instruction_list): # if last instruction slide, require '1' press to start the experiment 
            event.waitKeys(keyList=['b'])
        else:
            event.waitKeys()

def rest_instructions():
    # List of instructions
    # Each entry in list corresponds to a seperate slide 
    # TODO: Adapt to button box
    instruction_list = ["During the next scan, look at the cross on the screen and think of nothing in particular. Please try move as little as possible.\n\nPress the middle button if you are ready.",
    "The scan will begin shortly."]

    # Loop over instructions list, presenting each string as a seperate slide
    for idx,message in enumerate(instruction_list):
        idx = idx+1
        instruct = visual.TextStim(win, message, color = (1.0, 1.0, 1.0))
        instruct.draw()
        win.flip()
        if idx == len(instruction_list): # if last instruction slide, require 'return' press to start the experiment 
            event.waitKeys(keyList=['return'])
        else:
            event.waitKeys()

def fixation():
    """
    Present fixation cross
    """
    cross = visual.TextStim(win, pos= (0,0), color ='black')
    cross.setText('+')
    cross.draw()
    win.flip()
    

    ExperimenterKeys = ['return']

    event.waitKeys(keyList = ExperimenterKeys)

    return
    

def endscreen():
    endtext = visual.TextStim(win, pos= (0,0), color ='white')
    endtext.setText('Thank you for your attention.\n Hang tight and someone will come get you!')
    endtext.draw()
    win.flip()

    ExperimenterKeys = ['return']

    event.waitKeys(keyList = ExperimenterKeys)
    
    return


################################ - GLOBAL PARAMETERS - ################################ 

mon = monitors.Monitor('myMonitor', width=35.56, distance=60)
mon.setSizePix([1600,900])
win = visual.Window(monitor=mon, fullscr =True) #define a window
my_image = visual.ImageStim(win)

################################ - RUN - ################################ 

# NOTE: r = LEFT, n = right, b = middle/accept 
# TODO Shuffle questions

path_to_repo = repopath() # Necessary for reading ESQs (stored in scratch/source)
beh_path =  os.path.join(path_to_repo,"data", "responses", f"{sub_num}", f"{ses_num}")
if not os.path.isdir(beh_path):
    os.makedirs(beh_path)
filename = f"{sub_num}_{ses_num}_{run_num}_{participant_info[3]}_rs_probs.csv"
outputpath = os.path.join(beh_path, filename)

globalclock = core.Clock() # start global stop watch 

esqs = os.path.join(path_to_repo, "data", "esqs")
esqname = '14_item_experience_sampling_questions_final.csv'
full_esq_path = os.path.join(esqs, esqname)
df = pd.read_csv(full_esq_path, nrows=14)
init_csv(outputpath)

#task_esq_instructions() 

#thought_probe(df, outputpath, globalclock, blockname='1')

rest_instructions()

fixation() 

rest_esq_instructions() 

df = df.sample(frac=1).reset_index(drop=True)
thought_probe(df, outputpath, globalclock, blockname='2')

rest_instructions()

fixation()

rest_esq_instructions() 

df = df.sample(frac=1).reset_index(drop=True)
thought_probe(df, outputpath, globalclock, blockname='3')

endscreen()

win.close() # close the screen safely 
#Written by Christina Kampoureli 28/03/2023

# Import necessary libraries
from psychopy import visual, core, event, gui
import random
import os 
import csv
from datetime import datetime
import json
import glob
from PIL import Image 
import numpy as np
from utils.esqs_beh import create_csv, thought_probe 

######GUI##########################################################

# Create a dialog box to collect participant information
dlg = gui.Dlg(title="Participant Information")
dlg.addField('subject')
dlg.addField('session', choices=['1', '2', '3', '4', '5'])
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

#####SET UP WINDOW #################################################

# Set up window and fixation cross
win = visual.Window(size=(800, 600), fullscr=True, units='pix', winType='pyglet')
fixation = visual.TextStim(win, text='+', pos=(0, 0), color='white')

#### FIND JSON ################################################

repos_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
repo_path = os.path.join(repos_path, "nf_attention_adhd")
jsons = os.path.join(repo_path, "data", "jsons")
beh_path =  os.path.join(repo_path,"data", "responses", f"{sub_num}", f"{ses_num}")
# Create the directory if it does not exist
if not os.path.isdir(beh_path):
    os.makedirs(beh_path)
protocol_path = os.path.join(repo_path,"data", "protocols", f"{sub_num}", f"{ses_num}")
# Create the directory if it does not exist
if not os.path.isdir(protocol_path):
    os.makedirs(protocol_path)

# Construct filename and full path to JSON file
filename = f'sub-{subject}_ses-{session}_run-{run}_group-{group}_task-training.json'
json_path = os.path.join(jsons, filename)

#### SET UP STIMULI ################################################

# define the relative path to the stimuli
repos_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
repo_path = os.path.join(repos_path, "nf_attention_adhd")
stim_path = os.path.join(repo_path,"data", "stimuli")

csv_info = create_csv(participant_info, beh_path, 'training')

##### SET UP EXPERIMENT VARIABLES ###################################

image_duration = 1
fixation_start_duration = 5
fixation_instr_duration = 1
fixation_duration= 3
fixation_end_duration= 3

#### INSTRUCTIONS ####################################################

# Display instructions
group_instr = group.split('-')
welcome = visual.TextStim(win, text=f'In this task you will be shown overlapping images of faces and scenes and you will need to pay attention either to the face or the scene, depending on the instructions. \n\n When the instruction says "{group_instr[0]}", you will have to press 1 everytime the face is {group_instr[0]}. \n\n When the instruction says "{group_instr[1]}" you will have to press 1 everytime the scene is {group_instr[1]}.\n\n Press 1 to continue.',  height=30, units='pix')
welcome.draw()
win.flip()
event.waitKeys(keyList='1')
win.flip()

###### CSV #############################################################

header = ['subject_num', 'session', 'run', 'group', 'block_number','target_category', 'target_subcategory', 'stimulus_onset', 'stimulus_duration', 'blended_stimuli', 'response', 'response_time', 'accuracy']

date_string = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"{sub_num}_{ses_num}_{run_num}_{participant_info[3]}_task-training_beh.csv"
full_csv_path = os.path.join(beh_path, filename)

def write_data_to_csv(participant_info, block_number,target_category, target_subcategory, stimulus_onset, stimulus_duration, blended_stimuli, response, response_time, accuracy):
    row = [sub_num, ses_num, run_num, participant_info[3], block_number, target_category, target_subcategory, stimulus_onset, stimulus_duration,blended_stimuli, response, response_time, accuracy]
    with open(full_csv_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(header)
        writer.writerow(row)

#######ADJUSTED IMAGE AND FIXATION DURATION ############################################

# Define a function to calculate the adjusted video duration based on onset time
def get_adjusted_image_duration(image_start_time, target_interval=1):
    time_elapsed = image_start_time % target_interval
    adjusted_duration = image_duration - time_elapsed
    return adjusted_duration

def get_adjusted_fixation_duration(fixation_start_time, fixation_duration, target_interval=1):
    time_elapsed = fixation_start_time % target_interval
    adjusted_duration = fixation_duration - time_elapsed
    return adjusted_duration

#############BLEND IMAGES##############################################

def blend_images(image1_filename, image2_filename, alpha=0.5):
    # Determine the subdirectories to search
    category_im1 = ''
    if 'M' in image1_filename:
        category_im1 += 'male/'
    elif 'F' in image1_filename:
        category_im1 += 'female/'
    if 'I' in image1_filename:
        category_im1 += 'indoor/'
    elif 'O' in image1_filename:
        category_im1 += 'outdoor/'

    category_im2 = ''
    if 'M' in image2_filename:
        category_im2 += 'male/'
    elif 'F' in image2_filename:
        category_im2 += 'female/'
    if 'I' in image2_filename:
        category_im2 += 'indoor/'
    elif 'O' in image2_filename:
        category_im2 += 'outdoor/'

    # Locate the images in the subdirectory
    image1_path = os.path.join(stim_path, category_im1, image1_filename)
    image2_path = os.path.join(stim_path, category_im2, image2_filename)

    # Load the images
    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)

    # Blend the images using alpha blending
    blended_image = Image.blend(image1, image2, alpha)

    return blended_image

###CORRECT RESPONSE#######################################

def get_correct_response(target_sub, pair):
    if target_sub == "male":
        if "M" in pair[0]:
            return '1'
        elif "F" in pair[0]:
            return None
    elif target_sub == "female":
        if "F" in pair[0]:
            return '1'
        elif "M" in pair[0]:
            return None
    elif target_sub == "indoor":
        if "I" in pair[0]:
            return '1'
        elif "O" in pair[0]:
            return None
    elif target_sub == "outdoor":
        if "O" in pair[0]:
            return '1'
        elif "I" in pair[0]:
            return None
    return None

########GENERAL#########################################################

# Create a new instance of the monotonic clock to reset the timer
monotonicClock = core.MonotonicClock()

#####RUN STUDY#############################################
fixation_start_time = monotonicClock.getTime()
adjusted_duration_fix = get_adjusted_fixation_duration(fixation_start_time, fixation_start_duration)
fixation_end_time = fixation_start_time + adjusted_duration_fix
while monotonicClock.getTime() <fixation_end_time:
        fixation.draw()
        win.flip()
# Open and read the json file
with open(json_path, 'r') as f:
    data = json.load(f)

# Loop over the keys in the json file
block_counter = 0
image_pairs = []
for key in data.keys():
    # Check if the key ends with "info"
    first_image_start_time = None
    last_image_end_time = None
    if key.endswith("info"):
        num_block = data[key][0]
        target_sub = data[key][1]
        non_target_sub = data[key][2]

        # Determine target category
        if "male" in target_sub or "female" in target_sub:
            target_cat = "face"
        elif "indoor" in target_sub or "outdoor" in target_sub:
            target_cat = "scene"
        else:
               target_cat = None
        # Display instructions for 1 second
        instructions = visual.TextStim(win, text=f"{target_sub}", height=30, units='pix')
        instructions_start_time = monotonicClock.getTime()
        instructions.draw()
        win.flip()
        core.wait(1) #hardcoded
        write_data_to_csv(participant_info, np.nan, "instructions", np.nan, instructions_start_time, "1", np.nan, np.nan, np.nan, np.nan)#hardcoded
        fixation_start_time = monotonicClock.getTime()
        adjusted_duration_fix = get_adjusted_fixation_duration(fixation_start_time, fixation_instr_duration)
        fixation_end_time = fixation_start_time + adjusted_duration_fix
        while monotonicClock.getTime() <fixation_end_time:
                fixation.draw()
                win.flip()
        write_data_to_csv(participant_info, np.nan, "fixation", np.nan, fixation_start_time, adjusted_duration_fix, np.nan, np.nan, np.nan, np.nan)
        # Increase the counter by 1
        block_counter += 1
    # Check if the key ends with "order"
    if key.endswith("order"):
        # Print all the pairs of images
        image_pairs = data[key]
        i=0
        for i, pair in enumerate(image_pairs):
            i += 1
            # Get the correct response for the current image
            correct_response = get_correct_response(target_sub, pair)
            image_start_time = monotonicClock.getTime()
            # Calculate the onset time for the current image
            adjusted_duration = get_adjusted_image_duration(image_start_time)
            image_end_time = image_start_time + adjusted_duration
            # If this is the first image, record the start time
            if first_image_start_time is None:
                first_image_start_time = int(image_start_time)*1000
            
            # Blend the images in the pair
            blended_image = blend_images(pair[0], pair[1])
            
            # Display the blended image
            image = visual.ImageStim(win, image=blended_image)

            # Initialize the response and response time variables
            response = None
            response_time = None

            while monotonicClock.getTime() < image_end_time:
                keys = event.getKeys(keyList=['1'], timeStamped=monotonicClock)
                if keys and response is None:
                    response = keys[0][0]
                    response_time = (keys[0][1] - image_start_time) 
                    #print(f"Response received: {response} at time {keys[0][1]:.4f}, response time: {response_time:.4f} ms")

                image.draw()
                win.flip()

            # Determine accuracy of response
            correct_response = get_correct_response(target_sub, pair)
            print('correctresponse', correct_response)
            if correct_response is None:
                accuracy = 1 if response is None else 0
            elif correct_response == '1':
                accuracy = 1 if response == '1' else 0
            else:
                accuracy = 0
            print('accuracy', accuracy)
            write_data_to_csv(participant_info, num_block, target_cat, target_sub, image_start_time, adjusted_duration, pair, response, response_time, accuracy)
        # Record the end time of the last image
        last_image_end_time = int(image_end_time)*1000

        fixation_start_time = monotonicClock.getTime()
        adjusted_duration_fix = get_adjusted_fixation_duration(fixation_start_time, fixation_duration)
        fixation_end_time = fixation_start_time + adjusted_duration_fix
        while monotonicClock.getTime() <fixation_end_time:
                fixation.draw()
                win.flip()
        write_data_to_csv(participant_info, np.nan, "fixation", np.nan, fixation_start_time, adjusted_duration_fix, np.nan, np.nan, np.nan, np.nan)
       


################ THOUGHT PROBE PRESENTATION ##########
instructions_thought = visual.TextStim(win, text = 'Now we are going to ask you questions about your thoughts during the task you just completed. \n\n Press 3 to navigate to the right, and 2 to navigate to the left, and 1 to submit your reponse. \n\n Please press 1 to continue.', height=30, units='pix')
instructions_thought.draw()
win.flip()
event.waitKeys(keyList='1')
thought_probe(participant_info, monotonicClock.getTime(), win, csv_info, 'training') 

#########BYE SCREEN#####################################
def get_instructions_end(session, run):
    if session == '1' and run == '1':
        instructions_text = 'Thank you for your attention.\n\n You have completed this task!'
    elif session == '5' and run == '1':
        instructions_text = 'Thank you for your attention.\n\n You have completed this task!'
    instructions = visual.TextStim(win, text=instructions_text, height=30, units='pix')
    return instructions

instructions = get_instructions_end(session, run)
instructions.draw()
win.flip()
event.waitKeys(keyList='space')

# Flip the window when the trials are finished
win.flip()

# Close the window when the trials are finished
win.close()














# Import the necessary libraries
from psychopy import visual, core, event, gui, sound
import random
import csv
import os
from datetime import datetime


# Create a dialog box to collect participant information
dlg = gui.Dlg(title="Participant Information")
dlg.addField('subject')
dlg.addField('session', choices=['1', '5'])

participant_info = dlg.show()

# convert participant_info[0] to an integer
sub_num_int = int(participant_info[0])
sub_ses_int = int(participant_info[1])

# format the integer as a zero-padded two-digit string
sub_num = f"sub-{sub_num_int:02d}"
ses_num = f"ses-{sub_ses_int:02d}"

# If the user clicks "Cancel", exit the script
if not dlg.OK:
    core.quit()
    
repos_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
repo_path = os.path.join(repos_path, "nf_attention_adhd")
beh_path =  os.path.join(repo_path,"data", "responses", f"{sub_num}", f"{ses_num}")
if not os.path.exists(beh_path):
    os.makedirs(beh_path)


# Set up the window and the stimulus
win = visual.Window(size=[800, 600], fullscr=True, units='pix', color=[0.5, 0.5, 0.5])
box = visual.Rect(win, width=200, height=200, lineColor='white', fillColor='black')
dot = visual.Circle(win, radius=10, fillColor='white', pos=[0, 0])

# Set up the trial parameters
num_blocks = 50
num_trials = 6
num_dots_options = [3]*2 + [4]*2 + [5]*2
trial_dur = 5.0 #default is  but changed it
min_dist = 40

# Set up the CSV file

# Additional header field for CSV
header = ['participant_num', 'session','block_num', 'trial_num', 'num_dots', 'correct_ans', 'resp', 'correct', 'rt', 'relative_start_time']
date_string = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"{sub_num}_{ses_num}_sa-dots.csv"
full_csv_path = os.path.join(beh_path, filename)
print('full_csv_path',full_csv_path)


def write_data_to_csv(sub_num, ses_num, block_num, trial_num, num_dots, correct_ans, response, correct, rt, relative_start_time):
    row = [sub_num, ses_num, block_num, trial_num, num_dots, correct_ans, response, correct, rt, relative_start_time]
    with open(full_csv_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(header)
        writer.writerow(row)


# Display instructions
instructions = visual.TextStim(win, text='In this task you will be presented with a square. Within this square you will see 3 dots, 4 dots, or 5 dots.\n\nWhen you see 4 dots, you should press "1".\n\nIf you see 3 or 5 dots you should press "2".\n\nThis game takes a long time because we want to find out how good you are at this when you grow tired.\n\n Press "1" when you are ready.')
instructions.draw()
win.flip()
event.waitKeys(keyList=['1'])

# Initialize global clock and first_trial_start_time
global_clock = core.MonotonicClock()
first_trial_start_time = None

# Begin the blocks
for block in range(num_blocks):
    # Display instructions for each block
    random.shuffle(num_dots_options)#shuffle for every block
    block_instructions = visual.TextStim(win, text=f'Block {block + 1} out of {num_blocks}.\n\nPress "1" to start.')
    block_instructions.draw()
    win.flip()
    event.waitKeys()

    # Begin the trials within the block
    for trial_num in range(num_trials):

        # Randomly select the number of dots for this trial
        num_dots = num_dots_options[trial_num]

        # Record the start time of the current trial
        current_trial_start_time = global_clock.getTime()
        
        # Record the start time of the first trial, if it hasn't been recorded yet
        if first_trial_start_time is None:
            first_trial_start_time = current_trial_start_time
        
        # Compute the start time of this trial relative to the first trial
        relative_start_time = current_trial_start_time - first_trial_start_time
        
        # Initialize reaction time clock
        rt_clock = core.Clock()
        
        # Determine the correct answer for this trial
        if num_dots == 4:
            correct_ans = '1'
        else:
            correct_ans = '2'
        
        # Randomly set the positions of the dots, avoiding overlaps
        positions = []
        for j in range(num_dots):
            while True:
                pos = (random.uniform(-80, 80), random.uniform(-80, 80))
                if all(((pos[0] - x)**2 + (pos[1] - y)**2) > min_dist**2 for (x, y) in positions):
                    positions.append(pos)
                    break
                    
        # Draw the dots and the box
        box.draw()
        for j in range(num_dots):
            dot.pos = positions[j]
            dot.draw()
        win.flip()
        
        # Start the reaction time clock
        rt_clock.reset()
        
        # Wait for response and collect reaction time
        resp = None
        rt = None
        while rt_clock.getTime() < trial_dur:
            if 0.2 < rt_clock.getTime() < 8.0:
                keys = event.getKeys(keyList=['1', '2'])
                if keys:
                    resp = keys[0]
                    rt = rt_clock.getTime()  # This is the reaction time
                    break
        
        # Categorize the response as correct or wrong
        if resp == correct_ans:
            correct = 1
            beep = False
        else:
            correct = 0
            beep = True # play the beep sound if the response is wrong
            
        
        
        write_data_to_csv(sub_num, ses_num, block + 1, trial_num + 1, num_dots, correct_ans, resp, correct, rt, relative_start_time)


# Clear the screen for the next trial
win.flip()

# Display instructions
instructions = visual.TextStim(win, text='Thank you for your attention. You have completed this task!')
instructions.draw()
win.flip()
event.waitKeys()

# Flip the window when the trials are finished
win.flip()

# Close the window when the trials are finished
win.close()


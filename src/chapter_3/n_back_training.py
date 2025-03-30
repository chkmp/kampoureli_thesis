from psychopy import visual, core, event, gui
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


# Initialize window
win = visual.Window(
    size=[800, 600],
    units="pix",
    fullscr=True,
    color=[-1, -1, -1]  # RGB for black background
)

# Create squares
squares = []
nRows = 3
nCols = 3
square_size = 50
spacing = 10

# Calculate starting point for the grid
start_x = -((nCols - 1) * (spacing + square_size) + square_size) / 2
start_y = ((nRows - 1) * (spacing + square_size) + square_size) / 2

# Create squares
for i in range(nRows):
    for j in range(nCols):
        x = start_x + j * (square_size + spacing)
        y = start_y - i * (square_size + spacing)
        
        square = visual.Rect(
            win=win,
            units="pix",
            width=square_size,
            height=square_size,
            fillColor=[-1, -1, -1],  # Black
            lineColor=[1, 1, 1],  # White border to simulate grid lines
            pos=[x, y]
        )
        squares.append(square)
        
# Initialize parameters
n_conditions = [0, 1, 2]
n_blocks_per_condition = 2
n_trials_per_block = 10 # for training 
target_ratio = 0.25
stim_duration = 0.5  # in seconds
intertrial_duration = 1.3  # in seconds
fixation_duration = 3.0  # in seconds between blocks

# Initialize data collection
data = []


repos_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
repo_path = os.path.join(repos_path, "nf_attention_adhd")
beh_path =  os.path.join(repo_path,"data", "responses", f"{sub_num}", f"{ses_num}")
if not os.path.exists(beh_path):
    os.makedirs(beh_path)
    
# Function to draw fixation
def draw_fixation(duration):
    fixation = visual.TextStim(win, text='+', color=[1, 1, 1], height=50)
    fixation.draw()
    win.flip()
    core.wait(duration)

# Function to draw instruction
def draw_instruction(text, duration):
    instruction = visual.TextStim(win, text=text, color=[1, 1, 1], height=50)
    instruction.draw()
    win.flip()
    core.wait(duration)



# Set up the CSV file

# Additional header field for CSV
header = ['participant_num', 'session','condition', 'block_num', 'trial_num', 'is_target', 'square', 'correct_response', 'key_press']
date_string = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"{sub_num}_{ses_num}_n-back_training.csv"
full_csv_path = os.path.join(beh_path, filename)
#print('full_csv_path',full_csv_path)


def write_data_to_csv(sub_num, ses_num, condition, block_num, trial_num, is_target, square, correct_response,  key_press):
    row = [sub_num, ses_num, condition, block_num, trial_num, is_target, square, correct_response, key_press]
    with open(full_csv_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(header)
        writer.writerow(row)

def generate_is_target_trials(n_trials, target_ratio, condition):
    # Determine the number of initial non-target trials based on the condition
    initial_non_targets = condition if condition <= 1 else 2
    
    # Calculate the number of target and non-target trials for the remaining trials
    num_target_trials = int((n_trials - initial_non_targets) * target_ratio)
    num_non_target_trials = n_trials - num_target_trials - initial_non_targets

    # Create lists for target and non-target trials
    target_trials = [1] * num_target_trials
    non_target_trials = [0] * num_non_target_trials

    # Combine and shuffle the target and non-target trials
    combined_trials = target_trials + non_target_trials
    random.shuffle(combined_trials)

    # Check and fix consecutive True values
    for i in range(len(combined_trials) - 1):
        if combined_trials[i] and combined_trials[i+1]:
            # Find a False to swap with
            for j in range(i + 2, len(combined_trials)):
                if not combined_trials[j]:
                    combined_trials[i+1], combined_trials[j] = combined_trials[j], combined_trials[i+1]
                    break

    # Prepend initial non-target trials
    combined_trials = [0] * initial_non_targets + combined_trials

    return combined_trials


# Pseudorandomize conditions in 2-block chunks
# Create a list that repeats each condition n_blocks_per_condition times
randomized_conditions = [0]*n_blocks_per_condition + [1]*n_blocks_per_condition + [2]*n_blocks_per_condition



# Display instructions
instructions = visual.TextStim(win, text='In this task you will be presented with a grid of 9 squares.\n\nWhen you are in the 0-back condition, you will need to press "1" every time the middle square (5th) square lights up. \n\nWhen you are in the 1-back condition, you will need to press "1" every time the square that lights up, is the same as the one before (1-back). \n\n When you are in the 2-back condition, you will need to press "1" every time the square that lights up, is the same as the one before last (2-back).\n\n Press "1" when you are ready.')
instructions.draw()
win.flip()
event.waitKeys(keyList=['1'])

# Main experimental loop
current_condition = None
last_idx = None
last_target_trial = None

for n in randomized_conditions:
    if n != current_condition:  # If the condition changes, show instruction
        draw_instruction(f"{n}-back condition.", 2)
        current_condition = n  # Update the current condition
    
    for block in range(1):  # 2 blocks for each condition
        correct_count = 0  # Reset the count at the start of each block
        history = []

        is_target_trials = generate_is_target_trials(n_trials_per_block, target_ratio, n)

        for trial in range(n_trials_per_block):
            is_target = is_target_trials[trial]
            correct_response = 0  # Reset the correct_response flag
            # Initialize clock object at the beginning of the trial
            trial_clock = core.Clock()

            if n == 0:  # 0-back
                if is_target:
                    target_idx = 4  # Middle square
                else:
                    available_idxs = [i for i in range(9) if i != 4 and i != last_idx]
                    target_idx = random.choice(available_idxs)

            elif n == 1:  # 1-back
                if is_target and len(history) > 0:
                    target_idx = history[-1]  # Allow immediate repetition
                else:
                    available_idxs = [i for i in range(9) if i != last_idx]
                    target_idx = random.choice(available_idxs)

            elif n == 2:  # 2-back
                if is_target and len(history) > 1:
                    target_idx = history[-2]
                else:
                    available_idxs = [i for i in range(9) if i not in history[-2:]]
                    target_idx = random.choice(available_idxs)
                    
            # Update last_idx and history
            last_idx = target_idx
            #print('last_idx_final', last_idx)
            history.append(target_idx)
            if len(history) > n + 1:  # Keep only the necessary history
                history.pop(0)
            
            


            # Change square color
            square = squares[target_idx]
            square.fillColor = [1, 1, 1]

            # Draw and flip
            for s in squares:
                s.draw()
            win.flip()

            # Start the clock
            trial_clock.reset()
            
            # Initialize keys variable
            keys = []
            
            while trial_clock.getTime() < intertrial_duration:
                # After 0.5 seconds, reset the square color to black
                if trial_clock.getTime() > stim_duration:
                    square.fillColor = [-1, -1, -1]
                    
                    # Draw and flip back to original
                    for s in squares:
                        s.draw()
                    win.flip()
            
                # Check for keypresses, it won't wait but will collect keypresses so far
                new_keys = event.getKeys(keyList=['1'])
                if new_keys:
                    keys.extend(new_keys)
                    print('keys', keys)
                

            # Check for correct response
            if is_target and keys and '1' in keys:
                correct_response = 1
                correct_count+=1
            elif not is_target and not keys:
                correct_response = 1       
                correct_count+=1     

            write_data_to_csv(sub_num, ses_num, n, block+1, trial+1, int(is_target), target_idx + 1, correct_response, str(keys) if keys else "None")
            print('keypress:',str(keys), 'trial:', trial+1)


            # Reset square color
            square.fillColor = [-1, -1, -1]

            # Draw and flip
            for s in squares:
                s.draw()
            win.flip()

            # Wait inter-trial interval
            core.wait(intertrial_duration)

        # Display the number of correct responses at the end of each block
        #feedback = f"Correct: {correct_count} out of {n_trials_per_block}"
        feedback = visual.TextStim(win, text=f'Correct: {correct_count} out of {n_trials_per_block}.\nPress "1" to continue.')
        feedback.draw()
        win.flip()
        event.waitKeys(keyList='1')
        
        # Draw fixation between blocks
        draw_fixation(fixation_duration)

# Display instructions
instructions = visual.TextStim(win, text='Thank you for your attention. You have completed the training for this task!')
instructions.draw()
win.flip()
event.waitKeys()

# Close window
win.close()
core.quit()

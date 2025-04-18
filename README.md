# kampoureli_thesis
Script repository for "Attention Training with Real-Time fMRI Neurofeedback: Protocol Optimisation and Implementation in Adult Attention Deficit Hyperactivity Disorder (ADHD)" thesis.

Collaborators: Will Strawson, Chris Racey, Michael Luehrs, Andreas Bressler

**Scripts located in `src/chapter_2`**

- **fmriprep.sh**  
  Script to preprocess fMRI data using fmriprep in a singularity container.

- **glm_nfattention_im.m**  
  Wrapper for GLM single trial analysis for a specified subject. Needs to be called with `glm_attention_im_cluster.sh`.

- **glm_nfattention_im_cluster.sh**  
  Job script to run `glm_nfattention_im.m` function on a compute cluster using SGE.
  
- **gm_mask.py**  
  Script to create subject-specific gray matter mask from fmriprep outputs.

- **roi_svm_perm_withinrun.m**  
  This script performs ROI-based SVM classification (within-run cross-fold validation) with permutation testing on fMRI data for a specific subject, utilizing multiple masks. Needs to be called with `roi_svm_perm_cluster.sh`.

- **roi_svm_perm_betweenrun.m**  
  This script performs ROI-based SVM classification (training on one run, testing on an independent) with permutation testing on fMRI data for a specific subject, utilizing multiple masks. Needs to be called with `roi_svm_perm_cluster.sh`.

- **roi_svm_perm_cluster.sh**  
  Job script to run `roi_svm_perm_*run.m` functions on a compute cluster using SGE.

- **blender.py**  
  This script is to create blended image stimuli for Experiment 1.

- **trimmed_means_anovas.r**  
  This script is to run the trimmed means anovas for run comparisons.

- **feedback.py**  
  Script for stimulus presentation during feedback runs.

- **functional_localizer_static.py**  
  Script for stimulus presentation for the static functional localizer.

- **functional_localizer_video.py**  
  Script for stimulus presentation for the dynamic functional localizer.

- **training.py**  
Script for stimulus presentation during training runs.

- **jsonmaker.py**  
Script to create the json files for `training.py` and `feedback.py`.

- **esqs.py**  
Script for thought probs, gets called within `training.py` and `feedback.py`.


**Scripts located in `src/chapter_3`**

- **feedback.py**  
  Script for stimulus presentation during feedback runs.

- **jsonmaker.py**  
Script to create the json files for `training.py` and `feedback.py`.

- **n_back.py**  
  Script for visuospatial n-back task.

- **sa_dots.py**  
  Script for sustained attention dots task.

- **training_beh.py**  
Script for stimulus presentation during training runs (for outside the scanner).

- **training.py**  
Script for stimulus presentation during training runs (for inside  the scanner).

- **esqs.py**  
Script for thought probs, gets called within `training.py` and `feedback.py`.





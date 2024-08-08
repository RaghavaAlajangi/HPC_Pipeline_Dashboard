# Auto-Rapid HPC Pipeline Request

Pipeline for analysis of Auto-rapid data.


### How to use this template:

Specify a parameter or a list of parameters that you want to execute as a pipeline/s in the below yaml file.

Choosing multiple files will create a matrix of jobs (multiple jobs).


- To start the job type the following in a comment:
  
      Go

- To cancel the job, type the following in a comment:

      Cancel

Updates will be displayed as comments when the process starts and ends.
For example, when the job(s) is finished, a comment with "Finished" will appear.

## Your Pipeline Details

```python
params:
  mode_mp: 'mp'  # 'seq' or 'mp'
  mp_batch_size: 1000
  mp_core_count: 16
  # integer (lower means less strict) or 'auto' calculates it
  efp_thresh: 'auto'
  exclude_empty_frames: True
  # "all" or an integer. You may end up with more than this number, as images may have multiple events
  event_images_to_detect: "all"
  ## MATLAB_PHA_THRESH_VAL=0.5 from Kyoo's MATLAB script. Lower to include more info
  phase_thresh: 0.5
  refocus: True


data: 
  - GUCKDIV:\Data\AutoRAPID\AutoRAPID\2024-06-06_SGR_blood and KC167 cells test\11-00-39\ar_data_0004.hdf5, 
  - GUCKDIV:/Data/Auto-RAPID/file2.hdf5, 
  - GUCKDIV:/Data/Auto-RAPID/file3.hdf5
```

```bash

```
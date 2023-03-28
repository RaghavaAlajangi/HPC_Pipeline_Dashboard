# flake8: noqa: F401
simple_template = """
<!-- pred_simple -->

# Pipeline Request

Pipeline for segmentation and/or classification (prediction) and analysis of data.


### How to use this template:

Tick the Steps in "Your Pipeline Details" you wish to execute.
See this video link [] for how to use this template.

Choosing multiple Segmentation or Prediction algorithms will create a matrix of
jobs (multiple jobs).


- To start the job type the following in a comment:
  
      Go

- To cancel the job, type the following in a comment:

      Cancel

Updates will be displayed as comments when the process starts and ends.
For example, when the job(s) is finished, a comment with "Finished" will appear.

## Your Pipeline Details

- **Segmentation**
   - Segmentation Algorithm
      - [ ] mlunet: UNET
      <!-- option end -->
      - [ ] legacy: Legacy thresholding with OpenCV
      <!-- option end -->
      - [ ] watershed: Watershed algorithm
      <!-- option end -->
      - [ ] std: Standard-deviation-based thresholding
      <!-- option end -->


- **Prediction**
   - Classification Model
      - [ ] MNet
      - [ ] Bloody Bunny


- **Post Analysis**
   - [ ] Benchmarking
   - [ ] Scatter Plots


- **Data to Process**
   - [ ] DCOR: cfs
   - [ ] DCOR: control
   - [ ] DCOR: figshare-7771184-v2
   - [ ] DCOR: 89bf2177-ffeb-9893-83cc-b619fc2f6663
   - [ ] DCOR: f7fa778f-6abd-1b53-ae5f-9ce12601d6f8
   - [ ] DVC: data_raw/test_data/calibration_beads.rtdc
   - [ ] All Data
"""

advanced_template = """
<!-- pred_advanced -->

# Pipeline Request ADVANCED

Pipeline for segmentation and/or classification (prediction) and analysis of data.

**Note**: This is the advanced template. If you are not sure which template to use, then you should probably
use the other template (simple).

### How to use this template:

Tick the Steps in "Your Pipeline Details" you wish to execute.
See this video link [] for how to use this template.

Choosing multiple Segmentation or Prediction algorithms will create a matrix of
jobs (multiple jobs). You can change the keyword=value.



- To start the job type the following in a comment:
  
      Go

- To cancel the job, type the following in a comment:

      Cancel

Updates will be displayed as comments when the process starts and ends.
For example, when the job(s) is finished, a comment with "Finished" will appear.


## Your Pipeline Details

- **Segmentation**
  - dcevent version:
    - [ ] dcevent version=latest
  - Segmentation Algorithm
    - [ ] mlunet: UNET
    <!-- option end -->
    - [ ] legacy: Legacy thresholding with OpenCV
      - [ ] thresh=-6
      - [ ] blur=0
      - [ ] binaryops=5
      - [ ] diff_method=1
      - [ ] clear_border=True
      - [ ] fill_holes=True
      - [ ] closing_disk=5
    <!-- option end -->
    - [ ] watershed: Watershed algorithm
      - [ ] clear_border=True
      - [ ] fill_holes=True
      - [ ] closing_disk=5
    <!-- option end -->
    - [ ] std: Standard-deviation-based thresholding
      - [ ] clear_border=True
      - [ ] fill_holes=True
      - [ ] closing_disk=5
    <!-- option end -->
  - Background Correction/Subtraction Method
    - [ ] rollmed: Rolling median RT-DC background image computation
      - [ ] kernel_size=100
      - [ ] batch_size=10000
    <!-- option end -->
    - [ ] sparsemed: Sparse median background correction with cleansing
      - [ ] kernel_size=200
      - [ ] split_time=1.0
      - [ ] thresh_cleansing=0
      - [ ] frac_cleansing=0.8
    <!-- option end -->
  - Available gating options:
    - [ ] norm gating:
      - [ ] online_gates=False
      - [ ] size_thresh_mask=5
    <!-- option end -->
  - Further Options:
    - [ ] --reproduce=False


- **Prediction**
  - dcml version
    - [ ] dcml version=latest
  - Classification Model
    - [ ] MNet
      - [ ] MNet version=latest
    - [ ] Bloody Bunny
      - [ ] Bloody Bunny version=latest


- **Post Analysis**
   - [ ] Benchmarking
   - [ ] Scatter plot


- **Data to Process**
   - [ ] DCOR: cfs
   - [ ] DCOR: control
   - [ ] DCOR: figshare-7771184-v2
   - [ ] DCOR: 89bf2177-ffeb-9893-83cc-b619fc2f6663
   - [ ] DCOR: f7fa778f-6abd-1b53-ae5f-9ce12601d6f8
   - [ ] DVC: data_raw/test_data/calibration_beads.rtdc
   - [ ] All Data
"""

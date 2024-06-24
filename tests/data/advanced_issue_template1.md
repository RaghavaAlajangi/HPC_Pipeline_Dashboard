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
  - dcevent version
    - [ ] dcevent version=latest
    <!-- option end -->
  - Segmentation Algorithm
    - [x] mlunet: UNET
      - [x] model_file=unet-228-accel_g2_6383e.ckp
    <!-- option end -->
    - [x] legacy: Legacy thresholding with OpenCV
      - [x] thresh=-2
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
    - [x] sparsemed: Sparse median background correction with cleansing
      - [x] kernel_size=200
      - [x] split_time=1
      - [x] thresh_cleansing=0
      - [x] frac_cleansing=0.8
    <!-- option end -->
  - Available gating options
    - [ ] norm gating
      - [ ] online_gates=False
      - [ ] size_thresh_mask=0
    <!-- option end -->
  - Further Options
    - [ ] --reproduce
    <!-- option end -->
- **Prediction**
  - Classification Model
    - [x] bloody-bunny_g1_bacae: Bloody Bunny
    <!-- option end -->
- **Post Analysis**
  - [ ] Benchmarking
    <!-- option end -->
  - [ ] Scatter Plot
    <!-- option end -->
- **Data to Process**
  - [x] HSMFS:/Data/RTDC - UKER/KK_for_testing_analysis_pipeline/rai9346ac24f58900f3c2997412/M002_data.rtdc
  - [x] HSMFS:/Data/RTDC - UKER/KK_for_testing_analysis_pipeline/rai9346ac24f58900f3c2997412/M001_data.rtdc

    <!-- option end -->
- __Author__
   - [x] username=raghava.alajangi
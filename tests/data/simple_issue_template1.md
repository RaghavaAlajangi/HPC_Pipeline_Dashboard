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
      - [x] mlunet: UNET
        - [x] model_file=unet-228-accel_g2_b428b.ckp
      <!-- option end -->
      - [ ] legacy: Legacy thresholding with OpenCV
      <!-- option end -->
      - [ ] watershed: Watershed algorithm
      <!-- option end -->
      - [ ] std: Standard-deviation-based thresholding
      <!-- option end -->
  - Further Options:
    - [ ] --reproduce
    - [ ] --num-frames
    <!-- option end -->

- **Prediction**
   - Classification Model
      - [ ] mnet: MNet
      - [ ] bloody-bunny_g1_bacae: Bloody Bunny
   <!-- option end -->

- **Post Analysis**
   - [ ] Benchmarking
   - [ ] Scatter Plots
   <!-- option end -->

- **Data to Process**
   - [x] DCOR: 89bf2177-ffeb-9893-83cc-b619fc2f6663

    <!-- option end -->
- __Author__
   - [x] username=raghava.alajangi
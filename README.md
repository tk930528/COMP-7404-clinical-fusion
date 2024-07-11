## Group Project of Group 7, COMP7404 (Summer Semester in 2024)

The source code is mainly retrived from the repository of the paper *Combining structured and unstructured data for predictive models: a deep learning approach* we referenced  in our group project. The github link of the project is: https://github.com/onlyzdd/clinical-fusion. In this paper, it proposed two frameworks, Fusion-CNN and Fusion-LSTM. We try to do experiments on these models in a purpose of understanding recent advances in machine learning.

### File List

```
Group_7
|- src
   |- clinical-fusion-master
      |- ... (Source code without data)
|- videos_for_demo
   |- cnn_train.mp4
   |- cnn_test.mp4
   |- lstm_train.mp4
   |- lstm_test.mp4
   |- demo.mp4 (*)
|- README.md
|- change_of_code.md
```

(*): This is the demo we should have displayed on our presentation. The others are unclipped original videos.

### Requirements

The current workspace is `src/clinical-fusion-master`.

#### Dataset

The data applied to train the framework is retrieved from the MIMIC-III database. In this paper, they did not use all of the data and just sampled a part of it to do experiments.

For convenience, we would directly provide Google Drive links of sampled data files which are generated in the **step 3** below. Some of the CSV files would be very large, especially `CHARTEVENTS.csv`. But with the processed CSV file, it is no need for you to download all CSV files required in **step 1**. Anyway, we will still give the links if you want to test the SQL queries provided by the original author.

Note that you will still need to run the command provided in the <u>[Pre-processing](#0)</u> part, this part is mainly for sampling from the initial data and packing them into some new files but not pre-processing. The data which is not sampled would not be applied in the training or testing period.

These 5 files are requisite for successfully running pre-processing codes and *main.py*, you can find all of them in the 1st and the 2nd link. Please put all of them under `data/mimic`.

*Link 1: [three_sql_csv.zip](https://drive.google.com/file/d/1dbd0TtlXVQ3Zg1_MEtNL6PPOaF4TXWBG/view?usp=sharing)*

```python
'adm_details.csv'
'pivoted_lab.csv'
'pivoted_vital.csv'
```

*Link 2: [two_data_csv.zip](https://drive.google.com/file/d/173O45bOzbdVrWL97nc5Wle7UUO55i1Gu/view?usp=sharing)*
```python
'DIAGNOSES_ICD.csv'
'NOTEEVENTS.csv'
```

If you have downloaded the sampled data and are not interested in the full procedure of sampling data, you can now skip to the next part <u>[Software](#1)</u>.

The 3rd link contains all of the CSV files you will need in the **step 1** below, except `CHARTEVENTS.csv`, it can be found in the 4th link.

*Link 3: [req_csv.zip](https://drive.google.com/file/d/1fjhKIrVrf_6ymE0d1jmgebP8xD48uYRZ/view?usp=drive_link)*

*Link 4: [CHARTEVENTS.csv.gz](https://drive.google.com/file/d/1oM14vlHkT2ni8oDiFeZ_bFgE9TMT_sWB/view?usp=drive_link)*

MIMIC-III database analyzed in the study is available on [PhysioNet](https://mimic.physionet.org/about/mimic) repository. If you have obtained the original data but not the sampled data, To prepare for the dataset, you need to follow these instructions:

**Step 1.** After you have obtained the data from PhysioNet or the Google Drive link above, place these `.csv` files under `data/mimic`. Note that `CHARTEVENTS.csv` is compressed as a `.gz` file, you should decompress it first to get this CSV file. It is very large! (>=20GB) If you decide not to download the sampled data above, please make sure you have enough space. All CSV files might need at least 30GB of disk space.

```python
'ADMISSIONS.csv'
'CHARTEVENTS.csv'
'DIAGNOSES_ICD.csv'
'ICUSTAYS.csv'
'LABEVENTS.csv'
'NOTEEVENTS.csv'
'PATIENTS.csv'
```

**Step 2.** Import the CSV files above (except `DIAGNOSES_ICD.csv`) into SQL as tables. Make sure the name of each table is same as its original CSV file.

**Step 3.** Run 3 SQL queries under `query`. If successful, 3 new views will be generated. Convert these views to CSV files and put them under `data/mimic`. They are:

```python
'adm_details.csv'
'pivoted_lab.csv'
'pivoted_vital.csv'
```

Then you have finished the first preparation for the dataset.

#### <div id=1> Software </div>

Here are the requirements of package version given by the original author of this paper:

- Python: 3.6.10
- Gensim: 3.8.0
- NLTK: 3.4.5
- Numpy: 1.14.2
- Pandas: 0.25.3
- Scikit-learn: 0.20.1
- Tqdm: 4.42.1
- PyTorch: 1.4.0

But in our experiment, we did not follow the demands above as we encountered difficulties in downgrading some packages. But we still succeeded in running the code and getting the results we displayed during our presentation. Here is our versions of packages:

- Python: 3.8.18
- Gensim: 3.8.0
- NLTK: 3.7
- Numpy: 1.24.3
- Pandas: 1.2.4
- Scikit-learn: 1.1.1
- Tqdm: 4.65.0
- PyTorch: 2.2.1+cu118

We recommend you to follow the requirements provided by the original author to avoid any unexpected issues. By the way, we will give some steps about how we changed the code to make sure it could be runned in our environment later.

#### Adjustments

We guess the original author of the paper might have mistaken something, so the complier would still raise an error as it cannot find some extra CSV files which is actually no need in the experiment. The program file we submitted is an updated version and runnable in our environment. We attached another Markdown file `change_of_code.md` to introduce some changes made by us. There is one issue that is related to your python version so you should check it first to decide if you need to change it or not:

- In *main.py*: You may find a syntax error in `tensor.cuda(async=True)` if your python version is >=3.7. Update it with `tensor.cuda(non_blocking=True)`. Leave it if there is no syntax error.


### <div id=0> Pre-processing </div>

With updated code and make sure you have collected all necessary files, you can run these commands to implement pre-processing:

```sh
$ python 00_define_cohort.py # define patient cohort and collect labels
$ python 01_get_signals.py # extract temporal signals (vital signs and laboratory tests)
$ python 02_extract_notes.py --firstday # extract first day clinical notes
$ python 03_merge_ids.py # merge admission IDs
$ python 05_preprocess.py # run preprocessing
$ python 06_doc2vec.py --phase train # train doc2vec model
$ python 06_doc2vec.py --phase infer # infer doc2vec vectors
```

If successful, you will find 3 additional folders: `files`, `initial_data`, `resample_dir` and 8 CSV files under the directory `data/processed`:

```python
'demo.csv'
'earlynotes.csv'
'features.csv'
'labels_icd.csv'
'llos.csv'
'los.csv'
'mortality.csv'
'readmit.csv'
```

and also a new doc2vec model in the folder `models`.

You may notice the command about `04_statistics.py` is missing. Depending on your numpy version, if you did not follow the requirements of package version provided by original author, it will raise an error. But this python file is only for statistics, it will not affect the final result. Thus, we think you can ignore it if you fail to run this file.

### Run

To train the models proposed in the paper we referenced, run the commands:

```sh
$ python main.py [--model {cnn|lstm}] [--epoch 20] [--lr 0.005] [--task {mortality|llos|readmit}] [--use-text {0|1}]
```

After running this command, a saved model file should be generated at `models/best.ckpt`. Then, you can test the model by running:

```sh
$ python main.py [--model {cnn|lstm}] [--phase test] [--task {mortality|llos|readmit}]
```

The file `best.ckpt` will be updated every time you finish training. That is to say, if you have trained a CNN (or LSTM) model, you can only test the model by setting the param of model as `cnn` (or `lstm`). The param `--use-text` will decide if the network use the unstructured data as input or not. (Default is `1`)

You can also manually change the values in *main.py* to control these params. For example, You can set `args.use_unstructure = 1` to use unstructured data in training process. The declaration in *main.py* would have a higher priority than the params in the command.
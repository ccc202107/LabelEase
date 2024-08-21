# LabelEase

> Implementation and datasets for ISSRE2024 TAR paper 'LabelEase: A Semi-Automatic Tool for Efficient and Accurate Trace Labeling in Microservices'.



## Artifact Description

### code

- **Frontend Code**: Files for the front-end application located in the `frontend/` folder.
- **Backend Code**: Algorithm and back-end code located in the `backend/` folder.

### dataset

We provide a trace anomaly detection dataset in 

```shell
./backend/LabelEase/data/data1.zip
```



## Environment Setup

All experiments are run on a server with two 16C32T Intel(R) Xeon(R) Gold 5218 CPU @ 2.30 GHz, one NVIDIA(R) Tesla(R) V100S, and 192 GB RAM.

The implementation of LabelEase is in Python 3.7.0, with PyTorch 1.5.0 serving as the primary deep learning framework.

A list of required Python libraries is located in the `.\backend\LabelEase\requirements.txt`.



## Getting Started

### start quickly

```shell
cd .\backend\LabelEase\
pip install -r .\requirements.txt
python run.py
```

### backend

```shell
cd .\backend\
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### frontend

```shell
cd .\frontend\
npm install
npm run dev
```



## Reproducibility Instructions

**Initialize Environment**:

- Make sure all dependencies are installed, and the backend and frontend are correctly configured.

**Run Experiments**:

- Execute the backend server and load the frontend application as specified. Perform trace labeling using the provided tools.

**Validate Results**:

- Compare your results with those reported in the paper to confirm that the tool produces the same outcomes.

By these instructions being followed, the trace labeling results should be reproducible and the claims made in the paper can be verified.

# TraceEase


We provide a trace anomaly detection dataset in 
```shell
./backend/TraceEase/data/data1.zip
```



## start quickly

```shell
cd .\backend\TraceEase\
pip install -r .\requirements.txt
python run.py
```



## backend

```
cd .\backend\
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```



## frontend

```
cd .\frontend\
npm install
npm run dev
```


# How to use `anomaly_detection.py`

1. A `db.cfg` file can be located in this repository's `notebooks` folder. Fill in your credentials in this cfg file and download this file. At the top of `anomaly_detection.py`, there is a variable called `database_path`. Assign the location of your `db.cfg` file to this variable.

2. If you wish to change the bounds of 15 minute anomaly detection:

      i. At the top of the file, there is a variable called `anomaly_percentile`. This is one of the variables passed in the `anomalous` function. This function accepts this variable as its last parameter. This value is a percentage prediction interval region for the ARIMA/ETS forecast. 
      
     ii. The value is currently set at `99` %. Change this value to your preference. The default value in R is `95`. 

3. If you wish to change the bounds of trend deviation detection:

      i. At the top of the file, there is another variable called `IQR_multiplier`. This is one of the variables passed in the `trend` function. This function accepts this variable as its last parameter, which is the multiplicative IQR factor that determines the upper and lower bounds for trend deviation. These boundas are calculated through the classical box plot method of outlier detection. This method is as follows: given a datapoint x, if x lies outside the following range: 
      
      <img src="http://latex.codecogs.com/gif.latex?Q3%20&plus;%201.5*IQR%20%5Cgeq%20x%20%5Cgeq%20Q1%20-%201.5*IQR" /> 

      Then x is an outlier. 
      
    iii. The default is `2`. The larger the value, the greater the bounds. In traditional statistical outlier detection, this value is 1.5 Change this value to your preference. 
     
4. If you wish to see the total number of outliers produced:

      i. Call `g.outliers` from the command line. `g` is a `grand_count` object which keeps track of the number of outliers calculated, whether they are trend deviations or individual 15 minute anomalies. It also keeps track of the number of anomaly graphs and trend graphs produced, which can be accessed through calling `g.anomaly_graph_count` or `g.trend_graph_count` respectively. 

5. Run `anomaly_detection.py` from your command line. You will have a folder called `found_anomalies` in your Documents folder. In this folder, all graphs containing trend deviations and anomalies will appear, in addition to a CSV containing all 15 minute anomalies. The anomaly graphs are labeled as `anomaly_X.png`, and trend gaphs are labeled as `trend_X.png`. 

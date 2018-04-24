# How to use `anomaly_detection.py`

1. A `db.cfg` file can be located in this repository's `notebooks` folder. Fill in your credentials in this cfg file and download this file. At the top of `anomaly_detection.py`, substitue the location of your downloaded `db.cfg` file as the input of the `CONFIG.read` function. 

2. If you wish to change the bounds of 15 minute anomaly detection:

      i. Proceed to the end of the file, within the `for` loop. 
      
      ii. The function `anomalous` accepts a percentile value as its last parameter. This value is a percentage prediction interval region for the ARIMA forecast. 
      
      iii. The value is currently set at `98` %. Change this value to your preference. The default value in R is `95`. 

3. If you wish to change the bounds of trend deviation detection:

      i. Proceed to the end of the file, within the `for` loop. 
      
      ii. The function `trend` accepts a numeric value as its last parameter, which is the multiplicative IQR factor that determines the upper and lower bounds for trend deviation. The spread is calculated through the classical box plot method of outlier detection. This method is as follows: given a datapoint x, if x lies outside the following range: 
      
      <img src="http://latex.codecogs.com/gif.latex?Q3%20&plus;%201.5*IQR%20%5Cgeq%20x%20%5Cgeq%20Q1%20-%201.5*IQR" /> 

      Then x is an outlier. 
      
    iii. The default is `2`. The larger the value, the greater the bounds. In traditional statistical outlier detection, this value is 1.5 Change this value to your preference. 

4. Run `anomaly_detection.py` from your command line. 

# How to use `anomaly_detection.py`

1. At the 15th line of the file, substitue the location of your `db.cdg` file as the input of the `CONFIG.read` function

2. If you wish to change the bounds of 15 minute anomaly detection:

      i. proceed to the 266th line of code. 
      
      ii. The function `anomalous` accepts a percentile value as its last parameter. 
      
      iii. The default is `98`. Change this value to your preference.

3. If you wish to change the bounds of trend deviation detection:

      i. Proceed to the 269th line of code. 
      
      ii. The function `trend` accepts a numeric value as its last parameter, which is the multiplicative IQR factor that determines the upper and lower bounds for trend deviation. 
      
      iii. The default is `2`. The larger the value, the greater the bounds. In traditional statistical outlier detection, this value is 1.5 Change this value to your preference. 

4. Run `anomaly_detection.py` from your command line. 

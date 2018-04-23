import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
import pandas as pd
import configparser
from psycopg2 import connect
import psycopg2.sql as pg
import pandas.io.sql as pandasql
import matplotlib.pyplot as plt
from scipy.stats import iqr
from numpy import percentile


CONFIG = configparser.ConfigParser()
CONFIG.read(r'C:\Users\alouis2\Documents\Python Scripts\db.cfg')
dbset = CONFIG['DBSETTINGS']
con = connect(**dbset)
pd.options.display.mpl_style = 'default'

import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
ts=robjects.r('ts')
append = robjects.r('append')
ro.r('install.packages("forecast")')
forecast=importr('forecast')
from rpy2.robjects import pandas2ri
pandas2ri.activate()

# Grab the newest distinct intersection, leg, and direction combinations


def get_new(): 
    # get_new: None -> pd.Dataframe
    # requires: None
    
    strSQL = '''SELECT DISTINCT intersection_name, leg, dir 
                FROM miovision.volumes_15min_new 
                INNER JOIN miovision.intersections USING (intersection_uid)
                WHERE classification_uid IN (1,4,5)
                ORDER BY intersection_name, leg, dir'''
    data = pandasql.read_sql(pg.SQL(strSQL), con)
    return data

newest = get_new()


# We will use grab() to grab a relevant dataframe given user inputs

def grab(dow, intersection, direction, int_leg):
    
    ## grab: str str str str => pd.DataFrame
    
    ## requires: dowNOT IN ('Saturday', 'Sunday')
    ##           intersection: 'Street1 / Street2'
    ##           direction in ('EB', 'WB')
    ##           int_leg in ('E', 'W')
    
    strSQL = '''WITH ts AS (SELECT datetime_bin, sum(volume) as volume
                FROM miovision.volumes_15min
            INNER JOIN miovision.intersections USING (intersection_uid)
            WHERE classification_uid in (1,4,5)
            AND intersection_name = '%s'
            AND (leg = '%s' AND dir = '%s')
            AND extract(dow from datetime_bin) in (%s)
            and extract('hour' from datetime_bin) >= 6
            and extract('hour' from datetime_bin) < 20
            GROUP BY datetime_bin
            ORDER BY datetime_bin),
            
            proper AS (SELECT datetime_bin::date, COUNT(volume)
            from ts
            group by datetime_bin::date
            having count(volume) = 56)
            
            select * from ts
            where datetime_bin::date in (select datetime_bin from proper)''' % (intersection, int_leg, direction, dow)
            
    return pandasql.read_sql(pg.SQL(strSQL), con)

# forecast() will develop an 24 hour ARIMA forecast given historic data. The forecast will contain 95th percentile bounds that we will use to detect anomalous data

def forecast(dow, intersection, direction, int_leg):
    
    ## forecast: str str str str => pd.Dataframe
    
    ## requires same constrains as `grab`
    
    data = grab(dow, intersection, direction, int_leg)
    
    rdata = ts(data.volume.values, frequency = 56)    
    
    rstring="""function(testdata){
                library(forecast)
                fitted_model<-auto.arima(testdata)
                forecasted_data<-forecast(fitted_model,h=56)
                outdf<-data.frame(forecasted_data)
                outdf
                }"""
     
    rfunc = robjects.r(rstring)
    r_df = rfunc(rdata)
    forecast_df = pandas2ri.ri2py(r_df)
    
    return forecast_df



# anomalous() detects anomalous datapoints given a new data frame, and produces a graph of the new data along with highlighted anomalies 

def anomalous(dow, intersection, direction, int_leg, new_dataframe, percentile = 95):
    
    ## anomoulous: str str str str pd.Dataframe int => str
    
    ## requires: dow, intersection, direction, int_leg: strings as used in forecast function
    ##           new_dataframe: pd.DataFrame containing two columns- 'datetime_bin' and 'volume'
    ##                          The format of this dataframe is the same as the one returned by
    ##                          the grab function
    ##           percentile: int, either 95 or 80
    
    # get upper and lower bounds according ot percentiles
    upper = forecast(dow, intersection, direction, int_leg)['Hi.%s' % percentile]
    
    upper = pd.DataFrame(upper).reset_index()['Hi.%s' % percentile] 
    lower = forecast(dow, intersection, direction, int_leg)['Lo.%s' % percentile]
    lower = pd.DataFrame(lower).reset_index()['Lo.%s' % percentile] 
    new_volume = new_dataframe['volume']
    
    # create a list of sublists containing outlier index, outlier, forcast, error, outlier type
    upper_outliers = [[list(new_volume-upper).index(i), new_dataframe['volume'][list(new_volume-upper).index(i)], list(upper)[list(new_volume-upper).index(i)], 'upper', i*i] for i in list(new_volume-upper) if i > 0]
    lower_outliers = [[list(new_volume-lower).index(i),  new_dataframe['volume'][list(new_volume-lower).index(i)], list(lower)[list(new_volume-lower).index(i)], 'lower', i*i] for i in list(new_volume-lower) if i < 0]
    for sublist in lower_outliers:
        sublist[0] = new_dataframe['datetime_bin'][sublist[0]]
    for sublist in upper_outliers:
        sublist[0] = new_dataframe['datetime_bin'][sublist[0]]
    
    # concatenate and convert to dataframe
    outliers = lower_outliers + upper_outliers

    
    if outliers != []:
        outliers = pd.DataFrame(outliers, columns = ['datetime_bin', 'volume', 'forecasted_volume', 'outlier_type', 'squared error']).sort_values(by=['datetime_bin'])
        print(outliers, len(outliers))
        
        # plot new data with highlighted outliers 
        data_dates = list(new_dataframe['datetime_bin'].apply(lambda d: d.time()))
        data_volumes = list(new_dataframe['volume'])
        out_dates = list(outliers['datetime_bin'].apply(lambda d: d.time()))
        out_volumes = list(outliers['volume'])
        
        
        plt.figure(figsize = (17,10))
        plt.scatter(out_dates, out_volumes, c = '#FF00FF', s = 150, alpha = 0.7)
        plt.plot(data_dates, data_volumes, c= 'blue', linewidth = 2.5, alpha = 0.7)
        plt.plot(data_dates, upper, data_dates, lower, c = 'c', alpha = 0.1)
        plt.fill_between(data_dates, lower, upper, facecolor = 'c', alpha = 0.1)
        font = {'family' : 'normal',
            'weight' : 'bold',
            'size'   : 18}
        plt.rc('font', **font)
        plt.title("Volume Anomalies for %s (%s, %s Leg, %s)" % (intersection, str(new_dataframe['datetime_bin'][0].date()), int_leg, direction))
        plt.xlabel("Timestamp")
        plt.ylabel("Volume")
        plt.xticks(data_dates[::4], fontsize = 12, rotation = 30)
        plt.tight_layout()
        plt.show()


# trend ()produces a trend plot, with a data cutoff located at the moment new data is introduced to the dataset. Moreover, it highlights trend bounds of historic data.
# Ideally, the trend of the new data should not veer off from the upper and lower bounds. If the new data does, the trend component is likely deviating significantly 
# the norm, and the new data should be investigated

def trend(dow, intersection, direction, int_leg, new_dataframe):
    
    ## trend: str str str str str => matplotlibplot 
    
    ## requires: dow, intersection, direction, int_leg: strings as used in all previous functions
    ##           new_dataframe: pd.DataFrame containing two columns- 'datetime_bin' and 'volume'
    ##                          The format of this dataframe is the same as the one returned by
    ##                          the grab function
    
    # grab data
    data = grab(dow, intersection, direction, int_leg)
    data['datetime_bin'] = pd.to_datetime(data['datetime_bin'])
    intervals = len(data.groupby(data['datetime_bin'].dt.strftime('%d')).count()['datetime_bin']) #number of periods
    
    rdata = ts(append(data.volume.values, new_dataframe.volume.values), frequency = 56)
    
    rstring="""function(testdata){
                library(forecast)
                decomp <- stl(testdata, s.window = 'periodic')
                outdf<-as.data.frame(decomp$time.series)
                outdf
                }"""
    
    rfunc = robjects.r(rstring)
    r_df = rfunc(rdata)
    decomp_as_df = pandas2ri.ri2py(r_df)  
    
    trendvalues = decomp_as_df['trend'] #all data including new data
    oldtrend = trendvalues[0:len(data)-1] #old data
    
    # Create bounds (via scipy.stats.iqr and numpy.percentile)
    pct = [percentile(oldtrend, 25), percentile(oldtrend, 75)] #25th percentile and 75th
    iqrange = (iqr(oldtrend))
    lower_bound = pct[0] - (iqrange * 1.5)
    upper_bound = pct[1] + (iqrange * 1.5)
    
    
    if False in list(lower_bound <= trendvalues[len(data):]) or False in list(upper_bound >= trendvalues[len(data):]):
        # Plot Data With Bounds and data cutoff
        print(1)
        plt.figure(figsize = (18,10))
        plt.plot(trendvalues, linewidth = 2, color = 'blue', alpha = 0.7, label = 'Trend Volume')
        plt.axvline(x=(56*intervals)-1, c = '#FF00FF', linewidth = 4, alpha = 0.7, linestyle = '--', label = 'New Data Cutoff')
        plt.axhline(lower_bound, alpha = 0.5, color = 'c')
        plt.axhline(upper_bound,  alpha = 0.5, color = 'c')
        plt.axhspan(lower_bound, upper_bound, alpha = 0.1, facecolor = 'c', label = 'Trend Bounds')
        plt.title("%s Trendline with New Data (%s Leg, %s)" % (intersection, int_leg, direction))
        plt.ylabel("Volume Trend")
        plt.legend()
        plt.show()



# run the script over all distinct combos 

for i in range(len(newest)): 
    strSQL = '''SELECT extract(dow from datetime_bin) as dow
                FROM miovision.volumes_15min_new
                LIMIT 1'''
    
    dow = int(pandasql.read_sql(pg.SQL(strSQL), con)['dow'].values[0])
    
    intersection = newest['intersection_name'].values[i]
    
    direction = newest['dir'].values[i]
    
    int_leg = newest['leg'].values[i]
    
    strSQL = '''SELECT datetime_bin, sum(volume) as volume
                    	FROM miovision.volumes_15min_new
                    	INNER JOIN miovision.intersections USING (intersection_uid)
                    	WHERE classification_uid in (1,4,5)
                    	AND intersection_name = '%s'
                    	AND (leg = '%s' AND dir = '%s')
                    	and extract('hour' from datetime_bin) >= 6
                    	and extract('hour' from datetime_bin) < 20
                GROUP BY datetime_bin
                ORDER BY datetime_bin''' % (intersection, int_leg.upper(), direction.upper()) 
                
    new_data = pandasql.read_sql(pg.SQL(strSQL), con)
    
    for j in ['trend', 'anomalous']:
        
        if j == 'anomalous':
            anomalous(dow, intersection, direction, int_leg, new_data)
        
        elif j == 'trend':
            trend(dow, intersection, direction, int_leg, new_data)


con.close() 





















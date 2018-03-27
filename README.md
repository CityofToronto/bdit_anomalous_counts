# Anomalous Counts Project

## Overview
The City of Toronto is currently receiving multimodal count data at 30+ in the downtown core. This data will start being ingested into the team's internal database on an daily basis.

The purpose of this project is to build a tool to identify anomalous data for potential investigation as an initial screen for QC.

## Key Questions

**1. Does the data generally look OK?:"** For a specific mode-leg-direction-intersection-date combination, does the data overall appear to be in line with past data?

**2. Are there any strange data points?:** Does any of the more granular data points look completely out of line? If too low, this may be indicative of an incident or road closure. If too high, this may be indicative of a special event. Either way, these should be investigated.

## Decision Points
Prior to implementation, some research and exploratory analysis will be required in order to make decisions on a number of key components of this model.

**1. What Type of Model?:** Given the wide variety of case studies available in the subject area of time series modelling and anomaly detection, there are a number of different approaches that could be implemented for this project. Possible options include ARIMA, Seasonal-trend detection using LOESS (STL), or some clustering-derived metric.

**2. What Level of Granularity?:** What granularity provides the right balance between predictive power (given a larger dataset) and limited noise? Possible options include 15 minutes, 30 minutes, or 1 hour.

**3. How Should Days be Grouped?:** What groupings should be used to categorize weekdays together for comparison? Should two seperate categories be created for weekdays (e.g. Mon-Wed, Thu-Fri)? Should each weekday be treated seperately? What about weekends? Should this decision be made individually for each intersection or treated as a general rule across all intersections? And if the former, can this decision be automated?

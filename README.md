# Anomalous Counts Project

## Overview
The City of Toronto is currently receiving multimodal count data at 30+ in the downtown core. This data will start being ingested into the team's internal database on an daily basis.

The purpose of this project is to build a tool to identify anomalous data for potential investigation as an initial screen for QC.

## Decision Points
Prior to implementation, some research and exploratory analysis will be required in order to make decisions on a number of key components of this model.

**1. What Type of Model?:** Given the wide variety of case studies available in the subject area of time series modelling and anomaly detection, there are a number of different approaches that could be implemented for this project. Possible options include ARIMA, Seasonal-trend detection using LOESS (STL), or some clustering-derived metric.

**2. What Level of Granularity?:** 

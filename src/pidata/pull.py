import sys
import clr

sys.path.append(r'C:\Program Files (x86)\PIPC\AF\PublicAssemblies\4.0')
clr.AddReference('OSIsoft.AFSDK')

from OSIsoft.AF import *
from OSIsoft.AF.PI import *
from OSIsoft.AF.Asset import *
from OSIsoft.AF.Data import *
from OSIsoft.AF.Time import *
from OSIsoft.AF.UnitsOfMeasure import *

piServers = PIServers()

import datetime
import time
import pandas as pd
import numpy as np
import json

from dateutil.relativedelta import relativedelta, MO
from dateutil import parser

from .utils import strip_timestamp


def aggregated_vals(tags, start_time="-30d", end_time="", interval='12h', method='Average', server='default'):

    """Will return a pandas dataframe of aggregated values (averaged values by default) between `start_time` and `end_time`, within the given interval
    
    Arguments: 
    tags         :  list or list like
    start_time   :  Time of the first data point. Default: '-30d' (thirty days ago)
    end_time     :  Time of the last data point. Default: '' (empty/current time)
    interval     :  Time between data points. Default: '12h'
    method       :  Instead of returning the average value over the interval, the returned values can be specified as one of the following: 
                    Total
                    Average (Default)
                    Minimum
                    Maximum
                    Range
                    StdDev - Standard deviation.
                    PopulationStdDev - Population standard deviation.
                    Count
                    PercentGood - Percentage of data with good value. 
                    TotalWithUOM
                    All
                    AllForNonNumeric
                    Please see: https://techsupport.osisoft.com/Documentation/PI-AF-SDK/html/T_OSIsoft_AF_Data_AFSummaryTypes.htm
    server       :  Name of the PI server to use. Uses the default if none is provided"""
                 

    if server != 'default':
        piServer = PIServer.FindPIServer(server)
    else:
        piServer = piServers.DefaultPIServer
        
    if piServer is None:
        piServer = piServers.DefaultPIServer
        
    time_range = AFTimeRange(start_time, end_time)
    span = AFTimeSpan.Parse(interval)
    
    data = pd.DataFrame(columns=tags)
    
    for tag in tags: 
        pt = PIPoint.FindPIPoint(piServer, tag)
        name = pt.Name.lower()
        
        summary_type_object = eval('AFSummaryTypes.' + method)
        averages = pt.Summaries(time_range, span, summary_type_object, AFCalculationBasis.TimeWeighted, AFTimestampCalculation.Auto)
        
        for average in averages:
            for event in average.Value:                        
                 try:
                     data.at[strip_timestamp(event.Timestamp), tag] = np.float32(event.Value)
                 except TypeError:
                     data.at[strip_timestamp(event.Timestamp), tag] = None # On exception populate with NaN
                   
    return data

def recorded_vals(tags, start_time="-30d", end_time="", server='default'):
    """Will return a pandas df of recorded vals between start and end time, with an the given interval
    
    Arguments: 
    tags         :  list or list like
    start_time   :  Time of the first data point. Default: '-30d' (thirty days ago)
    end_time     :  Time of the last data point. Default: '' (empty/current time)
    server       :  Name of the PI server to use. Uses the default if none is provided"""
    
    if server != 'default':
        piServer = PIServer.FindPIServer(server)
    else:
        piServer = piServers.DefaultPIServer
        
    if piServer is None:
        piServer = piServers.DefaultPIServer
        
    time_range = AFTimeRange(start_time, end_time)
    
    data = pd.DataFrame(columns=tags)
    
    for tag in tags: 
        pt = PIPoint.FindPIPoint(piServer, tag)
        name = pt.Name.lower()
        
        recorded = pt.RecordedValues(time_range, AFBoundaryType.Inside, "", False)
        
        for event in recorded:
            try:
                data.at[strip_timestamp(event.Timestamp), tag] = np.float32(event.Value)
            except TypeError:
                data.at[strip_timestamp(event.Timestamp), tag] = None # On exception populate with NaN
    
    return data

def interp_vals(tags, start_time="-30d", end_time="", interval='12h', server='default'):
    """Will return a pandas df of averaged vals between start and end time, with an the given interval
    
    Arguments:  
    tags         :  list or list like
    start_time   :  Time of the first data point. Default: '-30d' (thirty days ago)
    end_time     :  Time of the last data point. Default: '' (empty/current time)
    interval     :  Time between data points. Default: '12h'
    server       :  Name of the PI server to use. Uses the default if none is provided"""
    
    if server != 'default':
        piServer = PIServer.FindPIServer(server)
    else:
        piServer = piServers.DefaultPIServer
        
    if piServer is None:
        piServer = piServers.DefaultPIServer
    
    time_range = AFTimeRange(start_time, end_time)
    span = AFTimeSpan.Parse(interval)
    
    data = pd.DataFrame(columns=tags)
    
    for tag in tags: 
        pt = PIPoint.FindPIPoint(piServer, tag)
        name = pt.Name.lower()
        
        interpolated = pt.InterpolatedValues(time_range, span, "", False)
        
        for event in interpolated: 
            if str(event.Value) == 'Bad Input': # Revise this at some point 
                None
            else:
                data.at[strip_timestamp(event.Timestamp), tag] = event.Value
    
    return data


def current_vals(tags, server='default'):
    """Returns the last recorded values at the time of running the function

    Arguments: 
    tags         :  list or list like
    server       :  Name of the PI server to use. Uses the default if none is provided"""
    
    if server != 'default':
        piServer = PIServer.FindPIServer(server)
    else:
        piServer = piServers.DefaultPIServer
        
    if piServer is None:
        piServer = piServers.DefaultPIServer
        
    return [PIPoint.FindPIPoint(piServer, tag).CurrentValue().Value for tag in tags]
    

def batch_aggregated_vals(tags, start_time, end_time, interval,period,increment,method='Average',verbose=False,save_csv=False,filename="",return_df=True, server='default'):
    """ 
    Puprose: fetch large averaged data in batches to ease load on server
    function parameter description:
    tags        : list of tags to download
    start_time  : start date time in string format where batch fetch begin
    end_time    : end data time in string format where batch ends
    interval    : period over which to average data e.g. '4H', '2D'
    method      : aggregation method that will be given to aggregated_vals
    period      : time period to define batch size e.g. 'days','months'
    increment   : number of time periods in a batch
    verbose     : verbose output of progress (default = False)
    save_csv    : save progress files. Default is False.
    filename    : name of file without the extension.  Function will add suffix
    return_df   : whether or not to return the data as a pandas dataframe (default=True)
    """
    
    if server != 'default':
        piServer = PIServer.FindPIServer(server)
    else:
        piServer = piServers.DefaultPIServer
        
    if piServer is None:
        piServer = piServers.DefaultPIServer
        
    bigdata=pd.DataFrame()
    if save_csv:
        filename_suffix = filename+'.csv'
        with open(filename_suffix, 'w') as f:
            bigdata.to_csv(f, header=False) #create empty csv file/overwrite any file with the same name 
    
    start_dt = parser.parse(start_time)    #the start time
    end_dt = parser.parse(end_time)    # the end of the time
    suffix=1
    if verbose:
        print('Collecting data from %s to %s as %s-ly averages in batches of  %s %s:' % (start_time, end_time, interval,increment,period))
    kwargs={period:increment}
    block_end = start_dt+relativedelta(**kwargs)
    while block_end < end_dt:
        if verbose:
            print('Collecting block %s to %s' % (str(start_dt), str(block_end)))
        data = aggregated_vals(tags,str(start_dt),str(block_end),interval,method=method)
        data.index.names = ['DateTime']
        bigdata = bigdata.append(data, sort=True, verify_integrity=True)

        if verbose:
            print('Done')
            
        if save_csv:
            filename_suffix = filename+'.csv'
            open_file_method = 'w' if suffix==1 else 'a'
            add_headings = True if suffix==1 else False
            with open(filename_suffix, open_file_method) as f:
                bigdata.to_csv(f, header=add_headings)
            bigdata = pd.DataFrame() #reset the bigdata variable in save_csv mode
            if verbose:
                print('Progress saved to %s' % (filename_suffix))
                
        start_dt=block_end
        block_end =start_dt+relativedelta(**kwargs)
        suffix=suffix+1
    if verbose:
        print('Collecting block %s to %s' % (str(start_dt), str(end_dt)))     
    data = aggregated_vals(tags,str(start_dt),str(end_dt),interval,method=method)
    data.index.names = ['DateTime']
    bigdata = bigdata.append(data,sort=True, verify_integrity=True)
    if verbose:
        print('Batch fetch completed.')
    
    if save_csv:
        filename_suffix = filename+'.csv'
        with open(filename_suffix, 'a') as f:
            bigdata.to_csv(f, header=False)

        if verbose:
            print('Data saved to %s' % (filename_suffix))
            
    if return_df:
        if save_csv:
            return pd.read_csv(filename_suffix, index_col=0)
        else: 
            return bigdata.astype(float)
        
    else: 
        return None

def batch_recorded_vals(tags, start_time, end_time,period,increment,verbose=False,save_csv=False,filename="",return_df=True, server='default'):
    """ 
    Puprose: fetch large averaged data in batches to ease load on server
    function parameter description:
    tags        : list of tags to download
    start_time  : start date time in string format where batch fetch begin
    end_time    : end data time in string format where batch ends
    
    
    period      : time period to define batch size e.g. 'days','months'
    increment   : number of time periods in a batch
    verbose     : verbose output of progress (default = False)
    save_csv    : save progress files. Default is False.
    filename    : name of file without the extension.  Function will add suffix
    return_df   : whether or not to return the data as a pandas dataframe (default=True)
    """
    
    if server != 'default':
        piServer = PIServer.FindPIServer(server)
    else:
        piServer = piServers.DefaultPIServer
        
    if piServer is None:
        piServer = piServers.DefaultPIServer
        
    bigdata=pd.DataFrame()
    if save_csv:
        filename_suffix = filename+'.csv'
        with open(filename_suffix, 'w') as f:
            bigdata.to_csv(f, header=False) #create empty csv file/overwrite any file with the same name 
    
    start_dt = parser.parse(start_time)    #the start time
    end_dt = parser.parse(end_time)    # the end of the time
    suffix=1
    if verbose:
        print('Collecting data from %s to %s in batches of  %s %s:' % (start_time, end_time,increment,period))
    kwargs={period:increment}
    block_end = start_dt+relativedelta(**kwargs)
    while block_end < end_dt:
        if verbose:
            print('Collecting block %s to %s' % (str(start_dt), str(block_end)))
        data = recorded_vals(tags,str(start_dt),str(block_end))
        data.index.names = ['DateTime']
        bigdata = bigdata.append(data, sort=True, verify_integrity=True)

        if verbose:
            print('Done')
            
        if save_csv:
            filename_suffix = filename+'.csv'
            open_file_method = 'w' if suffix==1 else 'a'
            add_headings = True if suffix==1 else False
            with open(filename_suffix, open_file_method) as f:
                bigdata.to_csv(f, header=add_headings)
            bigdata = pd.DataFrame() #reset the bigdata variable in save_csv mode
            if verbose:
                print('Progress saved to %s' % (filename_suffix))
                
        start_dt=block_end
        block_end =start_dt+relativedelta(**kwargs)
        suffix=suffix+1
    if verbose:
        print('Collecting block %s to %s' % (str(start_dt), str(end_dt)))     
    data = recorded_vals(tags,str(start_dt),str(end_dt))
    data.index.names = ['DateTime']
    bigdata = bigdata.append(data,sort=True, verify_integrity=True)
    if verbose:
        print('Batch fetch completed.')
    
    if save_csv:
        filename_suffix = filename+'.csv'
        with open(filename_suffix, 'a') as f:
            bigdata.to_csv(f, header=False)

        if verbose:
            print('Data saved to %s' % (filename_suffix))
            
    if return_df:
        if save_csv:
            return pd.read_csv(filename_suffix, index_col=0)
        else: 
            return bigdata.astype(float)
        
    else: 
        return None


def recorded_vals_dict(tags, start_time="-30d", end_time="", server='default'):
    """A dictionary version of the recorded vals function for better efficiency for large amounts of data
    Will return a dictionary of recorded vals between start and end time, with an the given interval
    Arguments: 
    tags: list or list like"""

    if server != 'default':
        piServer = PIServer.FindPIServer(server)
    else:
        piServer = piServers.DefaultPIServer
        
    if piServer is None:
        piServer = piServers.DefaultPIServer
        
    time_range = AFTimeRange(start_time, end_time)

    data = {tag : {} for tag in tags}

    for tag in tags: 
        pt = PIPoint.FindPIPoint(piServer, tag)
        name = pt.Name.lower()

        recorded = pt.RecordedValues(time_range, AFBoundaryType.Inside, "", False)

        for event in recorded:
            data[tag][event.Timestamp.ToString(AFLocaleIndependentFormatProvider())] = str(event.Value)

    return data


def batch_recorded_vals_dict(tags, start_time, end_time,period,increment,verbose=False,save_csv=False,filename="",return_df=True, server='default'):
    """ 
    A dictionary version of the batch recorded vals function for better efficiency for large amounts of data

    Puprose: fetch large averaged data in batches
    function parameter description:
    tags        : list of tags to download
    start_time  : start date time in string format where batch fetch begin
    end_time    : end data time in string format where batch ends
    
    
    period      : time period to define batch size e.g. 'days','months'
    increment   : number of time periods in a batch
    verbose     : verbose output of progress (default = False)
    save_csv    : save progress files. Default is False.
    filename    : name of file without the extension.  Function will add suffix
    return_df   : whether or not to return the data as a pandas dataframe (default=True)
    """
     
    if server != 'default':
        piServer = PIServer.FindPIServer(server)
    else:
        piServer = piServers.DefaultPIServer
        
    if piServer is None:
        piServer = piServers.DefaultPIServer
        
    bigdata = {tag : {} for tag in tags}
    start_dt = parser.parse(start_time)    #the start time
    end_dt = parser.parse(end_time)    # the end of the time
    suffix=1
    if verbose:
        print('Collecting data from %s to %s in batches of  %s %s:' % (start_time, end_time,increment,period))
    kwargs={period:increment}
    block_end = start_dt+relativedelta(**kwargs)
    while block_end < end_dt:
        if verbose:
            print('Collecting block %s to %s' % (str(start_dt), str(block_end)))
        data = recorded_vals_dict(tags,str(start_dt),str(block_end))
        
        for tag in tags:
            bigdata[tag].update(data[tag])

        if verbose:
            print('Done')
            
                
        start_dt=block_end
        block_end =start_dt+relativedelta(**kwargs)
        suffix=suffix+1
    if verbose:
        print('Collecting block %s to %s' % (str(start_dt), str(end_dt)))     
    data = recorded_vals_dict(tags,str(start_dt),str(end_dt))

    bigdata[tag].update(data[tag])
    if verbose:
        print('Batch fetch completed.')
    
    if save_csv:
        filename_suffix = filename+'.json'
        j = json.dumps(bigdata)
        with open(filename_suffix, 'w') as f:
            f.write(j)
            f.close()

        if verbose:
            print('Data saved to %s' % (filename_suffix))
            
    if return_df:

#         if save_csv:
#             return pd.read_csv(filename_suffix, index_col=0)
#         else: 
        return bigdata
        
    else: 
        return None
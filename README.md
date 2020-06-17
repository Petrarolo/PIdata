# PIdata
An easy to use python package for extracting data from an OSI PI historian/server via the OSI PI SDK. Based on this blog post: https://pisquare.osisoft.com/people/rborges/blog/2016/08/01/pi-and-python-pithon

## Rules for the package and new features:
1. Written in python/ironpython
2. Simple to use (specifically for people new to python)
3. Customisable (exposing the PI SDK as python functions/objects)
4. Integrate well with existing python handling tools (e.g. pandas dfs)
5. Does not reinvent existing tools as these are what makes python great

## Prerequisites: 
OSI PI installed on your machine, connected the historian (probably already the case if you were looking for this package)

## Installation:

    pip install PIdata

## Basic usage:
To pull hourly averages for the '24T1345.PV' tag:

    df = pidata.pull.aggregated_vals(['24T1345.PV'], start_time='1/1/2020', end_time='2/2/2020', interval='1h')

## Similar projects:
A python library for OSIsoft's PI Web API
FernandoRodriguezP/OSIsoftPy
onamission21/AF-SDK-for-Python
alyasaud/PITHON

## Contributing
I shared this package because it makes my life easier and hoped others would also find it useful. If you do, please star the repo on github and share with your colleagues. 
Many thanks to the people that have contributed their code thus far. Please feel free to submit a pull request, report a bug or request a feature.

## Functions: 

### Pull functions (pidata.pull)

#### pidata.pull.aggregated_vals
Will return a pandas df of aggregated values (averaged values by default) between start and end time, within the given interval
    
    Arguments: 
    tags         :  list or list like
    method       :  Instead of returning the average value over the interval, the returned value can be specified as one of the following: 
                    Total - A totalization over the time range.
                    Average - The average value over the time range.
                    Minimum - The minimum value over the time range.
                    Maximum - The maximum value over the time range.
                    Range - The range of values over the time range (Maximum-Minimum)
                    StdDev - The standard deviation over the time range.
                    PopulationStdDev - The population standard deviation over the time range.
                    Count - The sum of event count over the time range when calculation basis is event weighted. The sum of event time duration over the time range when calculation basis is time weighted.
                    PercentGood - Percent of data with good value during the calculation period. For time weighted calculations, the percentage is based on time.
                    TotalWithUOM, All, AllForNonNumeric (TODO)
                    Please see: https://techsupport.osisoft.com/Documentation/PI-AF-SDK/html/T_OSIsoft_AF_Data_AFSummaryTypes.htm

#### pidata.pull.recorded_vals
Will return a pandas df of recorded vals between start and end time, with an the given interval
    
    Arguments: 
    tags: list or list like

#### pidata.pull.interp_vals
Will return a pandas df of averaged vals between start and end time, with an the given interval
    
    Arguments: 
    tags: list or list like

#### pidata.pull.current_vals

#### pidata.pull.batch_aggregated_vals
Puprose: fetch large averaged data in batches
    
    Arguments:
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

#### pidata.pull.batch_recorded_vals
Puprose: fetch large averaged data in batches
    
    Arguments: 
    tags        : list of tags to download
    start_time  : start date time in string format where batch fetch begin
    end_time    : end data time in string format where batch ends
    period      : time period to define batch size e.g. 'days','months'
    increment   : number of time periods in a batch
    verbose     : verbose output of progress (default = False)
    save_csv    : save progress files. Default is False.
    filename    : name of file without the extension.  Function will add suffix
    return_df   : whether or not to return the data as a pandas dataframe (default=True)
    
#### pidata.pull.recorded_vals_dict
A dictionary version of the recorded vals function for better efficiency for large amounts of data.

#### pidata.pull.batch_recorded_vals_dict
Same as batch_recorded_vals but returns a dictionary. 

### Utility functions (pidata.utils)

#### pidata.utils.strip_timestamp
Internal function. Converts PI timestamp format to python datetime format. 

#### pidata.utils.validate_tags
Will check each PI Tag in list tag and return list of tags found or NOT found (depending on parameter return_found)
    
    tags: list of PI query filters
    returns: list of all tag names that match the PI queries if return_found=True 
             OR list of the given PI queries that did not match any tags if return_found=False


## How do I change the PI Server:
TODO

## Exposing the SDK:
TODO

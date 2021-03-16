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

from dateutil.relativedelta import relativedelta, MO
from dateutil import parser

from .utils import strip_timestamp
    

def fetch_attributes(tags, attributes=[], get_all=False, server='default'):
    """
    Puprose: Returns a dataframe of attributes
    tags       : list
    attributes : list

    Attributes is a list of one or more of the following*:
        Archiving
        ChangeDate
        Changer
        Clamp
        Compressing
        CompressionDeviation
        CompressionMaximum
        CompressionMinimum
        ... for complete list please see https://techsupport.osisoft.com/Documentation/PI-AF-SDK/html/T_OSIsoft_AF_PI_PICommonPointAttributes.htm
    *case insensitive
    """
    
    if server != 'default':
        piServer = PIServer.FindPIServer(server)
    else:
        piServer = piServers.DefaultPIServer
        
    if piServer is None:
        piServer = piServers.DefaultPIServer
    
    data = pd.DataFrame(columns=tags)

    for tag in tags: 
        point_object = PIPoint.FindPIPoint(piServer, tag)
        
        if get_all == True: 
            #find the names of valid attributes
            attributes = point_object.FindAttributeNames('')
        
        point_object.LoadAttributes('') #will load all the available attributes, can limit this to only the desired ones
        fetched_attributes = point_object.GetAttributes(attributes) # a dictionary with 'attributes' as the keys 
        point_object.UnloadAllAttributes('')
        
        #then load into dataframe (later: load into dictionary then convert to dataframe)
        for i in attributes:
            data.at[i, tag] = fetched_attributes[i]
    
    return data
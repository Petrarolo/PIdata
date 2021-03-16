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
piServer = piServers.DefaultPIServer;

import datetime
import time
import pandas as pd
import numpy as np

from dateutil.relativedelta import relativedelta, MO
from dateutil import parser


def strip_timestamp(timestamp):
    """Converts PI timestamp format to python datetime format"""
    return datetime.datetime.strptime(timestamp.ToString(AFLocaleIndependentFormatProvider()), '%m/%d/%Y %H:%M:%S')


def validate_tags(tags,return_found=True, server='default'):
    """Will check each PI Tag in list tag and return list of tags found or NOT found (depending on parameter return_found)
    
    tags: list of PI query filters
    returns: list of all tag names that match the PI queries if return_found=True 
             OR list of the given PI queries that did not match any tags if return_found=False"""

    if server != 'default':
        piServer = PIServer.FindPIServer(server)
    else:
        piServer = piServers.DefaultPIServer
        
    if piServer is None:
        piServer = piServers.DefaultPIServer
        
    checklist=[]
    for tag in tags:

        points=PIPoint.FindPIPoints(piServer,tag)
        
        valid_tags=0
        for pt in points:
            valid_tags +=1
            if return_found:
                checklist.append(str(pt))
                
        if not return_found and valid_tags==0:
            checklist.append(tag)

    return list(set(checklist)) #maybe remove the list() function
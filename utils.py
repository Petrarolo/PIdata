import sys
import clr

sys.path.append(r'C:\Program Files (x86)\PIPC\AF\PublicAssemblies\4.0')
clr.AddReference('OSIsoft.AFSDK')

piServers = PIServers()
piServer = piServers.DefaultPIServer;

from OSIsoft.AF.Time import AFLocaleIndependentFormatProvider

import datetime


def strip_timestamp(timestamp):
    """Converts PI timestamp format to python datetime format"""
    return datetime.datetime.strptime(timestamp.ToString(AFLocaleIndependentFormatProvider()), '%m/%d/%Y %H:%M:%S')


def validate_tags(tags,return_found=True):
    """Will check each PI Tag in list tag and return list of tags found or NOT found (depending on parameter return_found)
    
    tags: list of PI query filters
    returns: list of all tag names that match the PI queries if return_found=True 
             OR list of the given PI queries that did not match any tags if return_found=False"""

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
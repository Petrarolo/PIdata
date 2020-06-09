# PIdata
An easy to use python package for extracting data from an OSI PI historian/server via the OSI PI SDK. Based on this blog post: https://pisquare.osisoft.com/people/rborges/blog/2016/08/01/pi-and-python-pithon

Rules for the package and new features:
1. Writen in python/ironpython
2. Simple to use (specifically for people new to python)
3. Customisable (exposing the PI SDK as python functions/objects)
4. Integrate well with existing python handling tools (e.g. pandas dfs)
5. Does not reinvent existing tools as these are what makes python great

Methods
pidata
	pull (historised data extraction)
		aggregated_vals 
        recorded_vals
		interp_vals
        current_vals
        batch_aggregated_vals
        batch_recorded_vals
        batch_aggregated_vals_json
        batch_recorded_vals_json
	meta (tag metadata extraction)
		get_attributes/attributes
    utils (utility functions)
        strip_timestamp
        validate_tags

Prerequisites: 
OSI PI installed on your machine, connected the historian (probably already the case if you were looking for this package)

Installation:
pip install PIdata

Usage:
TODO

Similar projects:
A python library for OSIsoft's PI Web API
FernandoRodriguezP/OSIsoftPy
onamission21/AF-SDK-for-Python
alyasaud/PITHON

Contributing
I shared this package because it makes my life easier and hoped others would also find it useful. If you do, please star the repo on github and share with your colleagues. 
Many thanks to the people that have contributed their code thus far. Please feel free to submit a pull request, report a bug or request a feature.

How do I change the PI Server:
TODO

Exposing the SDK:
TODO

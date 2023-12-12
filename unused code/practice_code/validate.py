# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 16:12:40 2023

@author: 20230077
"""

def validate(TE, TR, TI, slice):
    valid = True 
    messages = {}
    
    try: TE = float(TE)
    except: 
        valid = False
        messages['TE'] = "Invalid TE value"
    
    try: TR = float(TR)
    except: 
        valid = False
        messages['TR'] = "Invalid TR value"
    
    try: TI = float(TI)
    except: 
        valid = False
        messages["TI"] = "Invalid TI value"
    
    try: slice = int(slice)
    except: 
        valid = False
        messages["slice"] = "Invalid slice value"
    
    return valid, messages 
    
[result,messages] = validate("dfdf",2,"erere",4.2)
if result == False: 
    print("false") 
else: print("true")

for key in messages:
    print(messages[key])
    
if "TR" in messages:
    messages["TR"] = messages["TR"] + ("Another message")
    
else: messages["TR"] = "Another message"   
print(messages["TR"])
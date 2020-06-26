# This is part of MiMiCPy

"""

This module contains the helper functions to efficiently
convert a pdb line to dict, or convert the whole file to a dataframe

"""

from .parser import Parser
from ..utils.errors import MiMiCPyError
import pandas as pd

keys = ['record', 'serial', 'name', 'altLoc', 'resname', 'chainID', 'resid', 'iCode', 'x', 'y', 'z',\
        'occupancy', 'tempFactor', 'element', 'charge']

def readLine(line):
    vals = {}
    vals['record'] = line[:6].strip()
    
    if vals['record'] != 'HETATM' and vals['record'] != 'ATOM':
        vals['content'] = line[6:]
        return vals
    
    vals['serial'] = line[6:11].strip()
    vals['name'] = line[12:16].strip()
    vals['altLoc'] = line[16]
    vals['resname'] = line[17:20].strip()
    vals['chainID'] = line[21]
    vals['resSeq'] = line[22:26].strip()
    vals['iCode'] = line[26]
    vals['x'] = line[30:38].strip()
    vals['y'] = line[38:46].strip()
    vals['z'] = line[46:54].strip()
    vals['occupancy'] = line[54:60].strip()
    vals['tempFactor'] = line[60:66].strip()
    vals['element'] = line[76:78].strip()
    vals['charge'] = line[78:80].strip()
    
    return vals

def parseFile(pdb, lines=1000):
    # ATOM/HETATM line is always 78 bytes/chars
    file = Parser(pdb, 78*lines)
    
    pdb_lst = []
    
    for chunk in file:
        
        for line in chunk.splitlines():
            try:
                vals = readLine(line)
            except: # if only part of line was read
                file.f.seek(-len(line), 1) # push back the file pointer to start of line
            
            if vals['record'] == 'ATOM' or vals['record'] == 'HETATM':
                pdb_lst.append(vals)
                
    return pd.DataFrame(pdb_lst)

def _fitStr(s, n):
    return (n - len(s))*' '

def _errHandle(s, mx):
    s = s.strip()
    if len(s) > mx:
        return s[:len(s)-mx+1]
    elif len(s) < 1:
        return ' '
    else:
        return s
    
def _fitNo(no, space):
    if isinstance(no, str):
        raise MiMiCPyError(f"{no} is string, expected numeric")
    
    float_len = len(str(no))
    int_len = len(str(int(no)))
    
    #print((no, space, float_len, int_len, space-int_len-2))
    
    if float_len <= space:
        return str(no)+(" "*(space-float_len))
    else:
        extra = space-int_len-1
        return '{:.{}f}'.format(round(no, extra), extra)
    
def _charge(no):
    q = round(no)
    if q > 9: q = 1 # not space for q > 9
    
    if q == 0: return "0 "
    elif q > 0: return f"{q}+" 
    else: return f"{-q}-"

def writeLine(record='ATOM', serial='1', name='XX', altLoc=' ', resname='XXX', chainID='A',\
              resid=1, iCode=' ', x=00.00, y=00.00, z=00.00, occupancy=1.00, tempFactor=00.00,
              element='C', charge=' '):
    
    record = _errHandle(record, 6)
    record = record + _fitStr(record, 6)
    
    serial = _fitNo(serial, 5)
    
    name = _errHandle(name, 4)
    #name = ' ' + name
    name = _fitStr(name, 4) + name
    
    altLoc = _errHandle(altLoc, 1)
    
    resname = _errHandle(resname, 3)
    resname = resname + _fitStr(resname, 3)
    
    chainID = _errHandle(chainID, 1)
    
    resid = _errHandle(str(resid), 1)
    resid = _fitStr(resid, 4) + resid
    
    iCode = _errHandle(iCode, 1)
    
    x = _fitNo(x, 7) + ' '
    y = _fitNo(y, 7) + ' '
    z = _fitNo(z, 7) + ' '
    
    occupancy = _errHandle(str(occupancy), 6)
    occupancy = _fitStr(occupancy, 6) + occupancy
    
    tempFactor = _errHandle(str(tempFactor), 6)
    tempFactor = _fitStr(tempFactor, 6) + tempFactor
    
    element = ''.join([e for e in element if e.isalpha()])
    element = _errHandle(element, 2)
    element = _fitStr(element, 2) + element
    
    charge = _charge(charge)
    
    return record + serial + ' ' + name + altLoc + resname + ' ' + chainID + resid + iCode + ' '*3 +\
            x + y + z + occupancy + tempFactor + ' '*10 + element + charge

def writeFile(df, box=[]):
    
    df['serial'] = df.index
    
    col_to_drop = [l for l in df.columns if l not in keys]
    df = df.drop(col_to_drop, axis=1)
    
    pdb = ''
    
    for i, row in df.iterrows():
        pdb += writeLine(**row.to_dict()) + '\n'
    
    # add box writing
    pdb = "REMARK    GENERATED BY MIMICPY\nMODEL        1\n"+pdb+"TER\nENDMDL"
    
    return pdb
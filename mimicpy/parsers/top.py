from . import top_reader
import re
import os

def read(topol_file, nonstd_atm_types={}, buff=1000, guess_elems=True):
    file = top_reader.Parser(topol_file, buff)
    # we assume that .top if not too big and can be fully loaded to memory
    # gromacs usually only writes at most one molecule to .top file
    topol_txt = "".join(file)
    
    # get all itp files in .top
    include_file_list = re.compile(r"#include\s+[\"\'](.+)\s*[\"\']", re.MULTILINE).findall(topol_txt)
    
    # get ffnonbonded.itp in forcefield directory
    ffnonbonded = os.path.join(os.path.dirname(include_file_list[0]), 'ffnonbonded.itp')
    atm_types = top_reader.atomtypes(ffnonbonded, buff) # get atomtypes to symb dict
    atm_types.update(nonstd_atm_types)
    
    mols_data = top_reader.molecules(topol_txt) # mol, no. list
    mols = [m[0] for m in mols_data]
    
    # clear the mol_df of ITPParser
    # this is a static var of class, so is const b/w objects
    top_reader.ITPParser.mol_df = {}
    
    
    itp_parser = top_reader.ITPParser(mols, atm_types, buff, guess_elems) # init itp parser
    
    # parse .top file, in case if some atoms defined these
    itp_parser.parse('topol.top', topol_txt)
    
    # parse itp files
    for file in include_file_list[1:]:
        itp_parser.parse(file)
    
    mol_df = dict(zip(itp_parser.mols, itp_parser.dfs))
    
    return mols_data, mol_df
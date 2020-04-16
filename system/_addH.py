from pygmx.system import handlePDB
import pyshell.local as cmd
from rdkit.Chem import PandasTools
from io import StringIO

def _cleanPdb(sdf, pdb, resname):
    print("Assigning correct atom names..")
    
    atm_names = [a.GetProp('molFileAlias') for i in range(len(sdf)) for a in sdf.loc[i]['ROMol'].GetAtoms()]
    
    pdb_str = ""
    atm_i = 0 # counter for atom name
    h_i = 1 # counter for new hydrogen atom name
    # hydrogen atom names are addedas H1, H2, H3, ....
    for line in pdb.splitlines():
        header = line.split()[0]
        if header == "HETATM":
            line = handlePDB.editLine(line, name=atm_names[atm_i], resName=resname)
            atm_i += 1
        elif header == "ATOM":
        #ATOM is hydrogen atom, so add H1, H2...
            hstr = "H" + str(h_i) # create hydrogen atom name
            line = handlePDB.editLine(line, name=hstr, resName=resname) # add the res name also
            h_i += 1
        
        pdb_str += line + '\n'

    return pdb_str

def _multChains(pdb):
    pdb_str = ""
    n_chains = 0
    stack = []
    stack_idx = 0
    
    print("Assigning correct chain IDs..")
    
    for line in pdb.splitlines():
        splt = handlePDB.readLine(line)
        
        if splt['record'] == "COMPND":
            n_chains += 1
            stack_idx = 0
            
        if splt['record'] == "HETATM" or splt['record'] == "ATOM":
            
            line = handlePDB.editLine(line, chainID=chr(ord('A')+n_chains-1), resSeq=str(n_chains))
            if splt['element'] == 'H':
                if n_chains == 1:
                    stack.append(handlePDB.readLine(line)['name'])
                else:
                    line = handlePDB.editLine(line, name=stack[stack_idx])
                    stack_idx += 1
            
        pdb_str += line + '\n'

    return pdb_str, n_chains
    
def do(sdf, pH, name):
    if pH == 0:
        return _donoH(sdf, name)
    
    print("**Adding Hydrogens**")
    
    print(f"Cleaning sdf..")
    
    sdf_text = StringIO()            
    PandasTools.WriteSDF(sdf, sdf_text)
    
    pdb = cmd.runinSeq(['sed', '-n', '-e', '/A    1/,/M  END/!p'],\
                       ['sed', '/^A    1/d'],\
                       ['sed', '/^M  END/d'],\
                       ['print', "Converting to pdb using Openbabel.."],\
                       ['obabel', '-isdf', '-opdb'],\
                       ['print', f'Adding hydrogens at pH={pH}'],\
                       ['obabel', '-ipdb', f'-p {pH}', '-opdb'],\
                       stdin=sdf_text.getvalue(), decode=True)
    
    pdb, chains = _multChains(_cleanPdb(sdf, pdb, name))
    
    pdb = cmd.run('grep', 'HETATM\|ATOM', stdin=pdb, decode=True)
    print("**Done**")
    return pdb, chains

def _donoH(sdf, name):
    sdf_text = StringIO()            
    PandasTools.WriteSDF(sdf, sdf_text)
    print(f"Cleaning sdf..")
    pdb = cmd.runinSeq(['sed', '-n', '-e', '/A    1/,/M  END/!p'],\
                       ['sed', '/^A    1/d'],\
                       ['sed', '/^M  END/d'],\
                       ['print', "Converting to pdb using Openbabel.."],\
                       ['obabel', '-isdf', '-opdb'],
                       stdin=sdf_text.getvalue(), decode=True)
    
    pdb, chains = _multChains(_cleanPdb(sdf, pdb, name))
    
    pdb = cmd.run('grep', 'HETATM\|ATOM', stdin=pdb, decode=True)
    print("**Done**")
    return pdb, chains
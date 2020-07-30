import mimicpy
from mimicpy.parsers.mpt import MPT
from mimicpy.scripts.mdp import MDP
from mimicpy.utils.errors import MiMiCPyError
import pandas as pd
import pytest

class MockSelector():
    def __init__(self):
        dct = {'type': [], 'resid': [], 'resname': [],\
            'name': [], 'charge': [], 'element': [], 'mass': [], 'mol': [], 'x': [], 'y': [], 'z': []}
    
        with open('prepare_test_files/qmatoms.txt', 'r') as f:
            for i, line in enumerate(f.readlines()):
                if i == 0:
                    self.box = line.split()
                elif i == 1:
                    mol = line.strip()
                elif i > 1:
                    name, x, y, z, q = line.split()
                    dct['type'].append(name)
                    dct['name'].append(name)
                    dct['element'].append(name[0])
                    dct['resname'].append(mol)
                    dct['mol'].append(mol)
                    dct['resid'].append(1)
                    dct['mass'].append(0)
                    dct['x'].append(float(x))
                    dct['y'].append(float(y))
                    dct['z'].append(float(z))
                    dct['charge'].append(float(q))
        
        self.df = pd.DataFrame(dct)
        self.df.index = self.df.index + 1
        
    def load(self, a,b):
        return [float(i) for i in self.box]
    
    def select(self, selection=None):
         return self.df
        
def read_mock_cpmd():
    lst = {}
    with open('prepare_test_files/cpmd_params.txt') as f:
        lines = f.readlines()
        lst['mm_box'] = [float(i) for i in lines[0].split()]
        lst['qm_box'] = [float(i) for i in lines[1].split()]
        lst['charge'] = float(lines[2])
        
    with open('prepare_test_files/overlaps.txt') as f:
        lst['overlaps'] = set(f.read().splitlines()[1:])
    
    from collections import defaultdict
    atoms = defaultdict(list)
    
    with open('prepare_test_files/cpmd_atoms.xyz', 'r') as f:
        for i, line in enumerate(f.readlines()):
            if i > 1:
                name, x, y, z = line.split()
                atoms[name].append([float(x),float(y),float(z)])
    
    return lst, atoms
            
        
def test_prepare():
    warns = mimicpy.utils.logger.LogString()
    mimicpy.redirectWarnings(warns)
    
    mock_mpt = MPT([], {}, 'w')
    mock_gro = pd.DataFrame()
    prep = mimicpy.Prepare(mock_mpt, mock_gro, MockSelector())
    
    prep.add()
    prep.delete() # delete all atoms
    
    with pytest.raises(MiMiCPyError) as e:
        assert prep.getInp()
    assert str(e.value) == "No QM atoms have been selected"
    
    prep.add()
    prep.clear() # again should clear everything
    
    mock_mdp = MDP(name='test', tcoupl='yes')
    
    with pytest.raises(MiMiCPyError) as e:
        assert prep.getInp(mdp=mock_mdp)
    assert str(e.value) == "No QM atoms have been selected"
    
    prep.add()
    ndx, cpmd = prep.getInp()
    
    import os
    assert cpmd.mimic.paths == f"1\n{os.getcwd()}"
    
    lst, atoms = read_mock_cpmd()
    
    assert [float(i) for i in cpmd.mimic.box.split()] == lst['mm_box']
    assert [float(i) for i in cpmd.system.cell.split()] == lst['qm_box']
    assert cpmd.system.charge == lst['charge']
    
    overlaps = set(cpmd.mimic.overlaps.splitlines()[1:])
    assert overlaps == lst['overlaps']
    
    assert cpmd.atoms['C'].coords == atoms['C']
    assert cpmd.atoms['H'].coords == atoms['H']
    assert cpmd.atoms['O'].coords == atoms['O']
    
    assert "Total charge of QM region" in warns.val and "not an integer up to 2 decimal places" in warns.val
    
    assert "integrator = mimic not set" in warns.val
    assert "QMMM-grps = QMatoms not set" in warns.val
    assert "Temperature coupling will not be active, set tcoupl = no" in warns.val
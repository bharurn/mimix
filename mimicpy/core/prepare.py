import logging
import pandas as pd
from ..io.mpt import Mpt
from ..scripts.mdp import Mdp
from ..scripts.cpmd import CpmdScript, Pseudopotential
from .._global import _Global as gbl
from ..utils.errors import SelectionError
from ..utils.constants import BOHR_RADIUS


class Preparation:

    def __init__(self, selector):  # TODO: Get box size from Selector
        self.qm_atoms = pd.DataFrame()  # TODO: Make private
        self.selector = selector

    @staticmethod
    def __clean_qdf(qdf):
        columns = Mpt.columns.copy()
        columns.extend(['x', 'y', 'z'])
        columns_to_drop = [l for l in qdf.columns if l not in columns]
        qdf.index = qdf.index.set_names(['id'])
        return qdf.drop(columns_to_drop, axis=1)

    def add(self, selection=None, is_link=False):
        qdf = Preparation.__clean_qdf(self.selector.select(selection))
        qdf.insert(2, 'is_link', [int(is_link)]*len(qdf))
        self.qm_atoms = self.qm_atoms.append(qdf)

    def delete(self, selection=None):
        qdf = Preparation.__clean_qdf(self.selector.select(selection))
        self.qm_atoms = self.qm_atoms.drop(qdf.index, errors='ignore')

    def clear(self):
        self.qm_atoms = pd.DataFrame()

    def get_qm_atoms(self):  # TODO: Use @property
        return self.qm_atoms

    def ndx_group(self):  # TODO: Make group name changeable
        indices = self.qm_atoms.index
        col_len = 15
        space_len = 6
        max_len = len(str(max(indices))) + 1
        spaces = space_len if max_len <= space_len else max_len
        ndx_group = '[ QMatoms ]'
        for i, idx in enumerate(indices):
            if i%col_len == 0:
                ndx_group += '\n'
            ndx_group += "{:{}}".format(idx, spaces) # TODO: Stick to f'...' syntax
        return ndx_group

    def prepare_mimic_run(self, inp_tmp=None, mdp_inp=None, ndx_out=None, inp_out=None):  # TODO: Provide default templates
        """Args:
            inp_tmp: cpmd input file, used as template
            mdp_inp: gromacs input file, checked for errors
            ndx_out: gromacs index file, output
            inp_out: mimic cpmd input file, output
        """

        def qm_cell():
            dims = [0, 0, 0]
            for i, r in enumerate(['x', 'y', 'z']):
                dims[i] = (abs(max(self.qm_atoms[r]) - min(self.qm_atoms[r])) + 0.7)/BOHR_RADIUS
            a, b, c = dims
            cell = ' '.join((str(round(a, 1)), str(round(b/a, 1)), str(round(c/a, 1)), '0 0 0'))
            return cell

        # Check for obvious errors in selection
        if self.qm_atoms.empty:
            raise SelectionError('No atoms have been selected for the QM partition.')

        # Delete self.mpt for better garbage collection
        try:
            del self.selector.mpt
        except AttributeError:
            pass

        # Retrieve number of steps and timestep from mdp_inp and do some checks
        try:
            mdp_inp = Mdp.from_file(mdp_inp)
            maxsteps, timestep, mdp_errors = mdp_inp.check()
        except:
            maxsteps, timestep, mdp_errors = 1000, 5.0, None  # TODO: Give warning that default values will be used
        if mdp_errors:
            logging.warning('Found md parameters which are inconsistent with MiMiC runs:')
            for error in mdp_errors:
                logging.warning('\t %s', error)

        # Create an index group in GROMACS format (and write it to a file)
        qm_ndx_group = self.ndx_group()
        if ndx_out:
            gbl.host.write(qm_ndx_group, ndx_out)
            logging.info('Wrote Gromacs index file to %s', ndx_out)

        # Create CPMD input script
        sorted_qm_atoms = self.qm_atoms.sort_values(by=['is_link', 'element']).reset_index()
        try:
            cpmd = CpmdScript.from_file(inp_tmp)  # TODO: Check for must-have sections
        except:
            cpmd = CpmdScript('Cpmd', 'System', 'Mimic', 'Atoms')  # TODO: Switch to default template

        # Get overlaps and atoms
        overlaps = f'{len(sorted_qm_atoms)}'
        for i, atom in sorted_qm_atoms.iterrows():
            gromacs_id = atom['id']
            cpmd_id = i + 1
            overlaps += f'\n2 {gromacs_id} 1 {cpmd_id}'
            element = str(atom['element']).lower()
            coords = [atom['x'], atom['y'], atom['z']]
            if atom['is_link']:
                element += '_link'
            if cpmd.atoms.has_parameter(element):
                pp_block = getattr(cpmd.atoms, element)
                pp_block.coords.append(coords)
            else:
                setattr(cpmd.atoms, element, Pseudopotential(element, coords))

        cpmd.mimic.overlaps = overlaps
        cpmd.mimic.box = ' '.join([str(s/BOHR_RADIUS) for s in self.selector.mm_box])
        cpmd.system.cell = qm_cell()

        total_charge = sum(self.qm_atoms['charge'])
        if not round(total_charge, 2).is_integer():
            logging.warning('Total charge of QM region is %s. Rounding to integer.', total_charge)
        cpmd.system.charge = round(total_charge)

        cpmd.cpmd.maxsteps = maxsteps
        cpmd.cpmd.timestep = timestep

        if inp_out is None:
            logging.info('Created new CPMD input script for MiMiC run')
        else:
            gbl.host.write(str(cpmd), inp_out)
            logging.info('Wrote new CPMD input script to %s', inp_out)

        return qm_ndx_group, cpmd

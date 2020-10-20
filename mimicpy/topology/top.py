"""Module for top files"""

import logging
from .itp import Itp
from .topol_dict import TopolDict
from ..utils.errors import MiMiCPyError


class Top:
    """reads top files"""

    def __init__(self, file, mode='r', buffer=1000, nonstandard_atomtypes=None, guess_elements=True, gmxdata=None):
        self.file = file
        self.mode = mode
        self.buffer = buffer
        self.nonstandard_atomtypes = nonstandard_atomtypes
        self.guess_elements = guess_elements
        self.gmxdata = None
        self._molecules = None
        self._topol_dict = None

        if mode == 'r':
            self.__read()
        elif mode == 'w':
            pass
        else:
            raise MiMiCPyError(f'{mode} is not a mode. Only r or w can be used.')

    @property
    def molecules(self):
        if self.mode == 'r':
            return self._molecules
        self.mode = 'r'
        self.__read()
        return self._molecules

    @property
    def topol_dict(self):
        if self.mode == 'r':
            return self._topol_dict
        self.mode = 'r'
        self.__read()
        return self._topol_dict

    def __read(self):
        """Read molecule and atom information"""

        top = Itp(self.file, mode='t', gmxdata=self.gmxdata)
        atom_types = top.atom_types
        molecule_types = top.molecule_types

        if self.nonstandard_atomtypes is not None:
            # TODO: Support non-standard atomtypes input as file (list, itp, ...)
            atom_types.update(self.nonstandard_atomtypes)

        atoms = {}
        for itp_file in top.topology_files:
            itp_file_name = itp_file.split('/')[-1] # print only file name, and not full path
            try:
                itp = Itp(itp_file, molecule_types, atom_types, self.buffer, 'r', self.guess_elements)
                if itp.topol is not None:
                    atoms.update(itp.topol)
                    logging.info('Read atoms from %s.', itp_file_name)
                else:
                    logging.info('No atoms found in %s.', itp_file_name)
            except OSError:
                logging.warning('Could not find %s. Skipping...', itp_file_name)
        topol_dict = TopolDict.from_dict(atoms)

        self._molecules = top.molecules
        self._topol_dict = topol_dict
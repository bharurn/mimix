from .script import Script


class Pseudopotential:

    def __init__(self, element, coords, pp_type='MT_BLYP', labels='KLEINMAN-BYLANDER', lmax='S'):
        self.element = element
        self.coords = [coords]
        self.pp_type = pp_type
        self.labels = labels
        self.lmax = lmax

    def __str__(self):
        if not self.pp_type.startswith('_'):
            self.pp_type = '_' + self.pp_type
        if not self.labels.startswith(' ') and self.labels != '':
            self.labels = ' ' + self.labels

        pp_block = '*'
        pp_block += f'{self.element}{self.pp_type}{self.labels}\n'
        pp_block += f'    LMAX={self.lmax.upper()}\n'
        pp_block += f'    {len(self.coords)}\n'

        for row in self.coords:
            pp_block += f' {row[0]:>18.12f} {row[1]:>18.12f} {row[2]:>18.12f}\n'

        return pp_block

    @classmethod
    def from_string():
        pass


class Section(Script):

    def __str__(self):
        section_string = ''
        for keyword in self.parameters:
            value = getattr(self, keyword)
            if not isinstance(value, Pseudopotential):
                section_string += f"\n{keyword.upper().replace('_', ' ')}"
            if value is not True:  # Looks odd here but might make sense in the user python script
                section_string += f"\n{str(value).upper()}"  # TODO: Check for False
        return section_string

    def from_string(self):
        pass


class CpmdScript(Script):

    def __init__(self, *sections):
        super().__init__()
        for section in sections:
            setattr(self, section, Section())

    def __str__(self):
        cpmd_script = ''
        for section in self.parameters:
            section_string = str(getattr(self, section))
            cpmd_script += f'\n&{section.upper()}{section_string}\n&END\n'
        return cpmd_script

    def from_string(self):
        pass
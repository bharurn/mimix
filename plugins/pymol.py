
##### MiMiCPy PyMOL settings script
##
import mimicpy
from pymol import cmd

def prepqm(top, selection=None, is_link=False, inp=None, mdp=None, ndx='index.ndx', out='cpmd.inp'):
    try:
        qm = mimicpy.Preparation(mimicpy.PyMOL(top))
    except FileNotFoundError as e:
        print('\n\nError: Cannot find file {}! Exiting..\n'.format(e.filename))
        sys.exit(1)
    except (mimicpy.utils.errors.ParserError, mimicpy.utils.errors.MiMiCPyError) as e:
        print(e)
        sys.exit(1)
    
    try:
        qm.add(selection, is_link)
        qm.get_mimic_input(inp, mdp, ndx, out)
    except mimicpy.utils.errors.SelectionError as e:
        print(e)
    except FileNotFoundError as e:
        print('\n\nError: Cannot find file {}! Exiting..\n'.format(e.filename))
        sys.exit(1)

cmd.extend('prepqm', prepqm)
##
##################################
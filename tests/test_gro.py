from mimicpy.io.gro import Gro


def _get_gro_info(gro_file):

    with open(gro_file) as f:
        lines = f.readlines()
        number_of_atoms = int(lines[1].strip())
        box = lines[-1].split()
    
    return number_of_atoms, box


def test_read():
    file_to_check = 'gro_files/gro1.gro'
    gro_file = Gro(file_to_check)
    coords, box = gro_file.read(buffer=1)
    number_of_atoms_to_check, box_to_check = _get_gro_info(file_to_check)
    box = [str(a) for a in box] # conversion for comparison to naive reader function
    assert box == box_to_check
    assert len(coords) == number_of_atoms_to_check

    file_to_check = 'gro_files/gro1.gro'
    gro_file = Gro(file_to_check)
    coords, box = gro_file.read(buffer=2)
    number_of_atoms_to_check, box_to_check = _get_gro_info(file_to_check)
    box = [str(a) for a in box] # conversion for comparison to naive reader function
    assert box == box_to_check
    assert len(coords) == number_of_atoms_to_check

    file_to_check = 'gro_files/gro1.gro'
    gro_file = Gro(file_to_check)
    coords, box = gro_file.read()
    number_of_atoms_to_check, box_to_check = _get_gro_info(file_to_check)
    box = [str(a) for a in box] # conversion for comparison to naive reader function
    assert box == box_to_check
    assert len(coords) == number_of_atoms_to_check

    file_to_check = 'gro_files/4aj3.gro'
    gro_file = Gro(file_to_check)
    coords, box = gro_file.read()
    number_of_atoms_to_check, box_to_check = _get_gro_info(file_to_check)
    box = [str(a) for a in box] # conversion for comparison to naive reader function
    assert box == box_to_check
    assert len(coords) == number_of_atoms_to_check
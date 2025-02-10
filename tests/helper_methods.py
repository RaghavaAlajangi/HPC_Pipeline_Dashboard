import pathlib
import tempfile
import zipfile


def extract_data(zip_file):
    """Extract zip file content from data directory, return directory"""
    zpath = pathlib.Path(__file__).resolve().parent / "data" / zip_file
    # unpack
    arc = zipfile.ZipFile(str(zpath))

    # extract all files to a temporary directory
    edest = tempfile.mkdtemp(prefix=zpath.name)
    arc.extractall(edest)
    return pathlib.Path(edest)


def retrieve_test_drive(zip_file):
    """Extract contents of zip file and return drive dir"""
    return extract_data(zip_file)

# Copyright  2015, Province of British Columbia
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license

import subprocess
import os

def get_short_commit_id(path):
    """
    Return a shortened commit id corresponding to the HEAD revision
    of path within a git repository.

    Returns None if path is not within a git repository.
    """
    cwd = os.getcwd()
    try:
        os.chdir(path)
        p = subprocess.Popen(['git', 'rev-parse', '--short', 'HEAD'],
            stdout=subprocess.PIPE)
        output, _ = p.communicate()
        if p.wait():
            return None
    finally:
        os.chdir(cwd)
    return output.strip()

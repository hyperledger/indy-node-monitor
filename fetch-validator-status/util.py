import sys
from DidKey import DidKey

verbose = False

def enable_verbose(enable):
    global verbose
    verbose = enable

def log(*args):
    if verbose:
        print(*args, "\n", file=sys.stderr)

def create_did(seed):
    ident = None
    if seed:
        try:
            ident = DidKey(seed)
            log("DID:", ident.did, " Verkey:", ident.verkey)
        except:
            log("Invalid seed.  Continuing anonymously ...")
    return ident
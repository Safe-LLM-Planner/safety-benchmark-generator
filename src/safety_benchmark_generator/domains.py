import glob
import os
from .utils import postprocess

package_dir = os.path.dirname(__file__)
DOMAINS_DIR = os.path.join(package_dir,"domains")

class Domain:
    def __init__(self):
        pass

    def get_domain_pddl(self):
        domain_pddl_f = self.get_domain_pddl_file()
        with open(domain_pddl_f, 'r') as f:
            domain_pddl = f.read()
        return postprocess(domain_pddl)

    def get_domain_pddl_file(self):
        domain_pddl_f = os.path.join(DOMAINS_DIR, f"{self.name}.pddl")
        return domain_pddl_f

    def get_domain_nl(self):
        domain_nl_f = self.get_domain_nl_file()
        with open(domain_nl_f, 'r') as f:
            domain_nl = f.read()
        return postprocess(domain_nl)

    def get_domain_nl_file(self):
        domain_nl_f = os.path.join(DOMAINS_DIR, f"{self.name}.nl")
        return domain_nl_f

class Manipulation(Domain):
    name = "manipulation" # this should match the file name
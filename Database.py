from nwchem_parse import nwchem_parser
from nwchem_parse import nw_atom, nw_orbital
import mysql.connector
from mysql.connector import Error
import re

"""
Example run:

fn = Path to NWchem output file
db = Name of schema in database (Should be same as prefix ex. La-9+
pw = Your password to the database
usr = Your username for the database

# Stores data in database
store_data = database_storage(fn, usr, pw, db)

db = Name of schema in database (Should be same as prefix ex. La-9+
pw = Your password to the database
usr = Your username for the database

# Initializes data retrieval class
retrieve_data = database_retrieval(db, usr, pw)

# Get all data from schema
retrieve_data.get_all()
"""

class database_retrieval():
    _runinfo = dict()
    _atom_dict = dict()
    _orbital_dict_alpha = dict()
    _orbital_dict_beta = dict()
    _energies = dict()
    _total_density = dict()
    _spin_density = dict()
    _gradient_dict = dict()
    _overlap_dict = dict()
    connection = 0

    # Getters and Setters
    @property
    def energies(self): return self._energies
    @energies.setter
    def energies(self, val): self._energies = val

    @property
    def atom_dict(self): return self._atom_dict
    @atom_dict.setter
    def atom_dict(self, val): self._atom_dict = val

    @property
    def runinfo(self): return self._runinfo

    @runinfo.setter
    def runinfo(self, val): self._runinfo = val

    @property
    def orbital_dict_alpha(self): return self._orbital_dict_alpha

    @orbital_dict_alpha.setter
    def orbital_dict_alpha(self, val): self._orbital_dict_alpha = val

    @property
    def orbital_dict_beta(self): return self._orbital_dict_beta

    @orbital_dict_beta.setter
    def orbital_dict_beta(self, val): self._orbital_dict_beta = val

    @property
    def total_density(self): return self._total_density

    @total_density.setter
    def total_density(self, val): self._total_density = val

    @property
    def spin_density(self): return self._spin_density

    @spin_density.setter
    def spin_density(self, val): self._spin_density = val

    @property
    def gradient_dict(self): return self._gradient_dict

    @gradient_dict.setter
    def overlap_dict(self, val): self._gradient_dict = val

    @property
    def overlap_dict(self): return self._overlap_dict

    @overlap_dict.setter
    def overlap_dict(self, val): self._overlap_dict = val

    def __init__(self, db, usr, pwd):
        self.db = db
        self.usr = usr
        self.pwd = pwd
        self.connection = create_db_connection("%", usr, pwd, db)

    def get_all(self):
        self._runinfo = self.get_run_info(self.connection)
        self._atom_dict = self.get_geo_info(self.connection)
        self._energies = self.get_energy(self.connection)
        self._total_density = self.get_totalDensity(self.connection)
        self._spin_density = self.get_spinDensity(self.connection)
        self._orbital_dict_alpha = self.get_alphaOrbital_info(self.connection)
        self._orbital_dict_beta = self.get_betaOrbital_info(self.connection)
        self._gradient_dict = dict()
        self._overlap_dict = self.get_overlap_info(self.connection)

    def get_run_info(self, connection):
        _runinfo = dict()
        get = """ SELECT * FROM run_info; """
        results = read_query(connection, get)
        _runinfo['prefix'] = results[0][0]
        _runinfo['date'] = results[0][1]
        _runinfo['NW_branch'] = float(results[0][2])
        _runinfo['NW_revision'] = float(results[0][3])
        _runinfo['GA_revision'] = float(results[0][4])

        return _runinfo

    def get_geo_info(self, connection):
        _atoms = dict()
        get = """ SELECT * FROM geometry; """
        results = read_query(connection, get)
        for at in results:
            new_atom = nw_atom(id=float(at[0]), species=at[1], charge=float(at[2]))
            _atoms[new_atom.id] = new_atom

        return _atoms

    def get_energy(self, connection):
        _energy = dict()
        get = """ SELECT * FROM initial_energy; """
        results = read_query(connection, get)

    def get_totalDensity(self, connection):
        _total = dict()
        get = """ SELECT * FROM total_density_mulliken; """
        results = read_query(connection, get)
        data = []
        for at in results:
            res = at[3].strip('][').split(' ')
            for i in range(len(res)):
                res[i] = float(res[i])
            new_atom = nw_atom(id=float(at[0]), species=at[1], charge=float(at[2]), shell_charges=res)
            data.append(new_atom)

        _total['Mulliken Population Analysis'] = data

        get = """ SELECT * FROM total_density_lowdin; """
        results = read_query(connection, get)
        data = []
        for at in results:
            res = at[3].strip('][').split(' ')
            for i in range(len(res)):
                res[i] = float(res[i])
            new_atom = nw_atom(id=float(at[0]), species=at[1], charge=float(at[2]), shell_charges=res)
            data.append(new_atom)

        _total['Lowdin Population Analysis'] = data

        return _total

    def get_spinDensity(self, connection):
        _spin = dict()
        get = """ SELECT * FROM spin_density_mulliken; """
        results = read_query(connection, get)
        data = []
        for at in results:
            res = at[3].strip('][').split(' ')
            for i in range(len(res)):
                res[i] = float(res[i])
            new_atom = nw_atom(id=float(at[0]), species=at[1], charge=float(at[2]), shell_charges=res)
            data.append(new_atom)

        _spin['Mulliken Population Analysis'] = data

        get = """ SELECT * FROM spin_density_lowdin; """
        results = read_query(connection, get)
        data = []
        for at in results:
            res = at[3].strip('][').split(' ')
            for i in range(len(res)):
                res[i] = float(res[i])
            new_atom = nw_atom(id=float(at[0]), species=at[1], charge=float(at[2]), shell_charges=res)
            data.append(new_atom)

        _spin['Lowdin Population Analysis'] = data
        return _spin

    def get_alphaOrbital_info(self, connection):
        alpha = dict()
        get = """ SELECT * FROM alpha_orbital; """
        results = read_query(connection, get)
        for orbital in results:
            basatoms = []
            basefuncs = []
            for w in orbital[3].split(") "):
                basisfun = re.split(',\s', w)
                basisfun[0] = float(basisfun[0].replace("(", ""))
                basisfun[1] = float(basisfun[1].replace(" ", ""))
                whitelist = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                basisfun[3] = ''.join(filter(whitelist.__contains__, basisfun[3]))
                basisfun[3] = basisfun[3].strip()
                t = re.search(r'\((.*?)\)', basisfun[2]).group(1)
                t = t.split(",")
                new_atom = nw_atom(float(t[0]), t[1])
                basisfun[2] = new_atom
                basatoms.append(new_atom)
                basefuncs.append(basisfun)

            n = nw_orbital(vector=orbital[0], E=float(orbital[1]), occ=float(orbital[7]))
            n.basisatoms = basatoms
            n.basisfuncs = basefuncs
            n.isHOMO = (orbital[5] == 1)
            n.isLUMO = (orbital[6] == 1)
            n.spin = float(orbital[8])
            cent = orbital[4].strip('][').split(' ')
            for i in range(len(cent)):
                cent[i] = float(cent[i])
            n.center = cent
            alpha[n.vector] = n
        return alpha

    def get_betaOrbital_info(self, connection):
        beta = dict()
        get = """ SELECT * FROM alpha_orbital; """
        results = read_query(connection, get)
        for orbital in results:
            basatoms = []
            basefuncs = []
            for w in orbital[3].split(") "):
                basisfun = re.split(',\s', w)
                basisfun[0] = float(basisfun[0].replace("(", ""))
                basisfun[1] = float(basisfun[1].replace(" ", ""))
                whitelist = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                basisfun[3] = ''.join(filter(whitelist.__contains__, basisfun[3]))
                basisfun[3] = basisfun[3].strip()
                t = re.search(r'\((.*?)\)', basisfun[2]).group(1)
                t = t.split(",")
                new_atom = nw_atom(float(t[0]), t[1])
                basisfun[2] = new_atom
                basatoms.append(new_atom)
                basefuncs.append(basisfun)

            n = nw_orbital(vector=orbital[0], E=float(orbital[1]), occ=float(orbital[7]))
            n.basisatoms = basatoms
            n.basisfuncs = basefuncs
            n.isHOMO = (orbital[5] == 1)
            n.isLUMO = (orbital[6] == 1)
            n.spin = float(orbital[8])
            cent = orbital[4].strip('][').split(' ')
            for i in range(len(cent)):
                cent[i] = float(cent[i])
            n.center = cent
            beta[n.vector] = n
        return beta

    def get_overlap_info(self, connection):
        get = """ SELECT * FROM orbital_overlap """
        results = read_query(connection, get)
        r = 1
        overlap = dict()
        for i in results:
            entry = dict()
            entry['alpha'] = i[0]
            entry['beta'] = i[1]
            entry['overlap'] = i[2]
            overlap[str(r)] = entry
            r += 1
        return overlap


    def get_orbital_info(self, connection):
        al = self.get_alphaOrbital_info(connection)
        be = self.get_betaOrbital_info(connection)

        return al, be


class database_storage():
    def __init__(self, fn, usr, pwd, db):
        self.usr = usr
        self.pwd = pwd
        self.fn = fn
        self.db = db
        #self.cp = cp
        que = """ CREATE DATABASE """ + str(db)
        nw = nwchem_parser(fn)
        server = create_server_connection("%", usr, pwd)
        d = create_database(server, que)
        connection = create_db_connection("%", usr, pwd, db)
        self.runinfo_storage(nw._runinfo, connection)
        self.totalDensity_storage(nw._total_density, connection)
        self.spinDensity_storage(nw._spin_density, connection)
        self.geometry_storage(nw._atom_dict, connection)
        self.alphaOrbital_storage(nw._orbital_dict_alpha, connection)
        self.betaOrbital_storage(nw._orbital_dict_beta, connection)
        self.orbitalOverlap_storage(nw._overlap_dict, connection)
        self.initialEnergy_storage(nw._energies, connection)
        self.gradient_storage(nw._gradient_dict, connection)

    def runinfo_storage(self, runinfo, connection):
        create_runinfo_table = """
                CREATE TABLE run_info (
                prefix VARCHAR(20) PRIMARY KEY,
                date VARCHAR(30),
                nwchem_branch VARCHAR(20),
                nwchem_revision VARCHAR(20),
                ga_revision VARCHAR(20));
                """
        execute_query(connection, create_runinfo_table)

        entry = (
        runinfo['prefix'], runinfo['date'], runinfo['NW_branch'], runinfo['NW_revision'], runinfo['GA_revision'])
        pop_entry = """ INSERT INTO run_info VALUES """ + str(entry)
        execute_query(connection, pop_entry)

    def geometry_storage(self, geoinfo, connection):
        create_geoinfo_table = """
        CREATE TABLE geometry (
        atom_id FLOAT,
        species VARCHAR(5),
        charge FLOAT);
        """
        execute_query(connection, create_geoinfo_table)

        entry = """ INSERT INTO geometry VALUES """
        for ob in geoinfo:
            atom = geoinfo[ob]
            if (atom.id != 1):
                entry += ", "
            e = (atom.id, atom.species, atom.charge)
            entry += str(e)
        entry += ";"
        execute_query(connection, entry)

    def totalDensity_storage(self, totdeninfo, connection):
        create_totdeninfo_table = """
        CREATE TABLE total_density_mulliken (
        id FLOAT,
        species VARCHAR(5),
        charge FLOAT,
        shell_charges VARCHAR(130));
        """
        execute_query(connection, create_totdeninfo_table)

        entry = """ INSERT INTO total_density_mulliken VALUES """
        for atom in totdeninfo['Mulliken Population Analysis']:
            if (atom.id != 1):
                entry += ", "
            sh_ch = ' '.join(str(e) for e in atom.shell_charges)
            e = (atom.id, atom.species, atom.charge, sh_ch)
            entry += str(e)
        entry += ";"
        execute_query(connection, entry)

        create_totdeninfo_table = """
            CREATE TABLE total_density_lowdin (
            id FLOAT,
            species VARCHAR(5),
            charge FLOAT,
            shell_charges VARCHAR(130));
            """
        execute_query(connection, create_totdeninfo_table)

        entry = """ INSERT INTO total_density_lowdin VALUES """
        for atom in totdeninfo['Lowdin Population Analysis']:
            if (atom.id != 1):
                entry += ", "
            sh_ch = ' '.join(str(e) for e in atom.shell_charges)
            e = (atom.id, atom.species, atom.charge, sh_ch)
            entry += str(e)
        entry += ";"
        execute_query(connection, entry)

    def spinDensity_storage(self, spindeninfo, connection):
        create_spindeninfo_table = """
        CREATE TABLE spin_density_mulliken (
        id FLOAT,
        species VARCHAR(5),
        charge FLOAT,
        shell_charges VARCHAR(130));
        """
        execute_query(connection, create_spindeninfo_table)

        entry = """ INSERT INTO spin_density_mulliken VALUES """
        for atom in spindeninfo['Mulliken Population Analysis']:
            if (atom.id != 1):
                entry += ", "
            sh_ch = ' '.join(str(e) for e in atom.shell_charges)
            e = (atom.id, atom.species, atom.charge, sh_ch)
            entry += str(e)
        entry += ";"
        execute_query(connection, entry)

        create_spindeninfo_table = """
            CREATE TABLE spin_density_lowdin (
            id FLOAT,
            species VARCHAR(5),
            charge FLOAT,
            shell_charges VARCHAR(130));
            """
        execute_query(connection, create_spindeninfo_table)

        entry = """ INSERT INTO spin_density_lowdin VALUES """
        for atom in spindeninfo['Lowdin Population Analysis']:
            if (atom.id != 1):
                entry += ", "
            sh_ch = ' '.join(str(e) for e in atom.shell_charges)
            e = (atom.id, atom.species, atom.charge, sh_ch)
            entry += str(e)
        entry += ";"
        execute_query(connection, entry)

    def initialEnergy_storage(self, initialeninfo, connection):
        create_initialeninfo_table = """
        CREATE TABLE initial_energy (
        total_energy FLOAT,
        1e_energy FLOAT,
        2e_energy FLOAT,
        HOMO FLOAT,
        LUMO FLOAT);
        """
        execute_query(connection, create_initialeninfo_table)

        entry = (
        initialeninfo['total'], initialeninfo['1e'], initialeninfo['2e'], initialeninfo['HOMO'], initialeninfo['LUMO'])
        pop_entry = """ INSERT INTO initial_energy VALUES """ + str(entry) + ";"
        execute_query(connection, pop_entry)

    def alphaOrbital_storage(self, orbitalinfo, connection):
        create_alphaoribital_table = """
        CREATE TABLE alpha_orbital (
        vector FLOAT,
        energy FLOAT,
        basisAtom VARCHAR(200),
        basisFuncs VARCHAR(400),
        center VARCHAR(50),
        isHOMO BOOLEAN,
        isLUMO BOOLEAN,
        occupancy FLOAT,
        spin FLOAT);
        """
        execute_query(connection, create_alphaoribital_table)

        entry = """ INSERT INTO alpha_orbital VALUES """
        for orbit in orbitalinfo:
            if (orbit != 10):
                entry += ", "
            org = orbitalinfo[orbit]
            basatom = ' '.join(str(i) for i in org.basisatoms)
            basfunc = ' '.join(str(i) for i in org.basisfuncs)
            cente = ' '.join(str(i) for i in org.center)
            e = (org.vector, org.E, basatom, basfunc, cente, org.isHOMO,
                 org.isLUMO, org.occ, org.spin)
            entry += str(e)
        entry += ";"

        execute_query(connection, entry)

    def betaOrbital_storage(self, orbitalinfo, connection):
        create_betaoribital_table = """
        CREATE TABLE beta_orbital (
        vector FLOAT,
        energy FLOAT,
        basisAtom VARCHAR(200),
        basisFuncs VARCHAR(400),
        center VARCHAR(50),
        isHOMO BOOLEAN,
        isLUMO BOOLEAN,
        occupancy FLOAT,
        spin FLOAT);
        """
        execute_query(connection, create_betaoribital_table)

        entry = """ INSERT INTO alpha_orbital VALUES """
        for orbit in orbitalinfo:
            if (orbit != 10):
                entry += ", "
            org = orbitalinfo[orbit]
            basatom = ' '.join(str(i) for i in org.basisatoms)
            basfunc = ' '.join(str(i) for i in org.basisfuncs)
            cente = ' '.join(str(i) for i in org.center)
            e = (org.vector, org.E, basatom, basfunc, cente, org.isHOMO,
                 org.isLUMO, org.occ, org.spin)
            entry += str(e)
        entry += ";"

        execute_query(connection, entry)

    def orbitalOverlap_storage(self, overlapinfo, connection):
        create_overlap_table = """
        CREATE TABLE orbital_overlap (
        alpha FLOAT,
        beta FLOAT,
        overlap FLOAT);
        """
        execute_query(connection, create_overlap_table)

        entry = """ INSERT INTO orbital_overlap VALUES """
        for en in overlapinfo:
            thing = overlapinfo[en]
            entry += str((thing['alpha'], thing['beta'], thing['overlap']))
            if(float(en) < len(overlapinfo)):
                entry += ", "
        entry += ";"
        execute_query(connection, entry)

    def gradient_storage(self, grad_info, connection):
        create_gradient_table = """
        CREATE TABLE gradient (
        )
        """
        print(2)


def read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")

def create_server_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created successfully")
    except Error as err:
        print(f"Error: '{err}'")


def create_db_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

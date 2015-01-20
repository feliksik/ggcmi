"""Module for defining the overall settings for a given AgGRID run

Task_picker imports this module and uses these settings for starting
the simulations. See the comments before each section.

Moreover, this module implements functions for building the soil and site
data:
- get_soil_data(longitude, latitude)
- get_site_data(soildata)
"""
import os, sys
from decimal import Decimal
import cPickle

class NoFAOSoilError(Exception):
    pass

def get_soil_data(longitude, latitude):
    """Build valid WOFOST soil data from for given longitude and latitude.

    Water holding capacity (WHC) and soil rootable depth (RDMSOL) are derived
    from an internal dict which provides the WHC and RD for each lon/lat
    grid cell centre (0.5x0.5 degrees). WHC and RD are derived from the
    FAO 1:5M soil map.

    For other soil inputs default values are used:
    "SMW":0.1     -  Wilting point [volumetric fraction]
    "K0":10.      -  Saturated hydraulic conductivity [cm/day]
    "KSUB":10.    -  Max percolation rate subsoil [cm/day]
    "SOPE":10.0   -  Max percolation rate subsoil [cm/day]
    "CRAIRC":0.05 -  Critical air content

    Field capacity (SMFCF) is estimated as SMW + WHC
    Porosity (SM0) is estimated as SMFCF + 0.05 + CRAIRC
    Soil rootable depth (RDMSOL) is directly take from the FAO database.
    """
    if not isinstance(longitude, Decimal):
        dlon = Decimal(round(longitude, 2))
    if not isinstance(latitude, Decimal):
        dlat = Decimal(round(latitude, 2))

    try:
        WHC, RDMSOL = soil_data[(dlon, dlat)]
    except KeyError:
	msg = "No soil data for lon/lat: %s/%s" % (dlon,dlat)
        raise NoFAOSoilError(msg)

    default_soildata = {"SMW":0.1, "K0":10., "KSUB":10., "SOPE":10.0,
                        "CRAIRC":0.05}
    # Field capacity as SMW + WHC
    SMFCF = default_soildata["SMW"] + WHC
    # Soil porosity as field capacity + 0.05 + CRAIRC
    SM0 = SMFCF + 0.05 + default_soildata["CRAIRC"]
    # Check for unrealistic values in SMFCF/SM0

    if SM0 > 0.7:
        SM0 = 0.7
        SMFCF = 0.6
    # Update soildata, WHC is not strictly necessary but is nice to calculate
    # the site variable WAV.
    default_soildata.update({"SMFCF":SMFCF, "SM0":SM0, "RDMSOL":RDMSOL,
                             "WHC":WHC})

    return default_soildata


def get_site_data(soildata):
    """Build the WOFOST site data.

    These are mostly constants, but most important is the initial amount of
    soil moisture in the soil profile. Currently this is set at 50% of the
    value between wilting point and field capacity.
    """
    sitedata = {"IFUNRN": 0,
                "SSMAX": 0.,
                "SSI": 0,
                "NOTINF": 0.,
                "SMLIM": soildata["SMFCF"],
                "WAV": soildata["WHC"]*soildata["RDMSOL"]
               }
    return sitedata



def getenv_or_die(name):
  envvar = os.getenv(name)
  if not envvar:
    import sys 
    sys.stderr.write("Error: Environment variable %s is not set\n" % name) 
    exit(1)
  return envvar


#database connection
username = getenv_or_die("DB_USER")
password = getenv_or_die("DB_PASS")
hostname = getenv_or_die("DB_HOST")
dbname   = getenv_or_die("DB_DATABASE")
connstr = 'mysql://%s:%s@%s/%s?charset=utf8' % (username, password, hostname, dbname)

# Folder for pcse code
pcse_dir = r"/opt/ggcmi/pcse"

# Top level folder for data
data_dir = getenv_or_die("DATA_INPUT_DIR")
data_output = getenv_or_die("DATA_OUTPUT_DIR")

# Meteorological input data in HDF5
hdf5_meteo_file = os.path.join(data_dir, "AgMERRA", "AgMERRA_1980-01-01_2010-12-31_final.hf5")

# file with the land mask
landmask_grid = os.path.join(data_dir, "geodata", "glob_landmask_resampled.flt")

# dummy code to avoid import of GridEnvelope2D from pcse.geo.gridenvelope2d 
class GridEnvelope2D:
    def __init__(self, ncols, nrows, xll, yll, dx, dy):
        pass; 

# regions and crop specific files with parameters
regions = {"World": GridEnvelope2D(720, 360, -180., -90., 0.5, 0.5),
            "NorthTemperate": GridEnvelope2D(720, 87, -180, 23.0, 0.5, 0.5),
            "Tropics": GridEnvelope2D(720, 94, -180., -23.5, 0.5, 0.5),
            "SouthTemperate": GridEnvelope2D(720, 87, -180, -66.5, 0.5, 0.5)}

# Definition of crops and parameter values
crop_info_sources = [
            ("Barley", "World", "BAR301.CAB", 1),
            ("Cassava", "World", "CASSAVA.W41", 2),
            ("Groundnuts", "World", "GR_NUT.W41", 1),
            ("Maize", "World", "MAIZ.W41", 1),
            ("Millet", "World", "MILLET.W41", 1),
            ("Potatoes", "World",  "POT702.CAB", 2),
            ("Pulses", "World", "PIGEOPEA.W41", 1),
            ("Rapeseed", "World", "RAP1002.CAB", 1),
            ("Rice", "World", "RIC501.CAB", 1),
            ("Rye", "World", "RYE.W41", 1),
            ("Sorghum", "World", "SORGHUM.W41", 1),
            ("Soybeans", "World", "SOYBEAN.W41", 1),
            ("Sunflower", "World", "SUN1101.CAB", 1),
            ("Wheat", "World", "WWH105.CAB", 1)]

# Location of crop parameter files , soil data and cropping calendars
crop_input_folder = "OtherInputs"
cabofile_folder = os.path.join(data_dir, crop_input_folder, "CROPD")

# Location of cropping calendars
growing_season_folder = os.path.join(data_dir, crop_input_folder, "GrowingSeason_vs1_24")
growing_season_file_suffix = "_growing_season_dates_v1.24.nc4"

# Location of soil data and loading of pickle file with soil properties
soil_data_folder = os.path.join(data_dir, crop_input_folder, "soildata")
soil_data_file = os.path.join(soil_data_folder, "GGCMI_grid_soil_type.pkl")
soil_data = cPickle.load(open(soil_data_file, "rb"))

# number of days to start simulation before the crop starts
days_before_CROP_START_DATE = 90
# Number of days to add to harvest date to allow variability in maturity
days_after_CROP_END_DATE = 14

# Location where output should be written

top_level_dir = data_output
output_folder = os.path.join(top_level_dir, "output")
output_file_template = "ggcmi_results_task_%010i.pkl"
shelve_folder = os.path.join(top_level_dir, "shelves")
results_folder = os.path.join(top_level_dir, "results_nc4")
log_folder = os.path.join(top_level_dir, "logs")

# Number of CPU's to use for simulations
# Several has options are possible:
# * None: use the amount of CPUs available as reported by
#   multiprocessing.cpu_count()
# * a positive integer number indicates the number of CPUs to use but
#   with a maximum of multiprocessing.cpu_count()
# * a negative integer number will be subtracted from multiprocessing
# .cpu_count() with a minimum of 1 CPU

try:
  number_of_CPU = int(os.getenv("NR_OF_CPUS"))
except Exception: # if not given, or non-integer
  number_of_CPU = None

# this is the maximum number of tasks that a worker is allowed to 
# execute.
max_tasks_per_worker = 1000 

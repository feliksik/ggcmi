# -*- coding: utf-8 -*-
# Copyright (c) 2004-2014 Alterra, Wageningen-UR
# Allard de Wit (allard.dewit@wur.nl), April 2014
import sys, os
import datetime
import logging

from sqlalchemy import create_engine, MetaData, Table

from . import db
from .models import Wofost71_PP, Wofost71_WLP_FD
from .settings import settings

def start_wofost(grid=31031, crop=1, year=2000, mode='wlp',
                   dsn=None):
    """Provides a convenient interface for starting a WOFOST instance
    
    If started with no arguments, the routine will connnect to the
    demo database and initialize WOFOST for winter-wheat (cropno=1)
    in Spain (grid_no=31031) for the year 2000 in water-limited
    production (mode='wlp')
    
    
    :param grid: grid number, defaults to 31031
    :param crop: crop number, defaults to 1 (winter-wheat in the demo database)
    :param year: year to start, defaults to 2000
    :param mode: production mode ('pp' or 'wlp'), defaults to 'wlp'
    :param dsn: PCSE DB as SQLAlchemy data source name
           defaults to `None` and in that case a connection to the demo
           database will be established.
           
    example::
    
        >>> import pcse
        >>> wofsim = pcse.start_wofost(grid=31031, crop=1, year=2000, 
        ...   mode='wlp')
        >>> 
        >>> wofsim
        <pcse.models.Wofost71_WLP_FD at 0x35f2550>
        >>> wofsim.run(days=300)
        >>> wofsim.get_variable('tagp')
        15261.752187075261
    """

    installdir = os.path.dirname(os.path.abspath(__file__))

    if dsn is None: # Assume SQlite demo DB
        db_location = os.path.join(settings.PCSE_USER_HOME, "pcse.db")
        dsn = "sqlite:///" + db_location
    
    # Open database connections
    pywofost_engine = create_engine(dsn)
    pywofost_metadata = MetaData(pywofost_engine)
    
    # Get input data from database
    sitedata  = db.pcse.fetch_sitedata(pywofost_metadata, grid, year)
    timerdata = db.pcse.fetch_timerdata(pywofost_metadata,grid, year, crop)
    cropdata = db.pcse.fetch_cropdata(pywofost_metadata, grid, year, crop)
    soildata = db.pcse.fetch_soildata(pywofost_metadata, grid)

    startdate = timerdata["START_DATE"]
    enddate = timerdata["END_DATE"]
    meteof = db.pcse.GridWeatherDataProvider(pywofost_metadata, grid_no=grid,
                startdate=startdate, enddate=enddate)
                             
    # Initialize PCSE/WOFOST
    mode = mode.strip().lower()
    if mode == 'pp':
        wofsim = Wofost71_PP(sitedata, timerdata, soildata, cropdata, meteof)
    if mode == 'wlp':
        wofsim = Wofost71_WLP_FD(sitedata, timerdata, soildata, cropdata, meteof)
    else:
        msg = "Unrecognized mode keyword: '%s' should be one of 'pp'|'wlp'"
        raise RuntimeError(msg)
    return wofsim

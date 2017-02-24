#!/usr/bin/env python
#
#  Join and import the SSURGO county level data
#  to shapefiles
#
from __future__ import print_function
import os
import subprocess

ogr2ogr_binary = "ogr2ogr"

# ------------------------------------------------------------------------

def ogr2ogr(in_fc, out_fc, options=None):
    
# Todo - get rid of subprocess - call ogr directly

    (folder, file) = os.path.split(in_fc)
    (base, ext) = os.path.splitext(file)

    args = [ogr2ogr_binary]
    if options: args += options
    args += [out_fc, in_fc]
    #print(args)
    try:
        p = subprocess.check_output(args)
        print(p)
    except subprocess.CalledProcessError as e:
        print("ogr2ogr failed with: %s" % e)
        return False
    return True

if __name__ == '__main__':
    
    counties = [ "OR051", "OR067", "OR071", "OR610", "OR643"]
    #counties = ['OR051']

    error = 0
    count = 0
    for county in counties:
        print(county)
        layer = "soilmu_a_%s" % county.lower()
     
        input_folder = os.path.join(county, "spatial")
        input_fc = layer + '.shp'
        
        # Have to chdir because of the SQL expression, using a path does not work for CSV file.
        os.chdir(input_folder)

        # You have to create this file from tabular/mapunit.txt and put it in the spatial folder so ogr can find it
        # You have to translate the PIPEs into tabs
        table = 'mapunit'
        csv = table + '.csv'
        if not os.path.exists(csv):
            print("ERROR: There is no mapunit file for %s" % county)
            error += 1
            continue

        sel = "%s.MUKEY as MUKEY, %s.hvf as farmlndcls" % (layer, table)
        where = "%s LEFT JOIN '%s'.%s ON %s.MUKEY=%s.mukey" % (layer, csv,table, layer,table)
        sql = "SELECT %s FROM %s" % (sel, where)
        print(sql)
        
        options = ['-sql', sql]
        output_fc = os.path.join(county + '_ssurgo.shp')
        if not ogr2ogr(input_fc, output_fc, options):
            error += 1

# ogr2ogr -sql "select soilmu_a_or067.MUSYM as musym, soilmu_a_or067.MUKEY as mukey, mapunit.soiltype as soiltype, mapunit.hvf as hvf
# from soilmu_a_or067 left join 'mapunit.csv'.mapunit on soilmu_a_or067.MUKEY=mapunit.mukey" outshape.shp soilmu_a_or067.shp

    
        table = 'muaggatt'
        csv   = table + '.csv'
        layer = county + '_ssurgo'
        keep = "%s.MUKEY as MUKEY, %s.farmlndcls as farmlndcls, " % (layer,layer)
        sel = keep + "muaggatt.iccdd as iccdd, muaggatt.iccdcdpct as iccdcdpct, muaggatt.niccdcd as niccdcd, muaggatt.niccdcdpct as niccdcdpct"
        where = "%s LEFT JOIN '%s'.%s ON %s.MUKEY=%s.mukey" % (layer, csv,table, layer,table)
        sql = "SELECT %s FROM %s" % (sel, where)
        print(sql)
        
        options = ['-sql', sql]
        input_fc = output_fc
        output_fc = os.path.join('../..', layer + '.shp')
        if not ogr2ogr(input_fc, output_fc, options):
            error += 1
        
        os.chdir('../..')
        count += 1
        
    print("%d files processed; %d errors" % (count, error))
    exit(error)

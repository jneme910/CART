# SDA_CreateAOI_Demo8.py
#
# Uses AOI in ArcMap to create a soil data table from SDA Query service. Developed as a testbed for CART soils data.
#
# This version (2) of the script will attempt to bypass all Phil's macros and
# create a temporary spatial table in SDA that contains AOI geometry for multiple PLUs and
# intersects that with soil polygons and runs other attribute queries.
#
# Added a new function (FormSDA_Queries) that will take the PLU geometry and use it to create a temporary spatial table
# in SDA.
#
# Trying to add a loop for generating SQL for multiple interps
#   1. Subsidence
#   2. Compaction
#   3. Organic Matter Depletion
#   4. Concentration of Salts
#
# Adding rating class domain values and 'order' for top two rating classes using sdvattribute.maplegendxml.
# Making the interps queries more dynamic by incorporating TRUNCATE on temporary tables, allowing a loop.
# Adding additional boolean parameters so that we can independently control whether the interps, properties and
#   soil polygon geometry queries are generated.
# Adding rolling sum for interps aggregation method per Chad Volkman's suggestion

# Soil properties to be added:
#     1. Prime farmland
#     2. EC
#     3. SAR (High)
#     4. Flooding
#     5. Ponding
#     6. Histosols
#     7. Gelisols
#     8. Hydric, wet spots
#     9. HEL?

# 2019-08-11
#
# How 'No Data' is handled.
# Some standard interps aren't generating a Not rated for each landunit when AOI is NOTCOM

# Trick: Use NotePad++ to find non-ascii characters. Search|Find Characters In Range|Non-ASCII Characters (128-255)

## ===================================================================================
class MyError(Exception):
    pass

## ===================================================================================
def PrintMsg(msg, severity=0):
    # prints message to screen if run as a python script
    # Adds tool message to the geoprocessor
    #
    #Split the message on \n first, so that if it's multiple lines, a GPMessage will be added for each line
    try:
        for string in msg.split('\n'):
            #Add a geoprocessing message (in case this is run as a tool)
            if severity == 0:
                arcpy.AddMessage(string)

            elif severity == 1:
                arcpy.AddWarning(string)

            elif severity == 2:
                arcpy.AddMessage("    ")
                arcpy.AddError(string)

    except:
        pass

## ===================================================================================
def errorMsg():
    try:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        theMsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
        PrintMsg(theMsg, 2)

    except:
        PrintMsg("Unhandled error in errorMsg method", 2)
        pass

## ===================================================================================
def Number_Format(num, places=0, bCommas=True):
    try:
    # Format a number according to locality and given places
        #locale.setlocale(locale.LC_ALL, "")
        if bCommas:
            theNumber = locale.format("%.*f", (places, num), True)

        else:
            theNumber = locale.format("%.*f", (places, num), False)
        return theNumber

    except:
        errorMsg()

        return "???"

## ===================================================================================
def CreateAOILayer(inputAOI, bClean, aoiShp):
    # Create new featureclass to use in assembling geometry query for Soil Data Access
    # Try to create landunit identification using CLU or PLU field attributes if available.

    try:

        simpleShp = os.path.join(env.scratchGDB, "aoi_simple")
        #PrintMsg(" \nCreating single part polygon shapefile: " + simpleShp, 1)

        if arcpy.Exists(simpleShp):
            arcpy.Delete_management(simpleShp, "FEATURECLASS")

        if arcpy.Exists(aoiShp):
            arcpy.Delete_management(aoiShp, "FEATURECLASS")

        arcpy.MultipartToSinglepart_management(inputAOI, simpleShp)  # Sometimes getting internal server error here

        cnt = int(arcpy.GetCount_management(simpleShp).getOutput(0))

        if cnt == 0:
            raise MyError, "No polygon features in " + simpleShp

        # Try applying output coordinate system and datum transformation
        env.outputCoordinateSystem = sdaCS
        env.GeographicTransformations = tm

        # Describe the single-part AOI layer
        desc = arcpy.Describe(simpleShp)
        fields = desc.fields
        fldNames = [f.baseName.upper() for f in fields]
        #PrintMsg(" \nsimpleShp field names: " + ", ".join(fldNames), 1)
        bLandunit = False

        # Keep original boundaries, but if attribute table contains landunit or LANDUNIT attributes, dissolve on that

        if ("PLU_ID" in fldNames and "PLU_NUMBER" in fldNames and "TRACT" in fldNames):
            # This must be a shapefile export from CD
            #
            # Go ahead and dissolve using landunit which was previously added
            PrintMsg(" \nUsing PLU export to build AOI for Soil Data Access query", 0)

            if not "LANDUNIT" in fldNames:
                arcpy.AddField_management(simpleShp, "landunit", "TEXT", "", "", 16)

            curFields = ["landunit", "tract", "plu_number"]

            with arcpy.da.UpdateCursor(simpleShp, curFields) as cur:
                for rec in cur:
                    # create stacked label for tract and field
                    landunit = "T" + str(rec[1]) + " Fld" + str(rec[2])
                    rec[0] = landunit
                    cur.updateRow(rec)

                del cur, rec

            PrintMsg(" \nDissolving PLU export to build AOI for Soil Data Access query", 0)
            arcpy.Dissolve_management(simpleShp, aoiShp, ["landunit"], "", "MULTI_PART")
            bLandunit = True
            arcpy.Delete_management(simpleShp)
            del simpleShp


        elif ("LAND_UNIT_TRACT_NUMBER" in fldNames and "LAND_UNIT_LAND_UNIT_NUMBER" in fldNames):
            # Planned land Unit featureclass
            # Go ahead and dissolve using landunit which will be added next
            if not "LANDUNIT" in fldNames:
                arcpy.AddField_management(simpleShp, "landunit", "TEXT", "", "", 20)

            curFields = ["landunit", "LAND_UNIT_TRACT_NUMBER", "LAND_UNIT_LAND_UNIT_NUMBER"]

            with arcpy.da.UpdateCursor(simpleShp, curFields) as cur:
                for rec in cur:
                    # create stacked label for tract and field
                    landunit = "T" + str(rec[1]) + " Fld" + str(rec[2])
                    rec[0] = landunit
                    cur.updateRow(rec)

                del cur, rec

            arcpy.Dissolve_management(simpleShp, aoiShp, ["landunit"], "", "MULTI_PART")
            bLandunit = True
            arcpy.Delete_management(simpleShp)
            del simpleShp

        elif "LANDUNIT" in fldNames:
            # User has created a featureclass with landunit attribute.
            # Regardless, dissolve any polygons on landunit
            arcpy.Dissolve_management(simpleShp, aoiShp, "landunit", "", "MULTI_PART")
            bLandunit = True
            arcpy.Delete_management(simpleShp)
            del simpleShp

        elif ("CLU_NUMBER" in fldNames and "TRACT_NUMB" in fldNames):
            # This must be a shapefile copy of CLU. Field names are truncated.
            # Keep original boundaries, but if attribute table contains LANDUNIT attributes, dissolve on that
            #
            # Go ahead and dissolve using landunit which was previously added
            if not "LANDUNIT" in fldNames:
                arcpy.AddField_management(simpleShp, "landunit", "TEXT", "", "", 20)

            curFields = ["landunit", "TRACT_NUMB", "CLU_NUMBER"]

            with arcpy.da.UpdateCursor(simpleShp, curFields) as cur:
                for rec in cur:
                    # create stacked label for tract and field
                    landunit = "T" + str(rec[1]) + " Fld" + str(rec[2])
                    rec[0] = landunit
                    cur.updateRow(rec)

                del cur, rec

            arcpy.Dissolve_management(simpleShp, aoiShp, ["landunit"], "", "MULTI_PART")
            bLandunit = True
            arcpy.Delete_management(simpleShp)
            del simpleShp

        elif ("TRACT_NUMB" in fldNames and "CLU_NUMBER" in fldNames):
            # This must be a shapefile copy of CLU. Field names are truncated.
            # Keep original boundaries, but if attribute table contains LANDUNIT attributes, dissolve on that
            #
            # Go ahead and dissolve using landunit which was previously added
            if not "LANDUNIT" in fldNames:
                arcpy.AddField_management(simpleShp, "landunit", "TEXT", "", "", 20)

            curFields = ["landunit", "TRACT_NUMB", "CLU_NUMBER"]

            with arcpy.da.UpdateCursor(simpleShp, curFields) as cur:
                for rec in cur:
                    # create stacked label for tract and field
                    landunit = "T" + str(rec[1]) + " Fld" + str(rec[2])
                    rec[0] = landunit
                    cur.updateRow(rec)

                del cur, rec

            arcpy.Dissolve_management(simpleShp, aoiShp, ["landunit"], "", "MULTI_PART")
            bLandunit = True
            arcpy.Delete_management(simpleShp)
            del simpleShp

        elif ("TRACT_NUMBER" in fldNames and "FARM_NUMBER" in fldNames and "CLU_NUMBER" in fldNames):
            # This must be a shapefile copy of CLU. Field names are truncated.
            # Keep original boundaries, but if attribute table contains LANDUNIT attributes, dissolve on that
            #
            # Go ahead and dissolve using landunit which was previously added
            if not "LANDUNIT" in fldNames:
                arcpy.AddField_management(simpleShp, "landunit", "TEXT", "", "", 20)

            curFields = ["landunit", "TRACT_NUMBER", "CLU_NUMBER"]

            with arcpy.da.UpdateCursor(simpleShp, curFields) as cur:
                for rec in cur:
                    # create stacked label for tract and field
                    landunit = "T" + str(rec[1]) + " Fld" + str(rec[2])
                    rec[0] = landunit
                    cur.updateRow(rec)

            arcpy.Dissolve_management(simpleShp, aoiShp, ["landunit"], "", "MULTI_PART")
            bLandunit = True

        elif ("CLUNBR" in fldNames and "TRACTNBR" in fldNames and "FARMNBR" in fldNames):
            # This must be a shapefile copy of CLU from Iowa
            # Keep original boundaries, but if attribute table contains LANDUNIT attributes, dissolve on that
            #
            # Go ahead and dissolve using landunit which was previously added
            if not "LANDUNIT" in fldNames:
                arcpy.AddField_management(simpleShp, "landunit", "TEXT", "", "", 20)

            curFields = ["landunit", "TRACTNBR", "CLUNBR"]

            with arcpy.da.UpdateCursor(simpleShp, curFields) as cur:
                for rec in cur:
                    # create stacked label for tract and field
                    landunit = "T" + str(rec[1]) + " Fld" + str(rec[2])
                    rec[0] = landunit
                    cur.updateRow(rec)

                del cur, rec

            arcpy.Dissolve_management(simpleShp, aoiShp, ["landunit"], "", "MULTI_PART")
            bLandunit = True
            arcpy.Delete_management(simpleShp)
            del simpleShp

        else:
            if arcpy.Exists(simpleShp):
                # I want to create a layer where LANDUNIT = OID
                # Rather arbitrary but we'll see how this works
                arcpy.AddField_management(simpleShp, "landunit", "TEXT", "", "", 20)
                with arcpy.da.UpdateCursor(simpleShp, ["OID@", "landunit"]) as cur:
                    for rec in cur:
                        id = rec[0]
                        cur.updateRow([id, "0"])

                #PrintMsg(" \nDissolving " + simpleShp, 1)
                arcpy.Dissolve_management(simpleShp, aoiShp, ["landunit"], "", "SINGLE_PART")

                with arcpy.da.UpdateCursor(aoiShp, ["OID@", "landunit"]) as cur:
                    for rec in cur:
                        id = rec[0]
                        cur.updateRow([id, "Fld" + str(id)])

                PrintMsg(" \nUsing original polygons to build AOI for Soil Data Access query...", 0)
                #time.sleep(0.5)
                arcpy.Delete_management(simpleShp)
                del simpleShp

            else:
                raise MyError, "Missing output " + simpleShp




        env.workspace = env.scratchFolder

        if not arcpy.Exists(aoiShp):
            raise MyError, "Missing AOI " + aoiShp

        arcpy.RepairGeometry_management(aoiShp, "DELETE_NULL")  # Need to make sure this isn't doing bad things.

        #PrintMsg(" \n" + aoiShp + " fields: " + (", ").join([fld.name for fld in arcpy.Describe(aoiShp).fields]), 1)

        # Calculate field acres here
        arcpy.AddField_management(aoiShp, "acres", "DOUBLE")

        # Get centroid of aoiShp which has a CS of Geographic WGS1984
        aoiDesc = arcpy.Describe(aoiShp)
        extent = aoiDesc.extent
        xCntr = (extent.XMax + extent.XMin) / 2.0
        yCntr = (extent.YMax + extent.YMin) / 2.0
        utmZone = int( (31 + (xCntr / 6.0) ) )

        # Calculate hemisphere and UTM Zone
        if yCntr > 0:  # Not sure if this is the best way to handle hemisphere
            zone = str(utmZone) + "N"

        else:
            zone = str(utmZone) + "S"

        # Central Meridian
        cm = ((utmZone * 6.0) - 183.0)

        # Get string version of UTM coordinate system
        #PrintMsg(" \nCalculated UTM Zone of " + zone + " for longitude of " + str(xCntr), 1)  # HI should be 5, came out 31 (-154.97d)
        #PrintMsg(" \n" + str(extent.XMax) + ", " + str(extent.YMax) + ", " + str(extent.XMin) + ", " + str(extent.YMin), 1)

        utmBase = "PROJCS['WGS_1984_UTM_Zone_xxx',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',zzz],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]];-5120900 -9998100 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision"
        wkt = utmBase.replace("xxx", zone).replace("zzz", str(cm))
        srAcres = arcpy.SpatialReference()
        srAcres.loadFromString(wkt)
        #PrintMsg(" \nUTM projection used: \n" + wkt, 1)

        # Temporary test to add diagnostic information
        #arcpy.AddField_management(aoiShp, "utm_zone", "TEXT", "", "", 8)
        #arcpy.AddField_management(aoiShp, "CM", "SHORT")

        #aoiFlds = ["SHAPE@AREA", "acres", "utm_zone", "cm"]
        aoiFlds = ["SHAPE@AREA", "acres"]

        #with arcpy.da.UpdateCursor(aoiShp, ["SHAPE@AREA", "acres", "utm_zone", "cm"], "", srAcres) as cur:
        with arcpy.da.UpdateCursor(aoiShp, ["SHAPE@AREA", "acres"], "", srAcres) as cur:
            # UTM coordinates (Meters)
            for rec in cur:
                if not rec[0] is None:
                    acres = round((rec[0] / 4046.8564224), 2)  # can't handle NULL
                    #newrec = [rec[0], acres, zone, cm]
                    newrec = [rec[0], acres]
                    cur.updateRow(newrec)

                else:
                    raise MyError, "Failed to get polygon area for AOI geometry"

        return True

    except MyError, e:
        # Example: raise MyError, "This is an error message"
        PrintMsg(str(e), 2)
        return False

    except:
        errorMsg()
        return False

## ===================================================================================
def AddNewFields(newTable, columnNames, columnInfo):
    # Create the empty output table that will contain the map unit AWS
    #
    # ColumnNames and columnInfo come from the Attribute query JSON string
    # MUKEY would normally be included in the list, but it should already exist in the output featureclass
    #
    try:
        # Dictionary: SQL Server to FGDB
        dType = dict()

        dType["int"] = "long"
        dType["bigint"] = "long"
        dType["smallint"] = "short"
        dType["tinyint"] = "short"
        dType["bit"] = "short"
        dType["varbinary"] = "blob"
        dType["nvarchar"] = "text"
        dType["varchar"] = "text"
        dType["char"] = "text"
        dType["datetime"] = "date"
        dType["datetime2"] = "date"
        dType["smalldatetime"] = "date"
        dType["decimal"] = "double"
        dType["numeric"] = "double"
        dType["float"] = "double"
        dType["udt"] = "text"  # probably geometry or geography data
        dType["xml"] = "text"

        dType2 = dict()
        dType2["ProviderSpecificDataType"] = "Microsoft.SqlServer.Types.SqlGeometry"

        # numeric type conversion depends upon the precision and scale
        dType["numeric"] = "float"  # 4 bytes
        dType["real"] = "double" # 8 bytes

        # Iterate through list of field names and add them to the output table
        i = 0

        # ColumnInfo contains:
        # ColumnOrdinal, ColumnSize, NumericPrecision, NumericScale, ProviderType, IsLong, ProviderSpecificDataType, DataTypeName
        # PrintMsg(" \nFieldName, Length, Precision, Scale, Type", 1)
        # Field soilgeog: [u'ColumnOrdinal=4', u'ColumnSize=2147483647', u'NumericPrecision=255', u'NumericScale=255', u'ProviderType=Udt', u'IsLong=True', u'ProviderSpecificDataType=Microsoft.SqlServer.Types.SqlGeometry', u'DataTypeName=tempdb.sys.geography']

        joinFields = list()

        # Get list of existing fields iin newTable
        existingFlds = [fld.name.upper() for fld in arcpy.Describe(newTable).fields]

        for i, fldName in enumerate(columnNames):
            vals = columnInfo[i].split(",")
            length = int(vals[1].split("=")[1])
            precision = int(vals[2].split("=")[1])
            scale = int(vals[3].split("=")[1])

            if fldName is None or fldName == "":
                raise MyError, "Query for " + os.path.basenaame(newTable) + " returned an empty fieldname (" + str(columnNames) + ")"

            try:
                # Need to handle 'udt' data type differently below.
                # getting ProviderType
                dataType = dType[vals[4].lower().split("=")[1]]

            except:
                PrintMsg(" \nFieldName " + fldName + ": " + str(vals), 1)
                raise MyError, "Cannot handle datatype '" + vals[4].lower().split("=")[1] + "'"

            if not fldName.upper() in existingFlds and not dataType == "udt" and not fldName.upper() in ["WKTGEOM", "WKBGEOG", "SOILGEOG"]:
                arcpy.AddField_management(newTable, fldName, dataType, precision, scale, length)
                joinFields.append(fldName)

        if arcpy.Exists(newTable):
            #PrintMsg(" \nNew table fields: " + ", ".join(joinFields), 1)
            return joinFields

        else:
            return []

    except MyError, e:
        # Example: raise MyError, "This is an error message"
        PrintMsg(str(e), 2)
        return []

    except:
        errorMsg()
        return []

## ===================================================================================
def GetUniqueValues(theInput, fieldName):
    # Create bracketed list of MUKEY values from spatial layer for use in query
    #
    try:
        # Tell user how many features are being processed
        theDesc = arcpy.Describe(theInput)
        theDataType = theDesc.dataType
        PrintMsg("", 0)

        #if theDataType.upper() == "FEATURELAYER":
        # Get Featureclass and total count
        if theDataType.lower() == "featurelayer":
            theFC = theDesc.featureClass.catalogPath
            theResult = arcpy.GetCount_management(theFC)

        elif theDataType.lower() in ["table", "featureclass", "shapefile"]:
            theResult = arcpy.GetCount_management(theInput)

        else:
            raise MyError, "Unknown data type: " + theDataType.lower()

        iTotal = int(theResult.getOutput(0))

        if iTotal > 0:
            sqlClause = ("DISTINCT " + fieldName, "ORDER BY " + fieldName)
            valList = list()

            with arcpy.da.SearchCursor(theInput, [fieldName], sql_clause=sqlClause) as cur:
                for rec in cur:
                    val = str(rec[0]).encode('ascii')

                    if not val == '' and not val in valList:
                        valList.append(val)

                del rec, cur

            #PrintMsg("\tmukey list: " + str(mukeyList), 1)
            return valList

        else:
            return []

    except MyError, e:
        # Example: raise MyError, "This is an error message"
        PrintMsg(str(e), 2)
        return []

    except:
        errorMsg()
        return []

## ===================================================================================
def TestLegends(outputValues):
    # Use to match unpublished interp output values with one of the existing map legend type
    # so that symbology can be defined for the new map layer

    try:

        dTests = dict()
        dTests["limitation1"] = {'colors': {1: {'blue': '0', 'green': '0', 'red': '255'}, 2: {'blue': '0', 'green': '255', 'red': '255'}, 3: {'blue': '0', 'green': '255', 'red': '0'}}, 'labels': {1: {'order': '1', 'value': 'Very limited', 'label': 'Very limited'}, 2: {'order': '2', 'value': 'Somewhat limited', 'label': 'Somewhat limited'}, 3: {'order': '3', 'value': 'Not limited', 'label': 'Not limited'}}, 'type': '2', 'name': 'Defined', 'maplegendkey': '5'}
        dTests["limitation2"] = {'colors': {1: {'blue': '0', 'green': '0', 'red': '255'}, 2: {'blue': '0', 'green': '170', 'red': '255'}, 3: {'blue': '0', 'green': '255', 'red': '0'}, 4: {'blue': '115', 'green': '178', 'red': '115'}}, 'labels': {1: {'order': '1', 'value': 'Very Severe', 'label': 'Very Severe'}, 2: {'order': '2', 'value': 'Severe', 'label': 'Severe'}, 3: {'order': '3', 'value': 'Moderate', 'label': 'Moderate'}, 4: {'order': '4', 'value': 'Slight', 'label': 'Slight'}}, 'type': '2', 'name': 'Defined', 'maplegendkey': '5'}
        dTests["suitability3"] = {'colors': {1: {'blue': '0', 'green': '0', 'red': '255'}, 2: {'blue': '0', 'green': '255', 'red': '255'}, 3: {'blue': '0', 'green': '255', 'red': '255'}}, 'labels': {1: {'order': '1', 'value': 'Poorly suited', 'label': 'Poorly suited'}, 2: {'order': '2', 'value': 'Moderately suited', 'label': 'Moderately suited'}, 3: {'order': '3', 'value': 'Well suited', 'label': 'Well suited'}}, 'type': '2', 'name': 'Defined', 'maplegendkey': '5'}
        dTests["suitability4"] = {'colors': {1: {'blue': '0', 'green': '0', 'red': '255'}, 2: {'blue': '0', 'green': '255', 'red': '255'}, 3: {'blue': '0', 'green': '255', 'red': '0'}}, 'labels': {1: {'order': '1', 'value': 'Unsuited', 'label': 'Unsuited'}, 2: {'order': '2', 'value': 'Poorly suited', 'label': 'Poorly suited'}, 3: {'order': '3', 'value': 'Moderately suited', 'label': 'Moderately suited'}, 4: {'order': '4', 'value': 'Well suited', 'label': 'Well suited'}}, 'type': '2', 'name': 'Defined', 'maplegendkey': '5'}
        dTests["susceptibility"] = {'colors': {1: {'blue': '0', 'green': '0', 'red': '255'}, 2: {'blue': '0', 'green': '255', 'red': '255'}, 3: {'blue': '0', 'green': '255', 'red': '0'}}, 'labels': {1: {'order': '1', 'value': 'Highly susceptible', 'label': 'Highly susceptible'}, 2: {'order': '2', 'value': 'Moderately susceptible', 'label': 'Moderately susceptible'}, 3: {'order': '3', 'value': 'Slightly susceptible', 'label': 'Slightly susceptible'}}, 'type': '2', 'name': 'Defined', 'maplegendkey': '5'}
        dTests["penetration"] = {'colors': {1: {'blue': '0', 'green': '0', 'red': '255'}, 2: {'blue': '0', 'green': '85', 'red': '255'}, 3: {'blue': '0', 'green': '170', 'red': '255'}, 4: {'blue': '0', 'green': '255', 'red': '255'}, 5: {'blue': '0', 'green': '255', 'red': '169'}, 6: {'blue': '0', 'green': '255', 'red': '84'}, 7: {'blue': '0', 'green': '255', 'red': '0'}}, 'labels': {1: {'order': '1', 'value': 'Unsuited', 'label': 'Unsuited'}, 2: {'order': '2', 'value': 'Very low penetration', 'label': 'Very low penetration'}, 3: {'order': '3', 'value': 'Low penetration', 'label': 'Low penetration'}, 4: {'order': '4', 'value': 'Moderate penetration', 'label': 'Moderate penetration'}, 5: {'order': '5', 'value': 'High penetration', 'label': 'High penetration'}, 6: {'order': '6', 'value': 'Very high penetration', 'label': 'Very high penetration'}, 7: {'order': '7', 'value': 'Very high penetration', 'label': 'Very high penetration'}}, 'type': '2', 'name': 'Defined', 'maplegendkey': '5'}
        dTests["excellent"] = {'colors': {1: {'blue': '0', 'green': '0', 'red': '255'}, 2: {'blue': '0', 'green': '170', 'red': '255'}, 3: {'blue': '0', 'green': '255', 'red': '169'}, 4: {'blue': '0', 'green': '255', 'red': '0'}}, 'labels': {1: {'order': '1', 'value': 'Poor', 'label': 'Poor'}, 2: {'order': '2', 'value': 'Fair', 'label': 'Fair'}, 3: {'order': '3', 'value': 'Good', 'label': 'Good'}, 4: {'order': '4', 'value': 'Excellent', 'label': 'Excellent'}}, 'type': '2', 'name': 'Defined', 'maplegendkey': '5'}
        dTests["risk1"] = {'colors': {1: {'blue': '0', 'green': '0', 'red': '255'}, 2: {'blue': '0', 'green': '255', 'red': '255'}, 3: {'blue': '0', 'green': '255', 'red': '0'}}, 'labels': {1: {'order': '1', 'value': 'Severe', 'label': 'Severe'}, 2: {'order': '2', 'value': 'Moderate', 'label': 'Moderate'}, 3: {'order': '3', 'value': 'Slight', 'label': 'Slight'}}, 'type': '2', 'name': 'Defined', 'maplegendkey': '5'}
        dTests["risk2"] = {'colors': {1: {'blue': '0', 'green': '0', 'red': '255'}, 2: {'blue': '0', 'green': '255', 'red': '255'}, 3: {'blue': '0', 'green': '255', 'red': '0'}}, 'labels': {1: {'order': '1', 'value': 'High', 'label': 'High'}, 2: {'order': '2', 'value': 'Medium', 'label': 'Medium'}, 3: {'order': '3', 'value': 'Low', 'label': 'Low'}}, 'type': '2', 'name': 'Defined', 'maplegendkey': '5'}

        for legendType, dTest in dTests.items():
            # get labels
            dLabels = dTest["labels"]
            legendValues = list()

            for order, vals in dLabels.items():
                val = vals["value"]
                legendValues.append(val)

            bMatched = True

            for val in outputValues:
                if not val in legendValues and not val.upper() == "NOT RATED" and not val is None:
                    bMatched = False

            if bMatched == True:
                #PrintMsg(" \nFound matching legend for unpublished interp: " + legendType, 1)
                dLegend["colors"] = dTest["colors"]
                dLegend["labels"] = dTest["labels"]
                dLegend["name"] = "Defined"
                dLegend["type"] = '2'
                dLegend["maplegendkey"] = '5'
                dSDV["maplegendkey"] = 5

                #PrintMsg(" \n" + str(dLegend), 1)
                break

            #else:
            #    PrintMsg(" \nNOT a matching legend for unpublished interp: " + legendType, 1)

        return True

    except MyError, e:
        PrintMsg(str(e), 2)
        return False

    except:
        errorMsg()
        return False

## ===================================================================================
def FormSDA_Queries(aoiDiss):
    #
    # Create a multipolygon insert to help build a multi-land unit spatial table in SDA
    #
    # /** SDA Query application="CART" rule="Generalized Resource Assessment" version="0.1" **/
    try:
        #PrintMsg(" \nForming query for AOI using layer: " + aoiDiss, 0)

        gcs = arcpy.SpatialReference(epsgWGS84)
        i = 0
        wkt = ""
        landunit = ""
        #landUnits = list()
        now = datetime.datetime.now()
        timeStamp = now.strftime('%Y-%m-%d T%H:%M:%S')

        # sQuery is the query string that will be incorporated into the SDA request
        #
        sQuery = "-- " + timeStamp + """ \n
/** SDA Query application="CART" rule="Generalized Resource Assessment" version="0.1" **/
-- BEGIN CREATING AOI QUERY
--
-- Declare all variables here
~DeclareChar(@attributeName,60)~
~DeclareChar(@ruleDesign,60)~
~DeclareChar(@ruleKey,30)~
~DeclareChar(@rating1,60)~
~DeclareChar(@rating2,60)~
~DeclareChar(@rating3,60)~
~DeclareChar(@rating4,60)~
~DeclareChar(@rating5,60)~
~DeclareChar(@rating6,60)~
~DeclareVarchar(@dateStamp,20)~
~DeclareInt(@minAcres)~
~DeclareInt(@minPct)~
~DeclareGeometry(@aoiGeom)~
~DeclareGeometry(@aoiGeomFixed)~
~DeclareChar(@ratingKey,70)~
~DeclareChar(@notRatedPhrase,15)~
~DeclareInt(@Level)~

-- Create AOI table with polygon geometry. Coordinate system must be WGS1984 (EPSG 4326)
CREATE TABLE #AoiTable
    ( aoiid INT IDENTITY (1,1),
    landunit CHAR(20),
    aoigeom GEOMETRY )
;

-- Insert identifier string and WKT geometry for each AOI polygon after this...
"""

        if bProjected:
            # Project geometry from AOI
            #PrintMsg("\tForm AOI query for projected data...", 1)

            with arcpy.da.SearchCursor(aoiDiss, ["landunit", "SHAPE@"]) as cur:
                for rec in cur:
                    landunit = str(rec[0]).replace("\n", " ")
                    #landUnits.append(landunit)
                    polygon = rec[1]                                  # original geometry
                    outputPolygon = polygon.projectAs(gcs, tm)        # simplified geometry, projected to WGS 1984
                    wkt = outputPolygon.WKT
                    #PrintMsg("\t\tlandunit: " + str(landunit), 1)
                    sQuery += " \nINSERT INTO #AoiTable ( landunit, aoigeom ) "
                    sQuery += " \nVALUES ('" + landunit + "', geometry::STGeomFromText('" + wkt + "', 4326));"

        else:
            # No projection required. AOI must be GCS WGS 1984
            # LandUnit attribute column is required for this to work. Need to add an alternative for Merged fields.

            #PrintMsg("\tForm spatial query 4", 1)

            with arcpy.da.SearchCursor(aoiDiss, ["landunit", "SHAPE@"]) as cur:
                for rec in cur:
                    landunit = str(rec[0]).replace("\n", " ")         # landunit was created with a newline separator between tract and field number. Need to remove it.
                    #landUnits.append(landunit)
                    polygon = rec[1]                                  # original geometry
                    wkt = polygon.WKT
                    sQuery += " \nSELECT @aoiGeom = GEOMETRY::STGeomFromText('" + wkt + "', 4326);"
                    sQuery += " \nSELECT @aoiGeomFixed = @aoiGeom.MakeValid().STUnion(@aoiGeom.STStartPoint());"
                    sQuery += " \nINSERT INTO #AoiTable ( landunit, aoigeom ) "
                    sQuery += " \nVALUES ('" + landunit + "', @aoiGeomFixed);"


        sQuery += """

-- End of AOI geometry section

-- #AoiAcres table to contain summary acres for each landunit
CREATE TABLE #AoiAcres
    ( aoiid INT,
    landunit CHAR(20),
    landunit_acres FLOAT )
;

-- #LandunitRatingsDetailed1 table
CREATE TABLE #LandunitRatingsDetailed1
    ( aoiid INT,
    landunit CHAR(20),
    attributename CHAR(60),
    rating_class CHAR(60),
    rating_value INT,
    rating_key CHAR(60),
    rating_pct FLOAT,
    rating_acres FLOAT,
    landunit_acres FLOAT )
;

-- #LandunitRatingsDetailed2 table
CREATE TABLE #LandunitRatingsDetailed2
    (landunit CHAR(20),
    attributename CHAR(60),
    rating_class CHAR(60),
    rating_value INT,
    rating_key CHAR(60),
    rating_pct FLOAT,
    rating_acres FLOAT,
    landunit_acres FLOAT,
    rolling_pct FLOAT,
    rolling_acres FLOAT )
;

-- #LandunitRatingsCART table
CREATE TABLE #LandunitRatingsCART
    (id INT,
    landunit CHAR(20),
    attributename CHAR(60),
    rating_class CHAR(60),
    rating_value INT,
    rating_key CHAR(60),
    rolling_pct FLOAT,
    rolling_acres FLOAT,
    landunit_acres FLOAT )
;

-- #LandunitRatingsCART2 table
-- This table will only contain the final, overall ratings for CART
CREATE TABLE #LandunitRatingsCART2
    (id INT IDENTITY (1,1),
    landunit CHAR(20),
    attributename CHAR(60),
    rating_class CHAR(60),
    rating_key CHAR(60),
    rating_value INT,  -- Need to change to rating_value
    rolling_pct FLOAT,
    rolling_acres FLOAT,
    landunit_acres FLOAT,
    soils_metadata VARCHAR(150) )
;

-- #AoiSoils table contains intersected soil polygon table with geometry
CREATE TABLE #AoiSoils
    ( polyid INT IDENTITY (1,1),
    aoiid INT,
    landunit CHAR(20),
    mukey INT,
    soilgeom GEOMETRY )
;

-- #AoiSoils2 table contains Soil geometry with landunits
CREATE TABLE #AoiSoils2
    ( aoiid INT,
    polyid INT,
    landunit CHAR(20),
    mukey INT,
    poly_acres FLOAT,
    soilgeog GEOGRAPHY )
;

-- #M2 table contains Soil map unit acres, aggregated by mukey (merges polygons together)
CREATE TABLE #M2
    ( aoiid INT,
    landunit CHAR(20),
    mukey INT,
    mapunit_acres FLOAT )
;

-- #FC table contains Soil map unit acres, aggregated by mukey Farm Class
CREATE TABLE #FC
    ( aoiid INT,
    landunit CHAR(20),
    mukey INT,
    mapunit_acres FLOAT,
    farmlndclass CHAR(30) )
;

-- #M4 table contains Component level data with cokey, comppct_r and mapunit sum-of-comppct_r (major components only)
CREATE TABLE #M4
(   aoiid INT,
    landunit CHAR(20),
    mukey INT,
    mapunit_acres FLOAT,
    cokey INT,
    compname CHAR(60),
    comppct_r INT,
    majcompflag CHAR(3),
    mu_pct_sum INT,
    major_mu_pct_sum INT,
    drainagecl CHAR(254)
    );

-- #M5 table contains Component level ratings for the currently selected soil interpretation
CREATE TABLE #M5
   ( aoiid INT,
    landunit CHAR(20),
    mukey INT,
    mapunit_acres FLOAT,
    cokey INT,
    compname CHAR(60),
    comppct_r INT,
    rating_class CHAR(60),
    mu_pct_sum INT )
;

-- #M6 table contains Component level ratings with adjusted component percent to account for missing minor components
CREATE TABLE #M6
   ( aoiid INT,
    landunit CHAR(20),
    mukey INT,
    mapunit_acres FLOAT,
    cokey INT,
    compname CHAR(60),
    comppct_r INT,
    rating_class CHAR(60),
    mu_pct_sum INT,
    adj_comp_pct FLOAT )
;

-- #M8 table contains Component acres by multiplying map unit acres with adjusted component percent
CREATE TABLE #M8
    ( aoiid INT,
    landunit CHAR(20),
    mukey INT,
    mapunit_acres FLOAT,
    cokey INT,
    compname CHAR(60),
    comppct_r INT,
    rating_class CHAR(60),
    MU_pct_sum INT,
    adj_comp_pct FLOAT,
    co_acres FLOAT )
;

-- #M10 table contains Aggregated rating class values and sum of component acres  by landunit (Tract and Field number)
CREATE TABLE #M10
    ( landunit CHAR(20),
    rating_class CHAR(60),
    rating_acres FLOAT )
;

-- Hydric table contains soils at the Map Unit, using all map units from table #M2.
CREATE TABLE #Hydric1
    (mukey INT,
    comp_count INT,        -- cnt_comp
    count_maj_comp INT,    -- cnt_mjr
    all_hydric INT,        -- cnt_hydric
    all_not_hydric INT,    -- cnt_nonhydric
    maj_hydric INT,        -- cnt_mjr_hydric
    maj_not_hydric INT,    -- cnt_mjr_nonhydric
    hydric_inclusions INT, -- cnt_minor_hydric
    hydric_null INT )      -- cnt_null_hydric
;

-- #Hydric2 table contains the Low, Rv, and High range for Hydric
CREATE TABLE #Hydric2
    (mukey INT,
    hydric_rating CHAR (25),
    low_pct FLOAT,
    rv_pct FLOAT,
    high_pct FLOAT )
;

-- #Hydric3 table contains hydric rating acres
CREATE TABLE #Hydric3
    (aoiid INT,
    landunit CHAR(20),
    attributename CHAR(60),
    AOI_Acres FLOAT,
    rating_class CHAR(60),
    rating_key CHAR(60),
    mukey INT,
    hydric_flag INT,
    low_acres FLOAT,
    rv_acres FLOAT,
    high_acres  FLOAT )
;

-- Identify all hydric components by map unit, using table #M4.
CREATE TABLE #Hydric_A
    (mukey INT,
    cokey INT,
    hydric_pct INT )
;

-- Hydric soils at the mapunit level, using all components where hydricrating = 'Yes'.
CREATE TABLE #Hydric_B
    (mukey INT,
    hydric_pct INT )
;

-- #SDV table contains rule settings from sdvattribute table
CREATE TABLE #SDV
    (attributekey BIGINT,
    attributename CHAR(60),
    attributetablename CHAR(30),
    attributecolumnname CHAR(30),
    attributelogicaldatatype CHAR(20),
    attributefieldsize SMALLINT,
    attributeprecision TINYINT,
    attributedescription NVARCHAR(MAX),
    attributeuom NVARCHAR(60),
    attributeuomabbrev NVARCHAR(30),
    attributetype CHAR(20),
    nasisrulename CHAR(60),
    ruledesign NVARCHAR(60),
    notratedphrase CHAR(15),
    mapunitlevelattribflag TINYINT,
    complevelattribflag TINYINT,
    cmonthlevelattribflag TINYINT,
    horzlevelattribflag TINYINT,
    tiebreakdomainname CHAR(40),
    tiebreakruleoptionflag TINYINT,
    tiebreaklowlabel CHAR(20),
    tiebreakhighlabel CHAR(20),
    tiebreakrule SMALLINT,
    resultcolumnname CHAR(10),
    sqlwhereclause CHAR(255),
    primaryconcolname CHAR(30),
    pcclogicaldatatype CHAR(20),
    primaryconstraintlabel CHAR(30),
    secondaryconcolname CHAR(30),
    scclogicaldatatype CHAR(20),
    secondaryconstraintlabel CHAR(30),
    dqmodeoptionflag TINYINT,
    depthqualifiermode CHAR(20),
    layerdepthtotop FLOAT,
    layerdepthtobottom FLOAT,
    layerdepthuom CHAR(20),
    monthrangeoptionflag TINYINT,
    beginningmonth CHAR(9),
    endingmonth CHAR(9),
    horzaggmeth CHAR(30),
    interpnullsaszerooptionflag TINYINT,
    interpnullsaszeroflag TINYINT,
    nullratingreplacementvalue CHAR(254),
    basicmodeflag TINYINT,
    maplegendkey SMALLINT,
    maplegendclasses TINYINT,
    maplegendxml XML,
    nasissiteid BIGINT,
    wlupdated DATETIME,
    algorithmname CHAR(50),
    componentpercentcutoff TINYINT,
    readytodistribute TINYINT,
    effectivelogicaldatatype CHAR(20),
    rulekey CHAR(30) )
;

-- #RatingClasses table contains the first six rating classes for each interp
CREATE TABLE #RatingClasses
    (attributename CHAR(60),
    ruledesign CHAR(60),
    rating1 CHAR(60),
    rating2 CHAR(60),
    rating3 CHAR(60),
    rating4 CHAR(60),
    rating5 CHAR(60),
    rating6 CHAR(60) )
;

-- #RatingDomain table containing the domain values for each CART rating for each interp
CREATE TABLE #RatingDomain
    (id INT IDENTITY (1,1),
    rating_key CHAR(60),
    attributename CHAR(60),
    rating_class CHAR(60),
    rating_value INT )
;

-- #DateStamps table to store survey area datestamps (sacatalog.saverest)
CREATE TABLE #DateStamps
    (landunit CHAR(20),
    datestamp VARCHAR(32) )
;

-- #LandunitMetadata table to store landunit metadata (survey area and saverest) which comes from #DateStamps
CREATE TABLE #LandunitMetadata
    (landunit CHAR(20),
    soils_metadata VARCHAR(150) )
;

-- End of CREATE TABLE section

-- Populate #SDV with interp metadata
INSERT INTO #SDV (attributename, attributecolumnname, attributelogicaldatatype, attributetype,
    attributeuom, nasisrulename, rulekey, ruledesign, notratedphrase, resultcolumnname,
    effectivelogicaldatatype, attributefieldsize, maplegendxml, maplegendkey, attributedescription,
    sqlwhereclause, secondaryconcolname, tiebreaklowlabel, tiebreakhighlabel)
    SELECT sdv.attributename, sdv.attributecolumnname, sdv.attributelogicaldatatype, sdv.attributetype,
    sdv.attributeuom, sdv.nasisrulename, md.rulekey, md.ruledesign, sdv.notratedphrase, sdv.resultcolumnname,
    sdv.effectivelogicaldatatype, sdv.attributefieldsize, sdv.maplegendxml, sdv.maplegendkey, sdv.attributedescription,
    sdv.sqlwhereclause, sdv.secondaryconcolname,tiebreaklowlabel, tiebreakhighlabel
    FROM sdvattribute sdv
    LEFT OUTER JOIN distinterpmd md ON sdv.nasisrulename = md.rulename
    WHERE sdv.attributename IN ('Agricultural Organic Soil Subsidence', 'Soil Susceptibility to Compaction', 'Organic Matter Depletion', 'Surface Salt Concentration', 'Suitability for Aerobic Soil Organisms', 'Hydric Rating by Map Unit')
    GROUP BY md.rulekey, sdv.attributename, sdv.attributecolumnname, sdv.attributelogicaldatatype, sdv.attributetype, sdv.attributeuom, sdv.nasisrulename, sdv.resultcolumnname, sdv.effectivelogicaldatatype,
    sdv.attributefieldsize, md.ruledesign, sdv.notratedphrase, sdv.maplegendxml, sdv.maplegendkey, sdv.attributedescription, sqlwhereclause, secondaryconcolname, tiebreaklowlabel, tiebreakhighlabel
;

-- Populate #AoiAcres table
INSERT INTO #AoiAcres (aoiid, landunit, landunit_acres )
    SELECT  aoiid, landunit,
    SUM( ROUND( ( ( GEOGRAPHY::STGeomFromWKB(aoigeom.STAsBinary(), 4326 ).STArea() ) / 4046.8564224 ), 3 ) ) AS landunit_acres
    FROM #AoiTable
    GROUP BY aoiid, landunit
;

-- Populate #AoiSoils table with intersected soil polygon geometry
INSERT INTO #AoiSoils (aoiid, landunit, mukey, soilgeom)
    SELECT A.aoiid, A.landunit, M.mukey, M.mupolygongeo.STIntersection(A.aoigeom ) AS soilgeom
    FROM mupolygon M, #AoiTable A
    WHERE mupolygongeo.STIntersects(A.aoigeom) = 1
;

-- Populate #AoiSoils2 Soil geometry with landunit attribute
INSERT INTO #AoiSoils2
    SELECT aoiid, polyid, landunit, mukey, ROUND((( GEOGRAPHY::STGeomFromWKB(soilgeom.STAsBinary(), 4326 ).STArea() ) / 4046.8564224 ), 3 ) AS poly_acres, GEOGRAPHY::STGeomFromWKB(soilgeom.STAsBinary(), 4326 ) AS soilgeog
    FROM #AoiSoils
;

-- Populate #M2 soil map unit acres, aggregated by mukey (merges polygons together)
INSERT INTO #M2
    SELECT DISTINCT M1.aoiid, M1.landunit, M1.mukey,
    ROUND (SUM (M1.poly_acres) OVER(PARTITION BY M1.landunit, M1.mukey), 3) AS mapunit_acres
    FROM #AoiSoils2 AS M1
    GROUP BY M1.aoiid, M1.landunit, M1.mukey, M1.poly_acres
;

-- Populate #FC table with Farm Land Class
INSERT INTO #FC
    SELECT aoiid, landunit, mu.mukey, mapunit_acres,
    CASE WHEN farmlndcl IS NULL  THEN 'Not rated'
        WHEN farmlndcl =  'All areas are prime farmland' THEN 'Prime'
        WHEN farmlndcl LIKE 'Prime if%' THEN 'Prime if'
        WHEN farmlndcl =  'Farmland of statewide importance' THEN 'State'
        WHEN farmlndcl LIKE 'Farmland of statewide importance, if%' THEN 'State if'
        WHEN farmlndcl = 'Farmland of local importance' THEN 'Local'
        WHEN farmlndcl LIKE 'Farmland of local importance, if%' THEN 'Local if'
        WHEN farmlndcl = 'Farmland of unique importance' THEN 'Unique'
        ELSE 'Not Prime'
    END AS farmlndclass
    FROM #M2 AS fcc
    INNER JOIN mapunit AS mu ON mu.mukey = fcc.mukey
;

-- Populate #M4 table with component level data with cokey, comppct_r and mapunit sum-of-comppct_r
INSERT INTO #M4
SELECT M2.aoiid, M2.landunit, M2.mukey, mapunit_acres, CO.cokey, CO.compname, CO.comppct_r, CO.majcompflag,
SUM (CO.comppct_r) OVER(PARTITION BY M2.landunit, M2.mukey) AS mu_pct_sum, (SELECT SUM (CCO.comppct_r)
FROM #M2 AS MM2
INNER JOIN component AS CCO ON CCO.mukey = MM2.mukey AND M2.mukey = MM2.mukey AND majcompflag = 'Yes' AND M2.landunit = MM2.landunit) AS  major_mu_pct_sum,
drainagecl
FROM #M2 AS M2
INNER JOIN component AS CO ON CO.mukey = M2.mukey
GROUP BY  M2.aoiid, M2.landunit, M2.mukey, mapunit_acres, CO.cokey, CO.compname, CO.comppct_r, CO.majcompflag, drainagecl
;

-- Populate #DateStamps with survey area dates for all soil mapunits involved
INSERT INTO #DateStamps
    SELECT DISTINCT AM.landunit, ([SC].[areasymbol] + ' ' + CONVERT(VARCHAR(32),[SC].[saverest],120) ) AS datestamp
    FROM #M4 AM
    INNER JOIN mapunit Mu ON AM.mukey = Mu.mukey
    INNER JOIN legend LG ON Mu.lkey = LG.lkey
    INNER JOIN sacatalog SC ON Lg.areasymbol = SC.areasymbol
;

-- Populate #LandunitMetadata table with landunit soils-metadata
--
INSERT INTO #LandunitMetadata
    SELECT DISTINCT
    landunit,
    STUFF((SELECT ' | ' + CAST([datestamp] AS VARCHAR(30))
    FROM #DateStamps dt2
    WHERE dt1.landunit = dt2.landunit
    FOR XML PATH ('') ), 1, 2, '') AS soils_metadata
    FROM #DateStamps dt1
;

-- END OF STATIC SECTION
-- ************************************************************************************************
"""

        #bPropertyQueries = True


        #PrintMsg(" \nOver ride property queries to always run", 1)

        if bCartQueries or bInterpQueries:
            # This was bPropertyQueries but I switched it out because nothing wa returned
            # Generate queries for selected soil properties

            arcpy.SetProgressorLabel("Adding Soil Property Queries")
            sPropertyQuery = """

-- BEGIN QUERIES FOR SOIL PROPERTIES...
-- ************************************************************************************************

---- START DRAINAGE CLASS------------
CREATE TABLE #drain
( aoiid INT ,
landunit CHAR(20),
landunit_acres FLOAT,
mukey INT,
mapunit_acres FLOAT,
cokey INT,
compname CHAR(280),
comppct_r INT,
majcompflag CHAR(4),
mu_pct_sum INT,
major_mu_pct_sum INT,
drainagecl CHAR(40),
adj_comp_pct DECIMAL (6, 2)
)
;

INSERT INTO #drain
SELECT #M4.aoiid, #M4.landunit, #AoiAcres.landunit_acres, mukey, mapunit_acres, cokey, compname,
comppct_r, majcompflag, mu_pct_sum, major_mu_pct_sum, drainagecl, (1.0 * comppct_r / NULLIF(mu_pct_sum, 0)) AS adj_comp_pct
FROM #M4
LEFT OUTER JOIN #AoiAcres ON #AoiAcres.aoiid = #M4.aoiid
;

CREATE TABLE #drain2
( aoiid INT ,
landunit CHAR(20),
landunit_acres FLOAT,
mukey INT,
mapunit_acres FLOAT,
cokey INT,
compname CHAR(280),
comppct_r INT,
majcompflag CHAR(4),
mu_pct_sum INT,
drainagecl CHAR(40),
adj_comp_pct DECIMAL (6, 2),
co_acres DECIMAL (10, 2))
;

-- Populate drainage class for mapunit and components
INSERT INTO #drain2
SELECT aoiid, landunit, landunit_acres,  mukey, mapunit_acres, cokey, compname, comppct_r,
majcompflag, mu_pct_sum, drainagecl, adj_comp_pct, ROUND ( (adj_comp_pct * mapunit_acres), 2) AS co_acres
FROM #drain
;

-- Begin SOC
CREATE TABLE #acpf
( aoiid INT ,
landunit CHAR(20),
mukey INT,
mapunit_acres FLOAT,
cokey INT,
compname CHAR(60),
comppct_r INT,
majcompflag  CHAR(3),
localphase CHAR(60),
hzname CHAR(20),
hzdept_r INT,
hzdepb_r INT,
awc_r FLOAT,
restrictiondepth INT,
restrictiodepth INT,
TOPrestriction	CHAR(80),
tcl CHAR(40),
thickness INT,
om_r FLOAT,
dbthirdbar_r FLOAT,
fragvol INT,
texture	CHAR(40),
chkey INT,
mu_pct_sum INT)
;

INSERT INTO #acpf
SELECT DISTINCT
MA44.aoiid ,
MA44.landunit,
MA44.mukey,
MA44.mapunit_acres,
MA44.cokey,
MA44.compname,
MA44.comppct_r,
MA44.majcompflag,
localphase,
hzname,
hzdept_r,
hzdepb_r,
awc_r ,
(SELECT CAST(MIN(resdept_r) AS INTEGER) FROM component LEFT OUTER JOIN corestrictions ON component.cokey = corestrictions.cokey WHERE component.cokey = coa.cokey AND reskind IS NOT NULL) AS restrictiondepth,
(SELECT CASE WHEN MIN (resdept_r) IS NULL THEN 200 ELSE CAST (MIN (resdept_r) AS INT) END FROM component LEFT OUTER JOIN corestrictions ON component.cokey = corestrictions.cokey WHERE component.cokey = coa.cokey AND reskind IS NOT NULL) AS restrictiodepth,
(SELECT TOP 1 reskind FROM component LEFT OUTER JOIN corestrictions ON component.cokey = corestrictions.cokey WHERE component.cokey = coa.cokey AND corestrictions.reskind IN ('Lithic bedrock','Duripan', 'Densic bedrock', 'Paralithic bedrock', 'Fragipan', 'Natric', 'Ortstein', 'Permafrost', 'Petrocalcic', 'Petrogypsic')
AND reskind IS NOT NULL ORDER BY resdept_r) AS TOPrestriction,
(SELECT TOP 1 texcl FROM chtexturegrp AS chtg INNER JOIN chtexture AS cht ON chtg.chtgkey=cht.chtgkey  AND chtg.rvindicator = 'yes' AND chtg.chkey=cha.chkey) AS tcl,
CASE WHEN (hzdepb_r-hzdept_r) IS NULL THEN 0 ELSE CAST((hzdepb_r - hzdept_r) AS INT) END AS thickness,
CASE WHEN texture LIKE '%PM%' AND (om_r) IS NULL THEN 35
WHEN texture LIKE '%MUCK%' AND (om_r) IS NULL THEN 35
WHEN texture LIKE '%PEAT%' AND (om_r) IS NULL THEN 35 ELSE om_r END AS om_r ,
CASE WHEN texture LIKE '%PM%' AND (dbthirdbar_r) IS NULL THEN 0.25
WHEN texture LIKE '%MUCK%' AND (dbthirdbar_r) IS NULL THEN 0.25
WHEN texture LIKE '%PEAT%' AND (dbthirdbar_r) IS NULL THEN 0.25 ELSE dbthirdbar_r END AS dbthirdbar_r,
(SELECT CASE WHEN SUM (cf.fragvol_r) IS NULL THEN 0 ELSE CAST (SUM(cf.fragvol_r) AS INT) END FROM chfrags cf WHERE cf.chkey = cha.chkey) as fragvol,
texture,
cha.chkey,
mu_pct_sum
FROM (#M4 AS MA44 INNER JOIN (component AS coa INNER JOIN  chorizon  AS cha  ON cha.cokey = coa.cokey  ) ON MA44.cokey=coa.cokey AND MA44.majcompflag = 'yes' )
LEFT OUTER JOIN  chtexturegrp AS ct ON cha.chkey=ct.chkey and ct.rvindicator = 'yes'
and CASE WHEN hzdept_r IS NULL THEN 2
WHEN texture LIKE '%PM%' AND om_r IS NULL THEN 1
WHEN texture LIKE '%MUCK%' AND om_r IS NULL THEN 1
WHEN texture LIKE '%PEAT%' AND om_r IS NULL THEN 1
WHEN texture LIKE '%PM%' AND dbthirdbar_r IS NULL THEN 1
WHEN texture LIKE '%MUCK%' AND dbthirdbar_r IS NULL THEN 1
WHEN texture LIKE '%PEAT%' AND dbthirdbar_r IS NULL THEN 1
WHEN om_r IS NULL THEN 2
WHEN om_r = 0 THEN 2
WHEN dbthirdbar_r IS NULL THEN 2
WHEN dbthirdbar_r = 0 THEN 2
ELSE 1 END = 1
;

-- Sums the Component Percent and eliminate duplicate values by cokey
SELECT landunit, aoiid, mapunit_acres , mukey, cokey, (1.0 * comppct_r / NULLIF(mu_pct_sum, 0)) AS adj_comp_pct
INTO #muacpf
FROM #acpf AS acpf2
WHERE acpf2.cokey=cokey
GROUP BY landunit, aoiid, mapunit_acres , mukey, cokey, comppct_r, mu_pct_sum
;

-- grab top depth for the mineral soil and will use it later to get mineral surface properties
-- Because of SOC this wasnt really needed. If any error add statement below back
SELECT compname, cokey, MIN(hzdept_r) AS min_t
INTO #hortopdepth
FROM #acpf
---WHERE texture NOT LIKE '%PM%' and texture NOT LIKE '%DOM' and texture NOT LIKE '%MPT%' AND texture NOT LIKE '%MUCK' AND texture NOT LIKE '%PEAT%'
GROUP BY  cokey, compname
;

-- Combine the mineral surface to grab surface mineral properties
SELECT #hortopdepth.cokey,
hzname,
hzdept_r,
hzdepb_r,
thickness,
texture AS texture_surf,
om_r AS om_surf,
dbthirdbar_r AS db_surf,
fragvol AS frag_surf,
chkey
INTO #acpf2
FROM #hortopdepth
INNER JOIN #acpf on #hortopdepth.cokey=#acpf.cokey AND #hortopdepth.min_t = #acpf.hzdept_r
ORDER BY #hortopdepth.cokey, hzname
;

SELECT
mukey,
cokey,
hzname,
restrictiodepth,
hzdept_r,
hzdepb_r,
CASE WHEN (hzdepb_r-hzdept_r) IS NULL THEN 0 ELSE CAST ((hzdepb_r - hzdept_r) AS INT) END AS thickness,
texture,
CASE WHEN dbthirdbar_r IS NULL THEN 0 ELSE dbthirdbar_r  END AS dbthirdbar_r,
CASE WHEN fragvol IS NULL THEN 0 ELSE fragvol  END AS fragvol,
CASE when om_r IS NULL THEN 0 ELSE om_r END AS om_r,
chkey
INTO #acpfhzn
FROM #acpf
;

--- Depth ranges for SOC ----
SELECT hzname, chkey, comppct_r, hzdept_r, hzdepb_r, thickness,
CASE WHEN hzdept_r < 150 then hzdept_r ELSE 0 END AS InRangeTop_0_150,
CASE WHEN hzdepb_r <= 150 THEN hzdepb_r WHEN hzdepb_r > 150 and hzdept_r < 150 THEN 150 ELSE 0 END AS InRangeBot_0_150,
CASE WHEN hzdept_r < 5 then hzdept_r ELSE 0 END AS InRangeTop_0_5,
CASE WHEN hzdepb_r <= 5 THEN hzdepb_r WHEN hzdepb_r > 5 and hzdept_r < 5 THEN 5 ELSE 0 END AS InRangeBot_0_5,
CASE WHEN hzdept_r < 30 then hzdept_r ELSE 0 END AS InRangeTop_0_30,
CASE WHEN hzdepb_r <= 30  THEN hzdepb_r WHEN hzdepb_r > 30  and hzdept_r < 30 THEN 30  ELSE 0 END AS InRangeBot_0_30,
---5 to 15
CASE WHEN hzdepb_r < 5 THEN 0
WHEN hzdept_r >15 THEN 0
WHEN hzdepb_r >= 5 AND hzdept_r < 5 THEN 5
WHEN hzdept_r < 5 THEN 0
WHEN hzdept_r < 15 then hzdept_r ELSE 5 END AS InRangeTop_5_15 ,
CASE WHEN hzdept_r > 15 THEN 0
WHEN hzdepb_r < 5 THEN 0
WHEN hzdepb_r <= 15 THEN hzdepb_r  WHEN hzdepb_r > 15 and hzdept_r < 15 THEN 15 ELSE 5 END AS InRangeBot_5_15,
---15 to 30
CASE WHEN hzdepb_r < 15 THEN 0
WHEN hzdept_r >30 THEN 0
WHEN hzdepb_r >= 15 AND hzdept_r < 15 THEN 15
WHEN hzdept_r < 15 THEN 0
WHEN hzdept_r < 30 then hzdept_r ELSE 15 END AS InRangeTop_15_30 ,
CASE WHEN hzdept_r > 30 THEN 0
WHEN hzdepb_r < 15 THEN 0
WHEN hzdepb_r <= 30 THEN hzdepb_r  WHEN hzdepb_r > 30 and hzdept_r < 30 THEN 30 ELSE 15 END AS InRangeBot_15_30,
--30 to 60
CASE WHEN hzdepb_r < 30 THEN 0
WHEN hzdept_r >60 THEN 0
WHEN hzdepb_r >= 30 AND hzdept_r < 30 THEN 30
WHEN hzdept_r < 30 THEN 0
WHEN hzdept_r < 60 then hzdept_r ELSE 30 END AS InRangeTop_30_60 ,
CASE   WHEN hzdept_r > 60 THEN 0
WHEN hzdepb_r < 30 THEN 0
WHEN hzdepb_r <= 60 THEN hzdepb_r  WHEN hzdepb_r > 60 and hzdept_r < 60 THEN 60 ELSE 30 END AS InRangeBot_30_60,
---60 to 100
CASE WHEN hzdepb_r < 60 THEN 0
WHEN hzdept_r >100 THEN 0
WHEN hzdepb_r >= 60 AND hzdept_r < 60 THEN 60
WHEN hzdept_r < 60 THEN 0
WHEN hzdept_r < 100 then hzdept_r ELSE 60 END AS InRangeTop_60_100 ,
CASE WHEN hzdept_r > 100 THEN 0
WHEN hzdepb_r < 60 THEN 0
WHEN hzdepb_r <= 100 THEN hzdepb_r  WHEN hzdepb_r > 100 and hzdept_r < 100 THEN 100 ELSE 60 END AS InRangeBot_60_100,
--100 to 200
CASE WHEN hzdepb_r < 100 THEN 0
WHEN hzdept_r >200 THEN 0
WHEN hzdepb_r >= 100 AND hzdept_r < 100 THEN 100
WHEN hzdept_r < 100 THEN 0
WHEN hzdept_r < 200 then hzdept_r ELSE 100 END AS InRangeTop_100_200 ,
CASE WHEN hzdept_r > 200 THEN 0
WHEN hzdepb_r < 100 THEN 0
WHEN hzdepb_r <= 200 THEN hzdepb_r  WHEN hzdepb_r > 200 and hzdept_r < 200 THEN 200 ELSE 100 END AS InRangeBot_100_200,
CASE WHEN hzdepb_r < 20 THEN 0
WHEN hzdept_r >50 THEN 0
WHEN hzdepb_r >= 20 AND hzdept_r < 20 THEN 20
WHEN hzdept_r < 20 THEN 0
WHEN hzdept_r < 50 then hzdept_r ELSE 20 END AS InRangeTop_20_50 ,
CASE WHEN hzdept_r > 50 THEN 0
WHEN hzdepb_r < 20 THEN 0
WHEN hzdepb_r <= 50 THEN hzdepb_r  WHEN hzdepb_r > 50 and hzdept_r < 50 THEN 50 ELSE 20 END AS InRangeBot_20_50,
CASE WHEN hzdepb_r < 50 THEN 0
WHEN hzdept_r >100 THEN 0
WHEN hzdepb_r >= 50 AND hzdept_r < 50 THEN 50
WHEN hzdept_r < 50 THEN 0
WHEN hzdept_r < 100 then hzdept_r ELSE 50 END AS InRangeTop_50_100 ,
CASE WHEN hzdept_r > 100 THEN 0
WHEN hzdepb_r < 50 THEN 0
WHEN hzdepb_r <= 100 THEN hzdepb_r  WHEN hzdepb_r > 100 and hzdept_r < 100 THEN 100 ELSE 50 END AS InRangeBot_50_100,
om_r, fragvol, dbthirdbar_r, cokey, mukey, 100.0 - fragvol AS frag_main
INTO #SOC
FROM #acpf
ORDER BY cokey, hzdept_r ASC, hzdepb_r ASC, chkey
;

SELECT mukey, cokey, hzname, chkey, comppct_r, hzdept_r, hzdepb_r, thickness,
InRangeTop_0_150,
InRangeBot_0_150,
InRangeTop_0_30,
InRangeBot_0_30,
InRangeTop_20_50,
InRangeBot_20_50,
InRangeTop_50_100 ,
InRangeBot_50_100,
(( ((InRangeBot_0_150 - InRangeTop_0_150) * ( ( om_r / 1.724 ) * dbthirdbar_r )) / 100.0 ) * ((100.0 - fragvol) / 100.0))  AS HZ_SOC_0_150,
(( ((InRangeBot_0_30 - InRangeTop_0_30) * ( ( om_r / 1.724 ) * dbthirdbar_r )) / 100.0 ) * ((100.0 - fragvol) / 100.0))  AS HZ_SOC_0_30,
---Removed * ( comppct_r * 100 )
((((InRangeBot_20_50 - InRangeTop_20_50) * ( ( om_r / 1.724 ) * dbthirdbar_r )) / 100.0 ) * ((100.0 - fragvol) / 100.0))  AS HZ_SOC_20_50,
---Removed * ( comppct_r * 100 )
((((InRangeBot_50_100 - InRangeTop_50_100) * ( ( om_r / 1.724 ) * dbthirdbar_r )) / 100.0 ) * ((100.0 - fragvol) / 100.0))  AS HZ_SOC_50_100,
(( ((InRangeBot_0_5 - InRangeTop_0_5) * ( ( om_r / 1.724 ) * dbthirdbar_r )) / 100.0 ) * ((100.0 - fragvol) / 100.0))  AS HZ_SOC_0_5,
(( ((InRangeBot_5_15 - InRangeTop_5_15) * ( ( om_r / 1.724 ) * dbthirdbar_r )) / 100.0 ) * ((100.0 - fragvol) / 100.0))  AS HZ_SOC_5_15,
(( ((InRangeBot_15_30 - InRangeTop_15_30) * ( ( om_r / 1.724 ) * dbthirdbar_r )) / 100.0 ) * ((100.0 - fragvol) / 100.0))  AS HZ_SOC_15_30,
(( ((InRangeBot_30_60 - InRangeTop_30_60) * ( ( om_r / 1.724 ) * dbthirdbar_r )) / 100.0 ) * ((100.0 - fragvol) / 100.0))  AS HZ_SOC_30_60,
(( ((InRangeBot_60_100 - InRangeTop_60_100) * ( ( om_r / 1.724 ) * dbthirdbar_r )) / 100.0 ) * ((100.0 - fragvol) / 100.0))  AS HZ_SOC_60_100,
(( ((InRangeBot_100_200 - InRangeTop_100_200) * ( ( om_r / 1.724 ) * dbthirdbar_r )) / 100.0 ) * ((100.0 - fragvol) / 100.0))  AS HZ_SOC_100_200
---Removed * ( comppct_r * 100 )
INTO #SOC2
FROM #SOC
ORDER BY  mukey ,cokey, comppct_r DESC, hzdept_r ASC, hzdepb_r ASC, chkey
;

---Aggregates and sum it by component.
SELECT DISTINCT cokey, mukey,
ROUND (SUM (HZ_SOC_0_150) over(PARTITION BY cokey) ,4) AS CO_SOC_0_150,
ROUND (SUM (HZ_SOC_0_30) over(PARTITION BY cokey) ,4) AS CO_SOC_0_30,
ROUND (SUM (HZ_SOC_20_50) over(PARTITION BY cokey),4) AS CO_SOC_20_50,
ROUND (SUM (HZ_SOC_50_100) over(PARTITION BY cokey),4) AS CO_SOC_50_100,
ROUND (SUM (HZ_SOC_0_5) over(PARTITION BY cokey),4) AS CO_SOC_0_5,
ROUND (SUM (HZ_SOC_5_15) over(PARTITION BY cokey),4) AS CO_SOC_5_15,
ROUND (SUM (HZ_SOC_15_30) over(PARTITION BY cokey),4) AS CO_SOC_15_30,
ROUND (SUM (HZ_SOC_30_60) over(PARTITION BY cokey),4) AS CO_SOC_30_60,
ROUND (SUM (HZ_SOC_60_100) over(PARTITION BY cokey),4) AS CO_SOC_60_100,
ROUND (SUM (HZ_SOC_100_200) over(PARTITION BY cokey),4) AS CO_SOC_100_200
INTO #SOC3
FROM #SOC2
GROUP BY mukey, cokey, HZ_SOC_0_150, HZ_SOC_0_30, HZ_SOC_20_50, HZ_SOC_50_100, HZ_SOC_0_5, HZ_SOC_5_15, HZ_SOC_15_30, HZ_SOC_30_60, HZ_SOC_60_100, HZ_SOC_100_200
;

SELECT DISTINCT #SOC3.cokey, #SOC3.mukey,  adj_comp_pct  AS WEIGHTED_COMP_PCT,
CO_SOC_0_30, CO_SOC_0_30 * adj_comp_pct AS WEIGHTED_CO_SOC_0_30,
CO_SOC_20_50, CO_SOC_20_50 * adj_comp_pct AS WEIGHTED_CO_SOC_20_50,
CO_SOC_50_100, CO_SOC_50_100 * adj_comp_pct AS WEIGHTED_CO_SOC_50_100,
CO_SOC_0_150, CO_SOC_0_150 * adj_comp_pct AS WEIGHTED_CO_SOC_0_150,
CO_SOC_0_5, CO_SOC_0_5 * adj_comp_pct AS WEIGHTED_CO_SOC_0_5,
CO_SOC_5_15, CO_SOC_5_15 * adj_comp_pct AS WEIGHTED_CO_SOC_5_15,
CO_SOC_15_30, CO_SOC_15_30 * adj_comp_pct AS WEIGHTED_CO_SOC_15_30,
CO_SOC_30_60, CO_SOC_30_60 * adj_comp_pct AS WEIGHTED_CO_SOC_30_60,
CO_SOC_60_100, CO_SOC_60_100 * adj_comp_pct AS WEIGHTED_CO_SOC_60_100,
CO_SOC_100_200 , CO_SOC_100_200  * adj_comp_pct AS WEIGHTED_CO_SOC_100_200
INTO #SOC4
FROM #SOC3
INNER JOIN #muacpf ON #muacpf.cokey = #SOC3.cokey
GROUP BY #SOC3.cokey, #SOC3.mukey,  adj_comp_pct , CO_SOC_0_30, CO_SOC_20_50,CO_SOC_50_100, CO_SOC_0_150, CO_SOC_0_5, CO_SOC_5_15, CO_SOC_15_30, CO_SOC_30_60,CO_SOC_60_100, CO_SOC_100_200
;

-- Unit Conversion
SELECT DISTINCT #M4.mukey, #M4.aoiid ,
#M4.landunit,
landunit_acres, mapunit_acres, ROUND (SUM (WEIGHTED_CO_SOC_0_30) OVER(PARTITION BY #M4.aoiid, #SOC4.mukey) ,4) * 100  AS SOCSTOCK_0_30 ,
ROUND (SUM (WEIGHTED_CO_SOC_20_50) OVER(PARTITION BY #M4.aoiid ,#SOC4.mukey) ,4) * 100  AS SOCSTOCK_20_50 ,
ROUND (SUM (WEIGHTED_CO_SOC_50_100) OVER(PARTITION BY #M4.aoiid ,#SOC4.mukey) ,4) * 100  AS SOCSTOCK_50_100,
ROUND (SUM (WEIGHTED_CO_SOC_0_150) OVER(PARTITION BY #M4.aoiid ,#SOC4.mukey) ,4) * 100  AS SOCSTOCK_0_150,
ROUND (SUM (WEIGHTED_CO_SOC_0_5) OVER(PARTITION BY #M4.aoiid ,#SOC4.mukey) ,4) * 100  AS SOCSTOCK_0_5 ,
ROUND (SUM (WEIGHTED_CO_SOC_5_15) OVER(PARTITION BY #M4.aoiid ,#SOC4.mukey) ,4) * 100  AS SOCSTOCK_5_15 ,
ROUND (SUM (WEIGHTED_CO_SOC_15_30) OVER(PARTITION BY #M4.aoiid ,#SOC4.mukey) ,4) * 100  AS SOCSTOCK_15_30 ,
ROUND (SUM (WEIGHTED_CO_SOC_30_60) OVER(PARTITION BY #M4.aoiid ,#SOC4.mukey) ,4) * 100  AS SOCSTOCK_30_60 ,
ROUND (SUM (WEIGHTED_CO_SOC_60_100) OVER(PARTITION BY #M4.aoiid ,#SOC4.mukey) ,4) * 100  AS SOCSTOCK_60_100 ,
ROUND (SUM (WEIGHTED_CO_SOC_100_200) OVER(PARTITION BY #M4.aoiid ,#SOC4.mukey) ,4) * 100  AS SOCSTOCK_100_200
INTO #SOC5
FROM #SOC4
LEFT OUTER JOIN #M4 ON #M4.mukey = #SOC4.mukey
LEFT OUTER JOIN #AoiAcres ON #AoiAcres.aoiid = #M4.aoiid
GROUP BY  #M4.mukey,  #SOC4.mukey,  #M4.aoiid ,
#M4.landunit,
landunit_acres, mapunit_acres,WEIGHTED_CO_SOC_0_30, WEIGHTED_CO_SOC_20_50, WEIGHTED_CO_SOC_50_100, WEIGHTED_CO_SOC_0_5, WEIGHTED_CO_SOC_5_15, WEIGHTED_CO_SOC_15_30, WEIGHTED_CO_SOC_30_60, WEIGHTED_CO_SOC_60_100, WEIGHTED_CO_SOC_100_200, #SOC4.WEIGHTED_CO_SOC_0_150
;

CREATE TABLE #SOC6
( aoiid INT,
landunit CHAR(20),
landunit_acres FLOAT,
SOCSTOCK_0_5_Weighted_Average DECIMAL (10, 2),
SOCSTOCK_0_30_Weighted_Average DECIMAL (10, 2),
SOCSTOCK_0_150_Weighted_Average DECIMAL (10, 2)
)
;

INSERT INTO #SOC6
SELECT DISTINCT
aoiid ,
landunit,
landunit_acres,
SUM ((mapunit_acres / landunit_acres) * SOCSTOCK_0_5) OVER(PARTITION BY aoiid) AS SOCSTOCK_0_5_Weighted_Average,
SUM ((mapunit_acres / landunit_acres) * SOCSTOCK_0_30) OVER(PARTITION BY aoiid) AS SOCSTOCK_0_30_Weighted_Average,
SUM ((mapunit_acres / landunit_acres) * SOCSTOCK_0_150) OVER(PARTITION BY aoiid) AS SOCSTOCK_0_150_Weighted_Average
FROM #SOC5
GROUP BY aoiid, landunit, mapunit_acres, landunit_acres, SOCSTOCK_0_5, SOCSTOCK_0_30, SOCSTOCK_0_150
;

--Begin AWS
CREATE TABLE #acpfaws
(aoiid INT ,
landunit CHAR(20),
mukey INT,
mapunit_acres DECIMAL (10, 2),
mu_pct_sum INT,
aws0150wta DECIMAL (10, 2) )
;

INSERT INTO #acpfaws
SELECT DISTINCT
MA44.aoiid ,
MA44.landunit,
MA44.mukey,
MA44.mapunit_acres,
mu_pct_sum,
aws0150wta
FROM (#M4 AS MA44
INNER JOIN muaggatt AS mt on MA44.mukey = mt.mukey )
;

CREATE TABLE #aws1
( aoiid INT,
landunit CHAR(20),
landunit_acres DECIMAL (10, 2),
AWS_Weighted_Average0_150 DECIMAL (10, 2) )
;

INSERT INTO #aws1
SELECT DISTINCT
#acpfaws.aoiid ,
#acpfaws.landunit,
landunit_acres,
SUM ((mapunit_acres / landunit_acres) * aws0150wta) OVER(PARTITION BY #acpfaws.aoiid) AS AWS_Weighted_Average0_150
FROM #acpfaws
LEFT OUTER JOIN #AoiAcres ON #AoiAcres.aoiid = #acpfaws.aoiid
GROUP BY #acpfaws.aoiid, #acpfaws.landunit, mapunit_acres, landunit_acres, aws0150wta
;

--Begin Aggregate Stability
CREATE TABLE #agg1
( aoiid INT ,
landunit CHAR(20),
mukey INT,
mapunit_acres FLOAT,
cokey INT,
compname CHAR(60),
comppct_r INT,
majcompflag  CHAR(3),
localphase CHAR(60),
hzname CHAR(20),
hzdept_r INT,
hzdepb_r INT,
claytotall FLOAT,
claytotalr FLOAT,
claytotalh FLOAT,
oml DECIMAL (6, 2) ,
omr DECIMAL (6, 2)  ,
omh DECIMAL (6, 2),
sar_l FLOAT,
sar_r FLOAT,
sar_h FLOAT,
cec7_l FLOAT,
cec7_r FLOAT,
cec7_h FLOAT,
ec_l FLOAT,
ec_r FLOAT,
ec_h FLOAT,
esp_l DECIMAL (10, 2),
esp_r DECIMAL (10, 2),
esp_h DECIMAL (10, 2),
tcl CHAR(40),
major_mu_pct_sum INT,
mu_pct_sum INT )
;

INSERT INTO #agg1
SELECT DISTINCT
MA44.aoiid ,
MA44.landunit,
MA44.mukey,
MA44.mapunit_acres,
MA44.cokey,
MA44.compname,
MA44.comppct_r,
MA44.majcompflag,
localphase,
hzname,
hzdept_r,
hzdepb_r,
CASE WHEN claytotal_l > 92 then 92 WHEN claytotal_l < 8 THEN 8 ELSE claytotal_l END AS claytotall,
CASE WHEN claytotal_r > 92 then 92 ELSE claytotal_r END AS claytotalr,
CASE WHEN claytotal_h > 92 then 92 ELSE claytotal_h END AS claytotalh,
CASE WHEN om_l <0.01 THEN 0.05 WHEN om_l > 17 then 17 ELSE om_l END AS oml,
CASE WHEN om_r <0.01 THEN 0.05 WHEN om_r > 17 then 17 ELSE om_r END AS omr ,
CASE WHEN om_h <0.01 THEN 0.05 WHEN om_h > 17 then 17 ELSE om_h END AS omh ,
sar_l,
sar_r,
sar_h,
cec7_l,
cec7_r,
cec7_h,
ec_l,
ec_r,
ec_h,
(100 * (-0.0126 + 0.01475 * sar_l)) / (1 + (-0.0126 + 0.01475 * sar_l)) AS esp_l,
(100 * (-0.0126 + 0.01475 * sar_r)) / (1 + (-0.0126 + 0.01475 * sar_r)) AS esp_r,
(100 * (-0.0126 + 0.01475 * sar_h)) / (1 + (-0.0126 + 0.01475 * sar_h)) AS esp_h,
(SELECT TOP 1 texcl FROM chtexturegrp AS chtg INNER JOIN chtexture AS cht ON chtg.chtgkey = cht.chtgkey  AND chtg.rvindicator = 'yes' AND chtg.chkey=cha.chkey) AS tcl,
major_mu_pct_sum, mu_pct_sum
FROM (#M4 AS MA44 INNER JOIN (component AS coa INNER JOIN chorizon  AS cha ON cha.cokey = coa.cokey AND cha.hzdept_r < 15 ) ON MA44.cokey = coa.cokey AND MA44.majcompflag = 'yes' )
;

CREATE TABLE #agg2
( aoiid INT ,
landunit CHAR(20),
mukey INT,
mapunit_acres FLOAT,
cokey INT,
compname CHAR(60),
comppct_r INT,
majcompflag  CHAR(3),
localphase CHAR(60),
hzname CHAR(20),
hzdept_r INT,
hzdepb_r INT,
claytotall FLOAT,
claytotalr FLOAT,
claytotalh FLOAT,
oml  FLOAT,
omr FLOAT,
omh  FLOAT,
sar_l FLOAT,
sar_r FLOAT,
sar_h FLOAT,
cec7_l FLOAT,
cec7_r FLOAT,
cec7_h FLOAT,
ec_l FLOAT,
ec_r FLOAT,
ec_h FLOAT,
esp_l FLOAT,
esp_r FLOAT,
esp_h FLOAT,
tcl CHAR(40),
sandy INT,
major_mu_pct_sum INT,
mu_pct_sum INT )
;

INSERT INTO #agg2
SELECT DISTINCT
aoiid ,
landunit,
mukey,
mapunit_acres,
cokey,
compname,
comppct_r,
majcompflag,
localphase,
hzname,
hzdept_r,
hzdepb_r,
claytotall,
claytotalr,
claytotalh,
oml ,
omr ,
omh ,
sar_l,
sar_r,
sar_h,
cec7_l,
cec7_r,
cec7_h,
ec_l,
ec_r,
ec_h,
CASE WHEN cec7_l < 50 + 0 AND cec7_l IS NOT NULL AND sar_l IS NOT NULL AND sar_l !=0 AND sar_l < 40 + 0  AND ec_l < 20 + 0 THEN esp_l
WHEN sar_l !=0 AND sar_l IS NOT NULL THEN 1.5 * sar_l / (1 + 0.015 * sar_l)
WHEN sar_l < 0.01 THEN 0 ELSE NULL END AS esp_l,
CASE WHEN cec7_r < 50 + 0 AND cec7_r IS NOT NULL AND sar_r IS NOT NULL AND sar_r !=0 AND sar_r < 40 + 0 AND ec_r < 20 + 0 THEN esp_r
WHEN sar_r !=0 and sar_r IS NOT NULL then 1.5 * sar_r / (1 + 0.015 * sar_r)
WHEN sar_r < 0.01 THEN 0 ELSE NULL END AS esp_r,
CASE WHEN cec7_h < 50 + 0 AND cec7_h IS NOT NULL AND sar_h IS NOT NULL AND sar_h !=0 AND sar_h < 40 + 0 AND ec_h < 20 + 0 THEN esp_h
WHEN sar_h !=0 AND sar_h IS NOT NULL THEN 1.5 * sar_h / (1 + 0.015 * sar_h)
WHEN sar_h < 0.01 THEN 0 ELSE NULL END AS esp_h,
tcl,
CASE WHEN  tcl = 'Loamy coarse sand' THEN 1
WHEN tcl = 'Loamy fine sand' THEN 1
WHEN tcl = 'Loamy sand'  THEN 1
WHEN tcl = 'Sand' THEN 1
WHEN tcl = 'Coarse sand' THEN 1
WHEN tcl = 'Fine sand' THEN 1 ELSE 0 END AS sandy,
major_mu_pct_sum,
mu_pct_sum
FROM #agg1
;

CREATE TABLE #agg3
( aoiid INT ,
landunit CHAR(20),
mukey INT,
mapunit_acres FLOAT,
cokey INT,
compname CHAR(60),
comppct_r INT,
majcompflag  CHAR(3),
localphase CHAR(60),
hzname CHAR(20),
hzdept_r INT,
hzdepb_r INT,
claytotall FLOAT,
claytotalr FLOAT,
claytotalh FLOAT,
oml FLOAT,
omr FLOAT,
omh FLOAT,
sandy INT,
AgStab_l DECIMAL (10, 2),
AgStab_r DECIMAL (10, 2),
AgStab_h DECIMAL (10, 2),
tcl CHAR(40),
major_mu_pct_sum INT,
mu_pct_sum INT )
;

INSERT INTO #agg3
SELECT DISTINCT
aoiid,
landunit,
mukey,
mapunit_acres,
cokey,
compname,
comppct_r,
majcompflag,
localphase,
hzname,
hzdept_r,
hzdepb_r,
claytotall,
claytotalr,
claytotalh,
oml,
omr,
omh,
sandy,
49.7 + 13.7 * LOG(oml) + 0.61 * claytotall - 0.0045 * POWER(claytotall, 2) - 0.28 * esp_h - 0.06 * POWER(esp_h, 2) AS AgStab_l,
49.7 + 13.7 * LOG(omr) + 0.61 * claytotalr - 0.0045 * POWER(claytotalr, 2) - 0.28 * esp_r - 0.06 * POWER(esp_r, 2) AS AgStab_r,
49.7 + 13.7 * LOG(omh) + 0.61 * claytotalh - 0.0045 * POWER(claytotalh, 2) - 0.28 * esp_l - 0.06 * POWER(esp_l, 2) AS AgStab_h,
tcl,
major_mu_pct_sum,
mu_pct_sum
FROM #agg2
;

CREATE TABLE #agg4
( aoiid INT ,
landunit CHAR(20),
landunit_acres FLOAT,
mukey INT,
mapunit_acres FLOAT,
cokey INT,
compname CHAR(60),
comppct_r INT,
majcompflag  CHAR(3),
localphase CHAR(60),
hzname CHAR(20),
hzdept_r INT,
hzdepb_r INT,
AgStab_l FLOAT,
AgStab_r FLOAT,
AgStab_h FLOAT,
tcl CHAR(40),
major_mu_pct_sum INT,
mu_pct_sum INT,
adj_comp_pct FLOAT,
thickness INT,
AGG_InRangeTop_0_15 INT,
AGG_InRangeBot_0_15 INT )
;

INSERT INTO #agg4
SELECT DISTINCT ag.aoiid ,
ag.landunit,
landunit_acres,
mukey,
mapunit_acres,
cokey,
compname,
comppct_r,
majcompflag,
localphase,
hzname,
hzdept_r,
hzdepb_r,
CASE WHEN AgStab_l > 100  THEN 100 WHEN claytotall >= 0  AND claytotall < 5 THEN NULL WHEN sandy=1 THEN null WHEN oml > 20 THEN NULL ELSE AgStab_l END AS AgStab_l,
CASE WHEN AgStab_r > 100  THEN 100 WHEN claytotalr >= 0  AND claytotalr < 5 THEN NULL WHEN sandy=1 THEN null WHEN omr > 20 THEN NULL ELSE AgStab_r END AS AgStab_r,
CASE WHEN AgStab_h > 100  THEN 100 WHEN claytotalh >= 0  AND claytotalh < 5 THEN NULL WHEN sandy=1 THEN null WHEN omh > 20 THEN NULL ELSE AgStab_h END AS AgStab_h,
tcl, major_mu_pct_sum, mu_pct_sum, (1.0 * comppct_r / NULLIF(mu_pct_sum, 0)) AS adj_comp_pct, CASE WHEN hzdepb_r IS NULL THEN 0
WHEN hzdept_r IS NULL THEN 0 ELSE hzdepb_r-hzdept_r END AS thickness,
CASE  WHEN hzdept_r < 15 THEN hzdept_r ELSE 0 END AS AGG_InRangeTop_0_15,
CASE  WHEN hzdepb_r <= 15 THEN hzdepb_r WHEN hzdepb_r > 15 and hzdept_r < 15 THEN 15 ELSE 0 END AS AGG_InRangeBot_0_15
FROM #AoiAcres
LEFT OUTER JOIN #agg3 AS ag ON ag.aoiid = #AoiAcres.aoiid WHERE majcompflag = 'Yes' GROUP BY ag.aoiid ,
ag.landunit,
landunit_acres,
mukey,
mapunit_acres,
cokey,
compname,
comppct_r,
majcompflag,
localphase,
hzname,
hzdept_r,
hzdepb_r,
AgStab_l , AgStab_h, AgStab_r,
claytotall, claytotalr, claytotalh,
sandy,
comppct_r,
major_mu_pct_sum,
mu_pct_sum,
oml, omr, omh,
tcl
;

CREATE TABLE #agg5
( aoiid INT ,
landunit CHAR(20),
landunit_acres FLOAT,
mukey INT,
mapunit_acres FLOAT,
cokey INT,
compname CHAR(60),
comppct_r INT,
majcompflag  CHAR(3),
localphase CHAR(60),
hzname CHAR(20),
hzdept_r INT,
hzdepb_r INT,
AgStab_l FLOAT,
AgStab_r FLOAT,
AgStab_h FLOAT,
tcl CHAR(40),
major_mu_pct_sum INT,
mu_pct_sum INT,
adj_comp_pct FLOAT,
thickness INT,
AGG_InRangeTop_0_15 INT,
AGG_InRangeBot_0_15 INT,
InRangeThickness INT,
InRangeSumThickness INT )
;

INSERT INTO #agg5
SELECT DISTINCT aoiid,
landunit,
landunit_acres,
mukey,
mapunit_acres,
cokey,
compname,
comppct_r,
majcompflag,
localphase,
hzname,
hzdept_r,
hzdepb_r,
AgStab_l,
AgStab_r,
AgStab_h,
tcl,
major_mu_pct_sum,
mu_pct_sum,
adj_comp_pct,
thickness,
AGG_InRangeTop_0_15,
AGG_InRangeBot_0_15,
CASE WHEN AGG_InRangeTop_0_15 IS NULL THEN 0
WHEN AGG_InRangeBot_0_15 IS NULL THEN 0 ELSE AGG_InRangeBot_0_15 - AGG_InRangeTop_0_15 END AS InRangeThickness,
SUM (CASE WHEN AGG_InRangeTop_0_15 IS NULL THEN 0
WHEN AGG_InRangeBot_0_15 IS NULL THEN 0 ELSE AGG_InRangeBot_0_15 - AGG_InRangeTop_0_15 END) OVER(PARTITION BY cokey, aoiid) AS InRangeSumThickness
FROM #agg4
GROUP BY aoiid ,
landunit,
landunit_acres,
mukey,
mapunit_acres,
cokey,
compname,
comppct_r,
majcompflag,
localphase,
hzname,
hzdept_r,
hzdepb_r,
AgStab_l,
AgStab_r,
AgStab_h,
tcl, major_mu_pct_sum,
mu_pct_sum,
adj_comp_pct,
thickness,
AGG_InRangeTop_0_15,
AGG_InRangeBot_0_15
;

CREATE TABLE #agg6
( aoiid INT,
landunit CHAR(20),
landunit_acres FLOAT,
mukey INT,
mapunit_acres FLOAT,
cokey INT,
compname CHAR(60),
localphase CHAR(60),
major_mu_pct_sum INT,
mu_pct_sum INT,
adj_comp_pct FLOAT ,
--AGG_InRangeTop_0_15 INT,
--AGG_InRangeBot_0_15 INT,
--InRangeThickness INT,
--InRangeSumThickness INT,
--AgStab_l FLOAT,
--AgStab_r FLOAT,
--AgStab_h FLOAT,
comp_weighted_average_l FLOAT,
comp_weighted_average_r FLOAT,
comp_weighted_average_h FLOAT )
;

INSERT INTO #agg6
SELECT DISTINCT  aoiid ,
landunit,
landunit_acres,
mukey,
mapunit_acres,
cokey,
compname,
localphase,
major_mu_pct_sum,
mu_pct_sum,
adj_comp_pct,
SUM ((InRangeThickness / CAST (InRangeSumThickness AS FLOAT)) * AgStab_l) OVER(PARTITION BY ag5.cokey, aoiid) AS comp_weighted_average_l,
SUM ((InRangeThickness / CAST (InRangeSumThickness AS FLOAT)) * AgStab_r) OVER(PARTITION BY ag5.cokey, aoiid) AS comp_weighted_average_r,
SUM ((InRangeThickness / CAST (InRangeSumThickness AS FLOAT)) * AgStab_h) OVER(PARTITION BY ag5.cokey, aoiid) AS comp_weighted_average_h
FROM  #agg5 AS ag5
WHERE InRangeSumThickness !=0
GROUP BY aoiid, landunit,
landunit_acres,
mukey,
mapunit_acres,
cokey,
compname,
localphase,
major_mu_pct_sum,
mu_pct_sum,
adj_comp_pct,
-- AgStab_l ,
--AgStab_r ,
--AgStab_h ,
--AGG_InRangeTop_0_15,
--AGG_InRangeBot_0_15,
InRangeThickness, InRangeSumThickness,
AgStab_l, AgStab_r, AgStab_h
;

---Map unit Aggregation for mapunit table
CREATE TABLE #agg7
( aoiid INT,
landunit CHAR(20),
landunit_acres FLOAT,
mukey INT,
mapunit_acres FLOAT,
major_mu_pct_sum INT,
mu_pct_sum INT,
MU_SUM_AGG_L DECIMAL (10, 2),
MU_SUM_AGG_R DECIMAL (10, 2),
MU_SUM_AGG_H DECIMAL (10, 2) )
--MU_Weighted_Average_R FLOAT )
;

-- Map Unit Aggregation
INSERT INTO #agg7
SELECT DISTINCT aoiid ,
landunit,
landunit_acres,
mukey,
mapunit_acres,
major_mu_pct_sum,
mu_pct_sum,
SUM (adj_comp_pct * comp_weighted_average_l) OVER(PARTITION BY ag6.mukey, aoiid ) AS MU_SUM_AGG_L,
SUM (adj_comp_pct * comp_weighted_average_r) OVER(PARTITION BY ag6.mukey, aoiid ) AS MU_SUM_AGG_R,
SUM (adj_comp_pct * comp_weighted_average_h) over(PARTITION BY ag6.mukey, aoiid ) AS MU_SUM_AGG_H
--(mapunit_acres/landunit_acres)*MU_SUM_AGG_R AS MU_Weighted_Average_R
FROM #agg6 AS ag6
GROUP BY aoiid ,
landunit,
landunit_acres,
mukey,
mapunit_acres,
major_mu_pct_sum,
mu_pct_sum,
adj_comp_pct,
comp_weighted_average_l,
comp_weighted_average_r,
comp_weighted_average_h
;

CREATE TABLE #agg7a
( aoiid INT,
landunit CHAR(20),
landunit_acres FLOAT,
mapunit_acres FLOAT,
MU_SUM_AGG_L  FLOAT,
MU_SUM_AGG_R FLOAT,
MU_SUM_AGG_H FLOAT )
;

INSERT INTO #agg7a
SELECT DISTINCT
aoiid ,
landunit,
landunit_acres,
mapunit_acres,
CASE WHEN MU_SUM_AGG_R = 0 THEN 0 ELSE  MU_SUM_AGG_L END AS MU_SUM_AGG_L ,
MU_SUM_AGG_R ,
CASE WHEN MU_SUM_AGG_R = 0 THEN 0 ELSE  MU_SUM_AGG_H END AS MU_SUM_AGG_H
FROM #agg7
GROUP BY aoiid, landunit, mapunit_acres, landunit_acres, MU_SUM_AGG_L, MU_SUM_AGG_R, MU_SUM_AGG_H
;

CREATE TABLE #agg8
( aoiid INT,
landunit CHAR(20),
landunit_acres FLOAT,
LU_AGG_Weighted_Average_L DECIMAL (10, 2),
LU_AGG_Weighted_Average_R DECIMAL (10, 2),
LU_AGG_Weighted_Average_H DECIMAL (10, 2) )
;

INSERT INTO #agg8
SELECT DISTINCT
aoiid ,
landunit,
landunit_acres,
SUM ((mapunit_acres / landunit_acres) * MU_SUM_AGG_L) OVER(PARTITION BY aoiid) AS LU_AGG_Weighted_Average_L,
SUM ((mapunit_acres / landunit_acres) * MU_SUM_AGG_R) OVER(PARTITION BY aoiid) AS LU_AGG_Weighted_Average_R,
SUM ((mapunit_acres / landunit_acres) * MU_SUM_AGG_H) OVER(PARTITION BY aoiid) AS LU_AGG_Weighted_Average_H
FROM #agg7a
GROUP BY aoiid, landunit, mapunit_acres, landunit_acres, MU_SUM_AGG_L, MU_SUM_AGG_R, MU_SUM_AGG_H
;

-- Flooding frequency and Ponding frequency
CREATE TABLE #pf
( aoiid INT,
landunit CHAR(20),
mukey INT,
mapunit_acres DECIMAL (10, 2),
cokey INT ,
cname CHAR(60),
copct INT,
majcompflag CHAR(3),
flodfreq CHAR(20),
pondfreq CHAR(20),
major_mu_pct_sum INT,
mu_pct_sum INT )
;

INSERT INTO #pf
SELECT DISTINCT
aoiid,
landunit,
M44.mukey,
mapunit_acres ,
M44.cokey AS cokey,
M44.compname AS cname,
M44.comppct_r AS copct ,
M44.majcompflag AS majcompflag,
(SELECT TOP 1 flodfreqcl FROM comonth, MetadataDomainMaster AS MD, MetadataDomainDetail AS DD WHERE comonth.cokey = M44.cokey AND flodfreqcl = ChoiceLabel AND DomainName = 'flooding_frequency_class' AND
MD.DomainID = DD.DomainID order by choicesequence desc) as flodfreq,
(SELECT TOP 1 pondfreqcl FROM comonth, MetadataDomainMaster AS MD, MetadataDomainDetail AS DD WHERE comonth.cokey = M44.cokey AND pondfreqcl = ChoiceLabel AND DomainName = 'ponding_frequency_class' AND
MD.DomainID = DD.DomainID ORDER BY choicesequence DESC) AS pondfreq,
major_mu_pct_sum, mu_pct_sum
FROM #M4 AS M44
INNER JOIN comonth AS CM ON M44.cokey = CM.cokey AND M44.majcompflag = 'yes'
AND CASE
WHEN (flodfreqcl IN ('occasional', 'common', 'frequent', 'very frequent')) THEN 1
WHEN (pondfreqcl IN ('occasional', 'common', 'frequent')) THEN 1
ELSE 2 END = 1
GROUP BY aoiid, landunit, M44.mukey, mapunit_acres, major_mu_pct_sum, mu_pct_sum, M44.cokey,M44.compname , M44.majcompflag, M44.comppct_r, flodfreqcl, pondfreqcl
;

CREATE TABLE #pf1
( aoiid INT,
landunit CHAR(20),
landunit_acres FLOAT,
mukey INT,
mapunit_acres FLOAT,
cokey INT ,
cname CHAR(60),
copct  INT,
majcompflag CHAR(3),
flodfreq CHAR(20),
pondfreq CHAR(20),
major_mu_pct_sum INT,
mu_pct_sum INT,
adj_comp_pct FLOAT )
;

INSERT INTO #pf1
SELECT DISTINCT pf.aoiid, pf.landunit, landunit_acres, mukey, mapunit_acres, cokey, cname, copct, majcompflag, flodfreq, pondfreq, major_mu_pct_sum, mu_pct_sum, (1.0 * copct / NULLIF(major_mu_pct_sum, 0)) AS adj_comp_pct
FROM #AoiAcres
LEFT OUTER JOIN #pf AS pf ON pf.aoiid = #AoiAcres.aoiid
GROUP BY pf.aoiid, pf.landunit, landunit_acres, mukey, mapunit_acres, cokey, cname, copct, majcompflag, flodfreq, pondfreq, major_mu_pct_sum, mu_pct_sum
;

CREATE TABLE #pf2
( aoiid INT,
landunit CHAR(20),
landunit_acres FLOAT,
mukey INT,
mapunit_acres FLOAT,
cokey INT,
cname CHAR(60),
copct INT,
major_MU_pct_sum INT,
MU_pct_sum INT,
adj_comp_pct FLOAT,
co_acres FLOAT )
;

INSERT INTO #pf2
SELECT  aoiid, landunit, landunit_acres, mukey, mapunit_acres, cokey, cname, copct, major_MU_pct_sum, MU_pct_sum, adj_comp_pct, ROUND ( (adj_comp_pct * mapunit_acres), 2) AS co_acres
FROM #pf1
;

-- Begin Organic and Hydric
CREATE TABLE #organic
( aoiid INT,
landunit CHAR(20),
mukey INT,
mapunit_acres FLOAT,
cokey INT ,
cname CHAR(60),
copct INT,
majcompflag CHAR(3),
mu_pct_sum INT,
taxgrtgroup CHAR(120),
taxsubgrp CHAR(120),
hydricrating CHAR(120),
organic_flag INT )
;

INSERT INTO #organic -- organic soils
SELECT
aoiid,
landunit,
M44.mukey,
mapunit_acres,
M44.cokey AS cokey,
M44.compname AS cname,
M44.comppct_r AS copct ,
M44.majcompflag AS majcompflag,
mu_pct_sum,
taxgrtgroup,
taxsubgrp,
hydricrating ,
CASE WHEN taxsubgrp LIKE '%hist%'THEN 1
WHEN taxsubgrp LIKE '%ists%'AND taxsubgrp NOT LIKE '%fol%' THEN 1
WHEN taxgrtgroup LIKE '%ists%'AND taxgrtgroup NOT LIKE '%fol%' THEN 1
WHEN hydricrating = 'Yes' THEN 1
END AS organic_flag
FROM #M4 AS M44
INNER JOIN component ON M44.cokey=component.cokey
;

CREATE TABLE #o1
( aoiid INT,
landunit CHAR(20),
landunit_acres FLOAT,
mukey INT,
mapunit_acres FLOAT,
cokey INT ,
cname CHAR(60),
copct INT,
majcompflag CHAR(3),
mu_pct_sum INT,
adj_comp_pct FLOAT,
taxgrtgroup CHAR(120),
taxsubgrp CHAR(120),
hydricrating CHAR(3))
;

-- Need to check to see if this #ol table is being used anywhere
INSERT INTO #o1
SELECT DISTINCT og.aoiid, og.landunit, landunit_acres, mukey, mapunit_acres, cokey, cname, copct, majcompflag, mu_pct_sum, CAST ((1.0 * copct / NULLIF(mu_pct_sum, 0)) AS DEC(10, 2)) AS adj_comp_pct,
taxgrtgroup,
taxsubgrp,
hydricrating
FROM #AoiAcres
LEFT OUTER JOIN #organic AS og ON og.aoiid = #AoiAcres.aoiid
WHERE organic_flag = 1
;

--Begin Water table
CREATE TABLE #wet
( aoiid INT,
landunit CHAR(20),
mukey INT,
mapunit_acres FLOAT,
cokey INT ,
cname CHAR(60),
copct INT,
majcompflag CHAR(3),
soimoistdept_l INT,
soimoistdept_r INT,
soimoiststat CHAR(7),
MIN_soimoistdept_l  INT,
MIN_soimoistdept_r INT,
major_MU_pct_sum INT,
mu_pct_sum INT )
;

INSERT INTO #wet
SELECT
aoiid,
landunit,
M44.mukey,
mapunit_acres,
M44.cokey AS cokey,
M44.compname AS cname,
M44.comppct_r AS copct ,
M44.majcompflag AS majcompflag,
soimoistdept_l,
soimoistdept_r,
soimoiststat,
MIN (soimoistdept_l) OVER(PARTITION BY M44.cokey) AS MIN_soimoistdept_l,
MIN (soimoistdept_r) OVER(PARTITION BY M44.cokey) AS MIN_soimoistdept_r,
major_MU_pct_sum, mu_pct_sum
FROM (#M4 AS M44 INNER JOIN (comonth AS CM  INNER JOIN  cosoilmoist AS COSM ON COSM.comonthkey = CM.comonthkey AND soimoiststat = 'Wet' AND CASE WHEN soimoistdept_l < 46 THEN 1 WHEN soimoistdept_r < 46 THEN 1 ELSE 2 END = 1
) ON M44.cokey = CM.cokey AND M44.majcompflag = 'yes'
INNER JOIN component ON  M44.cokey = component.cokey
AND (CASE WHEN soimoistdept_l IS NULL THEN soimoistdept_r ELSE soimoistdept_l END) = (SELECT MIN (CASE WHEN soimoistdept_l IS NULL THEN soimoistdept_r ELSE soimoistdept_l END)
FROM comonth AS CM2
INNER JOIN  cosoilmoist  AS COSM2  ON COSM2.comonthkey = CM2.comonthkey AND soimoiststat = 'Wet' AND CASE WHEN soimoistdept_l < 46 THEN 1 WHEN soimoistdept_r < 46 THEN 1 ELSE 2 END = 1 AND CM2.cokey=M44.cokey
))
WHERE CASE
WHEN (taxorder = 'gelisols'  AND taxtempcl IN ('hypergelic', 'pergelic', 'subgelic') AND CM.month IN ('jul', 'aug')) THEN 1
WHEN (taxtempregime IN ('cryic', 'pergelic', 'isofrigid') AND CM.month  IN ('jul', 'aug')) THEN 1
WHEN (taxtempregime IN ('frigid') AND CM.month IN ('may', 'jun', 'jul', 'aug', 'sep')) THEN 1
WHEN (taxtempregime IN ('mesic') AND CM.month IN ( 'apr','may', 'jun', 'jul', 'aug', 'sep', 'oct')) THEN 1
WHEN (taxtempregime IN ('thermic', 'hyperthermic') and CM.month IN ('mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct'))THEN 1
WHEN (taxtempregime IN ('isothermic', 'isohyperthermic', 'isomesic') AND CM.month IN ('feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov')) THEN 1
WHEN (CM.month IN ('jun', 'jul')) THEN 1
ELSE 2 END  = 1
;

CREATE TABLE #wet1
( aoiid INT,
landunit CHAR(20),
landunit_acres FLOAT,
mukey INT,
mapunit_acres FLOAT,
cokey INT ,
cname CHAR(60),
copct INT,
majcompflag CHAR(3),
MIN_soimoistdept_l INT,
MIN_soimoistdept_r INT,
major_MU_pct_sum INT,
mu_pct_sum INT,
adj_comp_pct FLOAT )
;

INSERT INTO #wet1
SELECT DISTINCT #AoiAcres.aoiid, #AoiAcres.landunit, landunit_acres, mukey, mapunit_acres, cokey, cname, copct, majcompflag, MIN_soimoistdept_l, MIN_soimoistdept_r, major_mu_pct_sum, mu_pct_sum, (1.0 * copct / major_mu_pct_sum) AS adj_comp_pct
FROM #AoiAcres
LEFT OUTER JOIN #wet AS wet ON wet.aoiid = #AoiAcres.aoiid
GROUP BY  #AoiAcres.aoiid, #AoiAcres.landunit, landunit_acres, mukey, mapunit_acres, cokey, cname, copct, majcompflag, MIN_soimoistdept_r, MIN_soimoistdept_l, major_mu_pct_sum, mu_pct_sum
;

CREATE TABLE #wet2
( aoiid INT,
landunit CHAR(20),
landunit_acres FLOAT,
mukey INT,
mapunit_acres FLOAT,
cokey INT,
cname CHAR(60),
copct INT,
major_MU_pct_sum INT,
MU_pct_sum INT,
adj_comp_pct FLOAT,
co_acres FLOAT )
;

INSERT INTO #wet2
SELECT aoiid, landunit, landunit_acres, mukey, mapunit_acres, cokey, cname, copct, major_MU_pct_sum,
MU_pct_sum, adj_comp_pct, ROUND ( (adj_comp_pct * mapunit_acres), 4) AS co_acres
FROM #wet1
;

-- Hydric Soil Interp begins here
INSERT INTO #Hydric_A (mukey, cokey, hydric_pct)
    SELECT DISTINCT M4.mukey, M4.cokey, M4.comppct_r AS hydric_pct
    FROM #M4 M4
    LEFT OUTER JOIN component C ON M4.cokey = C.cokey
    WHERE C.hydricrating = 'Yes'
;

-- Populate #Hydric_B with mapunit-level hydric percent ratings
INSERT INTO #Hydric_B (mukey, hydric_pct)
    SELECT mukey, SUM(hydric_pct) AS hydric_pct
    FROM #Hydric_A H1
    GROUP BY mukey
    ORDER BY mukey
;

-- Hydric Soil Interp
INSERT INTO #Hydric1 (mukey, comp_count, count_maj_comp, all_hydric, all_not_hydric, maj_hydric, maj_not_hydric, hydric_inclusions, hydric_null)
    SELECT DISTINCT M4.mukey,
    (SELECT TOP 1 COUNT(*)
    FROM mapunit
    INNER JOIN component ON component.mukey = mapunit.mukey AND mapunit.mukey = M4.mukey) AS comp_count,
    (SELECT TOP 1 COUNT(*)
    FROM mapunit
    INNER JOIN component ON component.mukey = mapunit.mukey AND mapunit.mukey = M4.mukey AND majcompflag = 'Yes') AS count_maj_comp,
    (SELECT TOP 1 COUNT(*)
    FROM mapunit
    INNER JOIN component ON component.mukey = mapunit.mukey AND mapunit.mukey = M4.mukey AND hydricrating = 'Yes' ) AS all_hydric,
    (SELECT TOP 1 COUNT(*)
    FROM mapunit
    INNER JOIN component ON component.mukey = mapunit.mukey AND mapunit.mukey = M4.mukey AND hydricrating  != 'Yes') AS all_not_hydric,
    (SELECT TOP 1 COUNT(*)
    FROM mapunit
    INNER JOIN component ON component.mukey = mapunit.mukey AND mapunit.mukey = M4.mukey AND majcompflag = 'Yes' AND hydricrating = 'Yes') AS maj_hydric,
    (SELECT TOP 1 COUNT(*)
    FROM mapunit
    INNER JOIN component ON component.mukey = mapunit.mukey AND mapunit.mukey = M4.mukey AND majcompflag = 'Yes' AND hydricrating != 'Yes') AS maj_not_hydric,
    (SELECT TOP 1 COUNT(*)
    FROM mapunit
    INNER JOIN component ON component.mukey = mapunit.mukey AND mapunit.mukey = M4.mukey AND majcompflag != 'Yes' AND hydricrating  = 'Yes' ) AS hydric_inclusions,
    (SELECT TOP 1 COUNT(*)
    FROM mapunit
    INNER JOIN component ON component.mukey = mapunit.mukey AND mapunit.mukey = M4.mukey AND hydricrating  IS NULL ) AS hydric_null
    FROM #M4 AS M4
;

-- Takes hydric count statistics and converts them to interpretation-type rating classes (hydric_rating)
INSERT INTO #Hydric2 (mukey, hydric_rating, low_pct, rv_pct, high_pct)
    SELECT
    mukey,
    CASE WHEN comp_count = all_not_hydric + hydric_null THEN 'Nonhydric'
        WHEN comp_count = all_hydric  THEN 'Hydric'
        WHEN comp_count != all_hydric AND count_maj_comp = maj_hydric THEN 'Predominantly hydric'
        WHEN hydric_inclusions >= 0.5 AND  maj_hydric < 0.5 THEN  'Predominantly nonhydric'
        WHEN maj_not_hydric >= 0.5  AND  maj_hydric >= 0.5 THEN 'Partially hydric'
        ELSE 'Error'
    END AS hydric_rating,

    CASE WHEN comp_count = all_not_hydric + hydric_null THEN 0.00 --'Nonhydric'
        WHEN comp_count = all_hydric  THEN 1 --'Hydric'
        WHEN comp_count != all_hydric AND count_maj_comp = maj_hydric THEN 0.80 --'Predominantly hydric'
        WHEN hydric_inclusions >= 0.5 AND  maj_hydric < 0.5 THEN 0.01 --'Predominantly nonhydric'
        WHEN maj_not_hydric >= 0.5  AND maj_hydric >= 0.5 THEN 0.15 --'Partially hydric'
        ELSE 0.00 --'Error'
    END AS low_pct,

    CASE WHEN comp_count = all_not_hydric + hydric_null THEN 0.00 --'Nonhydric'
        WHEN comp_count = all_hydric  THEN 1 --'Hydric'
        WHEN comp_count != all_hydric AND count_maj_comp = maj_hydric THEN 0.85 --'Predominantly hydric'
        WHEN hydric_inclusions >= 0.5 AND  maj_hydric < 0.5 THEN 0.05 --'Predominantly nonhydric'
        WHEN maj_not_hydric >= 0.5  AND  maj_hydric >= 0.5 THEN  0.50 --'Partially hydric'
        ELSE 0.00 --'Error'
    END AS rv_pct,

    CASE WHEN comp_count = all_not_hydric + hydric_null THEN 0.00 --'Nonhydric'
        WHEN comp_count = all_hydric  THEN 1 --'Hydric'
        WHEN comp_count != all_hydric AND count_maj_comp = maj_hydric THEN 0.99 --'Predominantly hydric'
        WHEN hydric_inclusions >= 0.5 AND maj_hydric < 0.5 THEN 0.20 --'Predominantly nonhydric'
        WHEN maj_not_hydric >= 0.5  AND maj_hydric >= 0.5 THEN  0.79 --'Partially hydric'
        ELSE 0.00 --'Error'
    END AS high_pct
    FROM #Hydric1
;

INSERT INTO #Hydric3 ( aoiid, landunit, attributename, aoi_acres, mukey, hydric_flag, low_acres, rv_acres, high_acres)
    SELECT DISTINCT aoiid,
    landunit,
    'Hydric Soils' AS attributename,
    ROUND (SUM (mapunit_acres ) OVER(PARTITION BY aoiid), 2) AS aoi_acres,
    H3.mukey,
    CASE WHEN hydric_rating = 'Nonhydric' THEN 0 ELSE 1 END AS hydric_flag,
    mapunit_acres * low_pct AS low_acres,
    mapunit_acres * rv_pct AS rv_acres ,
    mapunit_acres * high_pct AS high_acres
    FROM #Hydric2 AS H3
    INNER JOIN #M2 AS MH2 ON MH2.mukey = H3.mukey
    GROUP BY aoiid, landunit, H3.mukey, mapunit_acres, hydric_rating, low_pct, rv_pct, high_pct
;

-- ************************************************************************************************
-- END OF QUERIES FOR SOIL PROPERTIES...

"""

            sQuery += sPropertyQuery

        if bInterpQueries or bCartQueries :
            #  LOOP THROUGH RATING QUERIES
            #
            # Possible CART interpretations...
            #
            # attributename, nasisrulename, resultcolumnname, rulekey
            # 'Surface Salt Concentration', 'SOH - Concentration of Salts- Soil Surface', 'SurfSal', 62833
            # 'Soil Rutting Hazard', 'FOR - Soil Rutting Hazard', 'SoilRutHzd', 281
            # 'Organic Matter Depletion', 'SOH - Organic Matter Depletion', 'OrgMatDepl', 62834
            # 'Soil Susceptibility to Compaction', 'SOH - Soil Susceptibility to Compaction', 'SoilSuscCo', 57990
            # 'Suitability for Aerobic Soil Organisms' - 'SOH - Suitability for Aerobic Soil Organisms'
            # 'Pesticide Leaching Potential', 'AGR - Pesticide Loss Potential-Leaching', 'plpLeach', 34008
            # 'Pesticide Runoff Potential', 'AGR - Pesticide Loss Potential-Soil Surface Runoff', 'plpRunoff', 34027
            # 'AWM - Land Application of Municipal Sewage Sludge', 'Land Application of Municipal Sewage Sludge', 'LAMSSludge', 235
            #
            # TEST LIST
            attributeList = ['Surface Salt Concentration', 'Soil Susceptibility to Compaction', 'Organic Matter Depletion', 'Agricultural Organic Soil Subsidence', 'Suitability for Aerobic Soil Organisms']

            for attributeName in attributeList:
                time.sleep(1)
                msg = "Adding query for '" + attributeName + "'"
                arcpy.SetProgressorLabel(msg)

                sInterpQuery = """
-- Begin query for soil interpretation:  """ + attributeName + """
-- ************************************************************************************************

SELECT @attributeName = '""" + attributeName + """';
SELECT @minPct = 10;
SELECT @minAcres = 10;

-- Get ordered set of interphrc values from sdvattribute.maplegendxml. This is assumed to begin with the 'worst' rating. Need to double-check this for all interps.
SELECT @rating1 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[1]', 'VARCHAR(100)');
SELECT @rating2 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[2]', 'VARCHAR(100)');
SELECT @rating3 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[3]', 'VARCHAR(100)');
SELECT @rating4 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[4]', 'VARCHAR(100)');
SELECT @rating5 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[5]', 'VARCHAR(100)');
SELECT @rating6 = (SELECT maplegendxml FROM #SDV WHERE attributename = @attributeName).value('(/Map_Legend/Legend_Elements/Labels/@value)[6]', 'VARCHAR(100)');

-- Set interp rulekey and ruledesign as a variable to be used in cointerp query
SELECT @ruleKey = (SELECT rulekey FROM #SDV WHERE attributename = @attributeName);
SELECT @ruleDesign = (SELECT ruledesign FROM #SDV WHERE attributename = @attributeName)
SELECT @notRatedPhrase = (SELECT notratedphrase FROM #SDV WHERE attributename = @attributeName)
;

-- Add Not rated phrase to @rating variables
IF @notRatedPhrase IS NOT NULL
  IF @rating1 IS NULL (SELECT @rating1 = @notRatedPhrase)
  ELSE
    IF @rating2 IS NULL (SELECT @rating2 = @notRatedPhrase)
    ELSE
      IF @rating3 IS NULL (SELECT @rating3 = @notRatedPhrase)
      ELSE
        IF @rating4 IS NULL (SELECT @rating4 = @notRatedPhrase)
        ELSE
          IF @rating5 IS NULL (SELECT @rating5 = @notRatedPhrase)
          ELSE
            IF @rating6 IS NULL (SELECT @rating6 = @notRatedPhrase)
;

-- Append the rating classes for this interp to the #RatingClasses table
INSERT INTO #RatingClasses (attributename, ruledesign, rating1, rating2, rating3, rating4, rating5, rating6)
SELECT @attributeName AS attributename, @ruleDesign AS ruledesign, @rating1 AS rating1, @rating2 AS rating2, @rating3 AS rating3, @rating4 AS rating4, @rating5 AS rating5, @rating6 AS rating6
;

-- Populate the #RatingDomain table with a unique rating_key for this interp
SELECT @ratingKey = RTRIM(@attributeName) + ':1';
IF NOT @rating1 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating1, 1);
SELECT @ratingKey = RTRIM(@attributeName) + ':2';
IF NOT @rating2 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating2, 2);
SELECT @ratingKey = RTRIM(@attributeName) + ':3';
IF NOT @rating3 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating3, 3);
SELECT @ratingKey = RTRIM(@attributeName) + ':4';
IF NOT @rating4 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating4, 4);
SELECT @ratingKey = RTRIM(@attributeName) + ':5';
IF NOT @rating5 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating5, 5);
SELECT @ratingKey = RTRIM(@attributeName) + ':6';
IF NOT @rating6 IS NULL INSERT INTO #RatingDomain VALUES( @ratingKey, @attributename, @rating6, 6);

-- Populate component level ratings using the currently set soil interpretation
TRUNCATE TABLE #M5
INSERT INTO #M5
SELECT M4.aoiid, M4.landunit, M4.mukey, mapunit_acres, M4.cokey, M4.compname, M4.comppct_r, TP.interphrc AS rating_class, SUM (M4.comppct_r) OVER(PARTITION BY M4.landunit, M4.mukey) AS mu_pct_sum
FROM #M4 AS M4
LEFT OUTER JOIN cointerp AS TP ON M4.cokey = TP.cokey AND rulekey = @ruleKey
WHERE M4.majcompflag = 'Yes'
;

-- Populate component level ratings with adjusted component percent to account for the un-used minor components
TRUNCATE TABLE #M6
INSERT INTO #M6
SELECT aoiid, landunit, mukey, mapunit_acres, cokey, compname, comppct_r, rating_class, mu_pct_sum, (1.0 * comppct_r / NULLIF(mu_pct_sum, 0)) AS adj_comp_pct
FROM #M5
;

-- Populates component acres by multiplying map unit acres with adjusted component percent
TRUNCATE TABLE #M8
INSERT INTO #M8
SELECT  aoiid, landunit, mukey, mapunit_acres, cokey, compname, comppct_r, rating_class, MU_pct_sum, adj_comp_pct, ROUND ( (adj_comp_pct * mapunit_acres), 4) AS co_acres
FROM #M6
;

-- Aggregates the classes and sums up the component acres  by landunit (Tract and Field number)
TRUNCATE TABLE #M10
INSERT INTO #M10
SELECT landunit, rating_class, SUM (co_acres) AS rating_acres
FROM #M8
GROUP BY landunit, rating_class
ORDER BY landunit, rating_acres DESC
;

-- Detailed Landunit Ratings1: rating acres and rating percent by area for each soil-landunit polygon
INSERT INTO #LandunitRatingsDetailed1 (aoiid, landunit, attributename, rating_class, rating_key, rating_value, rating_pct, rating_acres, landunit_acres)
SELECT aoiid, M10.landunit, @attributeName AS attributename, M10.rating_class, RD.rating_key, RD.rating_value,
ROUND ((rating_acres / landunit_acres) * 100.0, 2) AS rating_pct,
ROUND (rating_acres, 2) AS rating_acres,
ROUND ( landunit_acres, 2) AS landunit_acres
FROM #M10 M10
LEFT OUTER JOIN #AoiAcres ON #AoiAcres.landunit = M10.landunit
INNER JOIN #RatingDomain RD ON M10.rating_class = RD.rating_class
WHERE RD.attributename = @attributeName
GROUP BY aoiid, M10.landunit, M10.rating_class, rating_key, rating_acres, landunit_acres, rating_value
ORDER BY landunit, attributename, rating_value DESC
;

-- #LandunitRatingsDetailed2 is populated with all information plus rolling_pct and rolling_acres which are using in the landunit summary rating.
INSERT INTO #LandunitRatingsDetailed2 (landunit, attributename, rating_class, rating_key, rating_value, rating_pct, rating_acres, landunit_acres, rolling_pct, rolling_acres)
    SELECT landunit, attributename, rating_class, rating_key, rating_value, rating_pct, rating_acres, landunit_acres,
    rolling_pct = SUM(rating_pct) OVER
        (
        PARTITION BY landunit
        ORDER BY rating_key ROWS UNBOUNDED PRECEDING
        ),
    rolling_acres = SUM(rating_acres) OVER
        (
        PARTITION BY landunit
        ORDER BY rating_key ROWS UNBOUNDED PRECEDING
        )
    FROM #LandunitRatingsDetailed1
    WHERE attributename = @attributeName
    ORDER BY landunit, attributename
;

-- #LandunitRatingsCART identifies the single, most limiting rating (per landunit) that comprises at least 10% by area or 10 acres. This record will have an id value of 1.
INSERT INTO #LandunitRatingsCART (id, landunit, attributename, rating_class, rating_key, rating_value, rolling_pct, rolling_acres, landunit_acres)
SELECT ROW_NUMBER() OVER(PARTITION BY landunit ORDER BY rating_key ASC) AS id,
landunit, attributename, rating_class, rating_key, rating_value, rolling_pct, rolling_acres, landunit_acres
FROM #LandunitRatingsDetailed2
WHERE attributename = @attributeName AND (rolling_pct >= @minPct OR rolling_acres >= @minAcres)
;

-- End of:  """ + attributeName + """
-- ************************************************************************************************
"""

                sQuery += sInterpQuery

        if bDiagnosticQuery:
            # hard-coded to False in the main
            PrintMsg(" \n\tAdding queries for diagnostic tables", 0)
            sQuery += """
-- Farm Class LUD detailed acres for each rating class by landunit
SELECT DISTINCT landunit, SUM (mapunit_acres) OVER(PARTITION BY aoiid, farmlndclass) AS rating_acres, farmlndclass
    FROM #FC
    GROUP BY aoiid, landunit, mapunit_acres, farmlndclass
;

-- Aggregate Stability LUD
SELECT DISTINCT landunit, landunit_acres, 'Aggregate Stability' AS rating_name,
LU_AGG_Weighted_Average_L AS Aggregate_Stability_L,
LU_AGG_Weighted_Average_R AS Aggregate_Stability_R,
LU_AGG_Weighted_Average_H AS Aggregate_Stability_H
FROM #agg8
;

-- Report AWS LUV
SELECT DISTINCT landunit, landunit_acres, 'Available Water Storage' AS rating_name,
AWS_Weighted_Average0_150 AS AWS_0_150
FROM #aws1
;

-- Farm Class LUD LandunitRatingsFarmClass
SELECT DISTINCT #FC.landunit, 'Farm Class' AS rating_name, SUM (mapunit_acres) OVER(PARTITION BY aoiid, farmlndclass) AS rating_acres,
CASE WHEN farmlndclass = 'Prime' THEN 1
WHEN farmlndclass = 'Prime if' THEN 2
WHEN farmlndclass = 'State' THEN 3
WHEN farmlndclass = 'State if' THEN 4
WHEN farmlndclass = 'Local' THEN 5
WHEN farmlndclass = 'Local if' THEN 6
WHEN farmlndclass = 'Not Prime' THEN 7
WHEN farmlndclass = 'Unique' THEN 8
WHEN farmlndclass = 'Not rated' THEN 9
ELSE -1
END AS rating_value,
farmlndclass AS rating_class
FROM #FC
GROUP BY aoiid, #FC.landunit, mapunit_acres, farmlndclass
;

-- Drainage class LUD
SELECT DISTINCT aoiid, landunit, landunit_acres, 'Drainage class Detailed113500' AS attributename, ROUND (SUM (co_acres) OVER(PARTITION BY aoiid, drainagecl), 2) AS drainage_class_acres,
CASE WHEN drainagecl = 'Excessively drained' THEN 1
WHEN drainagecl = 'Somewhat excessively drained' THEN 2
WHEN drainagecl = 'Well drained' THEN 3
WHEN drainagecl = 'Moderately well drained' THEN 4
WHEN drainagecl = 'Somewhat poorly drained' THEN 5
WHEN drainagecl = 'Poorly drained' THEN 6
WHEN drainagecl = 'Very poorly drained' THEN 7
WHEN drainagecl = 'Subaqueous' THEN 8
WHEN drainagecl IS NULL THEN 9
ELSE -1
END AS rating_value,
drainagecl AS rating_class
FROM #drain2
ORDER BY aoiid, drainage_class_acres DESC
;

"""

        if bSpatial:
            #PrintMsg(" \n\tAdding spatial query to return soil polygon geometry", 0)
            arcpy.SetProgressorLabel("Adding spatial query to return soil polygon geometry")
            sQuery += """
-- Spatial. Soil Map-landunit intersection returned as WKT geometry
SELECT landunit, AS2.mukey, MU.musym, MU.muname, poly_acres, soilgeog.STAsText() AS wktgeom
    FROM #AoiSoils2 AS2
    INNER JOIN mapunit MU ON AS2.mukey = MU.mukey
    ORDER BY polyid ASC
;

-- Soils basic component data
SELECT DISTINCT M4.compname, M4.comppct_r, M4.majcompflag, Mu.musym, Mu.muname, M4.cokey, M4.mukey
    FROM #M4 M4
    INNER JOIN mapunit Mu ON M4.mukey = Mu.mukey
    ORDER BY M4.mukey, M4.comppct_r DESC, M4.cokey
;

-- SDV attribute table needed to create soil interp map layers in ArcMap
SELECT attributename, attributecolumnname, attributelogicaldatatype, attributetype, attributeuom, nasisrulename, rulekey, ruledesign, notratedphrase,
    resultcolumnname, effectivelogicaldatatype, attributefieldsize,
    CAST(maplegendxml AS NVARCHAR(2048)) AS maplegendxml, maplegendkey,
    attributedescription, sqlwhereclause, secondaryconcolname, tiebreaklowlabel, tiebreakhighlabel
    FROM #SDV
;

"""

        if bInterpQueries:
            sQuery += """
-- Interpretation data for major components
SELECT M2.mukey, attributename, (SELECT TOP 1 interphrc
    FROM mapunit
    INNER JOIN component ON component.mukey=mapunit.mukey AND majcompflag = 'Yes'
    INNER JOIN cointerp AS coi ON component.cokey = coi.cokey AND mapunit.mukey = M2.mukey AND ruledepth = 0 AND TP.rulekey = coi.rulekey
    GROUP BY interphrc, comppct_r ORDER BY SUM(comppct_r) OVER(PARTITION BY interphrc) DESC) as interp_dcd
    FROM #M2 AS M2
    INNER JOIN component AS CO ON CO.mukey = M2.mukey AND majcompflag = 'Yes'
    LEFT OUTER JOIN cointerp AS TP ON CO.cokey = TP.cokey
    INNER JOIN #SDV AS s ON s.rulekey = TP.rulekey
    GROUP BY M2.mukey, rulename, TP.rulekey, attributename
    ORDER BY M2.mukey, rulename, TP.rulekey, attributename
;

-- Hydric MU
SELECT mukind,
    SUBSTRING( (SELECT DISTINCT ( ', ' +  cogm2.geomfname )
    FROM mapunit AS m2
    INNER JOIN component AS c2 ON c2.mukey = m2.mukey AND hydricrating = 'Yes' AND m2.mukey = mu.mukey
    INNER JOIN cogeomordesc AS cogm2 ON c2.cokey = cogm2.cokey AND cogm2.rvindicator='Yes' AND cogm2.geomftname = 'Landform' GROUP BY m2.mukey, cogm2.geomfname FOR XML PATH('') ), 3, 1000) AS hydric_landforms,

    SUBSTRING( (SELECT  DISTINCT ( ', ' +  cogm.geomfname )
        FROM mapunit AS m1
        INNER JOIN component AS c1 ON c1.mukey = m1.mukey AND hydricrating = 'Yes' AND m1.mukey = mu.mukey
        INNER JOIN cogeomordesc AS cogm ON c1.cokey = cogm.cokey AND cogm.rvindicator = 'Yes' AND cogm.geomftname = 'Microfeature' GROUP BY m1.mukey, cogm.geomfname FOR XML PATH('') ), 3, 1000) AS hydric_microfeatures,

    SUBSTRING( ( SELECT ( ', ' + hydriccriterion )
        FROM mapunit AS m
        INNER JOIN component AS c ON c.mukey = m.mukey AND hydricrating = 'Yes' AND m.mukey = mu.mukey
        INNER JOIN cohydriccriteria AS coh ON c.cokey = coh.cokey GROUP BY m.mukey, hydriccriterion ORDER BY hydriccriterion ASC FOR XML PATH('') ), 3, 1000) AS hydric_criteria,
    hydric_rating, low_pct, rv_pct, high_pct, mu.mukey
    FROM #Hydric2 AS mu
    INNER JOIN mapunit ON mapunit.mukey = mu.mukey
;

"""

        if bCartQueries:
            #PrintMsg(" \n\tAdding Final CART Queries", 0)
            arcpy.SetProgressorLabel("Adding Final CART Queries")
            sQuery += """
-- ************************************************************************************************
-- Final output queries follow...
-- ************************************************************************************************

-- Begin saving the final CART soil interpretation ratings for each landunit. The record for the overall landunit rating will have an id = 1.
INSERT INTO #LandunitRatingsCART2 (landunit, attributename, rating_class, rating_key, rating_value, rolling_pct, rolling_acres, landunit_acres, soils_metadata)
    SELECT LC.landunit, LC.attributename, LC.rating_class, LC.rating_key, LC.rating_value, rolling_pct, rolling_acres, landunit_acres, MD.soils_metadata
    FROM #LandunitRatingsCART LC
    INNER JOIN #RatingDomain RD ON LC.attributename = RD.attributename AND LC.rating_class = RD.rating_class
    INNER JOIN #LandunitMetadata MD ON LC.landunit = MD.landunit
    WHERE LC.id = 1
    ORDER BY landunit, rating_key
;

-- Ponding and Flooding CART
INSERT INTO #LandunitRatingsCART2 (landunit, attributename, rating_value, rating_class)
SELECT #pf2.landunit, 'Ponding or Flooding' AS rating_name,
CASE WHEN SUM (co_acres) IS NULL THEN 2
WHEN SUM (co_acres) > 0 THEN 1
WHEN SUM (co_acres) = 0 THEN 0
ELSE -1
END AS rating_value,
CASE WHEN SUM (co_acres) IS NULL THEN 'Not rated'
WHEN SUM (co_acres) > 0 THEN 'Yes'
WHEN SUM (co_acres) = 0 THEN 'No'
ELSE 'Error'
END AS rating_class
FROM #pf2
GROUP BY #pf2.landunit
ORDER BY #pf2.landunit
;

-- Water Table CART
INSERT INTO #LandunitRatingsCART2 (landunit, attributename, rating_value, rating_class)
SELECT landunit, 'Water Table' AS attribute_name,
CASE WHEN SUM (co_acres) IS NULL THEN 2
WHEN SUM (co_acres) > 0 THEN 1
WHEN SUM (co_acres) = 0 THEN 0
ELSE -1
END AS rating_value,
CASE WHEN SUM (co_acres) IS NULL THEN 'Not rated'
WHEN SUM (co_acres) > 0 THEN 'Yes'
WHEN SUM (co_acres) = 0 THEN 'No'
ELSE 'Error'
END AS rating_class
FROM #wet2
GROUP BY landunit
ORDER BY landunit
;

-- Hydric Soils CART
INSERT INTO #LandunitRatingsCART2 (landunit, attributename, rating_value, rating_class)
SELECT landunit, attributename,
CASE WHEN SUM(rv_acres) IS NULL THEN 2
WHEN SUM(rv_acres) > 0 THEN 1
WHEN SUM(rv_acres) = 0 THEN 0
END AS rating_key,
CASE WHEN SUM(rv_acres) IS NULL THEN 'Not rated'
WHEN SUM(rv_acres) > 0 THEN 'Yes'
WHEN SUM(rv_acres) = 0 THEN 'No'
END AS rating_class
FROM #Hydric3
GROUP BY landunit, attributename
ORDER BY landunit
;

-- SOC CART
INSERT INTO #LandunitRatingsCART2 (landunit, attributename, rating_value, rating_class)
SELECT DISTINCT landunit, 'Soil Organic Carbon Stock' AS attributename,
CASE WHEN SOCSTOCK_0_30_Weighted_Average = 0 THEN 0
WHEN SOCSTOCK_0_30_Weighted_Average > 0 AND SOCSTOCK_0_30_Weighted_Average < 10 THEN 1
WHEN SOCSTOCK_0_30_Weighted_Average >= 10 AND SOCSTOCK_0_30_Weighted_Average < 25 THEN 2
WHEN SOCSTOCK_0_30_Weighted_Average >= 25 AND SOCSTOCK_0_30_Weighted_Average < 50 THEN 3
WHEN SOCSTOCK_0_30_Weighted_Average >= 50 AND SOCSTOCK_0_30_Weighted_Average < 100 THEN 4
WHEN SOCSTOCK_0_30_Weighted_Average >= 100 THEN 5
WHEN SOCSTOCK_0_30_Weighted_Average IS NULL THEN 6
END AS rating_value,
CASE WHEN SOCSTOCK_0_30_Weighted_Average = 0 THEN 'None'
WHEN SOCSTOCK_0_30_Weighted_Average >0 AND SOCSTOCK_0_30_Weighted_Average < 10 THEN 'Very low'
WHEN SOCSTOCK_0_30_Weighted_Average >=10 AND SOCSTOCK_0_30_Weighted_Average < 25 THEN 'Low'
WHEN SOCSTOCK_0_30_Weighted_Average >=25 AND SOCSTOCK_0_30_Weighted_Average < 50 THEN 'Moderate'
WHEN SOCSTOCK_0_30_Weighted_Average >=50 AND SOCSTOCK_0_30_Weighted_Average < 100 THEN 'Moderately High'
WHEN SOCSTOCK_0_30_Weighted_Average >=100 THEN 'High'
WHEN SOCSTOCK_0_30_Weighted_Average IS NULL THEN 'Not rated'
END AS rating_class
FROM #SOC6
;

-- Aggregate Stability CART
INSERT INTO #LandunitRatingsCART2 (landunit, attributename, rating_value, rating_class)
SELECT DISTINCT  #agg8.landunit, 'Aggregate Stability' AS attributename,
CASE WHEN LU_AGG_Weighted_Average_R <25 THEN 1
WHEN LU_AGG_Weighted_Average_R >=25 AND LU_AGG_Weighted_Average_R <50 THEN 2
WHEN LU_AGG_Weighted_Average_R >=50 AND LU_AGG_Weighted_Average_R <75 THEN 3
WHEN LU_AGG_Weighted_Average_R >=75 THEN 4
WHEN LU_AGG_Weighted_Average_R IS NULL THEN 5
END AS rating_value,
CASE WHEN LU_AGG_Weighted_Average_R <25 THEN 'Low'
WHEN LU_AGG_Weighted_Average_R >=25 AND  LU_AGG_Weighted_Average_R <50 THEN 'Moderate'
WHEN LU_AGG_Weighted_Average_R >=50 AND  LU_AGG_Weighted_Average_R <75 THEN 'Moderately High'
WHEN LU_AGG_Weighted_Average_R >=75 THEN 'High'
WHEN LU_AGG_Weighted_Average_R IS NULL THEN 'Not Rated'
END AS rating_class
FROM #agg8
;

-- AWS CART
INSERT INTO #LandunitRatingsCART2 (landunit, attributename, rating_value, rating_class)
SELECT DISTINCT landunit, 'Available Water Storage' AS attributename,
CASE WHEN AWS_Weighted_Average0_150 IS NULL THEN 2
WHEN AWS_Weighted_Average0_150 > 0 THEN 1
WHEN AWS_Weighted_Average0_150 = 0 THEN 0
END AS rating_value,
CASE WHEN AWS_Weighted_Average0_150 IS NULL THEN 'Not rated'
WHEN AWS_Weighted_Average0_150 > 0 THEN 'Yes'
WHEN AWS_Weighted_Average0_150 = 0 THEN 'No'
END AS rating_class
FROM #aws1
;

-- For ArcMap LandUnit Rating table, also return rating_class.
SELECT LRC.landunit, LRC.attributename AS rating_name, LRC.rating_value, LRC.rating_class, a.landunit_acres
FROM #LandunitRatingsCART2 LRC
INNER JOIN #AoiAcres AS a ON a.landunit = LRC.landunit
ORDER BY LRC.landunit, LRC.attributename
;

-- Detailed CART data for ArcMap
SELECT landunit, attributename, rating_class, rating_value, rolling_pct, rolling_acres, landunit_acres
FROM #LandunitRatingsCART
ORDER BY landunit, attributename, rating_value ASC
;

"""

        if bSaveQuery:
            # Write query to a text file and display
            #PrintMsg(" \nDisplaying query in text editor...", 1)
            queryPath = os.path.join(env.scratchFolder, "CART_SoilsQuery.txt")
            fh = open(queryPath, "w")
            fh.write(sQuery)
            fh.close()
            os.startfile(queryPath)

        # Return Soil Data Access query string
        return sQuery



    except MyError, e:
        # Example: raise MyError, "This is an error message"
        # Write query to a text file
        return ""

    except:
        errorMsg()
        return ""

## ===================================================================================
def RunSDA_Queries(theURL, sQuery, gdb):
    #
    # JSON format
    #
    # Send spatial query to SDA Tabular Service and return a table. NO GEOMETRY.
    #
    # Format JSON table containing records with MUKEY and WKT Polygons to a polygon featureclass

    try:
        #bVerbose = True
        PrintMsg(" \nSubmitting request to Soil Data Access...", 0)

        #PrintMsg(" \nHardcoded query for NOTCOM problem", 1)

        xQuery = """


"""
        arcpy.SetProgressorLabel("Submitting request to Soil Data Access...")

        tableList = list() # list of new tables or featureclasses created from Soil Data Access

        # Tabular service to append to SDA URL

        # At some point I need to hard code the timeStamp so that it is no longer a run-time value
        now = datetime.datetime.now()
        timeStamp = now.strftime('%Y%m%d')

        url = theURL + "/" + "Tabular/post.rest"
        dRequest = dict()
        dRequest["format"] = "JSON+COLUMNNAME+METADATA"
        dRequest["query"] = sQuery
        dRequest["auditdata"] = '(application="CART" description="RA GIS" version="' + timeStamp + '")'

        if 1==2:
            PrintMsg(" \nSDA request parameters: \n", 0)
            PrintMsg(" \n\tURL: " + url, 0)
            PrintMsg(" \n\tAuditData: " + dRequest["*auditdata*"], 0)
            #PrintMsg("\tformat: " + dRequest["format"], 0)
            #PrintMsg("query: " + str(dRequest["query"]), 0)
            fh = open(r"c:\temp\xxQuery.txt", "w")
            fh.write(dRequest["query"])
            fh.close()

        # Create SDM connection to service using HTTP
        jData = json.dumps(dRequest)

        # Send request to SDA Tabular service
        req = urllib2.Request(url, jData)

        try:
            resp = urllib2.urlopen(req, timeout=30.0)  # A failure here will probably throw an HTTP exception

        except IOError as err:
            raise MyError, err

        except urllib2.HTTPError, err:
            # Currently the messages coming back from the server are not very helpful.
            # Bad Request could mean that the query timed out or tried to return too many JSON characters.
            #
            if hasattr(err, 'msg'):
                PrintMsg("HTTP Error: " + str(e.msg), 2)
                return tableList

            elif hasattr(err, 'code'):
                PrintMsg("HTTP Error: " + str(e.code), 2)
                return tableList

            else:
                PrintMsg("HTTP Error? ", 2)
                return tableList

        except httplib.BadStatusLine, err:

            if hasattr(err, 'msg'):
                PrintMsg("HTTP Error: " + str(err.msg), 2)
                return tableList

            elif hasattr(err, 'code'):
                PrintMsg("HTTP Error: " + str(err.code), 2)
                return tableList

            else:
                PrintMsg("HTTP Error (BadStatusLine)", 2)
                #errorMsg()
                return tableList

        except httplib.HTTPException, err:

            if hasattr(err, 'msg'):
                PrintMsg("HTTP Error: " + str(err.msg), 2)
                return tableList

            elif hasattr(err, 'code'):
                PrintMsg("HTTP Error: " + str(err.code), 2)
                return tableList

            else:
                PrintMsg("HTTP Error (" + str(err) + ")", 2)
                #errorMsg()
                return tableList

        except:
            errorMsg()
            return tableList

        responseStatus = resp.getcode()
        responseMsg = resp.msg
        jsonString = resp.read()
        resp.close()

        try:
            # Convert JSON string to Python dictionary
            data = json.loads(jsonString)
            #PrintMsg(" \nJson String: \n" + jsonString + " \n ", 1)

        except:
            errorMsg()
            raise MyError, "Spatial Request failed"

        del jsonString, resp, req

        if not "Table" in data:
            raise MyError, "No soils data returned for this AOI request"

        else:
            arcpy.SetProgressorLabel("Successfully retrieved data from Soil Data Access")
            PrintMsg(" \nImporting soils data into ArcMap...", 0)
            #PrintMsg(" \nData keys: " + ", ".join(sorted(data.keys())), 1)
            bSpatial = False  # flag to indicate spatial data was returned

            keyList = sorted(data.keys())
            arcpy.SetProgressorLabel("Importing data into ArcMap...")

            for key in keyList:
                # PrintMsg(" \nImporting JSON data for object: " + key, 1)
                dataList = data[key]     # Data as a list of lists. Service returns everything as string.

                # Get sequence number for table
                if key.upper() == "TABLE":
                    tableNum = 1

                else:
                    tableNum = int(key.upper().replace("TABLE", "")) + 1

                # Get column names and column metadata from first two list objects
                columnNames = dataList.pop(0)
                columnInfo = dataList.pop(0)

                if "wktgeom" in columnNames:
                    # my key field for geometry is present, create featureclass
                    #
                    if "landunit" and "mukey" in columnNames:
                        newTableName = "SoilMap_by_Landunit"

                    elif "landunit" in columnNames and "landunit_acres" in columnNames:
                        newTableName = "LandunitPolygons"

                    else:
                        newTableName = "UnknownTable" + str(tableNum)

                    newTable = os.path.join(gdb, newTableName)
                    PrintMsg(" \nCreating new featureclass (" + newTableName + ") from object: " + key, 0)
                    arcpy.SetProgressorLabel("Importing " + newTableName + " featureclass")
                    sr = arcpy.SpatialReference(4326)
                    arcpy.CreateFeatureclass_management(gdb, newTableName, "POLYGON", "", "DISABLED", "DISABLED", sr)
                    tableList.append(newTableName)

                else:
                    # no geometry present, create standalone table
                    #
                    # PrintMsg(" \nGot a table with these column names:  " + ", ".join(columnNames) , 1)

                    if "landunit" in columnNames and "attributename" in columnNames and "rating_class" in columnNames and "rolling_acres" in columnNames:
                        newTableName = "LandunitRatingsDetailed"

                    elif len(columnNames) == 5 and "landunit" in columnNames and "rating_name" in columnNames and "rating_value" in columnNames and "rating_class" in columnNames and "landunit_acres" in columnNames:
                        newTableName = "LandunitRatingsCART"

                    elif len(columnNames) == 3 and "landunit" in columnNames and "rating_name" in columnNames and "rating_value" in columnNames:
                        newTableName = "LandunitRatingsCART"

                    elif "landunit" in columnNames and "rating_name" in columnNames and "rating_value_hydric" in columnNames:
                        newTableName = "LandunitRatingsHydric"

                    elif "landunit" in columnNames and "rating_name" in columnNames and "rating_value_fc" in columnNames:
                        newTableName = "LandunitRatingsFarmClass"

                    elif "landunit" in columnNames and "rating_dcd" in columnNames and "acres_dcd" in columnNames:
                        newTableName = "LandunitRatingsDCD"

                    elif "Aggregate_Stability_R" in columnNames and "landunit" in columnNames and "landunit_acres" in columnNames:
                        newTableName = "LandunitRatingsAggregateStability"

                    elif "AWS_0_150" in columnNames and "landunit" in columnNames and "landunit_acres" in columnNames:
                        newTableName = "LandunitRatingsAWS"

                    elif "SOC_0_5" in columnNames and "landunit" in columnNames and "landunit_acres" in columnNames:
                        newTableName = "LandunitSOC"

                    elif "farmlndclass" in columnNames and "landunit" in columnNames and "rating_acres" in columnNames:
                        newTableName = "LandunitFarmLandClass"

                    elif "drainage_class_acres" in columnNames and "aoiid" in columnNames and "landunit" in columnNames and "landunit_acres" in columnNames:
                        #PrintMsg("\tLandunitAcres columns: " + (", ").join(columnNames), 1)
                        newTableName = "LandunitRatingsDrainageClass"

                    elif "aoiid" in columnNames and "landunit" in columnNames and "landunit_acres" in columnNames:
                        #PrintMsg("\tLandunitAcres columns: " + (", ").join(columnNames), 1)
                        newTableName = "LandunitAcres"

                    elif "total_acres" in columnNames:
                        newTableName = "TotalAcres"

                    elif "mukey" in columnNames and "cokey" in columnNames and "comppct_r" in columnNames and "rating" in columnNames:
                        newTableName = "MapunitComponentRatings"

                    elif "mukey" in columnNames and "musym" in columnNames and "cokey" in columnNames and "comppct_r" in columnNames:
                        newTableName = "Component_Info"

                    elif "mukey" in columnNames and "attributename" in columnNames and "interp_dcd" in columnNames:
                        newTableName = "MapunitInterps_DCD"

                    elif "attributename" in columnNames and "ruledesign" in columnNames and "rating1" in columnNames:
                        newTableName = "InterpRatingClasses"

                    elif "attributename" in columnNames and "rating_key" in columnNames and "rating" in columnNames:
                        newTableName = "RatingKeys"

                    elif "hydric_landforms" in columnNames and "hydric_microfeatures" in columnNames and "hydric_rating" in columnNames and "low_pct" in columnNames and "mukey" in columnNames:
                        newTableName = "MapunitHydricInterp"

                    elif "hydric_pct" in columnNames and "mukey" in columnNames:
                        newTableName = "MapunitHydric"

                    elif "landunit" in columnNames and "attributename" in columnNames and "aoiid_rv_pct" in columnNames:
                        newTableName = "LandunitHydric"

                    elif "attributename" in columnNames and "nasisrulename" in columnNames and "rulekey" in columnNames and "ruledesign" in columnNames:
                        newTableName = "SDV_Attribute"

                    else:
                        PrintMsg("\tUnknownTable columns: " + ",".join(columnNames), 1)
                        newTableName = "UnknownTable" + str(tableNum)

                    arcpy.SetProgressorLabel("Importing " + newTableName + " table")
                    newTable = os.path.join(gdb, newTableName)
                    #PrintMsg("Creating new table (" + newTableName + ") from object: " + key, 0)
                    #PrintMsg("Creating new table '" + newTableName + "'", 0)
                    arcpy.CreateTable_management(gdb, newTableName)
                    tableList.append(newTableName)

                newFields = AddNewFields(newTable, columnNames, columnInfo)

                if len(newFields) == 0:
                    raise MyError, ""


                # No projection necessary. Input and output coordinate systems are the same.
                #
                if "wktgeom" in columnNames:
                    newFields.append("SHAPE@WKT")

                with arcpy.da.InsertCursor(newTable, newFields) as cur:

                    if "wktgeom" in columnNames:
                        # This is a spatial dataset

                        for rec in dataList:
                            # add a new polygon record
                            cur.insertRow(rec)

                    else:
                        # this is a tabular-only dataset

                        for rec in dataList:
                            cur.insertRow(rec)

                # Create newlayer and add to ArcMap
                # This isn't being used currently. Perhaps I can use it above when the soils featureclass is created,
                # but don't actually add it to ArcMap.
                #
                if "wktgeom" in columnNames:
                    #PrintMsg(" \nTable with geometry has the following fields: " + ", ".join(columNames), 1)

                    if newTableName != "SoilMap_by_Landunit":
                        # unless it is soils layer (save for later AddFirstSoilMap)
                        tmpFL = "TempSoilsLayer"
                        tmpLayerFile = os.path.join(env.scratchFolder, "xxSoilsLayer.lyr")
                        arcpy.MakeFeatureLayer_management(newTable, tmpFL)
                        arcpy.SaveToLayerFile_management(tmpFL, tmpLayerFile)
                        soilsLayer = mapping.Layer(tmpLayerFile)
                        #PrintMsg("\tUpdating soil mapunit symbology to simple outline", 1)
                        arcpy.SetProgressorLabel("Updating soil mapunit symbology to simple outline")
                        dLayerDefinition = SimpleFeaturesJSON(0.1)
                        soilsLayer.updateLayerFromJSON(dLayerDefinition)
                        soilsLayer.name = newTableName
                        mapping.AddLayer(df, soilsLayer)
                        PrintMsg("\tCreated new soils map layer (" + soilsLayer.name + ")", 1)
                        time.sleep(3)

                elif newTableName in ["LandunitRatingsCART", "LandunitRatingsDetailed"]:
                    # Create table view just for LandunitRatingsCART
                    #PrintMsg(" \n\tCreating new table view (" + newTableName + ") from object: " + key, 0)
                    arcpy.SetProgressorLabel("Creating new table view (" + newTableName + ") from object: " + key)
                    viewTbl = mapping.TableView(newTable)
                    mapping.AddTableView(df, viewTbl)


            # Refresh TOC display for new interp layers
            #arcpy.RefreshTOC()

        #arcpy.RefreshActiveView()
        return tableList

    except MyError, e:
        # Example: raise MyError, "This is an error message"
        PrintMsg(str(e), 2)
        return []

    except:
        errorMsg()
        return []

## ===================================================================================
def CreateGroupLayer(grpLayerName):
    try:
        # Use template lyr file stored in current script directory to create new Group Layer
        # This SDVGroupLayer.lyr file must be part of the install package along with
        # any used for symbology. The name property will be changed later.
        grpLayerFile = os.path.join(os.path.dirname(sys.argv[0]), "SDV_GroupLayer.lyr")

        if not arcpy.Exists(grpLayerFile):
            raise MyError, "Missing group layer file (" + grpLayerFile + ")"

        #grpLayerName = "WSS Thematic Soil Maps"
        testLayers = mapping.ListLayers(mxd, grpLayerName, df)

        if len(testLayers) > 0:
            # If it exists, remove an existing group layer from previous run
            grpLayer = testLayers[0]
            #PrintMsg(" \nRemoving old group layer", 1)
            mapping.RemoveLayer(df, grpLayer)

        grpLayer = mapping.Layer(grpLayerFile)  # template group layer file
        grpLayer.visible = False
        grpLayer.name = grpLayerName
        grpLayer.description = "Group layer containing individual soil maps for CART"
##        mapping.AddLayer(df, grpLayer, "TOP")
##        grpLayer = mapping.ListLayers(mxd, grpLayerName, df)[0]   # not sure why I have this
##        grpDesc = arcpy.Describe(grpLayer)
##
##        if grpDesc.dataType.lower() != "grouplayer":
##            raise MyError, "Problem with group layer"

        #PrintMsg(" \nAdding group layer: " + str(grpLayer.name), 0)

        return grpLayer

    except MyError, e:
        # Example: raise MyError, "This is an error message"
        PrintMsg(str(e), 2)
        return ""

    except:
        errorMsg()
        return ""

## ===================================================================================
#def CreateInterpMaps(gdb, soilsLayer, tableList):
def CreateInterpMaps(gdb, soilsFC, tableList, soilsLayerFile):
    # Create each of the soil interp maps returned from Soil Data Access
    # Starts by creating a map layer using soilsLayerFile and then switching to unique
    # values symbology using a second template layer file.
    # Finally the soils map layer is stored in the dInterps dictionary.

    # Variable soilsLayer will be based upn soil polygons.

    dInterpLayers = dict()  # create a dictionary to hold all of the interp layers

    try:

        if "MapunitInterps_DCD" in tableList and "SDV_Attribute" in tableList and "SoilMap_by_Landunit" in tableList:

            # Start new method, using soils featureclass to create soilsLayer
            #soilsLayerName = "SoilMap_by_Landunit"
            #soilsLayer = arcpy.MakeFeatureLayer_management(soilsFC, soilLines)
            #soilsLayerFile = os.path.join(os.path.dirname(gdb), "Soil_Lines.lyr")
            #arcpy.SaveToLayerFile_management(soilsLayer, soilsLayerFile, "RELATIVE", "10.3")

            soilsLayer = mapping.Layer(soilsLayerFile)

            # Flatten the "MapunitInterps_DCD" table because it contains different attribute ratings in one column
            # get a distinct list of attributename values
            sqlClause = ("DISTINCT", "ORDER BY attributename")
            attsList = list()
            dOutputValues = dict()
            saTable = os.path.join(gdb, "MapunitInterps_DCD")

            with arcpy.da.SearchCursor(saTable, ["attributename", "interp_dcd"]) as cur:
                for rec in cur:
                    att, rating = rec
                    att = att.strip()
                    rating = rating.strip()

                    if not att in attsList:
                        attsList.append(att)
                        dOutputValues[att] = [rating]

                    else:
                        if not rating in dOutputValues[att]:
                            dOutputValues[att].append(rating)

            #if len(attsList) > 0:
            #    PrintMsg(" \nCreating soil interpretation maps for " + ", ".join(attsList), 0)

            for sdvAtt in attsList:
                #sdvAtt = sdvAtt
                outputValues = dOutputValues[sdvAtt]

                # Try creating the soil map layers without creating these table views. Trying to speed it up.
                interpTbl = mapping.TableView(saTable)
                interpTbl.name = "View_" + sdvAtt.replace(" ", "_")
                interpTbl.definitionQuery = "attributename = '" + sdvAtt + "'"

                # Get sdvattributes
                global dSDV
                dSDV = GetSDVAtts(gdb, sdvAtt, "Dominant Condition", "tiebreakhighlabel", False, "")

                # Setup input and output objects for interp maps
                #outputLayerName = sdvAtt + " Layer"

                outputLayerFile = os.path.join(os.path.dirname(gdb), "SDV_" + sdvAtt.replace(" ", "_") + ".lyr")
                parameterString = "Parameter String"
                creditsString = "Credits String"
                dLegend = GetMapLegend(dSDV, False)

                # Get map layer settings for documentation
                # Hardcoding these next two settings - temporary fix
                aggMethod = "Dominant condition"
                tieBreaker = dSDV["tiebreakhighlabel"]
                newFieldName = dSDV["resultcolumnname"]
                muDesc = arcpy.Describe(soilsLayer)
                soilsFC = muDesc.catalogPath
                tblDesc = arcpy.Describe(interpTbl)
                tbl = tblDesc.catalogPath

                # Save parameter settings for layer description
                if not dSDV["attributeuom"] is None:
                    parameterString = "Units of Measure: " +  dSDV["attributeuom"]
                    parameterString = parameterString + "\r\nAggregation Method: " + aggMethod + ";  Tiebreak rule: " + tieBreaker

                else:
                    parameterString = "\r\nAggregation Method: " + aggMethod + ";  Tiebreak rule: " + tieBreaker

                if dSDV["effectivelogicaldatatype"].lower() in ["float", "integer"]:
                    parameterString = parameterString + "\r\nUsing " + sRV.lower() + " values (" + dSDV["attributecolumnname"] + ") from " + dSDV["attributetablename"].lower() + " table"

                # Finish adding system information to description
                #
                #
                envUser = arcpy.GetSystemEnvironment("USERNAME")
                if "." in envUser:
                    user = envUser.split(".")
                    userName = " ".join(user).title()

                elif " " in envUser:
                    user = envUser.split(" ")
                    userName = " ".join(user).title()

                else:
                    userName = envUser

                # Get today's date
                d = datetime.date.today()
                toDay = d.isoformat()
                #today = datetime.date.today().isoformat()

                parameterString = parameterString + "\r\nGeoDatabase: " + gdb + "\r\n" + muDesc.dataType.title() + ": " + \
                muDesc.name + "\r\nRating Table: " + tblDesc.name

                creditsString = "\r\nCreated by " + userName + " on " + toDay + " using script " + os.path.basename(sys.argv[0])

                # End of map layer settings

                dLayerDefinition = CreateJSONLegend(dLegend, interpTbl, outputValues, "interp_dcd", sdvAtt, False)
                dLayerDefinition["fields"][0]["name"] = newFieldName.encode('ascii')
                dLayerDefinition["fields"][0]["alias"] = newFieldName.encode('ascii')
                dLayerDefinition["displayField"] = newFieldName.encode('ascii')
                dLayerDefinition['drawingInfo']['renderer']['field1'] = newFieldName.encode('ascii')

                # Copy the data for this interp to soils featureclass so it can be used to create all interp maps.
                bTransferred = TransferInterpData(soilsFC, interpTbl, sdvAtt, outputLayerFile, outputValues, parameterString, creditsString, dLayerDefinition, False)
                del interpTbl

                if bTransferred == False:
                    raise MyError, ""

                # Create empty template layer with unique values symbology
                sdvLyr = "SDV_PolygonUnique.lyr"
                sdvLyrFile = os.path.join(os.path.dirname(sys.argv[0]), sdvLyr)
                symbologyLayer = mapping.Layer(sdvLyrFile)

                # Try using soilsLayerFile to create a new mapping Layer for each interp
                interpLayer = mapping.Layer(soilsLayerFile)

                mapping.UpdateLayer(df, interpLayer, symbologyLayer, True)


                bLabeled = AddLabels(interpLayer, newFieldName, False, 12)

                # Now the symbology properties of the new interp layer can be updated to use the interp rating data
                interpLayer.symbology.valueField = newFieldName.encode('ascii')
                interpLayer.symbology.addAllValues()  # Not sure why I need this

                interpLayer.updateLayerFromJSON(dLayerDefinition)
                interpLayer.name = sdvAtt
                interpLayer.description = dSDV["attributedescription"] + "\r\n\r\n" + parameterString
                interpLayer.credits = creditsString
                interpLayer.visible = False
                interpLayer.transparency = 50
                dInterpLayers[sdvAtt] = interpLayer

        return dInterpLayers

    except MyError, e:
        # Example: raise MyError, "This is an error message"
        PrintMsg(str(e), 2)
        return dInterpLayers

    except:
        errorMsg()
        return dInterpLayers

## ===================================================================================
def GetSDVAtts(gdb, sdvAtt, aggMethod, tieBreaker, bFuzzy, sRV):
    # Create a dictionary containing SDV attributes for the selected attribute fields
    #
    try:
        # Open sdvattribute table and query for [attributename] = sdvAtt
        dSDV = dict()  # dictionary that will store all sdvattribute data using column name as key
        sdvattTable = os.path.join(gdb, "sdv_attribute")
        flds = [fld.name for fld in arcpy.ListFields(sdvattTable)]
        sql1 = "attributename = '" + sdvAtt + "'"

        # Dictionary for aggregation method abbreviations
        #
        global dAgg
        dAgg = dict()
        dAgg["Dominant Component"] = "DCP"
        dAgg["Dominant Condition"] = "DCD"
        dAgg["No Aggregation Necessary"] = ""
        dAgg["Percent Present"] = "PP"
        dAgg["Weighted Average"] = "WTA"
        dAgg["Most Limiting"] = "ML"
        dAgg["Least Limiting"] = "LL"
        dAgg[""] = ""


        if bVerbose:
            PrintMsg(" \nReading sdvattribute table into dSDV dictionary", 1)

        with arcpy.da.SearchCursor(sdvattTable, "*", where_clause=sql1) as cur:
            rec = cur.next()  # just reading first record
            i = 0
            for val in rec:
                try:
                    dSDV[flds[i].lower()] = val.strip()

                except:
                    dSDV[flds[i].lower()] = val

                #PrintMsg(str(i) + ". " + flds[i] + ": " + str(val), 0)
                i += 1

        # Revise some attributes to accomodate fuzzy number mapping code
        #
        # Temporary workaround for NCCPI. Switch from rating class to fuzzy number

        #if dSDV["interpnullsaszeroflag"]:
        #    bZero = True

        if dSDV["attributetype"].lower() == "interpretation" and (dSDV["effectivelogicaldatatype"].lower() == "float" or bFuzzy == True):
            #PrintMsg(" \nOver-riding attributecolumnname for " + sdvAtt, 1)
            dSDV["attributecolumnname"] = "INTERPHR"

            # WHAT HAPPENS IF I SKIP THIS NEXT SECTION. DOES IT BREAK EVERYTHING ELSE WHEN THE USER SETS bFuzzy TO True?
            # Test is ND035, Salinity Risk%
            # Answer: It breaks my map legend.

            if dSDV["attributetype"].lower() == "interpretation" and dSDV["attributelogicaldatatype"].lower() == "string" and dSDV["effectivelogicaldatatype"].lower() == "float":
                #PrintMsg("\tIdentified " + sdvAtt + " as being an interp with a numeric rating", 1)
                pass

            else:
            #if dSDV["nasisrulename"][0:5] != "NCCPI":
                # This comes into play when user selects option to create soil map using interp fuzzy values instead of rating classes.
                dSDV["effectivelogicaldatatype"] = 'float'
                dSDV["attributelogicaldatatype"] = 'float'
                dSDV["maplegendkey"] = 3
                dSDV["maplegendclasses"] = 5
                dSDV["attributeprecision"] = 2


        #else:
            # Diagnostic for batch mode NCCPI
            #PrintMsg(" \n" + dSDV["attributetype"].lower() + "; " + dSDV["effectivelogicaldatatype"] + "; " + str(bFuzzy), 1)


        # Workaround for sql whereclause stored in sdvattribute table. File geodatabase is case sensitive.
        if dSDV["sqlwhereclause"] is not None:
            sqlParts = dSDV["sqlwhereclause"].split("=")
            dSDV["sqlwhereclause"] = 'UPPER("' + sqlParts[0] + '") = ' + sqlParts[1].upper()

        if dSDV["attributetype"].lower() == "interpretation" and bFuzzy == False and dSDV["notratedphrase"] is None:
            # Add 'Not rated' to choice list
            dSDV["notratedphrase"] = "Not rated" # should not have to do this, but this is not always set in Rule Manager

        if dSDV["secondaryconcolname"] is not None and dSDV["secondaryconcolname"].lower() == "yldunits":
            # then this would be units for legend (component crop yield)
            #PrintMsg(" \nSetting units of measure to: " + secCst, 1)
            dSDV["attributeuomabbrev"] = secCst

        if dSDV["attributecolumnname"].endswith("_r") and sRV in ["Low", "High"]:
            # This functionality is not available with SDV or WSS. Does not work with interps.
            #
            if sRV == "Low":
                dSDV["attributecolumnname"] = dSDV["attributecolumnname"].replace("_r", "_l")

            elif sRV == "High":
                dSDV["attributecolumnname"] = dSDV["attributecolumnname"].replace("_r", "_h")

            #PrintMsg(" \nUsing attribute column " + dSDV["attributecolumnname"], 1)

        # Working with sdvattribute tiebreak attributes:
        # tiebreakruleoptionflag (0=cannot change, 1=can change)
        # tiebreaklowlabel - if null, defaults to 'Lower'
        # tiebreaklowlabel - if null, defaults to 'Higher'
        # tiebreakrule -1=use lower  1=use higher
        if dSDV["tiebreaklowlabel"] is None:
            dSDV["tiebreaklowlabel"] = "Lower"

        if dSDV["tiebreakhighlabel"] is None:
            dSDV["tiebreakhighlabel"] = "Higher"

        if tieBreaker == dSDV["tiebreakhighlabel"]:
            #PrintMsg(" \nUpdating dAgg", 1)
            dAgg["Minimum or Maximum"] = "Max"

        else:
            dAgg["Minimum or Maximum"] = "Min"
            #PrintMsg(" \nUpdating dAgg", 1)

        if aggMethod == "":
            aggMethod = dSDV["algorithmname"]

        if dAgg[aggMethod] != "":
            dSDV["resultcolumnname"] = dSDV["resultcolumnname"] + "_" + dAgg[aggMethod]

        #PrintMsg(" \nSetting resultcolumn name to: '" + dSDV["resultcolumnname"] + "'", 1)

        return dSDV

    except:
        errorMsg()
        return dSDV

## ===================================================================================
def AddFirstSoilMap(gdb, outputFC, soilsLayerFile, labelField, soilLayerName):

    # Test to see if starting with a layer file prevents the layer already exists error.
    #
    # Create the top soil polygon layer which will be simple black outline, no fill but with MUSYM labels, visible
    # Run SDA query to add NATMUSYM and MAPUNIT NAME to featureclass

    try:
        #PrintMsg(" \nAddFirstSoilMap function where newLayer (" + newLayerName + ") is added using " + newLayerFile, 1)
        newLayer = mapping.Layer(soilsLayerFile)
        valList = GetUniqueValues(newLayer, labelField)
        newLayer.name = soilLayerName
        newLayer.visible = True
        newLayer.transparency = 50


        # Update soilmap layer symbology using JSON dictionary
        ## Simple symbology. Black polygon outlines and no fill
        dLayerDefinition = SimpleFeaturesJSON(0.4)
        newLayer.updateLayerFromJSON(dLayerDefinition)

        if arcpy.Exists("Component_Info"):
            # Create relate to outputFC
            #PrintMsg("\tCreating relationshipclass", 1)
            relclass = os.path.join(os.path.dirname(outputFC), "z" + os.path.basename(outputFC) + "_" + "Component_Info")
            arcpy.CreateRelationshipClass_management(os.path.join(os.path.dirname(outputFC), "Component_Info"), outputFC, relclass, "SIMPLE", "", "", "NONE", "ONE_TO_MANY", "NONE", "mukey", "mukey")

        newLayer.transparency = 0
        bLabeled = AddLabels(newLayer, labelField, False, 12)

##        if scale < 12000:
##            newLayer.showLabels = True
##
##        else:
##            newLayer.showLabels = False

        return newLayer

    except MyError, e:
        # Example: raise MyError, "This is an error message"
        PrintMsg(str(e), 2)
        return None

    except:
        errorMsg()
        return None

## ===================================================================================
def AddFirstSoilMap_Bak(gdb, outputFC, newLayer, labelField, soilLayerName):
    # This one works, but...
    # Create the top soil polygon layer which will be simple black outline, no fill but with MUSYM labels, visible
    # Run SDA query to add NATMUSYM and MAPUNIT NAME to featureclass
    try:
        #PrintMsg(" \nAddFirstSoilMap function where newLayer (" + newLayerName + ") is added using " + newLayerFile, 1)

        valList = GetUniqueValues(newLayer, labelField)
        #newLayer = mapping.Layer(newLayerFile)  #fix this
        newLayer.name = soilLayerName
        newLayer.visible = True
        newLayer.transparency = 50
        bZoomed = ZoomToExtent(newLayer)
        mapAngle, scale = RotateMap(mxd, df)

        # Update soilmap layer symbology using JSON dictionary
        ## Simple symbology. Black polygon outlines and no fill
        dLayerDefinition = SimpleFeaturesJSON(0.4)
        newLayer.updateLayerFromJSON(dLayerDefinition)

        if arcpy.Exists("Component_Info"):
            # Create relate to outputFC
            #PrintMsg("\tCreating relationshipclass", 1)
            relclass = os.path.join(os.path.dirname(outputFC), "z" + os.path.basename(outputFC) + "_" + "Component_Info")
            arcpy.CreateRelationshipClass_management(os.path.join(os.path.dirname(outputFC), "Component_Info"), outputFC, relclass, "SIMPLE", "", "", "NONE", "ONE_TO_MANY", "NONE", "mukey", "mukey")

        newLayer.transparency = 0
        bLabeled = AddLabels(newLayer, labelField, False, 12)

        if scale < 12000:
            newLayer.showLabels = True

        else:
            newLayer.showLabels = False

        return newLayer

    except MyError, e:
        # Example: raise MyError, "This is an error message"
        PrintMsg(str(e), 2)
        return None

    except:
        errorMsg()
        return None

## ===================================================================================
def AddHydricSoilMap(hydricLayerName, layerFile, labelField, gdb):
    # Create the top layer which will be simple black outline, no fill with MUSYM labels, visible
    # Run SDA query to add NATMUSYM and MAPUNIT NAME to featureclass
    try:
        ratingTable = os.path.join(gdb, "MapunitHydricInterp")

        if not arcpy.Exists(ratingTable):
            raise MyError, "Missing rating table: " + ratingTable

        # CART domain values hardcoded...
        domainValues = ['Hydric', 'Predominantly hydric', 'Partially hydric', 'Predominantly nonhydric', 'Nonhydric']

        valList = GetUniqueValues(ratingTable, labelField)
        # PrintMsg(" \nvalList: " + str(valList), 1)
        legendList = []

        # Compare values in table with domain and generate an ordered list
        for val in domainValues:
            if val in valList:
                legendList.append(val)

        # PrintMsg(" \nUsing " + layerFile + " to create " + hydricLayerName, 1)

        hydricLayer = mapping.Layer(layerFile)  #fix this
        hydricLayer.name = hydricLayerName  # from global variable
        #newLayer.description = summary
        hydricLayer.visible = True
        hydricLayer.transparency = 50
        hydricLayer.showLabels = False
        #mapping.AddLayer(df, newLayer)

        # Get list of newLayer fields
        fieldInfo = dict()
        soilFields = [fld.name.lower() for fld in arcpy.Describe(hydricLayer).fields]
        # Get list of fields from hydric rating table
        ratingFields = arcpy.Describe(ratingTable).fields
        hydricFields = [fld.name.lower() for fld in ratingFields]
        dHydric = dict()

        for fld in ratingFields:
            dHydric[fld.name.lower()] = (fld.type, fld.length)

        #joinFields = list()

        for fld in hydricFields:
            if not fld in soilFields:
                fldType, fldLength = dHydric[fld][0], dHydric[fld][1]
                #joinFields.append((fld, fldInfo[0], fldInfo[1]))
                arcpy.AddField_management(hydricLayer, fld, fldType, "", "", fldLength)

        # Get mapunit values from ratingTable and use to populate map layer
        hydricFields.insert(0, "mukey")

        dMapunitHydric = dict()

        # Get all hydric data from MapunitHydricRating table and store in a dictionary
        # Problem with text fields. They are coming out as fixed length, padded with spaces
        with arcpy.da.SearchCursor(ratingTable, hydricFields) as cur:
            for rec in cur:
                mukey = rec[0]

                # Try stripping out spaces here?
                newrec = list()
                for val in rec:
                    try:
                        val = val.strip()
                    except:
                        pass

                    newrec.append(val)

                dMapunitHydric[mukey] = newrec

        with arcpy.da.UpdateCursor(hydricLayer, hydricFields) as cur:
            for rec in cur:
                mukey = rec[0]

                if mukey in dMapunitHydric:
                    newrec = dMapunitHydric[mukey]
                    cur.updateRow(newrec)

                else:
                    PrintMsg("\tMissing hydric mukey " + str(mukey) +" from " + hydricLayer.name, 1)

        # Update soilmap layer symbology using JSON dictionary
        installInfo = arcpy.GetInstallInfo()
        version = str(installInfo["Version"])

        #if version[0:4] in ["10.3", "10.4", "10.5", "10.6", "10.7", "10.8"]:
        #PrintMsg(" \n\tUpdating hydric map symbology using JSON string", 1)
        # Problem with padded strings returned for hydric_rating

        # Update layer symbology using JSON
        dLayerDefinition = {'drawingInfo': {'renderer': {'uniqueValueInfos': [
            {'symbol': {'color': ['255', '0', '0', 255], 'style': 'esriSFSSolid', 'type': 'esriSFS', 'outline': {'color': [255, 255, 255, 0], 'width': 0.0, 'style': 'esriSLSSolid', 'type': 'esriSLS'}}, 'description': '', 'value': 'Hydric', 'label': 'Hydric'},
            {'symbol': {'color': ['255', '127', '0', 255], 'style': 'esriSFSSolid', 'type': 'esriSFS', 'outline': {'color': [255, 255, 255, 0], 'width': 0.0, 'style': 'esriSLSSolid', 'type': 'esriSLS'}}, 'description': '', 'value': 'Predominantly hydric', 'label': 'Predominantly hydric'},
            {'symbol': {'color': ['255', '255', '0', 255], 'style': 'esriSFSSolid', 'type': 'esriSFS', 'outline': {'color': [255, 255, 255, 0], 'width': 0.0, 'style': 'esriSLSSolid', 'type': 'esriSLS'}}, 'description': '', 'value': 'Partially hydric', 'label': 'Partially hydric'},
            {'symbol': {'color': ['127', '255', '0', 255], 'style': 'esriSFSSolid', 'type': 'esriSFS', 'outline': {'color': [255, 255, 255, 0], 'width': 0.0, 'style': 'esriSLSSolid', 'type': 'esriSLS'}}, 'description': '', 'value': 'Predominantly nonhydric', 'label': 'Predominantly nonhydric'},
            {'symbol': {'color': ['0', '200', '0', 255], 'style': 'esriSFSSolid', 'type': 'esriSFS', 'outline': {'color': [255, 255, 255, 0], 'width': 0.0, 'style': 'esriSLSSolid', 'type': 'esriSLS'}}, 'description': '', 'value': 'Nonhydric', 'label': 'Nonhydric'},
            {'symbol': {'color': ['178', '178', '178', 255], 'style': 'esriSFSSolid', 'type': 'esriSFS', 'outline': {'color': [255, 255, 255, 0], 'width': 0.0, 'style': 'esriSLSSolid', 'type': 'esriSLS'}}, 'description': '', 'value': 'Not rated', 'label': 'Not rated'}],
            'field2': None, 'fieldDelimiter': ', ', 'field1': 'hydric_rating', 'defaultSymbol': None, 'field3': None, 'defaultLabel': None, 'type': 'uniqueValue'}}, 'displayField': 'hydric_rating', 'fields': [{'alias': 'hydric_rating', 'type': 'esriFieldTypeString', 'name': 'hydric_rating'}]}

        #PrintMsg(" \nHydric layer def: " + str(dLayerDefinition), 1)
        hydricLayer.updateLayerFromJSON(dLayerDefinition)

        bLabeled = AddLabels(hydricLayer, labelField, False, 12)


        return hydricLayer

    except MyError, e:
        # Example: raise MyError, "This is an error message"
        PrintMsg(str(e), 2)
        return None

    except:
        errorMsg()
        return None

## ===================================================================================
def TransferInterpData(soilsFC, outputTbl, outputLayerName, outputLayerFile, outputValues, parameterString, creditsString, dLayerDefinition, bFuzzy):
    # Adapted from CreateSoilMap 2019-04-29
    #
    # Get data from table view and write it to the soils featureclass

    try:
        # bVerbose = True
        msg = "Preparing soil map of '" + outputLayerName + "'..."
        arcpy.SetProgressorLabel(msg)
        #PrintMsg("\t" + msg, 0)

        if bVerbose:
            PrintMsg(" \nCurrent function : " + sys._getframe().f_code.co_name, 1)

        hasJoin = False

        # Create initial map layer using MakeQueryTable. Need to add code to make
        # sure that a join doesn't already exist, thus changind field names
        #muDesc = arcpy.Describe(soilsLayer)
        #fc = muDesc.catalogPath
        tblDesc = arcpy.Describe(outputTbl)
        tbl = tblDesc.catalogPath

        # Get properties from dSDV

        dType = dict()
        dType["integer"] = "long"
        dType["string"] = "text"
        dType["datetime"] = "date"
        dType["float"] = "double"
        dType["narrative text"] = "text"  # probably geometry or geography data
        dType["choice"] = "text"

        newFieldName = dSDV["resultcolumnname"]
        newDataType = dType[dSDV["effectivelogicaldatatype"].lower()]
        newFieldSize = dSDV["attributefieldsize"]

        tableList = [soilsFC, outputTbl]
        #joinSQL = os.path.basename(fc) + '.MUKEY = ' + os.path.basename(tbl) + '.MUKEY'

        # Create fieldInfo string
        dupFields = list()
        keyField = os.path.basename(soilsFC) + ".OBJECTID"
        fieldInfo = list()
        sFields = ""
        arcpy.AddField_management(soilsFC, newFieldName, newDataType, "", "", newFieldSize)
        dInterpData = dict() # store interp mapunit values in dictionary

        with arcpy.da.SearchCursor(outputTbl, ["mukey", "interp_dcd"]) as cur:
            for rec in cur:
                mukey, val = rec
                dInterpData[str(mukey)] = val  # table from SDA defines mukey as Integer or Long data type

        with arcpy.da.UpdateCursor(soilsFC, ["mukey", newFieldName]) as cur:
            for rec in cur:
                mukey = str(rec[0])

                if mukey in dInterpData:
                    newrec = [mukey, dInterpData[mukey]]

                else:
                    PrintMsg("\tNo data for mukey " + mukey, 1)
                    newrec = [mukey, None]

                cur.updateRow(newrec)

        return True



    except MyError, e:
        PrintMsg(str(e), 2)
        return False


    except:
        errorMsg()
        return False

#### ===================================================================================
##def ZoomToExtent(inputLayer):
##    # Create layer description string
##    try:
##
##        # zoom to new layer extent
##        #
##        # Describing a map layer extent always returns coordinates in the data frame coordinate system
##        try:
##            # Only the original, input soil shapefile layer will be used to
##            # define the mapscale and extent. The thematic maplayer will fail over to
##            # the next section which will go ahead and set the labels to MUSYM, but
##            # leave the soil map labels turned off.
##
##            # Not sure how this was working, since these coordinates are from
##            # the input layer's CSR, which may not be the same as the Data Frame CSR
##            newExtent = inputLayer.getExtent()
##
##            # Expand the extent by 10%
##            xOffset = (newExtent.XMax - newExtent.XMin) * 0.05
##            yOffset = (newExtent.YMax - newExtent.YMin) * 0.05
##            newExtent.XMin = newExtent.XMin - xOffset
##            newExtent.XMax = newExtent.XMax + xOffset
##            newExtent.YMin = newExtent.YMin - yOffset
##            newExtent.YMax = newExtent.YMax + yOffset
##
##            df.extent = newExtent
##            #dfScale = df.scale
##            #PrintMsg(" \nZoomToExtent Data frame scale is  1:" + Number_Format(df.scale, 0, True), 1)
##
##        except:
##            # Leave labels turned off for thematic map layers
##            errorMsg()
##            return False
##
##        return True
##
##    except MyError, e:
##        # Example: raise MyError, "This is an error message"
##        PrintMsg(str(e), 2)
##        return False
##
##    except:
##        errorMsg()
##        return False
##

## ===================================================================================
def ZoomAndRotateMap(inputLayer, mxd, df):
    # Create layer description string
    try:

        # zoom to new layer extent
        #
        # Describing a map layer extent always returns coordinates in the data frame coordinate system

        # Only the original, input soil shapefile layer will be used to
        # define the mapscale and extent. The thematic maplayer will fail over to
        # the next section which will go ahead and set the labels to MUSYM, but
        # leave the soil map labels turned off.

        # Another method of calculating the extent of the new AOI using data frome coordinates
        # Read the polygon geometry in using the original CSR, but then project to match the data frame CSR
        dfSR = df.spatialReference
        xList = list()
        yList = list()

        with arcpy.da.SearchCursor(inputLayer, ["SHAPE@"]) as cur:
            for rec in cur:
                aoiGeom = rec[0]
                dfGeom = aoiGeom.projectAs(dfSR, tm)
                geomExtent = dfGeom.extent
                xList.append(geomExtent.XMin)
                xList.append(geomExtent.XMax)
                yList.append(geomExtent.YMin)
                yList.append(geomExtent.YMax)

        xMin = min(xList)
        xMax = max(xList)
        yMin = min(yList)
        yMax = max(yList)
        # Get beginning extent
        newExtent = df.extent
        newExtent.XMin = xMin
        newExtent.YMin = yMin
        newExtent.XMax = xMax
        newExtent.YMax = yMax

        xOffset = (newExtent.XMax - newExtent.XMin) * 0.05
        yOffset = (newExtent.YMax - newExtent.YMin) * 0.05
        newExtent.XMin = newExtent.XMin - xOffset
        newExtent.XMax = newExtent.XMax + xOffset
        newExtent.YMin = newExtent.YMin - yOffset
        newExtent.YMax = newExtent.YMax + yOffset

        # Calculate center of display
        xCntr = ( newExtent.XMin + newExtent.XMax ) / 2.0
        yCntr = ( newExtent.YMin + newExtent.YMax ) / 2.0
        dfPoint1 = arcpy.Point(xCntr, yCntr)
        pointGeometry = arcpy.PointGeometry(dfPoint1, dfSR)
        #PrintMsg(" \nOriginal Data Frame Center in " + dfSR.name + ": " + str(xCntr) + ",  " + str(yCntr), 1)

        # Create same point but as Geographic WGS1984
        # Designed to handle dataframe coordinate system datums: NAD1983 or WGS1984.
        #
        outputSR = arcpy.SpatialReference(4326)        # GCS WGS 1984
        env.geographicTransformations = "WGS_1984_(ITRF00)_To_NAD_1983"
        pointGM = pointGeometry.projectAs(outputSR, "")
        pointGM1 = pointGM.firstPoint

        # calculate offset point as 1.0 degrees north
        wgsX1 = pointGM1.X
        wgsY2 = pointGM1.Y + 1.0
        offsetPoint = arcpy.Point(wgsX1, wgsY2)

        # Project north offset back to dataframe coordinate system
        offsetGM = arcpy.PointGeometry(offsetPoint, outputSR)

        dfOffset = offsetGM.projectAs(dfSR, "")
        dfPoint2 = dfOffset.firstPoint
        a = [dfPoint2.X, dfPoint2.Y, 0.0]

        b = [xCntr, yCntr, 0.0]

        c = [xCntr, (yCntr + 1000.0), 0.0]

        #PrintMsg(" \nRotateMap function offset coordinates:: " + str(b) + "\t" +  str(c))

        ba = [ aa-bb for aa, bb in zip(a,b) ]
        bc = [ cc-bb for cc, bb in zip(c,b) ]

        # Normalize vector
        nba = math.sqrt ( sum ( (x**2.0 for x in ba) ) )
        ba = [ x / nba for x in ba ]

        nbc = math.sqrt ( sum ( (x**2.0 for x in bc) ) )
        bc = [ x / nbc for x in bc ]

        # Calculate scalar from normalized vectors
        scale = sum ( (aa*bb for aa, bb in zip(ba,bc)) )

        # calculate the angle in radians
        radians = math.acos(scale)

        # Get the sign
        if (c[0] - a[0]) == 0:
            s = 0

        else:
            s = ( c[0] - a[0] ) / abs(c[0] - a[0])

        angle = s * ( -1.0 * round(math.degrees(radians), 1) )
        df.rotation = angle
        df.extent = newExtent
        #PrintMsg("\tMap rotation: " + str(angle) + " degrees \n ", 0)

        arcpy.RefreshActiveView()

        # A-----C
        # |    /
        # |   /
        # |  /
        # | /
        # |/
        # B

        return True

    except MyError, e:
        # Example: raise MyError, "This is an error message"
        PrintMsg(str(e), 2)
        return False

    except:
        errorMsg()
        return False

## ===================================================================================
def AddLabels(mapLayer, labelField, bLabeled, fontSize):
    # Set layer label properties to use MUSYM
    # Some layers we just want to set the label properties to use MUSYM, but
    # we don't want to display the labels.

    try:

        # Add mapunit symbol (MUSYM) labels
        desc = arcpy.Describe(mapLayer)
        fields = desc.fields
        fieldNames = [fld.name.lower() for fld in fields]

        if not labelField.lower() in fieldNames:
            PrintMsg("\t" + labelField + " not found in " + mapLayer.longName + "  " + ", ".join(fieldNames) + ")", 1)
            return False

        # PrintMsg("\t" + mapLayer.longName  + " using label field: " + labelField, 1)

        if mapLayer.supports("LABELCLASSES"):
            mapLayer.showClassLabels = True
            labelCls = mapLayer.labelClasses[0]
            oldLabel = labelCls.expression

            if fontSize > 0:
                #labelCls.expression = "<BOL> & [" + labelField + "] & </BOL>"
                # "<FNT size= '15'>" & [partname] & "</FNT>"
                s1 = '"<FNT size=' + "'" + str(fontSize) + "'>\""
                s2 = " & [" + labelField + "] & " + '"</FNT>"'
                labelString = '"<FNT size=' + "'" + str(fontSize) + "'>\"" + " & [" + labelField + "] & " + '"</FNT>"'
                labelCls.expression = labelString

            else:
                labelCls.expression = "[" + labelField + "]"

        else:
            PrintMsg(" \n\tLayer " + mapLayer.longName + " does not support labelclasses", 1)


        #mapLayer.showLabels = False

##        if df.scale <= 18000 and bLabeled:
##            #PrintMsg(" \n\tTurning " + mapLayer.name + " labels on at display scale of 1:" + str(Number_Format(df.scale, 0, True)), 1)
##            mapLayer.showLabels = True
##
##        else:
##            #PrintMsg(" \n\tTurning " + mapLayer.name + " labels off at display scale of 1:" + str(Number_Format(df.scale, 0, True)), 1)
##            #mapLayer.showLabels = False
##            mapLayer.showLabels = True

        #PrintMsg(" \nIn AddLabels, the scale is: " + str(df.scale), 1)


        return True

    except MyError, e:
        # Example: raise MyError, "This is an error message"
        PrintMsg(str(e), 2)
        return False

    except:
        errorMsg()
        return False

## ===================================================================================
def SimpleFeaturesJSON(width):
    # returns JSON string for soil lines and labels layer, given the width of the outline
    #
    try:

        outLineColor = [0, 0, 0, 255]  # black polygon outline

        d = dict()
        r = dict()

        r["type"] = "simple"
        s = {"type": "esriSFS", "style": "esriSFSNull", "color": [255,255,255,255], "outline": { "type": "esriSLS", "style": "esriSLSSolid", "color": outLineColor, "width": width }}
        r["symbol"] = s
        d["drawingInfo"]= dict()
        d["drawingInfo"]["renderer"] = r
        return d

    except MyError, e:
        # Example: raise MyError, "This is an error message"
        PrintMsg(str(e), 2)
        return dict()

    except:
        errorMsg()
        return dict()

## ===================================================================================
def UniqueValuesJSON(legendList, drawOutlines, ratingField, bSort):
    # returns Python dictionary for unique values template. Use this for text, choice, vtext.
    #
    # Problem: Feature layer does not display the field name in the table of contents just below
    # the layer name. Possible bug in UpdateLayerFromJSON method?
    try:

        #PrintMsg(" \nCurrent function : " + sys._getframe().f_code.co_name, 1)
        d = dict() # initialize return value


        # Over ride outlines and turn them off since I've created a separate outline layer.
        drawOutlines = False
        waterColor = [64, 101, 235, 255]
        gray = [178, 178, 178, 255]

        if drawOutlines == False:
            outLineColor = [0, 0, 0, 0]

        else:
            outLineColor = [110, 110, 110, 255]


        if bSort:
            legendList.sort()  # this was messing up my ordered legend for interps


        d = dict()
        d["drawingInfo"] = dict()
        d["drawingInfo"]["renderer"] = dict()
        d["fields"] = list()
        d["displayField"] = ratingField  # This doesn't seem to work

        d["drawingInfo"]["renderer"]["fieldDelimiter"] = ", "
        d["drawingInfo"]["renderer"]["defaultSymbol"] = None
        d["drawingInfo"]["renderer"]["defaultLabel"] = None

        d["drawingInfo"]["renderer"]["type"] = "uniqueValue"
        d["drawingInfo"]["renderer"]["field1"] = ratingField
        d["drawingInfo"]["renderer"]["field2"] = None
        d["drawingInfo"]["renderer"]["field3"] = None
        d["displayField"] = ratingField       # This doesn't seem to work
        #PrintMsg(" \n[drawingInfo][renderer][field1]: " + str(d["drawingInfo"]["renderer"]["field1"]) + " \n ",  1)

        # Add new rating field to list of layer fields
        dAtt = dict()
        dAtt["name"] = ratingField
        dAtt["alias"] = ratingField + " alias"
        dAtt["type"] = "esriFieldTypeString"
        d["fields"].append(dAtt)              # This doesn't seem to work

        # Add each legend item to the list that will go in the uniqueValueInfos item
        cnt = 0
        legendItems = list()
        uniqueValueInfos = list()

        for cnt in range(0, len(legendList)):
            rating = legendList[cnt]  # For some reason this is not just the rating value. This is a list containing [label, value, [r,g,b]]
            #PrintMsg("\tLabel: " + rating, 1)

            if rating == 'W':
                # Water symbol
                rgb = [151,219,242,255]
                #PrintMsg(" \nRGB: " + str(rgb), 1)
                legendItems = dict()
                legendItems["value"] = rating
                legendItems["description"] = ""  # This isn't really used unless I want to pull in a description of this individual rating
                legendItems["label"] = rating
                symbol = {"type" : "esriSFS", "style" : "esriSFSSolid", "color" : rgb, "outline" : {"color": waterColor, "width": 1.5, "style": "esriSLSSolid", "type": "esriSLS"}}
                legendItems["symbol"] = symbol
                uniqueValueInfos.append(legendItems)

            if rating == 'Not rated':
                # Gray shade
                rgb = gray
                #PrintMsg(" \nRGB: " + str(rgb), 1)
                legendItems = dict()
                legendItems["value"] = rating
                legendItems["description"] = ""  # This isn't really used unless I want to pull in a description of this individual rating
                legendItems["label"] = rating
                symbol = {"type" : "esriSFS", "style" : "esriSFSSolid", "color" : rgb, "outline" : {"color": outlineColor, "width": 0, "style": "esriSLSSolid", "type": "esriSLS"}}
                legendItems["symbol"] = symbol
                uniqueValueInfos.append(legendItems)

            else:
                # calculate rgb colors
                if ratingField.lower() == "musym":
                    rgb = [randint(0, 255), randint(0, 255), randint(0, 255), 255]  # for random colors

                else:
                    rgb = rating[2]

                #PrintMsg("\n\t" + str(cnt) + ". Rating value: " + str(rating[0]) + "  RGB: " + str(rgb), 1)
                legendItems = dict()
                legendItems["value"] = rating[0]
                legendItems["description"] = ""  # This isn't really used unless I want to pull in a description of this individual rating
                legendItems["label"] = rating[1]
                symbol = {"type" : "esriSFS", "style" : "esriSFSSolid", "color" : rgb, "outline" : {"color": outLineColor, "width": 0.4, "style": "esriSLSSolid", "type": "esriSLS"}}
                legendItems["symbol"] = symbol
                uniqueValueInfos.append(legendItems)

        d["drawingInfo"]["renderer"]["uniqueValueInfos"] = uniqueValueInfos
        #PrintMsg(" \n[drawingInfo][renderer][field1]: " + str(d["drawingInfo"]["renderer"]["field1"]) + " \n ",  1)
        #PrintMsg(" \nuniqueValueInfos: " + str(d["drawingInfo"]["renderer"]["uniqueValueInfos"]), 1)
        #PrintMsg(" \n" + str(d), 1)

        return d

    except MyError, e:
        # Example: raise MyError, "This is an error message"
        PrintMsg(str(e), 2)
        return d

    except:
        errorMsg()
        return d


## ===================================================================================
def CreateJSONLegend(dLegend, outputTbl, outputValues, ratingField, sdvAtt, bFuzzy):
    # This does not work for classes that have a lower_value and upper_value
    #
    try:
        # Input dictionary 'dLegend' contains two other dictionaries:
        #   dLabels[order]
        #    dump sorted dictionary contents into output table

        arcpy.SetProgressorLabel("Creating JSON map legend")
        #bVerbose = True

        if bVerbose:
            PrintMsg(" \nCurrent function : " + sys._getframe().f_code.co_name, 1)

            if ratingField.startswith("interp"):
                # Here are examples of the rating classes for the new Forestry Interps. Use these to test and create new
                # dLegend[name], dSDV[maplegendkey], dLegend[type] and dLegend[labels]

                # [[Slight, Moderate, Severe, Not rated], [Low, Medium, High, Not rated], [Well suited, Moderately suited, Poorly suited, Not suited, Not rated]]
                PrintMsg(" \nThis is an unpublished interpretation layer using '" + ratingField + "' field. Need to create custom legend", 1)

            else:
                PrintMsg(" \nRating field: " + ratingField, 1)
                PrintMsg(str(dLegend), 1)

        # New code to handle unpublished interps that have no xmlmaplegend information
        #
        if ratingField.startswith("interp") and dSDV["attributetype"] == "Interpretation":
            # see if the outputValues match any of the new Forestry Interps
            # For other unpublished interps that have a different set of rating classes,
            # the following dInterps dictionary will have to be modified.
            #
            # I still need to populate the map legend colors. Perhaps use the length of the selected dInterps list?
            #
            bTested = TestLegends(outputValues)

            if bTested == False:
                PrintMsg(" \nFailed to find matching legend for unpublished interp", 1)

        if dLegend is None or len(dLegend) == 0:
            raise MyError, "xxx No Legend"

        # Try adding 'Not rated' to legend here
        if 'Not rated' in outputValues:
            #PrintMsg(" \nAdding 'Not rated' to dLegend", 1)
            labelNum = len(dLegend["labels"]) + 1
            dLegend["labels"][labelNum] = {"order":str(labelNum), "value": 'Not rated', "label":"Not rated"}
            dLegend["colors"][labelNum] = {'blue': '178', 'green': '178', 'red': '178'}

        if bVerbose:
            # Map legend information exists
            PrintMsg(" \ndLegend name: " + dLegend["name"] + ", type: " + str(dLegend["type"]), 1)
            PrintMsg("Effectivelogicaldatatype: " + dSDV["effectivelogicaldatatype"].lower(), 1)
            PrintMsg("Maplegendkey: " + str(dSDV["maplegendkey"]), 1)
            PrintMsg(" \ndLegend labels: " + str(dLegend["labels"]), 1)
            PrintMsg(" \nOutput Values: " + str(outputValues), 1)
            PrintMsg(" \nNumber of outputValues: " + str(len(outputValues)) + " and number of dLegend labels: " + str(len(dLegend["labels"])), 1)

        bBadLegend = False

        if len(dLegend["labels"]) > 0 and dSDV["effectivelogicaldatatype"].lower() == "choice":
            # To address problem with Farmland Class where map legend values do not match actual data values, let's
            # try comparing the two.
            legendLabels = list()
            missingValues = list()
            badLabels = list()

            for labelIndx, labelItem in dLegend["labels"].items():
                legendLabels.append(labelItem["value"])

            for outputValue in outputValues:
                if not outputValue in legendLabels:
                    #PrintMsg("\tMissing data value (" + outputValue + ") in maplegendxml", 1)
                    bBadLegend = True
                    missingValues.append(outputValue)

            for legendLabel in legendLabels:
                if not legendLabel in outputValues:
                    #PrintMsg("\tLegend label not present in data (" + legendLabel + ")", 1)
                    bBadLegend = True
                    badLabels.append(legendLabel)

        legendList = list()  # Causing 'No data available for' error

        # Let's try checking the map information. If Random colors and nothing is set for map legend info,
        # bailout and let the next function handle this layer
        if dLegend["name"] == "Random" and len(dLegend["colors"]) == 0 and len(dLegend["labels"]) == 0:
            #PrintMsg(" \n\tNo map legend information available", 1)
            return dict()


        #PrintMsg("\tdSDV values: " + dSDV["effectivelogicaldatatype"].lower() + "; " + str(dSDV["maplegendkey"]), 1)
        #PrintMsg("\tdLegend name: '" + dLegend["name"] + "'", 1)

        # Problem creating legendList 4 error with the following parameters for 'Agricultural Organic Soil Subsidence'
        #Calling GetMapLegend 1643 in RunSDA_Queries
	#dSDV values: string              ; 5
	#dLegend name: Defined

        if dLegend["name"] == "Progressive":
            #PrintMsg(" \nLegend name: " + dLegend["name"] + " for " + sdvAtt, 1)

            if dSDV["maplegendkey"] in [3] and dSDV["effectivelogicaldatatype"].lower() in ['choice', 'string', 'vtext']:
                # This would be for text values using Progressive color ramp
                #

                #if dSDV["effectivelogicaldatatype"].lower() in ['choice', 'string', 'vtext']:

                legendList = list()

                numItems = sorted(dLegend["colors"])  # returns a sorted list of legend item numbers

                if len(numItems) == 0:
                    raise MyError, "dLegend has no color information"

                for item in numItems:
                    #PrintMsg("\t" + str(item), 1)

                    try:
                        # PrintMsg("Getting legend info for legend item #" + str(item), 1)
                        rgb = [dLegend["colors"][item]["red"], dLegend["colors"][item]["green"], dLegend["colors"][item]["blue"], 255]
                        rgb = [int(c) for c in rgb]
                        rating = dLegend["labels"][item]["value"]
                        legendLabel = dLegend["labels"][item]["label"]
                        legendList.append([rating, legendLabel, rgb])
                        #PrintMsg(str(item) + ". '" + str(rating) + "',  '" + str(legendLabel) + "'", 1)

                    except:
                        errorMsg()

            elif dSDV["maplegendkey"] in [3, 7] and dSDV["effectivelogicaldatatype"].lower() in ["float", "integer", "choice"]:  #
                PrintMsg(" \nCheck Maplegendkey for 7: " + str(dSDV["maplegendkey"]), 1)

                if "labels" in dLegend and len(dLegend["labels"]) > 0:
                    # Progressive color ramp for numeric values

                    # Get the upper and lower colors
                    upperColor = dLegend["UpperColor"]
                    lowerColor = dLegend["LowerColor"]

                    if outputValues and dSDV["effectivelogicaldatatype"].lower() == "choice":
                        # Create uppercase version of outputValues
                        dUpper = dict()
                        for val in outputValues:
                            dUpper[str(val).upper()] = val

                    # 4. Assemble all required legend information into a single, ordered list
                    legendList = list()
                    #PrintMsg(" \ndRatings: " + str(dRatings), 1)

                    # For NCCPI with maplegendkey = 3 and type = 1, labels is an ordered list of label numbers
                    labels = sorted(dLegend["labels"])  # returns a sorted list of legend items

                    valueList = list()

                    if dLegend["type"] != "1":   # Not NCCPI

                        for item in labels:
                            try:
                                #PrintMsg("Getting legend info for legend item #" + str(item), 1)
                                rating = dLegend["labels"][item]["value"]
                                legendLabel = dLegend["labels"][item]["label"]

                                if not rating in outputValues and rating.upper() in dUpper:
                                    # if the legend contains a value that has a case mismatch, update the
                                    # legend to match what is in outputValues
                                    #PrintMsg(" \nUpdating legend value for " + rating, 1)
                                    rating = dUpper[rating.upper()]
                                    legendLabel = rating
                                    dLegend["labels"][item]["label"] = rating
                                    dLegend["labels"][item]["value"] = rating

                                legendList.append([rating, legendLabel])
                                #PrintMsg("Getting legend value for legend item #" + str(item) + ": " + str(rating), 1)

                                if not rating in valueList:
                                    valueList.append(rating)

                            except:
                                errorMsg()

                    elif dLegend["type"] == "1": # This is NCCPI v3 or NirrCapClass?? Looks like this would overwrite the NCCPI legend labels??


                        for item in labels:
                            try:
                                rating = dLegend["labels"][item]["value"]
                                legendLabel = dLegend["labels"][item]["label"]

                                if not rating in outputValues and rating.upper() in dUpper:
                                    # if the legend contains a value that has a case mismatch, update the
                                    # legend to match what is in outputValues
                                    #PrintMsg(" \nUpdating legend value for " + rating, 1)
                                    rating = dUpper[rating.upper()]
                                    legendLabel = rating
                                    dLegend["labels"][item]["label"] = rating
                                    dLegend["labels"][item]["value"] = rating

                                legendList.append([rating, legendLabel])
                                #PrintMsg("Getting legend value for legend item #" + str(item) + ": " + str(rating), 1)

                                if not rating in valueList:
                                    valueList.append(rating)

                            except:
                                errorMsg()

                    if len(valueList) == 0:
                        raise MyError, "No value data for " + sdvAtt

                    else:
                        dColors = ColorRamp(dLegend["labels"], lowerColor, upperColor)

                    # Open legendList back up and add rgb colors
                    #PrintMsg(" \ndColors" + str(dColors) + " \n ", 1)

                    for cnt, clr in dColors.items():
                        rgb = [clr["red"], clr["green"], clr["blue"], 255]
                        rbg = [int(c) for c in rgb]
                        item = legendList[cnt - 1]
                        #item = legendList[cnt - 1]
                        item.append(rgb)
                        #PrintMsg(str(cnt) + ". '" + str(item) + "'", 0)
                        legendList[cnt - 1] = item
                        #PrintMsg(str(cnt) + ". '" + str(item) + "'", 1)


            elif dSDV["maplegendkey"] in [6]:
                #
                if "labels" in dLegend:
                    # This legend defines a number of labels with upper and lower values, along
                    # with an UpperColor and a LowerColor ramp.
                    # examples: component slope_r, depth to restrictive layer
                    # Use the ColorRamp function to create the correct number of progressive colors
                    legendList = list()
                    PrintMsg(" \ndRatings: " + str(dRatings), 1)
                    PrintMsg(" \ndLegend: " + str(dLegend), 1)
                    numItems = len(dLegend["labels"]) # returns a sorted list of legend item numbers. Fails for NCCPI v2

                    # 'LowerColor': {0: (255, 0, 0), 1: (255, 255, 0), 2: (0, 255, 255)}
                    lowerColor = dLegend["LowerColor"]
                    upperColor = dLegend["UpperColor"]

                    valueList = list()
                    dLegend["colors"] = ColorRamp(dLegend["labels"], lowerColor, upperColor)
                    #PrintMsg(" \ndLegend colors: " + str(dLegend["colors"]), 1)

                    if dLegend is None or len(dLegend["colors"]) == 0:
                        raise MyError, "xxx No Legend"

                    for item in range(1, numItems + 1):
                        try:
                            #PrintMsg("Getting legend info for legend item #"  + str(item) + ": " + str(dLegend["colors"][item]), 1)
                            #rgb = dLegend["colors"][item]
                            rgb = [dLegend["colors"][item]["red"], dLegend["colors"][item]["green"], dLegend["colors"][item]["blue"], 255]
                            rgb = [int(c) for c in rgb]
                            maxRating = dLegend["labels"][item]['upper_value']
                            minRating = dLegend["labels"][item]['lower_value']
                            valueList.append(dLegend["labels"][item]['upper_value'])
                            valueList.append(dLegend["labels"][item]['lower_value'])

                            #rating = dLegend["labels"][item]["value"]
                            if item == 1 and dSDV["attributeuomabbrev"] is not None:
                                legendLabel = dLegend["labels"][item]["label"] + " " + str(dSDV["attributeuomabbrev"])

                            else:
                                legendLabel = dLegend["labels"][item]["label"]

                            legendList.append([minRating, maxRating, legendLabel, rgb])
                            #PrintMsg(str(item) + ". '" + str(minRating) + "',  '" + str(maxRating) + "',  '" + str(legendLabel) + "'", 1)

                        except:
                            errorMsg()

                    if len(valueList) == 0:
                        raise MyError, "No data"

                    minValue = min(valueList)

                else:
                    # no "labels" in dLegend
                    # NCCPI version 2
                    # Legend Name:Progressive Type 1 MapLegendKey 6, float
                    #
                    PrintMsg(" \nThis section is designed to handle NCCPI version 2.0. No labels for the map legend", 1)
                    legendList = []



            else:
                # Maplegendkey test
                # Logic not defined for this type of map legend
                #
                raise MyError, "Problem creating legendList for: " + dLegend["name"] + "; maplegendkey " +  str(dSDV["maplegendkey"])  # Added the 3 to test for NCCPI. That did not help.


        elif dLegend["name"] == "Defined":
            #PrintMsg(" \nLegend name: " + dLegend["name"] + " for " + sdvAtt, 1)

            if dSDV["effectivelogicaldatatype"].lower() in ["integer", "float"]:  # works for Hydric (Defined, integer with maplegendkey=1)

                if dSDV["maplegendkey"] == 1:
                    # Hydric,
                    #PrintMsg(" \ndLegend for Defined, " + dSDV["effectivelogicaldatatype"].lower() + ", maplegendkey=" + str(dSDV["maplegendkey"]) + ": \n" + str(dLegend), 1)
                    # {1: {'blue': '0', 'green': '0', 'red': '255'}, 2: {'blue': '50', 'green': '204', 'red': '50'}, 3: {'blue': '154', 'green': '250', 'red': '0'}, 4: {'blue': '0', 'green': '255', 'red': '127'}, 5: {'blue': '0', 'green': '255', 'red': '255'}, 6: {'blue': '0', 'green': '215', 'red': '255'}, 7: {'blue': '42', 'green': '42', 'red': '165'}, 8: {'blue': '113', 'green': '189', 'red': '183'}, 9: {'blue': '185', 'green': '218', 'red': '255'}, 10: {'blue': '170', 'green': '178', 'red': '32'}, 11: {'blue': '139', 'green': '139', 'red': '0'}, 12: {'blue': '255', 'green': '255', 'red': '0'}, 13: {'blue': '180', 'green': '130', 'red': '70'}, 14: {'blue': '255', 'green': '191', 'red': '0'}}

                    # 4. Assemble all required legend information into a single, ordered list
                    legendList = list()
                    #PrintMsg(" \ndRatings: " + str(dRatings), 1)
                    numItems = sorted(dLegend["colors"])  # returns a sorted list of legend item numbers
                    valueList = list()

                    for item in numItems:
                        try:
                            #PrintMsg("Getting legend info for legend item #" + str(item), 1)
                            rgb = [dLegend["colors"][item]["red"], dLegend["colors"][item]["green"], dLegend["colors"][item]["blue"], 255]
                            rgb = [int(c) for c in rgb]
                            maxRating = dLegend["labels"][item]['upper_value']
                            minRating = dLegend["labels"][item]['lower_value']
                            valueList.append(dLegend["labels"][item]['upper_value'])
                            valueList.append(dLegend["labels"][item]['lower_value'])

                            #rating = dLegend["labels"][item]["value"]
                            legendLabel = dLegend["labels"][item]["label"]
                            legendList.append([minRating, maxRating, legendLabel, rgb])

                            #PrintMsg(str(item) + ". '" + str(minRating) + "',  '" + str(maxRating) + "',  '" + str(legendLabel) + "'", 1)

                        except:
                            errorMsg()

                    if len(valueList) == 0:
                        raise MyError, "No data"
                    minValue = min(valueList)

                else:
                    # integer values
                    #
                    #PrintMsg(" \ndLegend for Defined, " + dSDV["effectivelogicaldatatype"].lower() + ", maplegendkey=" + str(dSDV["maplegendkey"]) + ": \n" + str(dLegend), 1)

                    # {1: {'blue': '0', 'green': '0', 'red': '255'}, 2: {'blue': '50', 'green': '204', 'red': '50'}, 3: {'blue': '154', 'green': '250', 'red': '0'}, 4: {'blue': '0', 'green': '255', 'red': '127'}, 5: {'blue': '0', 'green': '255', 'red': '255'}, 6: {'blue': '0', 'green': '215', 'red': '255'}, 7: {'blue': '42', 'green': '42', 'red': '165'}, 8: {'blue': '113', 'green': '189', 'red': '183'}, 9: {'blue': '185', 'green': '218', 'red': '255'}, 10: {'blue': '170', 'green': '178', 'red': '32'}, 11: {'blue': '139', 'green': '139', 'red': '0'}, 12: {'blue': '255', 'green': '255', 'red': '0'}, 13: {'blue': '180', 'green': '130', 'red': '70'}, 14: {'blue': '255', 'green': '191', 'red': '0'}}

                    # 4. Assemble all required legend information into a single, ordered list
                    legendList = list()
                    #PrintMsg(" \ndRatings: " + str(dRatings), 1)
                    numItems = sorted(dLegend["colors"])  # returns a sorted list of legend item numbers

                    for item in numItems:
                        try:
                            #PrintMsg("Getting legend info for legend item #" + str(item), 1)
                            rgb = [dLegend["colors"][item]["red"], dLegend["colors"][item]["green"], dLegend["colors"][item]["blue"], 255]
                            rating = dLegend["labels"][item]["value"]
                            legendLabel = dLegend["labels"][item]["label"]
                            legendList.append([rating, legendLabel, rgb])
                            #PrintMsg(str(item) + ". '" + str(rating) + "',  '" + str(legendLabel) + "'", 1)

                        except:
                            errorMsg()


            elif dSDV["effectivelogicaldatatype"].lower() in ['choice', 'string', 'vtext']:
                # This would include some of the interps
                #Defined, 2, choice
                # PrintMsg(" \n \ndLegend['colors']: " + str(dLegend["colors"]) + " \n ", 1)
                # {1: {'blue': '0', 'green': '0', 'red': '255'}, 2: {'blue': '50', 'green': '204', 'red': '50'}, 3: {'blue': '154', 'green': '250', 'red': '0'}, 4: {'blue': '0', 'green': '255', 'red': '127'}, 5: {'blue': '0', 'green': '255', 'red': '255'}, 6: {'blue': '0', 'green': '215', 'red': '255'}, 7: {'blue': '42', 'green': '42', 'red': '165'}, 8: {'blue': '113', 'green': '189', 'red': '183'}, 9: {'blue': '185', 'green': '218', 'red': '255'}, 10: {'blue': '170', 'green': '178', 'red': '32'}, 11: {'blue': '139', 'green': '139', 'red': '0'}, 12: {'blue': '255', 'green': '255', 'red': '0'}, 13: {'blue': '180', 'green': '130', 'red': '70'}, 14: {'blue': '255', 'green': '191', 'red': '0'}}

                # 4. Assemble all required legend information into a single, ordered list
                #PrintMsg(" \ndLegend for Defined: " + str(dLegend) + " \n ", 1)

                legendList = list()
                numItems = sorted(dLegend["colors"])  # returns a sorted list of legend item numbers

                if bBadLegend:
                    # Problem with maplegend not matching data. Try replacing original labels and values.

                    for item in numItems:
                        try:
                            #PrintMsg("Getting legend info for legend item #" + str(item), 1)
                            rgb = [dLegend["colors"][item]["red"], dLegend["colors"][item]["green"], dLegend["colors"][item]["blue"], 255]
                            rating = dLegend["labels"][item]["value"]
                            legendLabel = dLegend["labels"][item]["label"]

                            # missingValues contains data values not in legend
                            # badLabels contains legend values not in data

                            if rating in outputValues:
                                # This one is good
                                legendList.append([rating, legendLabel, rgb])
                                #PrintMsg(str(item) + ". '" + str(rating) + "',  '" + str(legendLabel) + "'", 1)

                            else:
                                # This is a badLabel. Replace it with one of the missingValues.
                                if len(missingValues) > 0:
                                    rating = missingValues.pop(0)
                                    legendLabel = rating
                                    legendList.append([rating, legendLabel, rgb])

                        except:
                            errorMsg()

                    #if len(missingValues) > 0:
                    #    PrintMsg("\tFailed to add these data values to the map legend: " + "; ".join(missingValues), 1)

                else:
                    # Maplegendxml is OK. Use legend as is.
                    for item in numItems:
                        try:
                            #PrintMsg(" \n***Getting legend info for legend item #" + str(item), 1)
                            rgb = [dLegend["colors"][item]["red"], dLegend["colors"][item]["green"], dLegend["colors"][item]["blue"], 255]
                            rating = dLegend["labels"][item]["value"]
                            legendLabel = dLegend["labels"][item]["label"]
                            legendList.append([rating, legendLabel, rgb])
                            #PrintMsg(str(item) + ". '" + str(rating) + "',  '" + str(legendLabel) + "'", 1)

                        except:
                            errorMsg()


            else:
                raise MyError, "Problem creating legendList 4 for those parameters"

        elif dLegend["name"] == "Random":
            # This is where I would need to determine whether labels exist. If they do
            # I need to assign random color to each legend item
            #
            #
            # This one has no colors predefined
            # Defined, 2, choice

            # {1: {'blue': '0', 'green': '0', 'red': '255'}, 2: {'blue': '50', 'green': '204', 'red': '50'}, 3: {'blue': '154', 'green': '250', 'red': '0'}, 4: {'blue': '0', 'green': '255', 'red': '127'}, 5: {'blue': '0', 'green': '255', 'red': '255'}, 6: {'blue': '0', 'green': '215', 'red': '255'}, 7: {'blue': '42', 'green': '42', 'red': '165'}, 8: {'blue': '113', 'green': '189', 'red': '183'}, 9: {'blue': '185', 'green': '218', 'red': '255'}, 10: {'blue': '170', 'green': '178', 'red': '32'}, 11: {'blue': '139', 'green': '139', 'red': '0'}, 12: {'blue': '255', 'green': '255', 'red': '0'}, 13: {'blue': '180', 'green': '130', 'red': '70'}, 14: {'blue': '255', 'green': '191', 'red': '0'}}

            if len(dLegend["labels"]) > 0 and len(dLegend["colors"]) == 0:
                # Same as dLegend["type"] == "0": ????
                # 4. Assemble all required legend information into a single, ordered list
                # Capability Subclass dLegend:
                # dLegend: {'colors': {}, 'labels': {1: {'order': '1', 'value': 'e', 'label': 'Erosion'}, 2: {'order': '2', 'value': 's', 'label': 'Soil limitation within the rooting zone'}, 3: {'order': '3', 'value': 'w', 'label': 'Excess water'}, 4: {'order': '4', 'value': 'c', 'label': 'Climate condition'}}, 'type': '0', 'name': 'Random', 'maplegendkey': '8'}
                #
                legendList = list()
                labels = dLegend["labels"]  # returns a dictionary of label information
                numItems = len(labels) + 1
                rgbColors = rand_rgb_colors(numItems)
                #numItems += 1

                for i in range(1, numItems):
                    try:
                        #PrintMsg("Getting legend info for legend item #" + str(item), 1)
                        #
                        # Either this next line needs to get a random color or I need to generate a list of random colors for n-labels
                        #rgb = [dLegend["colors"][item]["red"], dLegend["colors"][item]["green"], dLegend["colors"][item]["blue"], 255]
                        rgb = rgbColors[i]
                        rating = dLegend["labels"][i]["value"]
                        legendLabel = dLegend["labels"][i]["label"]
                        legendList.append([rating, legendLabel, rgb])
                        #PrintMsg(str(i) + ". '" + str(rating) + "',  '" + str(legendLabel) + "',   rgb: " + str(rgb), 1)

                    except:
                        errorMsg()

        else:
            # Logic not defined for this type of map legend
            raise MyError, "Problem creating legendList 2 for those parameters"

        # Not sure what is going on here, but legendList is not right at all for ConsTreeShrub
        #

        # 5. Create layer definition using JSON string

        # Let's try maplegendkey as the driver...
        if dSDV["maplegendkey"] in [1,2,4,5,6,7,8] and len(legendList) == 0:
            PrintMsg("\tNo data available for " + sdvAtt + " \n ", 1)
            #raise MyError, "\tNo data available for " + sdvAtt + " \n "
            raise MyError, "xxx legendList is empty"

        if dSDV["maplegendkey"] in [1]:
            # Integer: only Hydric
            # Can I get Salinity Risk into DefinedBreaksJSON?
            #
            #PrintMsg(" \nGetting Defined Class Breaks as JSON", 1)
            # Missing minValue at this point
            dLayerDef = DefinedBreaksJSON(legendList, minValue, os.path.basename(outputTbl), ratingField)

        elif dSDV["maplegendkey"] in [2]:
            # Choice, Integer: Farmland class, TFactor, Corrosion Steel
            # PrintMsg(" \n2. Getting Unique Values legend as JSON", 1)
            dLayerDef = UniqueValuesJSON(legendList, os.path.basename(outputTbl), ratingField, True)
            #PrintMsg(" \nProblem 2 getting Unique Values legend as JSON", 1)

        elif dSDV["maplegendkey"] in [3]:
            # Float, Integer: numeric soil properties
            #PrintMsg(" \nGetting numeric Class Breaks legend as JSON", 1)
            dLayerDef = ClassBreaksJSON(os.path.basename(outputTbl), outputValues, ratingField, bFuzzy)

        elif dSDV["maplegendkey"] in [4]:
            # VText, String: Unique Values
            # PrintMsg(" \n4. Getting Unique Values legend as JSON", 1)
            dLayerDef = UniqueValuesJSON(legendList, os.path.basename(outputTbl), ratingField, True)

        elif dSDV["maplegendkey"] in [5]:
            # String: Interp rating classes
            #
            # Problem for maplegendkey 5. UniqueValuesJSON does not appear to preserve the order of the legend items.
            # PrintMsg(" \n5. Getting Unique Values legend as JSON: " + str(legendList) + " \n", 1)
            #dLayerDef = UniqueValuesJSON(legendList, os.path.basename(outputTbl), ratingField)
            dLayerDef = UniqueValuesJSON(legendList, outputTbl, ratingField, False)

        elif dSDV["maplegendkey"] in [6]:
            # Float, Integer: pH, Slope, Depth To...
            #PrintMsg(" \nGetting Defined Class Breaks as JSON", 1)
            # Missing minValue at this point
            #

            #
            if "labels" in dLegend:
                dLayerDef = DefinedBreaksJSON(legendList, minValue, os.path.basename(outputTbl), ratingField)

            else:
                dLayerDef = ClassBreaksJSON(os.path.basename(outputTbl), outputValues, ratingField, bFuzzy)

        elif dSDV["maplegendkey"] in [7]:
            # Choice: Capability Class, WEI, Drainage class
            # PrintMsg(" \n7. Getting Unique 'Choice' Values legend as JSON", 1)
            dLayerDef = UniqueValuesJSON(legendList, os.path.basename(outputTbl), ratingField, True)

        elif dSDV["maplegendkey"] in [8]:
            # Random: AASHTO, HSG, NonIrr Subclass
            PrintMsg(" \n8. Getting Unique 'Choice' Values legend as JSON (" + ", ".join(legendList) + ")", 1)
            dLayerDef = UniqueValuesJSON(legendList, os.path.basename(outputTbl), ratingField, True)

        else:
            PrintMsg(" \nCreating dLayerDefinition for " + dLegend["name"] + ", " + str(dSDV["maplegendkey"]) + ", " + dSDV["effectivelogicaldatatype"].lower(), 1)

        return dLayerDef

    except MyError, e:
        PrintMsg(str(e), 2)
        return dict()

    except:
        errorMsg()
        return dict()

## ===================================================================================
def AddFieldMap(aoiShp, gdb, aoiField, mxd, df, landunitName):
    # Add AOI layer with PartName labels to ArcMap display
    #
    try:
        #PrintMsg("\nAdding Land unit map..." + aoiShp, 0)

        # Copy landunit polygons to the output geodatabase
        aoiPolys = os.path.join(gdb, os.path.basename(aoiShp))
        arcpy.CopyFeatures_management(aoiShp, aoiPolys)
        tmpLandunitLayer = "tmpLandunits"

        if arcpy.Exists(aoiPolys):
            if arcpy.Exists(tmpLandunitLayer):
                arcpy.Delete_management(tmpLandunitLayer, "FEATURELAYER")

            boundaryLayerFile = os.path.join(env.scratchFolder, "Landunit_Boundary.lyr")

            if arcpy.Exists(boundaryLayerFile):
                arcpy.Delete_management(boundaryLayerFile)

            bndLayer = arcpy.MakeFeatureLayer_management(aoiPolys, tmpLandunitLayer)
            arcpy.SaveToLayerFile_management(tmpLandunitLayer, boundaryLayerFile, "ABSOLUTE")
            arcpy.Delete_management(tmpLandunitLayer, "FEATURELAYER")
            del tmpLandunitLayer

            aoiLayer = mapping.Layer(boundaryLayerFile)
            dLayerDefinition = SimpleFeaturesJSON(2.0)
            aoiLayer.updateLayerFromJSON(dLayerDefinition)
            aoiLayer.name = landunitName
            #arcpy.Delete_management(bndLayer, "FEATURELAYER")
            #del bndLayer
            bLabeled = AddLabels(aoiLayer, aoiField, True, 16)

            # Moving Zoom and Rotate Display to the AddFieldMap function which runs later
            #
            # Try combining ZoomToExtent and RotateMap functions
            #bZoomed = ZoomToExtent(newLayer)
            #mapAngle, scale = RotateMap(mxd, df)
            # New function
            bZoomed = ZoomAndRotateMap(aoiLayer, mxd, df)
##
##
##            if df.scale > 12000:
##                aoiLayer.showLabels = False
##
##            else:
##                aoiLayer.showLabels = True

            if arcpy.Exists(boundaryLayerFile):
                arcpy.Delete_management(boundaryLayerFile)

            arcpy.SaveToLayerFile_management(aoiLayer, boundaryLayerFile, "RELATIVE", "10.3")
            aoiLayer = mapping.Layer(boundaryLayerFile)

        else:
            raise MyError, "Failed to create landunit layer (" + aoiShp + ")"

        return aoiLayer

    except MyError, e:
        # Example: raise MyError, "This is an error message"
        PrintMsg(str(e), 2)
        return None

    except:
        errorMsg()
        return None

#### ===================================================================================
##def RotateMap(mxd, df):
##    # ArcMap function. Given mxd and active dataframe
##    #
##    try:
##        dfSR = df.spatialReference
##        rotation = df.rotation
##        extent = df.extent # XMin...
##
##        # Calculate center of display
##        xCntr = ( extent.XMin + extent.XMax ) / 2.0
##        yCntr = ( extent.YMin + extent.YMax ) / 2.0
##        dfPoint1 = arcpy.Point(xCntr, yCntr)
##        pointGeometry = arcpy.PointGeometry(dfPoint1, dfSR)
##
##        # Create same point but as Geographic WGS1984
##        # Designed to handle dataframe coordinate system datums: NAD1983 or WGS1984.
##        #
##        outputSR = arcpy.SpatialReference(4326)        # GCS WGS 1984
##        env.geographicTransformations = "WGS_1984_(ITRF00)_To_NAD_1983"
##        pointGM = pointGeometry.projectAs(outputSR, "")
##        pointGM1 = pointGM.firstPoint
##
##        wgsX1 = pointGM1.X
##        wgsY2 = pointGM1.Y + 1.0
##        offsetPoint = arcpy.Point(wgsX1, wgsY2)
##
##        # Project north offset back to dataframe coordinate system
##        offsetGM = arcpy.PointGeometry(offsetPoint, outputSR)
##
##        dfOffset = offsetGM.projectAs(dfSR, "")
##        dfPoint2 = dfOffset.firstPoint
##        a = [dfPoint2.X, dfPoint2.Y, 0.0]
##
##        b = [xCntr, yCntr, 0.0]
##
##        c = [xCntr, (yCntr + 1000.0), 0.0]
##
##        PrintMsg(" \nRotateMap function offset coordinates:: " + str(b) + "\t" +  str(c))
##
##        angle = 0
##
##        ba = [ aa-bb for aa,bb in zip(a,b) ]
##        bc = [ cc-bb for cc,bb in zip(c,b) ]
##
##        # Normalize vector
##        nba = math.sqrt ( sum ( (x**2.0 for x in ba) ) )
##        ba = [ x/nba for x in ba ]
##
##        nbc = math.sqrt ( sum ( (x**2.0 for x in bc) ) )
##        bc = [ x/nbc for x in bc ]
##
##        # Calculate scalar from normalized vectors
##        scale = sum ( (aa*bb for aa,bb in zip(ba,bc)) )
##
##        # calculate the angle in radian
##        radians = math.acos(scale)
##
##        # Get the sign
##        if (c[0] - a[0]) == 0:
##            s = 0
##
##        else:
##            s = ( c[0] - a[0] ) / abs(c[0] - a[0])
##
##        angle = s * ( -1.0 * round(math.degrees(radians), 1) )
##        df.rotation = angle
##        #arcpy.RefreshActiveView()
##
##        PrintMsg("\tMap rotation: " + str(angle) + " degrees \n ", 0)
##
##        return angle, scale
##
##        # A-----C
##        # |    /
##        # |   /
##        # |  /
##        # | /
##        # |/
##        # B
##
##    except MyError, e:
##        # Example: raise MyError, "This is an error message"
##        PrintMsg(str(e), 2)
##        return 0, 0
##
##    except:
##        errorMsg()
##        return 0, 0
##

## ===================================================================================
def GetMapLegend(dSDV, bFuzzy):
    # Get map legend values and order from maplegendxml column in sdvattribute table
    # Return dLegend dictionary containing contents of XML.

    # Problem with Farmland Classification. It is defined as a choice, but

    try:
        #bVerbose = True  # This function seems to work well, but prints a lot of messages.
        global dLegend
        dLegend = dict()
        dLabels = dict()

        #if bFuzzy and not dSDV["attributename"].startswith("National Commodity Crop Productivity Index"):
        #    # Skip map legend because the fuzzy values will not match the XML legend.
        #    return dict()

        arcpy.SetProgressorLabel("Getting map legend information")

        if bVerbose:
            PrintMsg(" \nCurrent function : " + sys._getframe().f_code.co_name, 1)

        xmlString = dSDV["maplegendxml"]

        #if bVerbose:
        #    PrintMsg(" \nxmlString: " + xmlString + " \n ", 1)

        # Convert XML to tree format
        tree = ET.fromstring(xmlString)

        # Iterate through XML tree, finding required elements...
        i = 0
        dColors = dict()
        legendList = list()
        legendKey = ""
        legendType = ""
        legendName = ""

        # Notes: dictionary items will vary according to legend type
        # Looks like order should be dictionary key for at least the labels section
        #
        for rec in tree.iter():

            if rec.tag == "Map_Legend":
                dLegend["maplegendkey"] = rec.attrib["maplegendkey"]

            if rec.tag == "ColorRampType":
                dLegend["type"] = rec.attrib["type"]
                dLegend["name"] = rec.attrib["name"]

                if rec.attrib["name"] == "Progressive":
                    dLegend["count"] = int(rec.attrib["count"])

            if "name" in dLegend and dLegend["name"] == "Progressive":

                if rec.tag == "LowerColor":
                    # 'part' is zero-based and related to count
                    part = int(rec.attrib["part"])
                    red = int(rec.attrib["red"])
                    green = int(rec.attrib["green"])
                    blue = int(rec.attrib["blue"])
                    #PrintMsg("Lower Color part #" + str(part) + ": " + str(red) + ", " + str(green) + ", " + str(blue), 1)

                    if rec.tag in dLegend:
                        dLegend[rec.tag][part] = (red, green, blue)

                    else:
                        dLegend[rec.tag] = dict()
                        dLegend[rec.tag][part] = (red, green, blue)

                if rec.tag == "UpperColor":
                    part = int(rec.attrib["part"])
                    red = int(rec.attrib["red"])
                    green = int(rec.attrib["green"])
                    blue = int(rec.attrib["blue"])
                    #PrintMsg("Upper Color part #" + str(part) + ": " + str(red) + ", " + str(green) + ", " + str(blue), 1)

                    if rec.tag in dLegend:
                        dLegend[rec.tag][part] = (red, green, blue)

                    else:
                        dLegend[rec.tag] = dict()
                        dLegend[rec.tag][part] = (red, green, blue)


            if rec.tag == "Labels":
                order = int(rec.attrib["order"])

                if dSDV["attributelogicaldatatype"].lower() == "integer":
                    # get dictionary values and convert values to integer
                    try:
                        val = int(rec.attrib["value"])
                        label = rec.attrib["label"]
                        rec.attrib["value"] = val
                        dLabels[order] = rec.attrib

                    except:
                        upperVal = int(rec.attrib["upper_value"])
                        lowerVal = int(rec.attrib["lower_value"])
                        rec.attrib["upper_value"] = upperVal
                        rec.attrib["lower_value"] = lowerVal
                        dLabels[order] = rec.attrib

                elif dSDV["attributelogicaldatatype"].lower() == "float" and not bFuzzy:
                    # get dictionary values and convert values to float
                    try:
                        val = float(rec.attrib["value"])
                        label = rec.attrib["label"]
                        rec.attrib["value"] = val
                        dLabels[order] = rec.attrib

                    except:
                        upperVal = float(rec.attrib["upper_value"])
                        lowerVal = float(rec.attrib["lower_value"])
                        rec.attrib["upper_value"] = upperVal
                        rec.attrib["lower_value"] = lowerVal
                        dLabels[order] = rec.attrib

                else:
                    dLabels[order] = rec.attrib   # for each label, save dictionary of values

            if rec.tag == "Color":
                # Save RGB Colors for each legend item

                # get dictionary values and convert values to integer
                red = int(rec.attrib["red"])
                green = int(rec.attrib["green"])
                blue = int(rec.attrib["blue"])
                dColors[order] = rec.attrib

            if rec.tag == "Legend_Elements":
                try:
                    dLegend["classes"] = rec.attrib["classes"]   # save number of classes (also is a dSDV value)

                except:
                    pass

        # Add the labels dictionary to the legend dictionary
        dLegend["labels"] = dLabels
        dLegend["colors"] = dColors

        # Test iteration methods on dLegend
        #PrintMsg(" \n" + dSDV["attributename"] + " Legend Key: " + dLegend["maplegendkey"] + ", Type: " + dLegend["type"] + ", Name: " + dLegend["name"] , 1)

        if bVerbose:
            PrintMsg(" \n" + dSDV["attributename"].strip() + "; MapLegendKey: " + dLegend["maplegendkey"] + ",; Type: " + dLegend["type"] , 1)

            for order, vals in dLabels.items():
                PrintMsg("\tNew " + str(order) + ": ", 1)

                for key, val in vals.items():
                    PrintMsg("\t\t" + str(order) + ". " + key + ": " + str(val), 1)

                try:
                    r = int(dColors[order]["red"])
                    g = int(dColors[order]["green"])
                    b = int(dColors[order]["blue"])
                    rgb = (r,g,b)
                    PrintMsg("\t\tRGB: " + str(rgb), 1)

                except:
                    pass

        if bVerbose:
            PrintMsg(" \ndLegend: " + str(dLegend), 1)

        return dLegend

    except MyError, e:
        # Example: raise MyError, "This is an error message"
        PrintMsg(str(e), 2)
        return dict()

    except:
        errorMsg()
        return dict()

## ===================================================================================
def GetValuesFromLegend(dLegend):
    # return list of legend values from dLegend (XML source)
    # modify this function to use uppercase string version of values

    try:
        legendValues = list()

        if len(dLegend) > 0:
            pass
            #dLabels = dLegend["labels"] # dictionary containing just the label properties such as value and labeltext Now a global

        else:

            PrintMsg(" \nChanging legend name to 'Progressive'", 1)
            PrintMsg(" \ndLegend: " + str(dLegend["name"]), 1)
            legendValues = list()
            #dLegend["name"] = "Progressive"  # bFuzzy
            dLegend["type"] = "1"

        labelCnt = len(dLabels)     # get count for number of legend labels in dictionary

        #if not dLegend["name"] in ["Progressive", "Defined"]:
        # Note: excluding defined caused error for Interp DCD (Haul Roads and Log Landings)

        if not dLegend["name"] in ["Progressive", "Defined"]:
            # example AASHTO Group Classification
            legendValues = list()      # create empty list for label values

            for order in range(1, (labelCnt + 1)):
                #legendValues.append(dLabels[order]["value"].title())
                legendValues.append(dLabels[order]["value"])

                if bVerbose:
                    PrintMsg("\tAdded legend value #" + str(order) + " ('" + dLabels[order]["value"] + "') from XML string", 1)

        elif dLegend["name"] == "Defined":
            #if dSDV["attributelogicaldatatype"].lower() in ["string", "choice]:
            # Non-numeric values
            for order in range(1, (labelCnt + 1)):
                try:
                    # Hydric Rating by Map Unit
                    legendValues.append(dLabels[order]["upper_value"])
                    legendValues.append(dLabels[order]["lower_value"])

                except:
                    # Other Defined such as 'Basements With Dwellings', 'Land Capability Class'
                    legendValues.append(dLabels[order]["value"])

        return legendValues

    except:
        errorMsg()
        return []

## ===================================================================================
## ===================================================================================
## MAIN
## ===================================================================================

# Import system modules
import sys, string, os, arcpy, locale, traceback, urllib2, httplib, socket, json, copy
import xml.etree.cElementTree as ET
# subprocess, collections, webbrowser

from arcpy import env
from copy import deepcopy
from random import randint

try:
    # Read input parameters
    inputAOI = arcpy.GetParameterAsText(0)                  # input AOI feature layer
    featureCnt = arcpy.GetParameter(1)                      # String. Number of polygons selected of total features in the AOI featureclass.
    outputLocation = arcpy.GetParameterAsText(2)            # Main folder where output tables and featureclasses may be stored
    bCartQueries = arcpy.GetParameter(3)                    # Return landunit-CART ratings
    bInterpQueries = arcpy.GetParameter(4)                  # Run Interp Query section and add to request
    bSpatial = arcpy.GetParameter(5)                        # Return soil polygon geometry
    bSaveQuery = arcpy.GetParameter(6)                      # Display system messages

    # For demonstration purposes...
    bVerbose = False
    bDiagnosticQuery = False

    from arcpy import mapping
    mxd = mapping.MapDocument("CURRENT")
    df = mxd.activeDataFrame

    sdaURL = r"https://sdmdataaccess.sc.egov.usda.gov"  # as of 2019-01-09 this URL is not working. Switched to the following...
    #sdaURL = r"https://sdmdataaccess.nrcs.usda.gov"
    #sdaURL = r"https://sdmdataaccess-dev.dev.sc.egov.usda.gov"
    PrintMsg(" \nUsing Soil Data Access service at: " + sdaURL, 0)

    #outputZipfile = r"c:\temp"
    bClean = False  # hardcode this for now
    timeOut = 0
    env.overwriteOutput = True  # See if this stops the loss of interp maps from prior runs. HydricSoilMap is the only survivor.
    env.addOutputsToMap = False

    # Check scratch geodatabase setting
    if os.path.basename(env.scratchGDB) == "Default.gdb":
        # Don't want to write to that geodatabase
        # Create a new one just for this script
        scratchGDB = os.path.join(env.scratchFolder, "scratch.gdb")

        if not arcpy.Exists(scratchGDB):
            arcpy.CreateFileGDB_management(os.path.dirname(scratchGDB), os.path.basename(scratchGDB), "10.0")
            env.scratchGDB = scratchGDB

        else:
            env.scratchGDB = scratchGDB


    # Commonly used EPSG numbers
    epsgWM = 3857 # Web Mercatur
    epsgWGS84 = 4326 # GCS WGS 1984
    epsgNAD83 = 4269 # GCS NAD 1983
    epsgAlbers = 102039 # USA_Contiguous_Albers_Equal_Area_Conic_USGS_version
    #tm = "WGS_1984_(ITRF00)_To_NAD_1983"  # datum transformation supported by this script

    # Get geographic coordinate system information for input and output layers
    validDatums = ["D_WGS_1984", "D_North_American_1983"]
    sdaCS = arcpy.SpatialReference(epsgWGS84)
    desc = arcpy.Describe(inputAOI)
    aoiCS = desc.spatialReference
    aoiName = os.path.basename(desc.nameString)

    if not aoiCS.GCS.datumName in validDatums:
        raise MyError, "AOI coordinate system not supported: " + aoiCS.name + ", " + aoiCS.GCS.datumName

    if aoiCS.GCS.datumName == "D_WGS_1984":
        tm = ""  # no datum transformation required
        #PrintMsg("\tNo datum transformation necessary", 0)

    elif aoiCS.GCS.datumName == "D_North_American_1983":
        tm = "WGS_1984_(ITRF00)_To_NAD_1983"
        #PrintMsg("\tApplying datum transformation: " + tm, 0)

    else:
        raise MyError, "AOI CS datum name: " + aoiCS.GCS.datumName

    # Determine whether
    if aoiCS.PCSName != "":
        # AOI layer has a projected coordinate system, so geometry will always have to be projected
        bProjected = True
        #PrintMsg(" \n\tAOI coordinate system: " + aoiCS.PCSName, 1)

    elif aoiCS.GCS.name != sdaCS.GCS.name:
        # AOI must be Geographic NAD 1983
        bProjected = True
        #PrintMsg(" \n\tAOI coordinate system: " + aoiCS.GCS.name, 1)

    else:
        bProjected = False

    # I stuck this over-ride into the script because I was ending up with datum-shift slivers
    bProjected = False



    # Define temporary featureclasses for AOI
    # Later on move it to the gdb after it has been created
    #tmpFolder = env.scratchFolder
    aoiShp = os.path.join(env.scratchGDB, "myAoi")

    if arcpy.Exists(aoiShp):
        arcpy.Delete_management(aoiShp, "FEATURECLASS")

    if arcpy.Exists(aoiShp):
        raise MyError, "Failed to delete previous AOI layer"

    bAOI = CreateAOILayer(inputAOI, bClean, aoiShp)

    if bAOI == False:
        raise MyError, "Problem processing landunit layer"

    # Look for PLU_ID in the inputAOI fields.
    aoiDesc = arcpy.Describe(inputAOI)
    aoiFields = aoiDesc.fields
    aoiFldNames = [f.baseName.upper() for f in aoiFields]
    #PrintMsg(" \naoiShp fields: " + ", ".join(aoiFldNames), 1)

    # Capture PLU_ID if it exists in the inputAOI layer

    if "PLU_ID" in aoiFldNames:
        pluList = list()

        with arcpy.da.SearchCursor(inputAOI, ["PLU_ID"]) as cur:
            for rec in cur:
                pluID = rec[0]

                if not pluID is None and not pluID == "" and not pluID in pluList:
                    pluList.append(str(pluID))

        if len(pluList) == 0:
            pluID = None

        elif len(pluList) == 1:
            pluID = pluList[0]

        else:
            pluID = "_".join(pluList)

    else:
        pluID = ""

    if not pluID is None and pluID != "":
        PrintMsg(" \nPLU_ID: " + pluID, 1)

    # Turn off the original AOI layer so that the highlighted polygons dont' clutter up the display
    selLayer = mapping.ListLayers(mxd, inputAOI, df)[0]
    selLayer.visible = False

    # Turn off other Soil Maps group layers to reduce display flashing effect
    layers = mapping.ListLayers(mxd, "*", df)
    choices = list()

    for lyr in layers:

        if lyr.isGroupLayer and lyr.name.startswith("Soil Maps "):
            lyr.visible = False


    # Get ordered list of part names or LU_ID
    luDesc = arcpy.Describe(aoiShp)
    luFields = luDesc.fields
    luFldNames = [f.baseName.upper() for f in luFields]
    landunits = list()

    if "LANDUNIT" in luFldNames:

        # Create an ordered list of landunits
        with arcpy.da.SearchCursor(aoiShp, ["landunit"]) as cur:
            for rec in cur:
                if not str(rec[0]) in landunits:
                    landunits.append(str(rec[0]).replace("\n", "").replace(" ", ""))

        PrintMsg(" \nList of selected Landunits: " + ", ".join(landunits), 0)


    # Setup output location

    if pluID is not None and pluID != "":
        # create folder name based upon planned landunit value(s) from PLU_ID
        outputLocation = os.path.join(outputLocation, "CART_PLU" + pluID)

        if len(landunits) > 0:
            gdb = os.path.join(outputLocation, "Soils_" + "_".join(landunits) + ".gdb")

        else:
            gdb = os.path.join(outputLocation, "Soils_PLU" + pluID + ".gdb")

    elif len(landunits) > 0:
        # create folder name based upon landunit value(s)
        outputLocation = os.path.join(outputLocation, "CART_" + "_".join(landunits))
        gdb = os.path.join(outputLocation, "Soils_" + "_".join(landunits) + ".gdb")

    else:
        outputLocation = os.path.join(outputLocation, "CART")
        i = 0
        gdb = os.path.join(outputLocation, "Soils_AOI.gdb")

        while arcpy.Exists(gdb):
            i += 1
            gdb = gdb.replace(".", str(i) + ".")

    # Check to make sure that the output subfolder and geodatabase don't exceed 160 characters
    # Not sure why it is failing at this length.

    if len(os.path.basename(gdb)) > 160:
        PrintMsg(" \nOutput folder: " + outputLocation + "  (" + str(len(os.path.basename(outputLocation))) + " chars)", 1)
        PrintMsg(" \nOutput database: " + os.path.basename(gdb) + "  (" + str(len(os.path.basename(gdb))) + " chars)", 1)
        raise MyError, "Length of output geodatabase name (" + os.path.basename(gdb) + ") exceeds operating system length"

    if len(os.path.basename(outputLocation)) > 160:
        PrintMsg(" \nOutput folder: " + outputLocation + "  (" + str(len(os.path.basename(outputLocation))) + " chars)", 1)
        PrintMsg(" \nOutput database: " + os.path.basename(gdb) + "  (" + str(len(os.path.basename(gdb))) + " chars)", 1)
        raise MyError, "Length of output folder name (" + os.path.basename(outputLocation) + ") exceeds operating system length"

    PrintMsg(" \nOutput folder: " + outputLocation, 0)
    PrintMsg(" \nOutput database: " + os.path.basename(gdb), 0)

    # Create output location and geodatabase
    if not arcpy.Exists(outputLocation):
        # Create new subfolder AND the new geodatabase
        arcpy.CreateFolder_management(os.path.dirname(outputLocation), os.path.basename(outputLocation))
        arcpy.CreateFileGDB_management(os.path.dirname(gdb), os.path.basename(gdb))

    else:
        # Subfolder already exists, see if the geodatabase also exists and try to overwrite it.

        if arcpy.Exists(gdb):
            try:
                arcpy.Delete_management(gdb)
                #arcpy.Delete_management(outputLocation)

            except:
                raise MyError, "Unable to delete existing geodatabase: " + gdb

        #arcpy.CreateFolder_management(os.path.dirname(outputLocation), os.path.basename(outputLocation))
        arcpy.CreateFileGDB_management(os.path.dirname(gdb), os.path.basename(gdb))

    env.workspace = gdb
    outputLocation = os.path.dirname(gdb)

    # End of setup output location

    # Define Group Layer name
    if pluID is not None and pluID != "":
        grpLayerName = "Soil Maps for PLU" + pluID
        bParts = True
        soilLayerName = "Soil Lines and Labels"
        landunitName = "Planned Land Units"

    elif len(landunits) > 0:
        grpLayerName = "Soil Maps for " + ", ".join(landunits)
        bParts = True
        soilLayerName = "Soil Lines and Labels"
        landunitName = "Landunits"

    else:
        # I will need to test this option so that non-PLU or non-CLU Boundaries will still be added
        grpLayerName = "Soil Maps"
        bParts = False
        soilLayerName = "Soil Lines and Labels"
        landunitName = "Landunits"


    # Make sure that the
    # Check for existing group layer and remove if found
    #layerList = mapping.ListLayers(mxd, grpLayerName, df)

    sQuery = FormSDA_Queries(aoiShp)

    if sQuery != "":
        # Send spatial query and use results to populate outputShp featureclass
        # Return list of table views that were used to create interp maps

        # Run all queries and generate tables, featureclasses
        tableList = RunSDA_Queries(sdaURL, sQuery, gdb)
        #PrintMsg(" \ntableList: " + ", ".join(tableList), 0)

        if len(tableList) == 0:
            arcpy.Delete_management(gdb)
            #arcpy.Delete_management(outputLocation)
            raise MyError, ""

        if bSpatial:
            grpLayer = CreateGroupLayer(grpLayerName)
            mapping.AddLayer(df, grpLayer, "TOP")

            grpLayer = mapping.ListLayers(mxd, grpLayerName, df)[0]   # unable to add layers to grpLayer unless I reset it
            grpDesc = arcpy.Describe(grpLayer)

            # Try creating a temporary soils featurelayer that will be used to create the initial layer file and then immediately
            # removed afterwards
            tmpSoils = "tmpSoilsFC"

            if grpDesc.dataType.lower() != "grouplayer":
                raise MyError, "Problem with group layer"

            soilFCName = "SoilMap_by_Landunit"
            soilsLayerFile = os.path.join(env.scratchFolder, "SoilMap_Layer.lyr")  # Base soils layer

        if bSpatial and soilFCName in tableList:
            soilsFC = os.path.join(gdb, soilFCName)

            if arcpy.Exists(tmpSoils):
                arcpy.Delete_management(tmpSoils, "FEATURELAYER")

            tmpSoilsLayer = arcpy.MakeFeatureLayer_management(soilsFC, tmpSoils)
            arcpy.SaveToLayerFile_management(tmpSoilsLayer, soilsLayerFile, "ABSOLUTE")

            arcpy.Delete_management(tmpSoilsLayer, "FEATURELAYER")
            del tmpSoilsLayer
            #soilsLayer = mapping.Layer(soilsLayerFile)

            # Creating interp layers
            dInterpLayers = CreateInterpMaps(gdb, soilsFC, tableList, soilsLayerFile)

            if dInterpLayers is None:
                raise MyError, "Interp layers object not populated"


            if not arcpy.Exists(soilsFC):
                raise MyError, "Missing soils featureclass: " + soilsFC


            # Soil Mapunit Map
            if arcpy.Exists(soilsFC) and arcpy.Exists(soilsLayerFile):
                # Add soil mapunit layer (with relate to component information)
                # The mapextent, map scale and dataframe rotation are set here.
                #
                #soilPolygonLayer = AddFirstSoilMap(gdb, soilsFC, soilsLayer, "musym", soilLayerName)
                soilPolygonLayer = AddFirstSoilMap(gdb, soilsFC, soilsLayerFile, "musym", soilLayerName)  # Try using soilsLayerFile to fix layer already exists error

                # Try updating the soilsLayerFile to a version that has symbology and labels.
                # Need to make sure it doesn't cause problems for interp or hydric maps
                if arcpy.Exists(soilsLayerFile):
                    arcpy.Delete_management(soilsLayerFile)

                arcpy.SaveToLayerFile_management(soilPolygonLayer, soilsLayerFile, "RELATIVE", "10.3")
                soilPolygonLayer = mapping.Layer(soilsLayerFile)

                if not soilPolygonLayer is None:
                    dInterpLayers["soilslayer"] = soilPolygonLayer

                else:
                    PrintMsg(" \nUnable to add soils layer to dictionary", 1)


            else:
                PrintMsg(" \nSkipping soilslayer addition to dictionary", 1)


            # Hydric Soil Map
            if "MapunitHydricInterp" in tableList:
                # PrintMsg("\tPreparing map for Hydric Soil Interpretation...", 0)
                # Create a soil map for Jason's hydric interpretation
                hydricLayerName = "HydricSoilMap"
                #arcpy.SetProgressorLabel("Adding Hydric Soil map layer to map display...")
                hydricLayer = AddHydricSoilMap(hydricLayerName, soilsLayerFile, "hydric_rating", gdb)

                if not hydricLayer is None:
                    #PrintMsg(" \nAdding hydriclayer to dictionary", 1)
                    dInterpLayers["hydriclayer"] = hydricLayer

            # Create aoi boundary map layer using the input aoi polygon featureclass
            if arcpy.Exists(aoiShp):
                # new AOI layer

                landunitLayer = AddFieldMap(aoiShp, gdb, "landunit", mxd, df, landunitName)

                if not landunitLayer is None:
                    #PrintMsg(" \nAdding landunit layer to dictionary...", 0)
                    dInterpLayers["landunitlayer"] = landunitLayer


            else:
                PrintMsg(" \nMissing aoiShp as input for landunits", 1)

            PrintMsg(" \nAdding soil interpretation maps...", 0)

            for sdvAtt, interpLayer in dInterpLayers.items():

                if not sdvAtt in ["soilslayer", "landunitlayer"]:
                    # Put soil lines and landunit layers at the top of the Group Layer
                    PrintMsg("\tAdding interp layer to map to display: " + interpLayer.name, 0)
                    arcpy.SetProgressor("Adding interp layer to map display: " + interpLayer.name)
                    mapping.AddLayerToGroup(df, grpLayer, dInterpLayers[sdvAtt], "BOTTOM")



            # Add soil lines and labels layer to group
            soilLinesLayer = dInterpLayers["soilslayer"]

            if df.scale < 12000:
              soilLinesLayer.showLabels = True

            PrintMsg(" \nAdding base layer to map display: " + soilLinesLayer.name, 0)
            arcpy.SetProgressor("Adding base layer to map display: " + soilLinesLayer.name)
            mapping.AddLayerToGroup(df, grpLayer, soilLinesLayer, "TOP")

            # Add landunits layer to group
            baseLayer = dInterpLayers["landunitlayer"]

            if df.scale < 30000:
              baseLayer.showLabels = True

            PrintMsg(" \nAdding base layer to map display: " + baseLayer.name, 0)
            arcpy.SetProgressor("Adding base layer to map display: " + baseLayer.name)
            mapping.AddLayerToGroup(df, grpLayer, baseLayer, "TOP")


            # Try saving the entire group layer to a new layer file and use this to
            # refresh the display so that labels are displayed properly for the base layers.
            # Not sure if this an ESRI bug, but I couldn't find an other way to fix it.
            # Save this group layerfile to the same folder as the geodatabase. To be kept permanently.
            #
            arcpy.SetProgressorLabel("Updating " + grpLayerName + " group layer")
            grpLayer.visible = False
            groupLyrFile = os.path.join(os.path.dirname(gdb), grpLayer.name + ".lyr")
            arcpy.SaveToLayerFile_management (grpLayer, groupLyrFile, "RELATIVE", "10.3")
            mapping.RemoveLayer(df, grpLayer)
            grpLayer = mapping.Layer(groupLyrFile)
            grpLayer.visible = True
            mapping.AddLayer(df, grpLayer, "TOP")
            arcpy.SetProgressorLabel("Finished generating soil maps")

            arcpy.RefreshActiveView()
            arcpy.RefreshTOC()

            try:
                del gdb, grpLayer

            except:
                pass


        elif bSpatial:
            raise MyError, "Empty spatial query, unable to retrieve soil polygons"



    PrintMsg(" \n ", 0)

except MyError, e:
    # Example: raise MyError, "This is an error message"
    PrintMsg(str(e), 2)

except:
    errorMsg()

finally:
    del mxd, df


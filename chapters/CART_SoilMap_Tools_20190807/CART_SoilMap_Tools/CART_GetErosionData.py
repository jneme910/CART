# CART_GetErosionData.py
#
# Uses AOI in ArcMap to create a soil polygon layer from CSU Rest service
# 2018-10-14 First version that sort of works. Problem only sends one polygon,
# instead of multiple polygons, each with AOID attached.
#
# Help for Postman test application Steve used.
# For CSU post requests, set
#
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
def CleanShapefile(inputAOI, bDissolve, bClean):
    # Not being used now. Keep it just in case testing finds PLU geometry errors.
    #
    # Export the selected featurelayer to shapefile format used as a shapefile name
    #
    # This version of the CleanShapefile function uses the FeatureclassToCoverage_conversion tool
    # It buffers and erases the edge of polygon boundaries only where there is a neighbor. This
    # means that we also need use the RemoveIntersections function to get rid of self-intersecting points.

    # 2017-02-02
    # When testing a shapefile with gaps and overlaps, I see that buffering the lines BEFORE dissolving
    # tends to result in slivers. These can look rather messy upon closer examination. It passes the WSS test,
    # but perhaps I should run the dissolve first (if option allows) before converting to a line coverage?
    #
    # For now I have made Dissolve the first step unless there are CLU or PARTNAME attribute fields in the AOI.
    # Please note that this method does not preserve the original single part polygons as WSS normally does.
    #
    # Alternate thought. Clip polygons from large to small.

    try:
        outputShp = os.path.join(env.scratchFolder, "myaoi.shp")

        if arcpy.Exists(outputShp):
            arcpy.Delete_management(outputShp, "FEATURECLASS")

        # If the user wants to skip the cleaning process, copy the input AOI directly to the outputShp
        # As of Jan 31, 2017 WSS has incorporated its own geometry cleaning process
        #
        if bClean == False:
            PrintMsg(" \nUsing original polygon geometry to create AOI", 0)
            env.workspace = env.scratchFolder

            # Do I need to set output coordinate system and transformation for the outputShp?
            #epsgWGS84 = 4326 # GCS WGS 1984
            outputSR = arcpy.SpatialReference(epsgWGS84)
            env.outputCoordinateSystem = outputSR
            env.geographicTransformations =  "WGS_1984_(ITRF00)_To_NAD_1983"
            arcpy.CopyFeatures_management(inputAOI, outputShp)

            return True

        else:
            PrintMsg(" \nCleaning polygon geometry to create AOI", 0)

            # temporary shapefiles. Some may not be used.
            #outputFolder = os.path.dirname(outputZipfile)
            #tmpFolder = env.scratchGDB
            tmpFolder = "IN_MEMORY"

            simpleShp = os.path.join(tmpFolder, "aoi_simple")
            dissShp = os.path.join(tmpFolder, "aoi_diss")
            lineShp = os.path.join(tmpFolder, "aoi_line")
            labelShp = os.path.join(tmpFolder, "aoi_label")
            polyShp = os.path.join(tmpFolder, "aoi_poly")
            pointShp = os.path.join(tmpFolder, "aoi_point")
            joinShp = os.path.join(tmpFolder, "aoi_join")
            cleanShp = os.path.join(tmpFolder, "aoi_clean")
            aoiCov = os.path.join(env.scratchFolder, "aoi_cov")

            # Create a new featureclass with just the selected polygons
            if arcpy.Exists(simpleShp):
                arcpy.Delete_management(simpleShp)

            if not arcpy.Exists(inputAOI):
                raise MyError, "Unable to find AOI layer: " + inputAOI

            arcpy.MultipartToSinglepart_management(inputAOI, simpleShp)
            #arcpy.CopyFeatures_management(inputAOI, simpleShp)

            cnt = int(arcpy.GetCount_management(simpleShp).getOutput(0))
            if cnt == 0:
                raise MyError, "No polygon features in " + simpleShp

            # Try to eliminate small slivers using Integrate function.
            # Integrate should also add vertices so both shared boundaries are the same.
            arcpy.Integrate_management(simpleShp, "0.05 Meters")  # was 0.1 Meters. Trying to figure out why my lines snapped and caused buffer problems

            # Describe the input layer
            desc = arcpy.Describe(simpleShp)
            #dataType = desc.featureclass.dataType.upper()
            fields = desc.fields
            fldNames = [f.baseName.upper() for f in fields]
            #PrintMsg(" \nsimpleShp field names: " + ", ".join(fldNames), 1)

            if bDissolve:
                # Always use dissolve unless there are CLU or partname attribute fields
                #PrintMsg(" \nDissolving unneccessary polygon boundaries for data request AOI...", 0)
                #arcpy.Dissolve_management(simpleShp, dissShp, "", "", "SINGLE_PART") # this is the original that works
                arcpy.Dissolve_management(simpleShp, dissShp, "", "", "MULTI_PART") # this is the one to test for common points

                # Let's get a count to see how many polygons remain after the dissolve
                dissCnt = int(arcpy.GetCount_management(dissShp).getOutput(0))
                #PrintMsg(" \nAfter dissolve, " + Number_Format(dissCnt, 0, True) + " polygons remain", 1)

            else:
                # Keep original boundaries, but if attribute table contains PARTNAME or LANDUNIT attributes, dissolve on that
                #

                if ("LAND_UNIT_TRACT_NUMBER" in fldNames and "LAND_UNIT_LAND_UNIT_NUMBER" in fldNames):
                    # Planned land Unit featureclass
                    # Go ahead and dissolve using partname which will be added next
                    PrintMsg(" \nUsing Planned Land Unit polygons to build AOI for data request", 0)
                    arcpy.AddField_management(simpleShp, "partname", "TEXT", "", "", 20)
                    curFields = ["PARTNAME", "LAND_UNIT_TRACT_NUMBER", "LAND_UNIT_LAND_UNIT_NUMBER"]

                    with arcpy.da.UpdateCursor(simpleShp, curFields) as cur:
                        for rec in cur:
                            # create stacked label for tract and field
                            partName = "T" + str(rec[1]) + "Fld" + str(rec[2])
                            rec[0] = partName
                            cur.updateRow(rec)

                    #arcpy.Dissolve_management(simpleShp, dissShp, ["PARTNAME"], "", "SINGLE_PART")
                    arcpy.Dissolve_management(simpleShp, dissShp, ["PARTNAME"], "", "MULTI_PART")

                    # Let's get a count to see how many polygons remain after the dissolve
                    dissCnt = int(arcpy.GetCount_management(dissShp).getOutput(0))
                    #PrintMsg(" \nAfter dissolve, " + Number_Format(dissCnt, 0, True) + " polygons remain in " + dissShp, 1)


                elif "PARTNAME" in fldNames:
                    # User has created a featureclass with partname attribute.
                    # Regardless, dissolve any polygons on partname
                    PrintMsg(" \nUsing partname polygon attributes to build AOI for data request (" + dissShp + ")", 0)
                    #arcpy.Dissolve_management(simpleShp, dissShp, "partname", "", "SINGLE_PART")
                    arcpy.Dissolve_management(simpleShp, dissShp, "partname", "", "MULTI_PART")

                    # Let's get a count to see how many polygons remain after the dissolve
                    dissCnt = int(arcpy.GetCount_management(dissShp).getOutput(0))
                    #PrintMsg(" \nAfter dissolve, " + Number_Format(dissCnt, 0, True) + " polygons remain", 1)


                elif ("CLU_NUMBER" in fldNames and "TRACT_NUMB" in fldNames and "FARM_NUMBE" in fldNames):
                    # This must be a shapefile copy of CLU. Field names are truncated.
                    # Keep original boundaries, but if attribute table contains LANDUNIT attributes, dissolve on that
                    #
                    # Go ahead and dissolve using partname which was previously added
                    PrintMsg(" \nUsing CLU shapefile to build AOI for data request (" + simpleShp + ")", 0)
                    arcpy.AddField_management(simpleShp, "partname", "TEXT", "", "", 20)
                    curFields = ["PARTNAME", "FARM_NUMBE", "TRACT_NUMB", "CLU_NUMBER"]

                    with arcpy.da.UpdateCursor(simpleShp, curFields) as cur:
                        for rec in cur:
                            # create stacked label for tract and field
                            #partName = "F" + str(rec[1]) + "T" + str(rec[2]) + "Fld" + str(rec[3])
                            partName = "T" + str(rec[2]) + "Fld" + str(rec[3])
                            rec[0] = partName
                            cur.updateRow(rec)

                    #arcpy.Dissolve_management(simpleShp, dissShp, ["PARTNAME"], "", "SINGLE_PART")
                    arcpy.Dissolve_management(simpleShp, dissShp, ["PARTNAME"], "", "MULTI_PART")

                    # Let's get a count to see how many polygons remain after the dissolve
                    dissCnt = int(arcpy.GetCount_management(dissShp).getOutput(0))
                    #PrintMsg(" \nAfter dissolve, " + Number_Format(dissCnt, 0, True) + " polygons remain", 1)


                elif ("TRACT_NUMBER" in fldNames and "FARM_NUMBER" in fldNames and "CLU_NUMBER" in fldNames):
                    # This must be a shapefile copy of CLU. Field names are truncated.
                    # Keep original boundaries, but if attribute table contains LANDUNIT attributes, dissolve on that
                    #
                    # Go ahead and dissolve using partname which was previously added
                    PrintMsg(" \nUsing CLU shapefile to build AOI for data request (" + simpleShp + ")", 0)
                    arcpy.AddField_management(simpleShp, "partname", "TEXT", "", "", 20)
                    curFields = ["PARTNAME", "FARM_NUMBE", "TRACT_NUMB", "CLU_NUMBER"]

                    with arcpy.da.UpdateCursor(simpleShp, curFields) as cur:
                        for rec in cur:
                            # create stacked label for tract and field
                            #partName = "F" + str(rec[1]) + "T" + str(rec[2]) + "Fld" + str(rec[3])
                            partName = "T" + str(rec[2]) + "Fld" + str(rec[3])
                            rec[0] = partName
                            cur.updateRow(rec)

                    #arcpy.Dissolve_management(simpleShp, dissShp, ["PARTNAME"], "", "SINGLE_PART")
                    arcpy.Dissolve_management(simpleShp, dissShp, ["PARTNAME"], "", "MULTI_PART")

                    # Let's get a count to see how many polygons remain after the dissolve
                    dissCnt = int(arcpy.GetCount_management(dissShp).getOutput(0))
                    #PrintMsg(" \nAfter dissolve, " + Number_Format(dissCnt, 0, True) + " polygons remain", 1)


                else:
                    dissShp = simpleShp
                    PrintMsg(" \nUsing original polygons to build AOI for data request...", 0)

            env.workspace = env.scratchFolder

            if not arcpy.Exists(dissShp):
                raise MyError, "Missing dissolved shapefile" + dissShp

            if not bClean:
                #PrintMsg(" \nSkipping RemoveCommonBoundaries function and Repair Geometry", 1)
                arcpy.CopyFeatures_management(simpleShp, outputShp)
                arcpy.Integrate_management(outputShp, "0.05 Meters")

            elif RemoveCommonBoundaries(dissShp, aoiCov, lineShp, pointShp, outputShp) == False:
                PrintMsg(" \nRunning RemoveCommonBoundaries function", 1)
                raise MyError, ""

            return True


    except MyError, e:
        # Example: raise MyError, "This is an error message"
        PrintMsg(str(e), 2)
        return False

    except:
        errorMsg()
        return False

## ===================================================================================
def NoCleanShapefile(inputAOI, bDissolve, bClean, aoiShp, dissShp):
    # Create a new featureclass with just the geometry and attributes necessary to
    # create an AOI request for the web service. Does not make any special attempts
    # to fix polygon geometry problems.
    try:
        # Create a new featureclass with just the selected polygons
        #PrintMsg(" \nCreating single part polygon shapefile: " + simpleShp, 1)
        simpleShp = os.path.join(tmpFolder, "aoi_simple")
        arcpy.MultipartToSinglepart_management(inputAOI, simpleShp)

        cnt = int(arcpy.GetCount_management(simpleShp).getOutput(0))

        if cnt == 0:
            raise MyError, "No polygon features in " + simpleShp

        # Describe the input layer
        desc = arcpy.Describe(simpleShp)
        fields = desc.fields
        fldNames = [f.baseName.upper() for f in fields]
        #PrintMsg(" \nsimpleShp field names: " + ", ".join(fldNames), 1)
        bpartname = False

        if bDissolve:
            # Dissolve to single part polygons
            PrintMsg(" \nDissolving polygons to create a single AOI...", 0)
            arcpy.Dissolve_management(simpleShp, aoiShp, "", "", "SINGLE_PART") # this is the one to test for common points

            # Let's get a count to see how many polygons remain after the dissolve
            dissCnt = int(arcpy.GetCount_management(aoiShp).getOutput(0))
            #PrintMsg(" \nAfter dissolve, " + Number_Format(dissCnt, 0, True) + " polygons remain", 0)

            if dissCnt > 0:
                # Make another copy to use a the dissolved version
                #PrintMsg("\tCopied dissolved layer to " + dissShp, 1)
                arcpy.CopyFeatures_management(aoiShp, dissShp)

        else:
            # Keep original boundaries, but if attribute table contains PARTNAME or LANDUNIT attributes, dissolve on that
            #
            # Create dissolved multipart shapefile to send to SDA, then union the results with the aoiShp

            # PrintMsg(" \nCreating dissolved boundary for possible use in combined tool with Soils layer", 1)
            arcpy.Dissolve_management(simpleShp, dissShp, "", "", "SINGLE_PART") # May need to keep this line!

            if ("LAND_UNIT_TRACT_NUMBER" in fldNames and "LAND_UNIT_LAND_UNIT_NUMBER" in fldNames):
                # Planned land Unit featureclass
                # Go ahead and dissolve using partname which will be added next
                PrintMsg(" \nUsing Planned Land Unit polygons to build AOI for web service", 0)
                arcpy.AddField_management(simpleShp, "partname", "TEXT", "", "", 20)
                curFields = ["PARTNAME", "LAND_UNIT_TRACT_NUMBER", "LAND_UNIT_LAND_UNIT_NUMBER"]

                with arcpy.da.UpdateCursor(simpleShp, curFields) as cur:
                    for rec in cur:
                        # create stacked label for tract and field
                        partName = "T" + str(rec[1]) + "\nFld" + str(rec[2])
                        rec[0] = partName
                        cur.updateRow(rec)

                arcpy.Dissolve_management(simpleShp, aoiShp, ["PARTNAME"], "", "MULTI_PART")
                bpartname = True

            elif ("LAND_UNIT.TRACT_NUMBER" in fldNames and "LAND_UNIT.LAND_UNIT_NUMBER" in fldNames):
                # Planned land Unit featureclass
                # Go ahead and dissolve using partname which will be added next
                PrintMsg(" \nUsing Planned Land Unit polygons to build AOI for web service", 0)
                arcpy.AddField_management(simpleShp, "partname", "TEXT", "", "", 20)
                curFields = ["PARTNAME", "LAND_UNIT.TRACT_NUMBER", "LAND_UNIT.LAND_UNIT_NUMBER"]

                with arcpy.da.UpdateCursor(simpleShp, curFields) as cur:
                    for rec in cur:
                        # create stacked label for tract and field
                        partName = "T" + str(rec[1]) + "\nFld" + str(rec[2])
                        rec[0] = partName
                        cur.updateRow(rec)

                arcpy.Dissolve_management(simpleShp, aoiShp, ["PARTNAME"], "", "MULTI_PART")
                bpartname = True

            elif "PARTNAME" in fldNames:
                # User has created a featureclass with partname attribute.
                # Regardless, dissolve any polygons on partname
                PrintMsg(" \nUsing partname polygon attributes to build AOI for web service", 0)
                arcpy.Dissolve_management(simpleShp, aoiShp, "partname", "", "MULTI_PART")
                bpartname = True

            elif ("CLU_NUMBER" in fldNames and "TRACT_NUMB" in fldNames and "FARM_NUMBE" in fldNames):
                # This must be a shapefile copy of CLU. Field names are truncated.
                # Keep original boundaries, but if attribute table contains LANDUNIT attributes, dissolve on that
                #
                # Go ahead and dissolve using partname which was previously added
                PrintMsg(" \nUsing CLU shapefile to build AOI for web service", 0)
                arcpy.AddField_management(simpleShp, "partname", "TEXT", "", "", 20)
                curFields = ["PARTNAME", "FARM_NUMBE", "TRACT_NUMB", "CLU_NUMBER"]

                with arcpy.da.UpdateCursor(simpleShp, curFields) as cur:
                    for rec in cur:
                        # create stacked label for tract and field
                        #partName = "F" + str(rec[1]) + "\nT" + str(rec[2]) + "\nN" + str(rec[3])
                        partName = "T" + str(rec[2]) + "\nFld" + str(rec[3])
                        rec[0] = partName
                        cur.updateRow(rec)

                arcpy.Dissolve_management(simpleShp, aoiShp, ["PARTNAME"], "", "MULTI_PART")
                bpartname = True

            elif ("TRACT_NUMBER" in fldNames and "FARM_NUMBER" in fldNames and "CLU_NUMBER" in fldNames):
                # This must be a shapefile copy of CLU. Field names are truncated.
                # Keep original boundaries, but if attribute table contains LANDUNIT attributes, dissolve on that
                #
                # Go ahead and dissolve using partname which was previously added
                PrintMsg(" \nUsing CLU shapefile to build AOI for web service", 0)
                arcpy.AddField_management(simpleShp, "partname", "TEXT", "", "", 20)
                curFields = ["PARTNAME", "FARM_NUMBER", "TRACT_NUMBER", "CLU_NUMBER"]

                with arcpy.da.UpdateCursor(simpleShp, curFields) as cur:
                    for rec in cur:
                        # create stacked label for tract and field
                        #partName = "F" + str(rec[1]) + "\nT" + str(rec[2]) + "\nN" + str(rec[3])
                        partName = "T" + str(rec[2]) + "\nFld" + str(rec[3])
                        rec[0] = partName
                        cur.updateRow(rec)

                arcpy.Dissolve_management(simpleShp, aoiShp, ["PARTNAME"], "", "MULTI_PART")
                bpartname = True

            elif ("CLUNBR" in fldNames and "TRACTNBR" in fldNames and "FARMNBR" in fldNames):
                # This must be a shapefile copy of CLU from Iowa
                # Keep original boundaries, but if attribute table contains LANDUNIT attributes, dissolve on that
                #
                # Go ahead and dissolve using partname which was previously added
                PrintMsg(" \nUsing CLU shapefile to build AOI for web service", 0)
                arcpy.AddField_management(simpleShp, "partname", "TEXT", "", "", 20)
                curFields = ["PARTNAME", "FARMNBR", "TRACTNBR", "CLUNBR"]

                with arcpy.da.UpdateCursor(simpleShp, curFields) as cur:
                    for rec in cur:
                        # create stacked label for tract and field
                        #partName = "F" + str(rec[1]) + "\nT" + str(rec[2]) + "\nN" + str(rec[3])
                        partName = "T" + str(rec[2]) + "\nFld" + str(rec[3])
                        #PrintMsg(partName, 1)
                        rec[0] = partName
                        cur.updateRow(rec)

                arcpy.Dissolve_management(simpleShp, aoiShp, ["PARTNAME"], "", "MULTI_PART")
                bpartname = True

            else:
                if arcpy.Exists(simpleShp):
                    #PrintMsg(" \nSaving " + simpleShp + " to " + aoiShp, 1)
                    arcpy.CopyFeatures_management(simpleShp, aoiShp)
                    PrintMsg(" \nUsing original polygons to build AOI for web service...", 0)

                else:
                    raise MyError, "Missing output " + simpleShp

        env.workspace = env.scratchFolder

        if not arcpy.Exists(aoiShp):
            raise MyError, "Missing AOI " + aoiShp

        arcpy.RepairGeometry_management(aoiShp, "DELETE_NULL")  # Need to make sure this isn't doing bad things.

        return True


    except MyError, e:
        # Example: raise MyError, "This is an error message"
        PrintMsg(str(e), 2)
        return False

    except:
        errorMsg()
        return False

## ===================================================================================
def FormRFactorQuery(theAOI):
    #
    # Create a simplified polygon from the input polygon using convex-hull.
    # Coordinates are GCS WGS1984 and format is WKT.
    # Returns spatial query (string) and clipPolygon (geometry)
    # The clipPolygon will be used to clip the soil polygons back to the original AOI polygon
    #
    # Note. SDA will accept WKT requests for MULTIPOLYGON if you make these changes:
    #     Need to switch the initial query AOI to use STGeomFromText and remove the
    #     WKT search and replace for "MULTIPOLYGON" --> "POLYGON".
    #
    # I tried using the MULTIPOLYGON option for the original AOI polygons but SDA would
    # fail when submitting AOI requests with large numbers of vertices. Easiest just to
    # using convex hull polygons and clip the results on the client side.

    try:

        aoicoords = dict()
        i = 0
        # Commonly used EPSG numbers
        #epsgWM = 3857 # Web Mercatur
        #epsgWGS = 4326 # GCS WGS 1984
        #epsgNAD83 = 4269 # GCS NAD 1983
        #epsgAlbers = 102039 # USA_Contiguous_Albers_Equal_Area_Conic_USGS_version
        #tm = "WGS_1984_(ITRF00)_To_NAD_1983"  # datum transformation supported by this script

        #gcs = arcpy.SpatialReference(epsgWGS84)

        # Compare AOI coordinate system with that returned by Soil Data Access. The queries are
        # currently all set to return WGS 1984, geographic.

        # Get geographic coordinate system information for input and output layers
        validDatums = ["D_WGS_1984", "D_North_American_1983"]
        aoiCS = arcpy.Describe(theAOI).spatialReference

        if not aoiCS.GCS.datumName in validDatums:
            raise MyError, "AOI coordinate system not supported: " + aoiCS.name + ", " + aoiCS.GCS.datumName

        if aoiCS.GCS.datumName == "D_WGS_1984":
            tm = ""  # no datum transformation required

        elif aoiCS.GCS.datumName == "D_North_American_1983":
            tm = "WGS_1984_(ITRF00)_To_NAD_1983"

        else:
            raise MyError, "AOI CS datum name: " + aoiCS.GCS.datumName

        env.geographicTransformations = tm
        sdaCS = arcpy.SpatialReference(epsgWGS84)

        # Determine whether
        if aoiCS.PCSName != "":
            # AOI layer has a projected coordinate system, so geometry will always have to be projected
            bProjected = True

        elif aoiCS.GCS.name != sdaCS.GCS.name:
            # AOI must be NAD 1983
            bProjected = True

        else:
            bProjected = False

        # Get list of field names
        desc = arcpy.Describe(theAOI)
        fields = desc.fields
        fldNames = [f.baseName.upper() for f in fields]
        features = list()
        aoiCoords = list()

        # This original next line only does one polygon. Do not use this version of dFeat
        dFeat = {"metainfo": {}, "parameter": [{"name": "aoas", "value": [[  {"name": "aoa_id","value": 999,"description": "Area of Analysis Identifier"  },  {"name": "aoa_geometry","type": "Polygon","coordinates": None  } ]]   }] }
        dAOI = {"name": "aoas", "value": [ ] }
        dAOAS = {"parameter": [ ] }
        aoidList = list()

        if "PARTNAME" in fldNames:
            #PrintMsg(" \nTESTING HERE!", 1)
            curFlds = ["SHAPE@", "partName"]

            if bProjected:
                # UnProject geometry from AOI to GCS WGS1984

                with arcpy.da.SearchCursor(theAOI, curFlds) as cur:
                    i = 0

                    for rec in cur:
                        theFeat = [ {"name": "aoa_id","value": "", "description": "Area of Analysis Identifier"  },  {"name": "aoa_geometry", "type": "Polygon","coordinates": None  } ]
                        polygon = rec[0].projectAs(sdaCS, tm)        # simplified geometry, projected to WGS 1984
                        partName = rec[1]
                        partName = partName.replace("\n", " ")
                        aoidList.append(partName)

                        #PrintMsg("\tPartName: " + partName, 1)
                        theFeat[0]["value"] = partName   # set the value in the polygon record's first dictionary to the PLU id
                        dJSON = json.loads(polygon.JSON)
                        featureList = dJSON['rings']
                        newFeatures = list()

                        for feature in featureList:
                            newFeature = list()

                            for coord in feature:
                                newFeature.append([round(coord[0], 6), round(coord[1], 6)])

                            newFeatures.append(newFeature)

                        theFeat[1]["coordinates"] = newFeatures  # set the coordinates in the polygon record's second dictionary to the geometry
                        dAOI["value"].append(theFeat)
                    dAOAS["parameter"].append(dAOI)

            else:
                # No projection required. AOI must be GCS WGS 1984

                with arcpy.da.SearchCursor(theAOI, curFlds) as cur:
                    for rec in cur:
                        # original geometry
                        theFeat = [ {"name": "aoa_id","value": "", "description": "Area of Analysis Identifier"  },  {"name": "aoa_geometry", "type": "Polygon","coordinates": None  } ]
                        partName = rec[1]
                        partName = partName.replace("\n", " ")
                        aoidList.append(partName)
                        #PrintMsg("\tPartName: " + partName, 1)
                        dJSON = json.loads(rec[0].JSON)
                        featureList = dJSON['rings']
                        newFeatures = list()

                        for feature in featureList:
                            newFeature = list()

                            for coord in feature:
                                #x = round(ring[0], 6)
                                #y = round(ring[1], 6)
                                newFeature.append([round(coord[0], 6), round(coord[1], 6)])

                            newFeatures.append(newFeature)

                    theFeat[1]["coordinates"] = newFeatures
                    dAOI["value"].append(theFeat)
                dAOAS["parameter"].append(dAOI)


        else:
            # No partname attribute. 2018-10-17 This one works correctly for inner rings.
            #
            curFlds = ["SHAPE@"]

            if bProjected:
                # UnProject geometry from AOI to GCS WGS1984

                with arcpy.da.SearchCursor(theAOI, curFlds) as cur:
                    for rec in cur:
                        theFeat = [ {"name": "aoa_id","value": "", "description": "Area of Analysis Identifier"  },  {"name": "aoa_geometry", "type": "Polygon","coordinates": None  } ]
                        polygon = rec[0].projectAs(sdaCS, tm)        # simplified geometry, projected to WGS 1984
                        dJSON = json.loads(polygon.JSON)
                        featureList = dJSON['rings']
                        newFeatures = list()

                        for feature in featureList:
                            newFeature = list()

                            for coord in feature:
                                newFeature.append([round(coord[0], 6), round(coord[1], 6)])

                            newFeatures.append(newFeature)

                    theFeat[1]["coordinates"] = newFeatures
                    dAOI["value"].append(theFeat)
                dAOAS["parameter"].append(dAOI)

            else:
                # No projection required. AOI must be GCS WGS 1984

                with arcpy.da.SearchCursor(theAOI, curFlds) as cur:
                    for rec in cur:
                        # original geometry
                        theFeat = [ {"name": "aoa_id","value": "", "description": "Area of Analysis Identifier"  },  {"name": "aoa_geometry", "type": "Polygon","coordinates": None  } ]
                        #sJSON = rec[0].JSON
                        dJSON = json.loads(rec[0].JSON)
                        featureList = dJSON['rings']
                        #newCoords = list()
                        newFeatures = list()

                        for feature in featureList:
                            newFeature = list()

                            for coord in feature:
                                newFeature.append([round(coord[0], 6), round(coord[1], 6)])

                            newFeatures.append(newFeature)

                    theFeat[1]["coordinates"] = newFeatures
                    dAOI["value"].append(theFeat)
                dAOAS["parameter"].append(dAOI)


        return dAOAS, aoidList


    except MyError, e:
        # Example: raise MyError, "This is an error message"
        PrintMsg(str(e), 2)
        return dict(), []

    except:
        errorMsg()
        return dict(), []

## ===================================================================================
def FormErosionQuery(param):
    #
    # Try to modify each feature parameter value from RFactor query to work with Eroson Index.
    #
    # How to display formatted json:
    # json.dumps(jsonData, sort_keys=True, indent=4)

    try:
        eiRequest = dict()
        newName = "AoAId"
        #PrintMsg(" \nparam: " + str(param), 0)

        if len(param) == 0:
            raise MyError, "Bad parameter: " + str(param)

        if not "name" in param[0]:
            raise MyError, "Bad parameter: " + str(param)

        if param[0]["name"] == "aoa_id":
            param[0]["name"] = newName

        eiRequest["parameter"] = param

        #PrintMsg(" \nModified request parameter for Land Unit: " + ": \n " + str(eiRequest), 0)
        return eiRequest

    except MyError, e:
        # Example: raise MyError, "This is an error message"
        PrintMsg(str(e), 2)
        return eiRequest

    except:
        errorMsg()
        return eiRequest

## ===================================================================================
def GetRFactorData(theURL, rFactorQuery, aoidList, dErosionData, headers):
    #
    # JSON format
    #
    # Send spatial query to WQM-12 service for RFactor

    try:

        # This request may return data for multiple land units
        # key = pluID, value = RFactor number

        if "metainfo" in rFactorQuery:
            del rFactorQuery["metainfo"]

        #PrintMsg(" \n" + theURL, 1)

        sData = json.dumps(rFactorQuery)
        #PrintMsg(" \nRFactor request: \n " + sData, 1)

        try:
            resp = requests.request("POST", theURL, data=sData, headers=headers, verify=False)

        except:
            del resp
            raise MyError, "Request failed: " + sData


        status = resp.status_code


        if status == 200:
            sJSON = resp.text
            json_data = json.loads(sJSON)

            if not "result" in json_data:
                raise MyError, "No data returned for this request: " + sData

            resultValues = json_data["result"][0]["value"]  # I believe this would be result for first polygon
            # each result will contain two dictionaries. One will have a 'name' of 'AoAId' and the other will be 'RFactor'

            for rec in resultValues:
                #PrintMsg("\trec: " + str(rec), 1)
                dID = rec[0]

                try:
                    dData = rec[1]

                except:
                    raise MyError(str(json_data), 1)

                if dID["name"].lower() == "aoaid":
                    pluID = dID["value"]

                    if dData["name"].lower() == "rfactor":
                        rFactor = float(dData["value"])
                        dErosionData[pluID] = {"RFactor": rFactor}

                    else:
                        raise MyError, "Problem parsing R Factor from results: " + str(dData)

                else:
                    raise MyError, "Problem parsing RFactor results: " + str(dID)

        else:
            raise MyError, str(status) + " '" + httplib.responses[status] + "' returned from service at " + theURL

        return dErosionData


    except MyError, e:
        # Example: raise MyError, "This is an error message"
        PrintMsg(str(e), 2)
        return dErosionData

    except urllib2.HTTPError, e:
        # Currently the messages coming back from the server are not very helpful.
        # Bad Request could mean that the query timed out or tried to return too many JSON characters.
        #
        if hasattr(e, 'code'):
            PrintMsg("HTTP Error: " + str(e.code), 2)
            return dErosionData

        elif hasattr(e, 'msg'):
            PrintMsg("HTTP Error: " + str(e.msg), 2)
            return dErosionData

        else:
            PrintMsg("HTTP Error? ", 2)
            return dErosionData

    except:
        errorMsg()
        return dErosionData


## ===================================================================================
def GetEIData(theURL, spatialQuery, dErosionData, headers):
    #
    # Improper JSON format from WEPOT 2.0 data
    #

    try:

        if "metainfo" in spatialQuery:
            del spatialQuery["metainfo"]

        sData = json.dumps(spatialQuery)
        #PrintMsg(" \nEP request: \n " + sData, 1)

        resp = requests.request("POST", theURL, data=sData, headers=headers,  verify=False)
        status = resp.status_code
        #PrintMsg("Post request status_code: " + str(status), 1)

        if status == 200:
            try:
                json_string = resp.text
                dJson = json.loads(json_string)
                #PrintMsg(" \nErosion Index data: " + str(dJson), 0)
                #PrintMsg(" \json_data type: " + str(type(json_data)), 1)

                # First check status. There may be no data available for this AOI.
                if not "metainfo" in dJson:
                    raise MyError, "Failed to return data from service, no metainfo either"

                returnStatus = dJson["metainfo"]["status"]

                #PrintMsg(" \nErosion service returned metainfo status of: " + str(returnStatus), 1)

                if str(returnStatus) == "Failed":
                    if "error" in dJson["metainfo"]:
                        raise MyError, str(dJson["metainfo"]["error"])


                # Get land unit id if available
                idInfo = dJson["parameter"][0]

                if idInfo["name"].lower() == "aoaid":
                    pluID = idInfo["value"]

                else:
                    pluID = ""

                if "result" in dJson:
                    results = dJson["result"]

                else:
                    raise MyError, "Failed to return data for request: " + str(dJson)

                if len(results) > 0:
                    #PrintMsg(" \nErosion Index data: ", 0)

                    for result in results:
                        if "name" in result:

                            if result["name"] in ["aoa_dom_water_compname", "aoa_water_ep"]:
                                #PrintMsg(" \n\t" + result["name"] + ":  " + result["value"], 0)

                                if pluID in dErosionData:
                                    # should already have RFactor populated
                                    dErosionData[pluID][result["name"]] = result["value"]

                                else:
                                    # Failed to get RFactor
                                    dErosionData[pluID] = {"RFactor": None}
                                    dErosionData[pluID][result["name"]] = result["value"]

            except MyError, e:
                # Example: raise MyError, "This is an error message"
                PrintMsg(str(e), 2)
                return dErosionData

            except:
                #PrintMsg("json_data: " + str(json_data), 1)
                errorMsg()


        else:
            raise MyError, str(status) + " '" + httplib.responses[status] + "' returned from service at " + theURL

        return dErosionData

    except MyError, e:
        # Example: raise MyError, "This is an error message"
        PrintMsg(str(e), 2)
        return dErosionData

    except urllib2.HTTPError, e:
        # Currently the messages coming back from the server are not very helpful.
        # Bad Request could mean that the query timed out or tried to return too many JSON characters.
        #
        if hasattr(e, 'code'):
            PrintMsg("HTTP Error: " + str(e.code), 2)
            return dErosionData

        elif hasattr(e, 'msg'):
            PrintMsg("HTTP Error: " + str(e.msg), 2)
            return dErosionData

        else:
            PrintMsg("HTTP Error? ", 2)
            return dErosionData

    except:
        errorMsg()
        return dErosionData


## ===================================================================================
def GetMatrix(rFactor, waterErosion):
    # create array for ratings  type = 'I'
    try:
        if str(rFactor) == "NA":
            raise MyError, "Unable to rate because RFactor was not available"

        if str(waterErosion) == "NA":
            raise MyError, "Unable to rate because Potential Water Erosion was not available"

        #m =  [[30, 40, 60, 80], [20, 30, 50, 60], [10, 20, 40, 60], [10, 10, 20, 40]]

        m = [ [10, 10, 20, 40], [10, 20, 40, 60], [20, 30, 50, 60], [30, 40, 60, 80] ]

        # Get X dimension from rFactor
        if rFactor <= 50:
            x = 0

        elif rFactor in range(50, 150):
            x = 1

        elif rFactor in range(150, 250):
            x = 2

        elif rFactor > 250:
            x = 3

        else:
            raise MyError, "RFactor (" + str(rFactor) + ") is out of range"


        # Get Y dimension from Potential Water Erosion
        if waterErosion < 0.05:
            y = 0

        elif 0.10 > waterErosion >= 0.05:
            y = 1

        elif 0.20 > waterErosion >= 0.10:
            y = 2

        elif waterErosion >= 0.20:
            y = 3

        else:
            raise MyError, "Water Erosion Potential (" + str(waterErosion) + ") is out of range"


        # Get point value from the matrix
        points = m[x][y]
        # PrintMsg(" \nMatrix Points (" + str(x) + ", " + str(y) + "):  " + str(points), 1)

        return points




    except MyError, e:
        # Example: raise MyError, "This is an error message"
        PrintMsg(str(e), 2)
        return 0

    except:
        errorMsg()
        return 0


## ===================================================================================
## ===================================================================================
## MAIN
## ===================================================================================

# Import system modules
import sys, string, os, arcpy, locale, traceback, urllib, urllib2, httplib, requests, json, datetime

from arcpy import env
from copy import deepcopy
from array import *
#from random import randint

try:
    # Read input parameters
    inputAOI = arcpy.GetParameterAsText(0)                    # input AOI feature layer
    featureCnt = arcpy.GetParameterAsText(1)                        # String. Number of polygons selected of total features in the AOI featureclass.
    #sQueryFile = arcpy.GetParameterAsText(2)                  # Text file containing FSA soils
    bDissolve = arcpy.GetParameter(2)                         # User does not want to keep individual polygon or field boundaries
    #outputShp = arcpy.GetParameterAsText(4)                         # Output soils featureclass
    bVerbose = False

    # Make sure that land units have been selected by the user.
    # Parse the featureCnt parameter string to get the actual count
    featureCnt = int(featureCnt.split(" ")[-1])
    #PrintMsg(" \n" + Number_Format(featureCnt, 0, True) + " features selected in " + inputAOI, 1)

    if featureCnt < 1:
        raise MyError, "User must select 1 or more land units in the " + inputAOI + " layer"

    # Several options for the different services are listed below.
    # The Colorado State services are development-only.
    # For production, the eauth.usda.gov services should be used.
    # There seems to be a problem with api.eauth.usda.gov/nrcs/cp/NRCS_RS_ConservationResourcesWQM/m/wqm/rfactor/1.2

    #rFactorURL = "http://csip.engr.colostate.edu:8083/csip-wqm/m/wqm/rfactor/1.2"                   # R Factor URL at CSU
    erosionURL = "https://api.eauth.usda.gov/nrcs/cp/NRCS_ConservationResourcesSOILS/d/wepot/2.0"  # erodibility indexes at NITC
    #erosionURL = "http://csip.engr.colostate.edu:8092/csip-soils/d/wepot/2.0"                     # erodibility index at CSU
    #erosionURL = "https://conservationresources.sc.egov.usda.gov/NRCS_ConservationResourcesSOILS/d/wepot/2.0"
    #rFactorURL = "https://api.eauth.usda.gov/nrcs/cp/NRCS_RS_ConservationResourcesWQM/m/wqm/rfactor/1.2"
    rFactorURL = "https://intapi.eauth.usda.gov/nrcs/cp/NRCS_RS_ConservationResourcesWQM/m/wqm/rfactor/1.2"

    bClean = False  # Hardcode this for now. Never 'clean' the geometry.
    timeOut = 0
    env.overwriteOutput= True
    env.addOutputsToMap = False

    # Commonly used EPSG numbers
    epsgWM = 3857 # Web Mercatur
    epsgWGS84 = 4326 # GCS WGS 1984
    epsgNAD83 = 4269 # GCS NAD 1983
    epsgAlbers = 102039 # USA_Contiguous_Albers_Equal_Area_Conic_USGS_version

    # Get geographic coordinate system information for input and output layers
    validDatums = ["D_WGS_1984", "D_North_American_1983"]
    desc = arcpy.Describe(inputAOI)
    aoiCS = desc.spatialReference
    aoiName = os.path.basename(desc.nameString)
    aoiCnt = int(arcpy.GetCount_management(inputAOI).getOutput(0))

    if not aoiCS.GCS.datumName in validDatums:
        raise MyError, "AOI coordinate system not supported: " + aoiCS.name + ", " + aoiCS.GCS.datumName

    if aoiCS.GCS.datumName == "D_WGS_1984":
        tm = ""  # no datum transformation required

    elif aoiCS.GCS.datumName == "D_North_American_1983":
        tm = "WGS_1984_(ITRF00)_To_NAD_1983"

    else:
        raise MyError, "AOI CS datum name: " + aoiCS.GCS.datumName

    sdaCS = arcpy.SpatialReference(epsgWGS84)

    # Determine whether
    if aoiCS.PCSName != "":
        # AOI layer has a projected coordinate system, so geometry will always have to be projected
        bProjected = True

    elif aoiCS.GCS.name != sdaCS.GCS.name:
        # AOI must be NAD 1983
        bProjected = True

    else:
        bProjected = False

    licenseLevel = arcpy.ProductInfo().upper()

    if licenseLevel != "ARCINFO":
        raise MyError, "License level must be Advanced to run this tool"

    # Define temporary featureclasses
    aoiShp = os.path.join(env.scratchFolder, "myaoi.shp")

    if arcpy.Exists(aoiShp):
        arcpy.Delete_management(aoiShp, "FEATURECLASS")

    tmpFolder = "IN_MEMORY"
    dissShp = os.path.join(tmpFolder, "aoi_diss")

    # Define output report (text file) that will be displayed at the end
    reportName = "SheetRill_ErosionFactors.txt"
    reportFile = os.path.join(env.scratchFolder, reportName)
    d = datetime.date.today()
    dateStamp = str(d.isoformat())

    if arcpy.Exists(reportFile):
        # remove report file from previous runs
        arcpy.Delete_management(reportFile)

    with open(reportFile, "w") as fh:
        fh.write("\nCART UAT for Sheet and Rill Erosion. Generated " + dateStamp + ".\n")
        fh.write(("-" * 60) + "\n")


    # Reformat AOI layer if needed and create a version with just the outer boundary (dissShp)
    # This simpler shapefile will be used to send the spatial request to SDA,
    # and then if partname exists, the aoiShp will be unioned with the outputSoils layer.
    #
    if aoiCnt == 1:
        # No need to dissolve input AOI if there is only one polygon
        bDissolve = False

    bCleaned = NoCleanShapefile(inputAOI, bDissolve, bClean, aoiShp, dissShp)

    if bCleaned:
        polyCnt = int(arcpy.GetCount_management(aoiShp).getOutput(0))
        fieldNames = [fld.name.upper() for fld in arcpy.Describe(aoiShp).fields]

        if "PARTNAME" in fieldNames:
            bParts = True
            #PrintMsg(" \naoi shapefile has partname, skipping", 1)

        else:
            bParts = False

        # Create dictionary to contain all results
        dErosionData = dict()

        # Create AOI using simplified polygon coordinates
        rFactorQuery, aoidList = FormRFactorQuery(aoiShp)

        #PrintMsg(" \nrFactorQuery: " + str(rFactorQuery), 0)

        if rFactorQuery != "":
            # Send spatial query and use results to populate outputShp featureclass
            #PrintMsg(" \nRFactor AOI Request: " + " \n" + str(rFactorQuery), 1)
            PrintMsg(" \nGetting RFactor data for selected land units...", 0)

            headers = {'Content-Type': 'application/json', 'cache-control': 'no-cache', 'Postman-Token': "97741c0f-2c82-4537-89f8-e78d859ac6a7"}

            dErosionData = GetRFactorData(rFactorURL, rFactorQuery, aoidList, dErosionData, headers)  # R Factor URL

            #if len(dErosionData) > 0:
            # Only request erosion data if the RFactor request was successful
            paramList = rFactorQuery["parameter"][0]["value"]
            PrintMsg(" \nGetting erodibility indices... \n", 0)
            #PrintMsg(" \nparamList: " + str(paramList), 0)

            for p in paramList:
                eiQuery = FormErosionQuery(p) # form EI request using just a single polygon

                if len(eiQuery) == 0:
                    raise MyError, ""

                dErosionData = GetEIData(erosionURL, eiQuery, dErosionData, headers)  #

                if len(dErosionData) == 0:
                    raise MyError, "Failed post request: \n " + str(eiQuery) + " \n"

            # Print data for user. Document the need to uncheck the 'Close this window if..'
            #keyList = ["aoa_dom_water_compname", "RFactor", "aoa_water_ep"]
            PrintMsg(" \nReporting results...", 0)

            for pluID, data in dErosionData.items():
                compName = "NA"
                rFactor = "NA"
                waterErosion = "NA"

                if pluID == "":
                    pluID = "NA"

                if "aoa_dom_water_compname" in data:
                    compName = data["aoa_dom_water_compname"]

                if "RFactor" in data:
                    rFactor = int(round(data["RFactor"], 0))

                if "aoa_water_ep" in data:
                    waterErosion = float(data["aoa_water_ep"])

                points = GetMatrix(rFactor, waterErosion)


                # Print soil factors to the console window
                PrintMsg(" \nLand Unit: " + pluID, 0)
                PrintMsg(" \n\tSoil: " + compName, 0)
                PrintMsg(" \n\tRFactor: " + str(rFactor), 0)
                PrintMsg(" \n\tWater Erosion Potential: " + str(waterErosion), 0)
                PrintMsg(" \n\tMatrix Points:  " + str(points), 0)

                with open(reportFile, "a") as fh:
                    PrintMsg(" \nSaving output information to:  " + reportFile, 0)
                    #fh.write("\nCART UAT for Sheet and Rill Erosion. Generated " + dateStamp + ".\n")
                    #fh.write(("-" * 60) + "\n")
                    fh.write("\nLand Unit: " + pluID + "\n")
                    fh.write("\tSoil: " + compName + "\n")
                    fh.write("\tRFactor: " + str(rFactor) + "\n")
                    fh.write("\tWater Erosion Potential: " + str(waterErosion) + "\n")
                    fh.write("\tErosion Matrix Points: " + str(points) + "\n")

        else:
            raise MyError, "Empty spatial query, unable to retrieve soil polygons"

        # Popup report file so that user has time to record the results and save the file to a permanent location.
        if arcpy.Exists(reportFile):
            with open(reportFile, "a") as fh:
                fh.write("\n\n**WARNING. This file will be overwritten unless it is \nsaved to a new folder location or with a new filename.")

            os.startfile(reportFile)

        if arcpy.Exists(dissShp):
            arcpy.Delete_management(dissShp)

        if arcpy.Exists(aoiShp):
            arcpy.Delete_management(aoiShp)

    PrintMsg(" \n ", 0)

except MyError, e:
    # Example: raise MyError, "This is an error message"
    PrintMsg(str(e), 2)

except:
    errorMsg()

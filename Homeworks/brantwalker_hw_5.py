###################################################################### 
# Edit the following function definition, replacing the words
# 'name' with your name and 'hawkid' with your hawkid.
# 
# Note: Your hawkid is the login name you use to access ICON, and not
# your firsname-lastname@uiowa.edu email address.
# 
# def hawkid():
#     return(["Caglar Koylu", "ckoylu"])
###################################################################### 
def hawkid():
    return(["Brant Walker", "brantwalker"])

###################################################################### 
# Problem 1 (30 Points)
#
# Given a polygon feature class in a geodatabase, a count attribute of the feature class(e.g., population, disease count):
# this function calculates and appends a new density column to the input feature class in a geodatabase.

# Given any polygon feature class in the geodatabase and a count variable:
# - Calculate the area of each polygon in square miles and append to a new column
# - Create a field (e.g., density_sqm) and calculate the density of the selected count variable
#   using the area of each polygon and its count variable(e.g., population) 
# 
# 1- Check whether the input variables are correct(e.g., the shape type, attribute name)
# 2- Make sure overwrite is enabled if the field name already exists.
# 3- Identify the input coordinate systems unit of measurement (e.g., meters, feet) for an accurate area calculation and conversion
# 4- Give a warning message if the projection is a geographic projection(e.g., WGS84, NAD83).
#    Remember that area calculations are not accurate in geographic coordinate systems. 
# 
###################################################################### 
import arcpy
arcpy.env.overwriteOutput=True

def calculateDensity(fcpolygon, attribute,geodatabase = "assignment2.gdb"):
    arcpy.env.workspace = geodatabase

    #Quick exception handling for file type
    describePoly = arcpy.Describe(fcpolygon)
    describeWork = arcpy.Describe(geodatabase)
    field_list = []
    
    for field in arcpy.ListFields(fcpolygon):
        field_list.append(field.name)
    
    if describePoly.shapetype != "Polygon" or describeWork.dataType != "Workspace":
        print("You did not give me the correct file types.")
        
    elif attribute not in field_list:
        print("{0} is not a field in {1}".format(attribute, fcpolygon))
        
    else:
        
        #create new field for our area calculation
        a_field = "area_sq_miles"
        arcpy.management.AddField(fcpolygon, a_field, "DOUBLE")
        
        # If the Polygon FC has a projected SR, give a warning and calculate it using AREA
        if describePoly.spatialReference.type == "Projected":
            print("{0} is a geographic projection - area calculations will not be accurate".format(fcpolygon))

            # Generate the extent coordinates using CalculateGeometry
            arcpy.CalculateGeometryAttributes_management(fcpolygon, [[a_field, "AREA"]], 
                                                         "MILES_US", "SQUARE_MILES_US")
            
        #If the PolygonFC has a geometric SR, calculate area with GEODESIC
        else:
            # Generate the extent coordinates using CalculateGeometry
            arcpy.CalculateGeometryAttributes_management(fcpolygon, [[a_field, "AREA_GEODESIC"]], 
                                                         "MILES_US", "SQUARE_MILES_US") 
            
        #create new field for our density calculation
        d_field = "density_sq_miles"
        arcpy.management.AddField(fcpolygon, d_field, "DOUBLE")
        
        #calculate the density of the count variable 
        #according to the size of the polygon.
        expression = "!" + attribute + "!/!" + a_field + "!"
        
        arcpy.CalculateField_management(fcpolygon, d_field, expression, "PYTHON3")



#calculateDensity("states48_albers", "POPULATION", workspace)

###################################################################### 
# Problem 2 (40 Points)
# 
# Given a line feature class (e.g.,river_network.shp) and a polygon feature class (e.g.,states.shp) in a geodatabase, 
# id or name field that could uniquely identify a feature in the polygon feature class
# and the value of the id field to select a polygon (e.g., Iowa) for using as a clip feature:
# this function clips the linear feature class by the selected polygon boundary,
# and then calculates and returns the total length of the line features (e.g., rivers) in miles for the selected polygon.
# 
# 1- Check whether the input variables are correct (e.g., the shape types and the name or id of the selected polygon)
# 2- Transform the projection of one to other if the line and polygon shapefiles have different projections
# 3- Identify the input coordinate systems unit of measurement (e.g., meters, feet) for an accurate distance calculation and conversion
#        
###################################################################### 
def estimateTotalLineLengthInPolygons(fcLine, fcClipPolygon, polygonIDFieldName, clipPolygonID, geodatabase = "assignment2.gdb"):
    arcpy.env.workspace = geodatabase

    #Quick exception handling for file type
    describeLine = arcpy.Describe(fcLine)
    describePoly = arcpy.Describe(fcClipPolygon)
    describeWork = arcpy.Describe(geodatabase)
    field_list = []
    
    for field in arcpy.ListFields(fcClipPolygon):
        field_list.append(field.name)
    
    if describePoly.shapetype != "Polygon" or describeWork.dataType != "Workspace":
        print("You did not give me the correct file types.")
        
    elif polygonIDFieldName not in field_list:
        print("{0} is not a field in {1}".format(polygonIDFieldName, fcClipPolygon))
        
    else: 
        #check if the projections are the same, if not, make them the same
        if describePoly.spatialReference.name != describeLine.spatialReference.name:
            
            # I believe we generally want the SR to be Geographic, so check and 
            #see if one FC has a geographic SR, and if so, change it to that SR 
            if describePoly.spatialReference.type == "Geographic":
                #new feature class
                fc_update = "fc_SR_transformed"
                
                # input fc, output fc, SR you desire
                # because the polygon SR is geographic, change the line fc to be the same
                arcpy.Project_management(fcLine, fc_update, describePoly.spatialReference)
                
                #set old feature class equal to the updated one
                arcpy.management.CopyFeatures(fc_update, fcLine)
                
            # either the line fc has a geographic SR, or both of them are projected.
            # either way, we continue
            else:
                #new feature class
                fc_update = "fc_SR_transformed"
                
                # input fc, output fc, SR you desire
                arcpy.Project_management(fcClipPolygon, fc_update, describeLine.spatialReference)
                
                #set old feature class equal to the updated one
                arcpy.management.CopyFeatures(fc_update, fcClipPolygon)
                
                
        #use update cursor delete all polygons that are not the one you want
        #this way we will be able to clip with just the polygon specified
        
        #create copy so we do not damage the original file
        fc_clip = "clipped_fcPolygon"
        arcpy.management.CopyFeatures(fcClipPolygon, fc_clip)
        
        with arcpy.da.UpdateCursor(fc_clip, [polygonIDFieldName]) as cursor:
            for row in cursor:
                #Check if the polygon is the one we want, otherwise delete it
                if row[0] != clipPolygonID:
                    #delete the polygon
                    cursor.deleteRow()
                
                else: 
                    continue
                
        del row
        del cursor
        
        
        #clip the line features with the individual polygon 
        
        #set new feature class 
        out_feature_class = "clipped_lines"

        # Execute Clip
        arcpy.Clip_analysis(fcLine, fc_clip, out_feature_class)
                
        #create table to hold the length
        out_table = "Line_length"
        stat_fields = [['Shape_Length', 'SUM']]

        arcpy.Statistics_analysis(out_feature_class, out_table, stat_fields)
        
        #Use search cursor to get the value for the sum of the rivers
        with arcpy.da.SearchCursor(out_table, ["SUM_Shape_Length"]) as cursor: 
            for row in cursor:
                #store value 
                line_length = row[0]

        del row
        del cursor
                                   
        #delete created feature classes and tables
        arcpy.management.Delete([out_table, out_feature_class, 
                                fc_clip])
                                   
        return line_length



#estimateTotalLineLengthInPolygons("north_america_rivers", "states48_albers", "STATE_NAME", "Iowa", workspace)

######################################################################
# Problem 3 (30 points)
# 
# Given an input point feature class, (i.e., eu_cities.shp) and a distance threshold and unit:
# Calculate the number of points within the distance threshold from each point (e.g., city),
# and append the count to a new field (attribute).
#
# 1- Identify the input coordinate systems unit of measurement (e.g., meters, feet, degrees) for an accurate distance calculation and conversion
# 2- If the coordinate system is geographic (latitude and longitude degrees) then calculate bearing (great circle) distance
#
######################################################################
def countObservationsWithinDistance(fcPoint, distance, distanceUnit, geodatabase = "assignment2.gdb"):
    arcpy.env.workspace = geodatabase

    #Quick exception handling for file type
    describePoint = arcpy.Describe(fcPoint)
    describeWork = arcpy.Describe(geodatabase)
    distance = float(distance)
    distanceUnit = distanceUnit.upper().replace(" ","")
    Unit_List = ["METERS","KILOMETERS","FEET","YARDS","MILES"]
    
    #see if the distance value can be turned into a float
    try:
        distance = float(distance)
    except:
        print("The distance needs to be a number")
        return 
        
    if describePoint.shapetype != "Point" or describeWork.dataType != "Workspace":
        print("You did not give me the correct file types.")
        
    elif distanceUnit.upper() not in Unit_List:
        print("{0} is not a feasible distance unit".format(distanceUnit))
        
    else:
        
        #create a buffer around the cities
        fc_buffer = "fcPoint_buffer"
        
        #buffer distance
        buffer = str(distance) + " {0}".format(distanceUnit)
        
        # specify the type of buffer analysis based on the SR of fcPoint
        if describePoint.spatialReference.type == "Projection":
            method = "PLANER"
        else:
            method = "GEODESIC"
            
        #execute the buffer
        arcpy.Buffer_analysis(fcPoint, fc_buffer, buffer, "#", "#", "#", "#", method)
        
        
        #specify new feature class
        fc_counts = "fc_cities_count"
        
        # this counts the number of points inside each buffer, creates 
        # new feature class with the counts. We calculate the counts, put them in a
        # dictionary, and then merge the counts with the original FC
        arcpy.SummarizeWithin_analysis(fc_buffer, fcPoint, fc_counts)
        
        #go through the new feature class, grab the ID and count of cities 
        # and put into a dictionary
        d_count = {}
        
        with arcpy.da.SearchCursor(fc_counts, ["FID_1", "Point_Count"]) as cursor: 
            for row in cursor:
                d_count[row[0]] = row[1]           
        del row
        del cursor
        
        #use this dictionary to update the original point feature class
        
        #create new field to hold our counts
        count_field = "Point_Count"
        arcpy.management.AddField(fcPoint, count_field, "SHORT")
        
        with arcpy.da.UpdateCursor(fcPoint, ["FID_1", count_field]) as cursor:
            for row in cursor:
                #Check if the geoid is in the dictionary
                if row[0] in d_count.keys():
                    #if the id exists, update the field with the value given by the key in the dictionary
                    row[1] = d_count[row[0]]

                #if the geoid is not in the dictionary, make it equal to zero
                else: 
                    row[1] = 0
                cursor.updateRow(row)

        del row
        del cursor
        
        #delete created feature classes and tables
        arcpy.management.Delete([fc_counts, fc_buffer])

######################################################################
# MAKE NO CHANGES BEYOND THIS POINT.
######################################################################
if __name__ == '__main__' and hawkid()[1] == "hawkid":
    print('### Error: YOU MUST provide your hawkid in the hawkid() function.')
    print('### Otherwise, the Autograder will assign 0 points.')

#countObservationsWithinDistance("eu_cities", 100, "MILES", workspace)

import arcpy
arcpy.env.overwriteOutput=True

# Note: Your hawkid is the login name you use to access ICON, and not
# your firsname-lastname@uiowa.edu email address.
# 
# def hawkid():
#     return(["Caglar Koylu", "ckoylu"])
###################################################################### 
def hawkid():
    return(["Brant Walker", "brantwalker"])

###################################################################### 
# Problem 1 (20 points)
# 
# Given an input point feature class (e.g., facilities or hospitals) and a polyline feature class, i.e., bike_routes:
# Calculate the distance of each facility to the closest bike route and append the value to a new field.
#        
###################################################################### 

def calculateDistanceFromPointsToPolylines(input_geodatabase, fcPoint, fcPolyline):
    arcpy.env.workspace = input_geodatabase
    
    #Quick exception handling for file type
    describePoint = arcpy.Describe(fcPoint)
    describePoly = arcpy.Describe(fcPolyline)
    
    if describePoint.shapetype != "Point" or describePoly.shapetype != "Polyline" or describeWork.dataType != "Workspace":
        print("You did not give me the correct file types.")
    
    else:
        in_features = fcPoint
        near_features = fcPolyline

        try:
            # set local variables
            in_features = fcPoint
            near_features = fcPolyline

            # execute the function, distance value is created in point 
            #feature class as field "NEAR_DIST" in meters
            arcpy.Near_analysis(in_features, near_features)

            # get geoprocessing messages
            print(arcpy.GetMessages())

        except arcpy.ExecuteError:
            print(arcpy.GetMessages(2))

        except Exception as err:
            print(err.args[0])

#calculateDistanceFromPointsToPolylines(input_geodatabase, "hospitals", "bike_routes")

######################################################################
# Problem 2 (30 points)
# 
# Given an input point feature class, i.e., facilities, with a field name (FACILITY) and a value ('NURSING HOME'), and a polygon feature class, i.e., block_groups:
# Count the number of the given type of point features (NURSING HOME) within each polygon and append the counts as a new field in the polygon feature class
#
######################################################################
def countPointsByTypeWithinPolygon(input_geodatabase, fcPoint, pointFieldName, pointFieldValue, fcPolygon):
    #  Set local variables
    arcpy.env.workspace = input_geodatabase
    
    #Quick exception handling for file type
    describePoint = arcpy.Describe(fcPoint)
    describePoly = arcpy.Describe(fcPolygon)
    field_list = []
    for field in arcpy.ListFields(fcPoint):
        field_list.append(field.name)
    
    if describePoint.shapetype != "Point" or describePoly.shapetype != "Polygon" or describeWork.dataType != "Workspace":
        print("You did not give me the correct file types.")
        
    elif pointFieldName not in field_list:
        print("{0} is not a field in {1}".format(pointFieldName, fcPoint))
    
    else:
        # create variables
        polys = fcPolygon
        points = fcPoint
        fcOut = "points_in_polygon"
        fcOutTable = "points_per_group"

        #count the number of points in each polygon
        arcpy.SummarizeWithin_analysis(polys, points, fcOut, '', 
                                       '', '', '', pointFieldName, 
                                       '', '', fcOutTable)

        #Create dictionary of pointFieldName values
        dict_pointFieldValue = {}

        #Put number of points (of specific type) in dictionary for each block group
        #In this case, we will use the join id in the table for the key, and then 
        #index the output feature class from summarize within
        
        #another exception handling: making sure pointValueName is in pointFieldname
        #at least once
        count = 0
        
        #create dictionary with keys = join ids and values = how many facilities 
        # of that type are in the block group
        with arcpy.da.SearchCursor(fcOutTable, ["Join_ID", pointFieldName, "Point_Count"]) as cursor: 
            for row in cursor:
                #check if the facility is the type we want
                if row[1] == pointFieldValue:
                    count += 1
                    dict_pointFieldValue[row[0]] = row[2]           
        del row
        del cursor
        
        #if the type we want does not show up at all, stop what we are doing
        if count == 0:
            return "{0} is not a value in {1}".format(pointValueName, pointFieldName)

        #now use update cursor to update the output feature class from summarize within
        # using the join_id value created as an index

        #create the field without white spaces that will hold the values
        fcOut_pointFieldValue = pointFieldValue.replace(" ", "_")
        
        arcpy.management.AddField(fcOut, fcOut_pointFieldValue, "SHORT")

        #using the dictionary we created, check each join_id and if it is in the dictionary
        #update the field we just created with the count in that block group
        with arcpy.da.UpdateCursor(fcOut, ["Join_ID", fcOut_pointFieldValue]) as cursor:
            for row in cursor:
                #Check if the geoid is in the dictionary
                if row[0] in dict_pointFieldValue.keys():
                    #if the id exists, update the field with the value given by the key in the dictionary
                    row[1] = dict_pointFieldValue[row[0]]

                #if the geoid is not in the dictionary, make it equal to zero
                else: 
                    row[1] = 0
                cursor.updateRow(row)

        del row
        del cursor

        #set the new feature class equal to the original feature class
        arcpy.management.CopyFeatures(fcOut, fcPolygon)

        #delete created feature classes and tables
        arcpy.management.Delete([fcOut, fcOutTable])

        #delete unnecessary fields that were created in the fcPolygon file
        arcpy.management.DeleteField(fcPolygon, ["Point_Count", "Join_ID"])

#countPointsByTypeWithinPolygon(input_geodatabase, "facilities", "FACILITY", "NURSING HOME", "block_groups")

######################################################################
# Problem 3 (50 points)
# 
# Given a polygon feature class, i.e., block_groups, and a point feature class, i.e., facilities,
# with a field name within point feature class that can distinguish categories of points (i.e., FACILITY);
# count the number of points for every type of point features (NURSING HOME, LIBRARY, HEALTH CENTER, etc.) within each polygon and
# append the counts to a new field with an abbreviation of the feature type (e.g., nursinghome, healthcenter) into the polygon feature class 

# HINT: If you find an easier solution to the problem than the steps below, feel free to implement.
# Below steps are not necessarily explaining all the code parts, but rather a logical workflow for you to get started.
# Therefore, you may have to write more code in between these steps.

# 1- Extract all distinct values of the attribute (e.g., FACILITY) from the point feature class and save it into a list
# 2- Go through the list of values:
#    a) Generate a shortened name for the point type using the value in the list by removing the white spaces and taking the first 13 characters of the values.
#    b) Create a field in polygon feature class using the shortened name of the point type value.
#    c) Perform a spatial join between polygon features and point features using the specific point type value on the attribute (e.g., FACILITY)
#    d) Join the counts back to the original polygon feature class, then calculate the field for the point type with the value of using the join count field.
#    e) Delete uncessary files and the fields that you generated through the process, including the spatial join outputs.  
######################################################################
def countCategoricalPointTypesWithinPolygons(fcPoint, pointFieldName, fcPolygon, workspace):
    arcpy.env.workspace = workspace
    
    #Quick exception handling for file type
    describePoint = arcpy.Describe(fcPoint)
    describePoly = arcpy.Describe(fcPolygon)
    describeWork = arcpy.Describe(workspace)
    field_list = []
    for field in arcpy.ListFields(fcPoint):
        field_list.append(field.name)
    
    if describePoint.shapetype != "Point" or describePoly.shapetype != "Polygon" or describeWork.dataType != "Workspace":
        print("You did not give me the correct file types.")
        
    elif pointFieldName not in field_list:
        print("{0} is not a field in {1}".format(pointFieldName, fcPoint))
    
    else:
        #set up variables
        polys = fcPolygon
        points = fcPoint
        fcOut = "points_in_polygon"
        fcOutTable = "points_per_group"

        #count the number of points in each polygon, in specific groups of facilities
        arcpy.SummarizeWithin_analysis(polys, points, fcOut, '', 
                                       '', '', '', pointFieldName, 
                                       '', '', fcOutTable)

        #Similar to before, create a dictionary with counts
        #We will use a nested dictionary that will take {ID:{facility type:count, facility type:count}}
        #in case there are more than one type of facility in a block group
        
        #Also, create a list of the types of facilities during this loop 
        #so we do not have to loop again in the future


        d = {}
        fields = []
        with arcpy.da.SearchCursor(fcOutTable, ["Join_ID", pointFieldName, "Point_Count"]) as cursor:
            for row in cursor:
                #clean up field name so it has no whitespaces and <14 letters
                #otherwise, arcpy will make the alias different from the field name
                field = row[1].replace(" ", "").replace("-","").lower()[:13]

                #create list of type of facility
                if field in fields:
                    continue
                else:
                    fields.append(field)

                #if the ID is in the output table (i.e. has at least one facility)
                #create a dictionary key for that ID so we can store the facility type and count
                if row[0] in d.keys():
                    continue
                else: 
                    d[row[0]] = {}
                    
                # store the count of each specific facility type inside the dictionary 
                # for the given ID 
                d[row[0]][field] = row[2]

        del row
        del cursor

        #now use update cursor to update the output feature class from summarize within
        # using the join_id value created as an index

        #for each facility type we have, create a field that will hold 
        # the number of that type of facility in each block group
        for field in fields:
            arcpy.management.AddField(fcOut, field, "SHORT")

        #append Join_ID to our fields list so we can use it in the update cursor 
        fields.append("Join_ID")

        
        #use update cursor to use the dictionary to create the counts for each 
        # type of facility in each respective block group (ID)
        
        #importantly - updating the output feature class from summary analysis
        #, which has the Join_ID field added
        with arcpy.da.UpdateCursor(fcOut, fields) as cursor:
            for row in cursor:
                #Check if the ID is in the dictionary
                #Join_ID is the last value of our "fields" list
                
                # row seems to have a tough time with row[fields.index("insert field value")],
                # so instead we create variables in this loop to avoid using
                # any extra tools
                
                ID = row[-1]
                if ID in d.keys():
                    #if Join_ID is in the dictionary, go through each type of facility
                    for field in fields[:-1]:
                        index = fields.index(field)
                        
                        #if that type of facility is a key in the nested dictionary 
                        # for that particular block group, update the 
                        # field for that type of facility in fcOut with the count
                        #otherwise, update the field for that type of facility as zero
                        if field in d[ID].keys():
                            row[index] = d[ID][field]
                        else:
                            row[index] = 0

                else:
                    #if the join_id is not in the dictionary, then the block group did 
                    # not have any points. Go through each of the created fields 
                    # for each type of facility and enter zero. 
                    for field in fields[:-1]:
                        index = fields.index(field)
                        row[index] = 0
                cursor.updateRow(row)

        del row
        del cursor

        #set the new feature class equal to the original feature class
        arcpy.management.CopyFeatures(fcOut, fcPolygon)

        #delete created feature classes and tables
        arcpy.management.Delete([fcOut, fcOutTable])

        #delete unnecessary fields that were created in the fcPolygon file
        arcpy.management.DeleteField(fcPolygon, ["Join_ID"])

    

######################################################################
# MAKE NO CHANGES BEYOND THIS POINT.
######################################################################
if __name__ == '__main__' and hawkid()[1] == "hawkid":
    print('### Error: YOU MUST provide your hawkid in the hawkid() function.')

#countCategoricalPointTypesWithinPolygons("facilities", "FACILITY", "block_groups", input_geodatabase)
    

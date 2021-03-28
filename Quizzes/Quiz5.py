import arcpy 

arcpy.env.overwriteOutput = True

#calculatePercentAreaOfPolygonAInPolygonB(input_geodatabase, fcPolygon1, fcPolygon2):

#Given an input polygon feature class, fcPolygonA (e.g., parks), and a second feature class, fcPolygonB (e.g., block_groups) :

#Calculate the percentage of the area of the first polygon features (fcPolygonA ) in the second polygon features (fcPolygonB), and 
#append the percentage of park area into a new field in the block groups feature class
#Make sure that your area calculations are as accurate as possible. 

def calculatePercentAreaOfPolygonAinPolygonB(input_geodatabase, fcPolygon1, fcPolygon2):
    desc1 = arcpy.Describe(fcPolygon1)
    desc2 = arcpy.Describe(fcPolygon2)
    desc3 = arcpy.Describe(input_geodatabase)
    
    if desc1.shapeType != "Polygon" or desc2.shapeType != "Polygon":
        print("You need to input polygons.")
    
    if desc3.dataType != "Workspace":
        print("You need to input a geodatabase or workspace.")
    
    #Continue on if the files were given correctly
    else:
        
        #intersect the two feature classes into one
        #Need to do this, especially when second feature class is block groups,
        #so we can add up all the parks in each specific block
        
        a_intersect_b = "fcPolygon1_intersect_fcPolygon2"
        arcpy.Intersect_analysis([fcPolygon2, fcPolygon1], a_intersect_b)
        
        
        #Create a field to hold the area calculation
        input_area_field = "fcPolygon1_area_sq_meters"
        arcpy.AddField_management(a_intersect_b, input_area_field, "DOUBLE")

        #Calculate the area of the field 
        arcpy.CalculateGeometryAttributes_management(a_intersect_b, 
                                                         [[input_area_field, "AREA_GEODESIC"]], 
                                                         "METERS")

        #get one fcPolygon1 area value for each block group (i.e. add them up)
        
        #Use dictionary, has unique keys, to add up area in each block group
        fcPolygon2_dict = {}
        
        #find the GEOID or FIPS field
        geoid_field = ""
        for field in arcpy.ListFields(fcPolygon2):
            #already found a geoid
            if geoid_field == "":
                if "geoid" in field.name.lower():
                    geoid_field = field.name
                elif "fips" in field.name.lower():
                    geoid_field = field.name
                    
                else:
                    "There is no GEOID or FIPS code in fcPolygon2"
        
        #use search cursor to go through each intersected item
        with arcpy.da.SearchCursor(a_intersect_b, [geoid_field, input_area_field]) as cursor:
            for row in cursor:
                #get the geoid value
                geoid = row[0]
                
                #check if geoid exists in dictionary, if so, add to it, if not, create a new key
                if geoid in fcPolygon2_dict.keys():
                    fcPolygon2_dict[geoid] += row[1]
                else:
                    fcPolygon2_dict[geoid] = row[1]
                    
        del row
        del cursor
        
        #create new field in fcPolygon 2 to hold our intersected Area value
        fc1_area_field = "fcPolygon1_area_sq_meters"
        arcpy.AddField_management(fcPolygon2, fc1_area_field, "DOUBLE")
        
        #use update cursor to fill in values of the field we just created
        with arcpy.da.UpdateCursor(fcPolygon2, [geoid_field, fc1_area_field]) as cursor:
            for row in cursor:
                #if geoid is in dictionary, add its value, otherwise add a zero
                if row[0] in fcPolygon2_dict.keys():
                    row[1] = fcPolygon2_dict[row[0]]
                else: 
                    row[1] = 0
                    
                #update it
                cursor.updateRow(row)
        
        del row
        del cursor
        
        #Create a new field to hold our calculated area percentage
        fc1_pct_field = "fcPolygon1_pct_area_sq_meters"
        arcpy.AddField_management(fcPolygon2, fc1_pct_field, "DOUBLE")
        
        #Calculate the field's area
        
        #find Polygon 2's area field name, otherwise create it
        fc2_area_field = ""
        for field in arcpy.ListFeatureClasses(fcPolygon2):
            if fc2_area_field == "":
                if "area" in field.name.lower():
                    fc2_area_field = field.name
                    
        #check if area field is still not found
        if fc2_area_field == "":
            #create the area field
            arcpy.AddField_management(fcPolygon2, "area_sq_meters", "DOUBLE")
            arcpy.CalculateGeometryAttributes_management(fcPolygon2, [["area_sq_meters", "AREA_GEODESIC"]],
                                                        "METERS")
            fc2_area_field = "area_sq_meters"
            
        #Calculate the field
        
        #create expression for the calculation 
        expression = "!" + fc1_area_field + "!/!" + fc2_area_field + "!"
        print(expression)
        
        arcpy.CalculateField_management(fcPolygon2, fc1_pct_field, expression, "PYTHON3")

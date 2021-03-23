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
# Problem 1 (10 Points)
#
# This function reads all the feature classes in a workspace (folder or geodatabase) and
# prints the name of each feature class and the geometry type of that feature class in the following format:
# 'states is a point feature class'

###################################################################### 
import arcpy

def printFeatureClassNames(workspace):
    #set the workspace correctly
    arcpy.env.workspace= workspace
    
    #Get list of all feature classes in the workspace
    featureclasses = arcpy.ListFeatureClasses()
          
    for feature in featureclasses:
        # Describe function allows me to return the geometry type
        desc = arcpy.Describe(feature)
        print("{0} is a {1} feature class".format(feature, desc.shapeType))

###################################################################### 
# Problem 2 (20 Points)
#
# This function reads all the attribute names in a feature class or shape file and
# prints the name of each attribute name and its type (e.g., integer, float, double)
# only if it is a numerical type

###################################################################### 
def printNumericalFieldNames(inputFc, workspace):
    #set the workspace
    arcpy.env.workspace = workspace
    
    #get a list of all the attributes in your input
    fieldlist = arcpy.ListFields(inputFc)
    
    #fields do not need to be described to find their type
    for field in fieldlist:
        #only print the field if it is a numerical type
        ty = field.type
        if ty == "Integer" or ty == "SmallInteger" or ty == "Double" or ty == "Float":
            print("{0} is the type {1}".format(field.name, field.type)) 

###################################################################### 
# Problem 3 (30 Points)
#
# Given a geodatabase with feature classes, and shape type (point, line or polygon) and an output geodatabase:
# this function creates a new geodatabase and copying only the feature classes with the given shape type into the new geodatabase

###################################################################### 
def exportFeatureClassesByShapeType(input_geodatabase, shapeType, output_geodatabase):
    
    featureclasses = arcpy.ListFeatureClasses(input_geodatabase)
    #Create a list to collect the features we want
    featuretype = []
    # for each feature, if it is of the type we want, add it to the list
    for feature in featureclasses:
        desc = arcpy.Describe(feature)
        if desc.shapeType == shapeType:
            featuretype.append(feature)
    #convert the list of features of the correct type into a geodatabase
    arcpy.conversion.FeatureClassToGeodatabase(featuretype, output_geodatabase)

###################################################################### 
# Problem 4 (40 Points)
#
# Given an input feature class or a shape file and a table in a geodatabase or a folder workspace,
# join the table to the feature class using one-to-one and export to a new feature class.
# Print the results of the joined output to show how many records matched and unmatched in the join operation. 

###################################################################### 
def exportAttributeJoin(inputFc, idFieldInputFc, inputTable, idFieldTable, workspace):
    
    arcpy.env.workspace = workspace
    arcpy.env.qualifiedFieldNames = False
    
    inFeatures = inputFc
    joinFieldFc = idFieldInputFc
    joinTable = inputTable
    # I never use this variable - what do the inputs represent?
    # I think I am confusing the inputs
    joinFieldTable = idFieldTable
    
    #Count the number of rows in the original file
    rows = arcpy.management.GetCount(joinTable)
    
    #Join the feature layer to the table, count the number of 
    #matches and the number of rows
    val_res = arcpy.ValidateJoin_management(inFeatures, joinFieldFc, joinTable, joinFieldTable)
    matched = int(val_res[0]) 
    row_count = int(val_res[1])
    
    unmatch = rows - matched
    
    print(arcpy.GetMessages()) # I think this will print messages about 
    #the join, but not sure what the messages will be

    # Validate the join returns matched rows before proceeding
    if matched >= 1:
        joined = arcpy.AddJoin_management(inFeatures, joinFieldFc, joinTable, joinFieldTable)

    # Copy the joined layer to a new permanent feature class
    arcpy.CopyFeatures_management(joined, "outFeatures")

    print(f"Output Features: {'outFeatures'} had matches {matched} and created {row_count} records, while {unmatch} records were unmatched.")

######################################################################
# MAKE NO CHANGES BEYOND THIS POINT.
######################################################################
if __name__ == '__main__' and hawkid()[1] == "hawkid":
    print('### Error: YOU MUST provide your hawkid in the hawkid() function.')

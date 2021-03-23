import arcpy

arcpy.env.workspace = r"C:\Users\Brant Walker\OneDrive - University of Iowa\CurrentClasses\Geospatial Programming\ArcPro Files\Quiz4\airports"

#Create a list of all the feature classes in the airport data
fclist = arcpy.ListFeatureClasses()
#Check and see what the list looks like
print(fclist)

#Create a buffer around certain types of data
#Iterate through each feature class
for fc in fclist:
    #create a name for the new buffer 
    inputname = fc[0:-4] #takes out .shp
    buffername = inputname + "_buffer.shp"
    
    #set the buffer = 0 for cases we don't need
    buffer=0
    #Check if the feature is one that needs a buffer
    #If so, create the buffer of an appropriate size
    if "seaplane" in fc:
        buffer = 7500
    elif "airport" in fc:
        buffer=15000
        
    #Create buffer
    # input, name of output, size of buffer and units
    arcpy.Buffer_analysis(fc, buffername, str(buffer) + ' Meters')

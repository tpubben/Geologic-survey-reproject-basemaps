import os
import arcpy
import re

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Basemap Tools"
        self.alias = "basemapTools"

        # List of tool classes associated with this toolbox
        self.tools = [mapConverter]


class mapConverter(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Find and Reproject Base Maps"
        self.description = "Finds all basemaps in a directory and reprojects to Canada Lambert Conformal Conic."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Folder to walk through
        param0 = arcpy.Parameter(
            displayName="Directory to walk",
            name="inputDir",
            parameterType="Required",
            direction="Input",
            datatype="DEWorkspace"
        )

        # Output geodatabase
        param1 = arcpy.Parameter(
            displayName="Output Geodatabase",
            name="outputGDB",
            parameterType="Required",
            direction="Input",
            datatype="DEWorkspace"
        )

        # Logfile Location
        param2 = arcpy.Parameter(
            displayName="Logfile Directory",
            name="LogDir",
            parameterType="Required",
            direction="Input",
            datatype="DEWorkspace"
        )

        params = [param0, param1, param2]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        #create a log file to be written to
        arcpy.env.overwriteOutput = True

        logName = parameters[2].valueAsText+'\\ProjectLog.txt'

        newLog = open(logName, 'w')
        newLog.close()

        #Walk the folder and create a list of names for feature datasets based on NTS map folders
        inputFolder = parameters[0].valueAsText
        outputGDB = parameters[1].valueAsText
        sr = arcpy.SpatialReference("P:/Energy/LHA09/LCC_Bases/Canada_Lambert_Conformal_Conic.prj")

        ntsFolders = []
        for child in os.listdir(inputFolder):
            child = child.split('_')
            child = 'NTS'+child[0]
            ntsFolders.append(child)

        #Create feature datasets in the file geodatabase for each of the NTS maps

        for item in ntsFolders:
            arcpy.CreateFeatureDataset_management(outputGDB, item, sr)

            #Drill down in top level folders to find "bases" and "Canvec" folders. This is the main loop.
            topLevelFolders = os.listdir(inputFolder)

        with open(logName, 'a') as logFile:
            logFile.write('---------BEGIN SEARCHING FOR BASES FOLDERS---------\n\n')
        logFile.close()

        for fldr in topLevelFolders:
            try:
                dirList = os.listdir(inputFolder+'\\'+fldr)
                if "Bases" in dirList:
                    baseFldr = inputFolder+'\\'+fldr+'\\Bases'
                    baseFldrList = os.listdir(baseFldr)
                    if "Canvec" in baseFldrList:
                        canvecFldr = baseFldr + '\\Canvec'
                    else:
                        with open(logName, 'a') as logFile:
                            logFile.write(fldr+' Has no Canvec Folder\n')
                        logFile.close()

                else:
                    with open(logName, 'a') as logFile:
                        logFile.write(fldr+" has no BASES folder!\n")
                    logFile.close()
            except:
                with open(logName) as logFile:
                    logFile.write(fldr+" Has had some other error.")
                logFile.close()


            arcpy.env.workspace = canvecFldr

            # Begin the projections
            with open(logName, 'a') as logFile:
                logFile.write('---------BEGIN PROJECTING FEATURES '+fldr+' ---------\n')
            logFile.close()

            for shpFile in arcpy.ListFeatureClasses():

                try:
                    shpSplit = shpFile.split('.')[0]
                    shpSplit = 'NTS'+shpSplit
                    FDSname = 'NTS'+fldr.split('_')[0]
                    outFDS = os.path.join(outputGDB, FDSname)
                    outFC = os.path.join(outFDS, shpSplit)
                    arcpy.Project_management(shpFile, outFC, sr)
                except:
                    with open(logName, 'a') as logFile:
                        logFile.write(shpFile+' Has had an error while projecting\n')
                    logFile.close()

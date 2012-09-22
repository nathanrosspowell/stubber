#!/usr/bin/python
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# build.py Authored by Nathan Ross Powell.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Imports.
import sys
import os
import yaml
import operator
# Local.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Super Build class that does all the set up work and writing.
class Build:
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Initalise the class with yaml folder and source code folder.
    def __init__( self, yamlFolder, sourceFolder ):
        self.yamlFolder = yamlFolder
        self.sourceFolder = sourceFolder

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # A virtual init function.
    def initBase( self ):
        pass

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # See where the yaml files live.
    def walkYamlFolder( self ):
        structure = {}
        for path, dirs, files in os.walk( self.yamlFolder ):
            s = os.path.splitext
            # Only get .yaml files.
            yamlFiles = [ f for f in files if s( f )[ 1 ] == ".yaml" ]
            if len( yamlFiles ):
                localPath = path.replace( self.yamlFolder, "" )
                structure[ localPath ] = yamlFiles
        self.structure = structure

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Replicate the structure of the yaml folder in the source folder.
    def makeDirs( self ):
        for localPath in self.structure:
            newDir = os.path.join( self.sourceFolder, localPath )
            if not os.path.exists( newDir ):
                try:
                    os.makedirs( newDir )
                except OSError as e:
                    print "Couldn't make files"
                    print "    ", e

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Make one list of all the needed file info.
    def makeBuildList( self ):
        join = os.path.join
        buildList = []
        for path, files in self.structure.iteritems():
            yamlPath = join( self.yamlFolder, path )
            sourcePath = join( self.sourceFolder, path )
            yamlList = []
            # Add the full path to each YAML file.
            for yamlFile in ( join( yamlPath, f ) for f in files ):
                 yamlList.append( yamlFile )
            if len( yamlList ):
                buildList.append( ( sourcePath, yamlList ) )
        if len( buildList ) is 0:
            raise Exception( "No Items to build. Check Paths" )
        self.buildList = buildList

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Get a dictionary from a YAML file.
    def getDict( self, fileName ):
        yamlDict = {}
        if os.path.isfile( fileName ):
            with open( fileName, 'r' ) as file:
                yamlDict = yaml.load( file.read() )
        else:
            print "No file", fileName
        return yamlDict

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # For each file, pass it to the buildFileData function, then write it out.
    def build( self ):
        self.initBase()
        base = os.path.basename
        split = os.path.splitext
        for path, files in self.buildList:
            for file in files:
                fileDict = self.getDict( file )
                fileData = self.buildFileData( path, file, fileDict )
                self.writeOutFile( path, file, fileData, fileDict )

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Tidy up the file then write it to disk.
    def writeOutFile( self, path, file, fileData, fileDict ):
        data = self.cleanUpWhitespace( fileData )
        folder = os.path.join( path, self.getFileName( fileDict[ "name" ] ) )
        sourceFile = "%s%s" % ( folder, self.fileExtension() )
        with open( sourceFile, 'w' ) as file:
            file.write( data )

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Break up any camel casing to be underscore seperated.
    def getFileName( self, string ): 
        n = ''
        for i in string:
            # Add in an '_' before each capital letter, except the first one.
            n = '%s%s%s' % ( n, "_" if len( n ) and i.isupper() else "", i ) 
        return n.strip().lower()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Remove duplicates of spacing (not leading) and line returns.
    def cleanUpWhitespace( self, fileData ):
        data = []
        addBlank = False
        for line in fileData.splitlines():
            if len( line ):
                if addBlank:
                    data.append( "\n" )
                    addBlank = False
                # Store the number of leading spaces that will get stripped.
                lead = len( line ) - len( line.lstrip() )
                # Reduce all spacing down to single spaces.
                cleanLine = " ".join( line.split() )
                # Add the leading spaces and the cleaned up line.
                data.append( "%s%s\n" % ( " " * lead, cleanLine ) )
            else:
                addBlank = True
        return "".join( data )

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Helper function to build.
def builder( yamlFolder, sourceFolder, buildClass ):
    build = buildClass( yamlFolder, sourceFolder )
    build.walkYamlFolder()
    build.makeDirs()
    build.makeBuildList()
    build.build()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Helper wrapper on builder, just pass the class.
def testBuild( buildClass ):
    yamlFolder = "/home/nathan/projects/stubber/stubs/"
    sourceFolder = "/home/nathan/projects/stubber/source/"
    builder( yamlFolder, sourceFolder, buildClass )

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Test using BuildCpp.
if __name__ == "__main__":
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Imports needed for the test.
    from buildCpp import BuildCpp
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Our forces settings for the test.
    testBuild( BuildCpp )

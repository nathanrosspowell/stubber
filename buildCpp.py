#!/usr/bin/python
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# buildCpp.py Authored by Nathan Ross Powell.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Imports.
# Local.
from build import Build

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Get feed files from the net and save them off with a better name.
class BuildCpp( Build ):
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Virtual init function to define instance data.
    def initBase( self ):
        self.convert = {
            "List" : "std::vector< %s >",
            "Map" : "std::map< %s, %s >",
        }
        self.mod = {
            "ref" : "&",
            "ptr" : "*",
            "refptr" : "&*",
            "ptrref" : "*&",
            "ptrptr" : "**",
            "ptrptrptr" : "***",
        }

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # What to save these files as.
    def fileExtension( self ):
        return ".cpp"

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # The internal build function.
    def buildFileData( self, path, file, fileData ):
        fileNameExt = "%s%s" % ( fileData[ "name" ], self.fileExtension() )
        fileNameCaps = fileData[ "name" ].upper()
        fileNameTitle = fileData[ "name" ].title()
        superClasses = self.superClass( fileData.get( "supers", [] ) )
        headers = ""
        forwardDecs = ""
        templateParams = self.templateParams( fileData.get( "template", [] ) )
        template = self.template( templateParams )
        funcs = lambda x: fileData[ "functions" ].get( x, {} )
        publicFuncs = self.makeFuncs( "public", funcs( "public" ) )
        protectedFuncs = self.makeFuncs( "protected", funcs( "protected" ) )
        privateFuncs = self.makeFuncs( "private", funcs( "private" ) )
        mem = lambda x: fileData[ "members" ].get( x, {} )
        publicMems = self.makeMems( "public", mem( "public" ) )
        protectedMems = self.makeMems( "protected", mem( "protected" ) )
        privateMems = self.makeMems( "private", mem( "private" ) )
        return self.fileLayout % locals()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Figure out what the format of the template parameters are.
    def templateParams( self, data ):
        if len( data ):
            params = "<"
            addSep = False
            for d in data:
                sep = "," if addSep else ""
                type = self.type( d[ "type" ] )
                # Format an optional default parameters.
                default = str( d.get( "default", "" ) )
                if len( default ):
                    default = " = %s" % ( default, )
                # Append each parameter.
                params += "%s %s %s%s" % ( sep, type, d[ "name" ], default )
                addSep = True
            params += " >"
            return params
        return ""

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # The class/function "template< ... >" syntax.
    def template( self, params ):
        if len( params):
            return "template%s\n" % ( params, )
        return ""

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Recursivly convert to correct types. Handles templates and type modifers.
    def type( self, type ):
        # "of" specs a template. e.g. "List of int", "Map of int, int"
        types = type.split( " of ", 1 )
        split = types[ 0 ].split()
        # Look for a type modifier. e.g. ptr-type = type* 
        mod = ""
        for i, s in enumerate( split ):
            mods = s.split( "-" )
            if len( mods ) > 1:
                # Remove and store the modifier.
                mod = mods[ 0 ]
                # Edit split via index, not the copy in this loop
                split[ i ] = mods[ 1 ]
        # Rebuild the type with no modifiers.
        types[ 0 ] = " ".join( split )
        # Get the final modifier string, if there is one.
        mod = self.mod.get( mod.lower(), "" )
        # If there was an "of", process the template params. 
        if len( types ) > 1:
            # Split up all the template arguments.
            temp = types[ 1 ].split( "," )
            # Convert each param with self.type( ... )
            templates = [ self.type( t.strip() ) for t in temp ]
            # Format for a template type that isn't in self.convert.
            default = "%s< %%s >" % ( types[ 0 ], )
            # Repace any types in self.convery. e.g. List = std::vector
            templateType = self.convert.get( types[ 0 ], default )
            # Format with a tuple of the templates list and any modifier.
            return "%s%s" % ( templateType % tuple( templates ), mod )
        return "%s%s" % ( types[ 0 ], mod )

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Make the inheritance syntax.
    def superClass( self, supers ):
        if len( supers ):
            sup = " :"
            addSep = False
            for s in supers:
                format = ( "," if addSep else "", self.type( s ) )
                sup += "%s public %s" % format
                addSep = True
            return sup
        else:
            return ""

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Build a function decleration.
    def processFunction( self, name, values ):
        value = lambda x: values.get( x, "" )
        retType = lambda x: self.type( values.get( x, "void" ) )
        args = ""
        seperate = False
        for name, type in values.get( "args", {} ).iteritems():
            t = self.type( type )
            args += "%s%s %s" % ( ", " if seperate else "", t, name )
            seperate = True
        if len( args ):
            args = " %s " % ( args, )
        type = ( "%s %s" % ( value( "dec" ), retType( "return" ) ) ).strip()
        mod = " %s" % ( value( "mod" ), ) if value( "mod" ) else ""
        return ( "%(type)s %(name)s(%(args)s)%(mod)s;" % locals() ).strip()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Build a member decleration.
    def processMember( self, name, type ):
        type = self.type( type )
        return ( "%(type)s m_%(name)s;" % locals() ).strip()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Function specific wrapper.
    def makeFuncs( self, name, data ):
        return self.makeSection( name, data, True )

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Member specific wrapper.
    def makeMems( self, name, data ):
        return self.makeSection( name, data, False )

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Make a encapsulated section.
    def makeSection( self, name, data, funcs ):
        items = ""
        nameTitle = name.title()
        section = "functions" if funcs else "members"
        for item, values in data.iteritems():
            if funcs:
                items += "    %s\n" % ( self.processFunction( item, values ), )
            else:
                items += "    %s\n" % ( self.processMember( item, values ), )
        return """
// %(nameTitle)s %(section)s.
%(name)s:
%(items)s"""[ 1 : ] % locals() if len( items ) else ""

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # The main template for the header file.
    fileLayout = """
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// %(fileNameExt)s Authored by Nathan Ross Powell.
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#ifndef __HEADER_%(fileNameCaps)s__
#define __HEADER_%(fileNameCaps)s__

%(headers)s
%(forwardDecs)s

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Definition of %(fileNameTitle)s%(templateParams)s.
%(template)sclass %(fileNameTitle)s %(superClasses)s
{
%(publicFuncs)s
%(protectedFuncs)s
%(privateFuncs)s
%(publicMems)s
%(protectedMems)s
%(privateMems)s
};

#endif __HEADER_%(fileNameCaps)s__
"""[ 1: -1 ]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Test run.
if __name__ == "__main__":
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Imports needed for test.
    from build import testBuild
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Test.
    testBuild( BuildCpp )

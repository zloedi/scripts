import sys
import subprocess
import platform

HOST_DIR = "../zhost/"
LIBS_DIR = HOST_DIR + "3rdparty/"

def Cmd( cmd ):
	#print( cmd )
	subprocess.Popen( cmd, shell = True ).communicate()

def Is64bitOS():
    return platform.architecture()[0] == "64bit"

def IsWindows():
    return platform.system()[0:9] == "CYGWIN_NT"

def NormalizePath( path ):
    return path

def HostCopyProperSDL( m32 = False ):
    # this assumes 64bit mingw. assumes too much
    Cmd( "rm ./SDL2.dll" )
    if m32:
        Cmd( "cp " + LIBS_DIR + "SDL2/i686-w64-mingw32/bin/SDL2.dll ./" )
    else:
        Cmd( "cp " + LIBS_DIR + "SDL2/x86_64-w64-mingw32/bin/SDL2.dll ./" )
    Cmd( "chmod +x ./SDL2.dll" )

def GetHostLflags( m32 ):
    lflags = ""
    if IsWindows():
        #lflags += " -L" + LIBS_DIR + "freetype/lib"
        if m32:
            lflags += " -L" + LIBS_DIR + "SDL2/lib/x86"
        else:
            lflags += " -L" + LIBS_DIR + "SDL2/lib/x64"
        #lflags += " -lfreetype"
        # keep the order here
        #lflags += " -lmingw32 -lSDL2main -lSDL2 -mwindows"
        lflags += " -lSDL2main -lSDL2 -mwindows"
        lflags += " -lopengl32"
    else:
        lflags += " `sdl2-config --libs`"
        lflags += " -lGL"
        lflags += " -lfreetype"
    return lflags

def GetHostCflags():
    cflags = " -I" + HOST_DIR
    cflags += " -I" + LIBS_DIR
    if IsWindows():
		#cflags += " -I" + LIBS_DIR + "freetype/include/freetype2/freetype"
        cflags += " -I" + LIBS_DIR + "SDL2/include"
    else:
        cflags += " `sdl2-config --cflags` `freetype-config --cflags`"
    return cflags

def GetHostObjs():
    return [
        "allocator",
        "cmd",
        "com_files",
        "com_str",
        "com_tokens",
        "con_draw",
        "con_font",
        "con_log",
        "con_main",
        "con_prompt",
        "r_sdl",
        "sys",
        "var",
        "util",
    ]

def CPPCompiler( m32 ):
    if IsWindows():
        if m32: 
            # 32 bit target
            cc = "i686-w64-mingw32-g++.exe"
        else:
            # 64 bit target
            cc = "x86_64-w64-mingw32-g++"
    else:
		cc = "g++"

    return cc

# TODO: pick proper linker/compiler for -m32 and -m64
def CCompiler( m32 ):
    if IsWindows():
        if m32:
            # 32 bit target
            cc = "i686-w64-mingw32-gcc.exe"
        else:
            # 64 bit target
            cc = "x86_64-w64-mingw32-gcc"
    else:
        cc = "gcc"

    return cc

def EmitLink( linker, target, targetDir, linkerFlags ):

    if IsWindows():
        linkerFlags += " -static-libgcc -static-libstdc++"

    return """

""" + target + """: $(OBJS)
	@echo ----------------- Compile successful -----------------
	@echo Linking $@... ; """ + linker + """ -o $@ $(OBJS) """ + linkerFlags + """
	@echo Copying $@ to \"""" + targetDir + """\" ; cp $@ \"""" + targetDir + """\"
"""

def CCObjExt( obj, m32 ):
    cc = CCompiler( m32 )
    o = obj
    ext = ".c"

    if len( obj ) >= 4 and obj[-4:] == ".cpp":
        cc = CPPCompiler()
        o = obj[:-4]
        ext = ".cpp"
    elif len( obj ) >= 2 and obj[-2:] == ".c":
        o = obj[:-2]

    return cc, o, ext

def EmitObjsAndDeps( dir, objs, appCFlags, fileUID, m32 ):
    out = ""
    for obj in objs:
        cflags = appCFlags + " -DFILE_UID=" + str( fileUID )

        cflags += " -Wall"
        cflags += " -Werror -Wformat=2"

        cc, o, ext = CCObjExt( obj, m32 )
        if cc == CCompiler( m32 ):
            cflags += " -std=gnu99"
            cflags += " -Woverride-init -Wold-style-declaration -Wmissing-parameter-type"
        elif cc == CPPCompiler():
            cflags += " -std=c++11"
        # get .c files dependencies
        cmd = cc + " -MM " + cflags + " \"" + dir + o + ext + "\""
        depString = subprocess.Popen( cmd, shell = True, stdout = subprocess.PIPE ).communicate()[0]
        out += '$(OUT_DIR)' + depString
        out += "\t@echo compiling $< ; "        + cc + " $(GLOBAL_CFLAGS) " + cflags + " -o $@ -c $<\n"
#out += "\t@echo assembly listing $< ; " + cc + " $(GLOBAL_CFLAGS) " + cflags + " -S -masm=intel -o $@.s -c $<\n"
        out += "\n"
        fileUID += 1
    return fileUID, out

def Configure( codeDir, 
               appObjs, 
               appCFlags, 
               appLinkerFlags, 
               targetDir, 
               targetName, 
               outputDir,
               m32 = False ):
    makefile      = outputDir + 'Makefile'

    debugDir      = codeDir + 'Debug/'
    debugTarget   = debugDir + targetName + '_dbg'

    releaseDir    = codeDir + 'Release/'
    releaseTarget = releaseDir + targetName
    
    profileDir    = codeDir + 'Profile/'
    profileTarget = profileDir + targetName + '_prof'
    
    globalFlags        = ""#-DALLOCATOR_FATAL_ERROR Z_FatalError "
    globalDebugFlags   = globalFlags + "-g -O0 -D_DEBUG"
    globalReleaseFlags = globalFlags + "-O3 -fno-strict-aliasing -ffast-math -funroll-loops -fomit-frame-pointer -fexpensive-optimizations"
    globalProfileFlags = globalFlags + "-O3 -pg -fno-strict-aliasing -ffast-math -funroll-loops -fexpensive-optimizations"    

    out = ''
    out += '''\

#####################################################################################

debug_app:
	@mkdir ''' + targetDir + ''' -p
	@mkdir ''' + debugDir + ''' -p
	@echo ----------------- Building Debug --------------- ; \\
	$(MAKE) -f "''' + makefile + '" "' + debugTarget + '" ' +\
        'OUT_DIR="' + debugDir + '" ' +\
        'GLOBAL_CFLAGS="' + globalDebugFlags + '" ' +\
        '''

release_app:
	@mkdir ''' + targetDir + ''' -p
	@mkdir ''' + releaseDir + ''' -p
	@echo ----------------- Building Release --------------- ; \\
	$(MAKE) -f ''' + makefile + ' "' + releaseTarget + '" ' +\
        'OUT_DIR="' + releaseDir + '" ' +\
        'GLOBAL_CFLAGS="' + globalReleaseFlags + '" ' +\
        '''

profile_app:
	@mkdir ''' + targetDir + ''' -p
	@mkdir ''' + profileDir + ''' -p
	@echo ----------------- Building Profile --------------- ; \\
	$(MAKE) -f ''' + makefile + ' "' + profileTarget + '" ' +\
        'OUT_DIR="' + profileDir + '" ' +\
        'GLOBAL_CFLAGS="' + globalProfileFlags + '" ' +\
        '''

all: debug_app release_app profile_app

clean:
	@rm "''' + debugDir + '''"*.o -vf
	@rm "''' + debugTarget + '''" -vf
	@rm "''' + releaseDir + '''"*.o -vf
	@rm "''' + releaseTarget + '''" -vf
	@rm "''' + profileDir + '''"*.o -vf
	@rm "''' + profileTarget + '''" -vf
	@rm "''' + targetName + '''_dbg.exe" -vf
	@rm "''' + targetName + '''_prof.exe" -vf
	@rm "''' + targetName + '''.exe" -vf

#####################################################################################

OBJS=\\
'''
    linker = CCompiler( m32 )

    for lst in appObjs:
        for obj in lst[1]:
            cc, o, ext = CCObjExt( obj, m32 )
            if cc == CPPCompiler( m32 ):
                linker = CPPCompiler( m32 )
            out += '\t$(OUT_DIR)' + o + '.o\\\n'

    out += "\n"

    out += EmitLink( linker, debugTarget, targetDir, appLinkerFlags )
    out += EmitLink( linker, releaseTarget, targetDir, appLinkerFlags )
    out += EmitLink( linker, profileTarget, targetDir, appLinkerFlags + " -pg" )
    out += '''

#####################################################################################

'''
    fileUID = 0

    for lst in appObjs:
        fileUID, res = EmitObjsAndDeps( lst[0], lst[1], appCFlags, fileUID, m32 )
        out += res

    file = open( makefile, 'w' )
    file.write( out )
    file.close()
    print "Created Makefile"

def PostConfigure( m32, useSDL ):
    Cmd( "make clean" );
    if useSDL and IsWindows():
        HostCopyProperSDL( m32 )

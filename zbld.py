import sys
import subprocess
import platform

LIBS_DIR = "3rdparty/"

def Cmd( cmd ):
	#print( cmd )
	subprocess.Popen( cmd, shell = True ).communicate()

def Is64bitOS():
    return platform.architecture()[0] == "64bit"

def IsWindows():
    return platform.system()[0:9] == "CYGWIN_NT"

def NormalizePath( path ):
    return path

def HostCopyProperSDLAndFriends( hostDir, m32 = False ):
    # this assumes 64bit mingw. assumes too much
    Cmd( "rm ./SDL2.dll" )
    Cmd( "rm ./libogg-0.dll" )
    Cmd( "rm ./libvorbis-0.dll" )
    Cmd( "rm ./libvorbisfile-3.dll" )
    Cmd( "rm ./gamecontrollerdb.txt" )
    if m32:
        Cmd( "cp " + hostDir + LIBS_DIR + "SDL2/i686-w64-mingw32/bin/SDL2.dll ./" )
        Cmd( "cp " + hostDir + LIBS_DIR + "SDL2_mixer/i686-w64-mingw32/bin/libogg-0.dll ./" )
        Cmd( "cp " + hostDir + LIBS_DIR + "SDL2_mixer/i686-w64-mingw32/bin/libvorbis-0.dll ./" )
        Cmd( "cp " + hostDir + LIBS_DIR + "SDL2_mixer/i686-w64-mingw32/bin/libvorbisfile-3.dll ./" )
    else:
        Cmd( "cp " + hostDir + LIBS_DIR + "SDL2/x86_64-w64-mingw32/bin/SDL2.dll ./" )
        Cmd( "cp " + hostDir + LIBS_DIR + "SDL2_mixer/x86_64-w64-mingw32/bin/libogg-0.dll ./" )
        Cmd( "cp " + hostDir + LIBS_DIR + "SDL2_mixer/x86_64-w64-mingw32/bin/libvorbis-0.dll ./" )
        Cmd( "cp " + hostDir + LIBS_DIR + "SDL2_mixer/x86_64-w64-mingw32/bin/libvorbisfile-3.dll ./" )
    Cmd( "cp "  + hostDir + LIBS_DIR + "gamecontrollerdb.txt ./" )
    Cmd( "chmod +x ./SDL2.dll" )

def GetHostLflags( hostDir, m32 = False ):
    lflags = ""
    if IsWindows():
        #lflags += " -L" + hostDir + LIBS_DIR + "freetype/lib"
        directory = hostDir + LIBS_DIR
        if m32:
            prefix = directory + "SDL2/i686-w64-mingw32/"
            lflags += " -L" + directory + "SDL2_mixer/i686-w64-mingw32/lib"
        else:
            prefix = directory + "SDL2/x86_64-w64-mingw32/"
            lflags += " -L" + directory + "SDL2_mixer/x86_64-w64-mingw32/lib"
        lflags += " `" + prefix + "bin/sdl2-config --prefix=" + prefix + " --static-libs`"
        #lflags += " -lfreetype"
        lflags += " -lSDL2_mixer"
        lflags += " -lwinmm"
    else:
        lflags += " `sdl2-config --libs`"
        lflags += " -lSDL2_mixer"
        lflags += " -lGL"
        lflags += " -lfreetype"
        lflags += " -lm"
    return lflags

def GetHostCflags( hostDir, m32 ):
    cflags = " -I" + hostDir
    cflags += " -I" + hostDir + LIBS_DIR
    if IsWindows():
	#cflags += " -I" + hostDir + LIBS_DIR + "freetype/include/freetype2/freetype"
        #cflags += " -I" + hostDir + LIBS_DIR + "SDL2/include"
        directory = hostDir + LIBS_DIR
        if m32:
            prefix = directory + "SDL2/i686-w64-mingw32/"
            cflags += " -I" + directory + "SDL2_mixer/i686-w64-mingw32/include"
        else:
            prefix = directory + "SDL2/x86_64-w64-mingw32/"
            cflags += " -I" + directory + "SDL2_mixer/x86_64-w64-mingw32/include"
        cflags += " `" + prefix + "bin/sdl2-config --prefix=" + prefix + " --cflags`"
    else:
        cflags += " `sdl2-config --cflags` `freetype-config --cflags`"
    return cflags

def GetHostObjs():
    objs = [
        "allocator",
        "cmd",
        "com_files",
        "com_random",
        "com_raster",
        "com_str",
        "com_tokens",
        "con_draw",
        "con_font",
        "con_log",
        "con_main",
        "con_prompt",
        "events",
        "input",
        "r_sdl",
        "sys_common",
        "util",
        "var",
    ]
    if IsWindows():
        objs.append( "sys_windows" )
    else:
        objs.append( "sys_unix" )
    return objs

def Windres( m32 ):
    if IsWindows():
        if m32: 
            # 32 bit target
            wr = "i686-w64-mingw32-windres"
        else:
            # 64 bit target
            wr = "x86_64-w64-mingw32-windres"
    else:
        wr = "NONE"

    return wr

def CPPCompiler( m32 ):
    if IsWindows():
        if m32: 
            # 32 bit target
            cc = "i686-w64-mingw32-g++"
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
            cc = "i686-w64-mingw32-gcc"
        else:
            # 64 bit target
            cc = "x86_64-w64-mingw32-gcc"
    else:
        cc = "gcc"

    return cc

def EmitLink( linker, target, targetDir, linkerFlags ):

    if IsWindows():
        linkerFlags += " -static -static-libgcc -static-libstdc++"

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
        cc = CPPCompiler( m32 )
        o = obj[:-4]
        ext = ".cpp"
    elif len( obj ) >= 2 and obj[-2:] == ".c":
        o = obj[:-2]
    elif len( obj ) >= 3 and obj[-3:] == ".rc":
        cc = Windres( m32 )
        o = obj[:-3]
        ext = ".rc"

    return cc, o, ext

def EmitObjsAndDeps( dir, objs, appCFlags, fileUID, m32 ):
    out = ""
    for obj in objs:
        cflags = appCFlags + " -DFILE_UID=" + str( fileUID )

        cflags += " -Wall -Wextra -Wformat=2" # -Wconversion"

        cc, o, ext = CCObjExt( obj, m32 )
        if cc == Windres( m32 ):
            out += '$(OUT_DIR)' + o + ".res: " + o + ext + "\n"
            out += "\t@echo compiling resource $< ; "        + cc + " $< -O coff -o $@\n"
        else:
            if cc == CCompiler( m32 ):
                cflags += " -std=gnu99"
                cflags += " -Woverride-init -Wold-style-declaration -Wmissing-parameter-type"
                cflags += " -Wno-misleading-indentation"
            elif cc == CPPCompiler( m32 ):
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

def Configure( appObjs, 
               codeDir = "./", 
               appCFlags = "", 
               appLinkerFlags = "",
               targetDir = "./", 
               targetName = "zhost", 
               outputDir = "./",
               useHost = True,
               hostDir = "../zhost/",
               m32 = False ):
    if useHost:
        appObjs = [( hostDir, GetHostObjs() )] + appObjs
        appCFlags += GetHostCflags( hostDir, m32 ) 
        appLinkerFlags += GetHostLflags( hostDir )

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
	$(MAKE) -j4 -f "''' + makefile + '" "' + debugTarget + '" ' +\
        'OUT_DIR="' + debugDir + '" ' +\
        'GLOBAL_CFLAGS="' + globalDebugFlags + '" ' +\
        '''

release_app:
	@mkdir ''' + targetDir + ''' -p
	@mkdir ''' + releaseDir + ''' -p
	@echo ----------------- Building Release --------------- ; \\
	$(MAKE) -j4 -f ''' + makefile + ' "' + releaseTarget + '" ' +\
        'OUT_DIR="' + releaseDir + '" ' +\
        'GLOBAL_CFLAGS="' + globalReleaseFlags + '" ' +\
        '''

profile_app:
	@mkdir ''' + targetDir + ''' -p
	@mkdir ''' + profileDir + ''' -p
	@echo ----------------- Building Profile --------------- ; \\
	$(MAKE) -j4 -f ''' + makefile + ' "' + profileTarget + '" ' +\
        'OUT_DIR="' + profileDir + '" ' +\
        'GLOBAL_CFLAGS="' + globalProfileFlags + '" ' +\
        '''

all: debug_app release_app profile_app

clean:
	@rm "''' + debugDir + '''"*.o -vf
	@rm "''' + debugDir + '''"*.res -vf
	@rm "''' + debugTarget + '''" -vf
	@rm "''' + releaseDir + '''"*.o -vf
	@rm "''' + releaseDir + '''"*.res -vf
	@rm "''' + releaseTarget + '''" -vf
	@rm "''' + profileDir + '''"*.o -vf
	@rm "''' + profileDir + '''"*.res -vf
	@rm "''' + profileTarget + '''" -vf
	@rm "''' + targetName + '''_dbg" -vf
	@rm "''' + targetName + '''_prof" -vf
	@rm "''' + targetName + '''" -vf
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
            if ext == '.rc':
                out += '\t$(OUT_DIR)' + o + '.res\\\n'
            else:
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

def PostConfigure( hostDir = "../zhost/", m32 = False, useSDL = True ):
    Cmd( "make clean" );
    if useSDL and IsWindows():
        HostCopyProperSDLAndFriends( hostDir, m32 )

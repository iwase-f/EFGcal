#!/usr/bin/env python
import sys, os, string, array

class Lapw5:
    def __init__(self, head = None, complex = 0):
        self.tails = ["clmsum", "clmval", "vcoul", "r2v", "vtotal"]
        if head:
            self.head = head
        else:
            self.head = os.path.basename(os.getcwd())

        self.shells = [3, 3, 3]
        if val:
            self.val = val
        else:   
            self.val = 0

        self.complex = complex
        if not complex and os.path.isfile(head + ".in1c"):
            print "seem to be complex version"
            self.complex = 1

        self.in5file = head + ".in5"
        if self.complex:
            self.in5file = head + ".in5c"

    def make_ctrl(self, origin, xend, yend, nx, ny):
        output = open(self.in5file, "w")
        output.write("%d  %d  %d  %d\n" % (origin[0], origin[1], origin[2], origin[3]))
        output.write("%d  %d  %d  %d\n" % (xend[0], xend[1], xend[2], xend[3]))
        output.write("%d  %d  %d  %d\n" % (yend[0], yend[1], yend[2], yend[3]))
        output.write("%d  %d  %d\n" % (self.shells[0], self.shells[1], self.shells[2]))
        output.write("%d   %d\n" % (nx, ny))
        output.write("RHO ADD  \n")
        if self.val == 0:
            output.write("ATU TOT NODEBUG\n")
        elif self.val == 1:
            output.write("ATU VAL NODEBUG\n")
        else:
            output.write("ATU VAL NODEBUG\n")    
        output.write("NONORTHO")
        output.close()

    def _make_def(self):
        deffile = "lapw5.def"
        cmd = "x lapw5 -d"
        if self.complex:
            cmd = cmd + " -c"
        os.system(cmd)

        if self.val != 1:
            input = open(deffile, "r")
            lines = input.readlines()
            input.close()
            output = open(deffile, "w")
            for l in lines:
               l = string.replace(l, "clmval", self.tails[self.val])
               output.write(l)
            output.close()

    def run(self):
        self._make_def()
        if self.complex:
            os.system("lapw5c lapw5.def")
        else:
            os.system("lapw5 lapw5.def")



def _string2angle(s):
    s = string.strip(s)
    if s:
        angle = string.atof(s)
        if angle == 0.0:
            angle = 90.0
        return angle
    else:
        return 90.0

def get_lattice(struct):
    input = open(struct, "r")
    line = input.readline()
    line = input.readline()
    lat_type = string.strip(line[:4])
    line = input.readline()
    line = input.readline()
    abc = map(string.atof, [line[0:10],line[10:20],line[20:30]])
    angle = map(_string2angle, [line[30:40],line[40:50],line[50:60]])
    return abc, angle

def collect_charge(head, num):
    rhofile = head + ".rho"
    rho = array.array("d")
    for i in range(num):
        suffix = ".%04d" % i
        rhof = rhofile + suffix
        input = open(rhof, "r") 
        line = input.readline()
        while 1:
            line = input.readline()
            if not line: break
            for word in string.split(line):
                rho.append(float(word))
    return rho

def erase_files(head, complex, num):
    rhofile = head + ".rho"
    in5file = head + ".in5"
    if complex:
        in5file = in5file + "c"
    for i in range(num):
        suffix = ".%04d" % i
        os.unlink(rhofile + suffix)
        os.unlink(in5file + suffix)
    
def hex2tri(v):
    x =  v[0] - v[1] + v[2]
    y =         v[1] + v[2]
    z = -v[0]        + v[2]
    denom = v[3]
    return [x,y,z,denom]
if __name__ == "__main__":
    import getopt

    def print_usage():
        usage = '''usage: venus.py [-h] [-v] [-p] [-S|V|C|R|T] nx ny nz
        -h   print help.
        -c   complex version of lapw5.
        -t   trigonal case.
        -v   verbose mode.
        -p   preserve intermediate files
        -S   generate total density map from case.clmsum (default)
        -V   generate valence density map from case.clmval
        -C   generate coulomb potential map from case.vcoul
        -R   generate exchange-correlation potential map from case.r2v
        -T   generate total potential map from case.vtotal\n'''
        sys.stderr.write(usage)

    try:
        options, resargs = getopt.getopt(sys.argv[1:], 'hctvpSVCRT')
    except getopt.error, s:
        sys.stderr.write(str(s)+"\n")
        print_usage()
        sys.exit(1)
    if len(resargs) < 3:
        print_usage()
        sys.exit(1)

    verbose = 0
    preserve = 0
    complex = 0
    trigonal = 0
    val = 0
    for option in options:
        if option[0] == "-h":
            print_usage()
            sys.exit()
        elif option[0] == "-v":
            verbose = 1
        elif option[0] == "-p":
            preserve = 1
        elif option[0] == "-c":
            complex = 1
        elif option[0] == "-t":
            trigonal = 1
            print "trigonal case"
        elif option[0] == "-S":
            print "using clmsum"
            val = 0
        elif option[0] == "-V":
            print "using clmval"
            val = 1
        elif option[0] == "-C":
            print "using vcoul"
            val = 2
        elif option[0] == "-R":
            print "using r2v"
            val = 3    
        elif option[0] == "-T":
            print "using vtotal"
            val = 4 

    nx, ny, nz = map(int, resargs[0:3])
    print "mesh:", nx, ny, nz

    head = os.path.basename(os.getcwd())
    lapw5 = Lapw5(head, complex)
    for x in range(nx):
        if verbose:
            print "    --> ", x
        origin = [x, 0, 0, nx-1]
        xend = [x, nx-1, 0, nx-1]
        yend = [x, 0, nx-1, nx-1]
        if trigonal:
            origin = hex2tri(origin)
            xend = hex2tri(xend)
            yend = hex2tri(yend)
        lapw5.make_ctrl(origin, xend, yend, ny, nz)
        lapw5.run()

        suffix = ".%04d" % x
        #print head
        #print suffix
        #print os.getcwd()
        #head = os.getcwd() + "/" + head
        #print head
        if complex:
          inf5file_iwase = head + ".in5c"
        else:
          inf5file_iwase = head + ".in5"
        os.rename(inf5file_iwase, inf5file_iwase + suffix)
        #os.rename(head + ".in5c", head + ".in5" + suffix)
        rhofile = head + ".rho"
        if os.path.exists(rhofile) and os.path.getsize(rhofile) > 0:
            os.rename(rhofile, rhofile + suffix)
        else:
            print rhofile, "does not exist or empty???"
            sys.exit(1)

    alat, angle = get_lattice(head + ".struct")
    output = open(head + ".rho3d", "w")
    output.write("cell\n")
    output.write("%f  %f  %f\n" % (alat[0], alat[1], alat[2]))
    output.write("%f  %f  %f\n" % (angle[0], angle[1], angle[2]))
    output.write("%d  %d  %d " % (nx, ny, nz))
    output.write("%f  %f  %f\n" % (alat[0], alat[1], alat[2]))

    rho = collect_charge(head, nx)
    i = 0
    for x in rho:
        output.write("%15.8e " % x)
        i = i + 1
        if (i % 5) == 0:
            output.write("\n")

    output.close()

    if not preserve:
        erase_files(head, lapw5.complex, nx)
    

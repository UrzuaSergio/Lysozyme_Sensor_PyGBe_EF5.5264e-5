#!/usr/bin/env python
# Calculated according to FelderPriluskySilmanSussman2007, but using center of mass
from numpy import *
from math import atan2

import os
import sys
from read_data import read_vertex, readpqr

def findDipole(xq, q):

    ctr = sum(transpose(xq)*abs(q), axis=1)/sum(abs(q))
#    ctr = average(xq, axis=0)
    r = xq - ctr
    d = sum(transpose(r)*q, axis=1)

    return d

def rotate_x(x, angle):

    xnew = zeros(shape(x))
    xnew[:,0] = x[:,0]
    xnew[:,1] = x[:,1]*cos(angle) - x[:,2]*sin(angle)
    xnew[:,2] = x[:,1]*sin(angle) + x[:,2]*cos(angle)

    return xnew


def rotate_y(x, angle):

    xnew = zeros(shape(x))
    xnew[:,0] = x[:,2]*sin(angle) + x[:,0]*cos(angle)
    xnew[:,1] = x[:,1]
    xnew[:,2] = x[:,2]*cos(angle) - x[:,0]*sin(angle)

    return xnew

def rotate_z(x, angle):

    xnew = zeros(shape(x))
    xnew[:,0] = x[:,0]*cos(angle) - x[:,1]*sin(angle)
    xnew[:,1] = x[:,0]*sin(angle) + x[:,1]*cos(angle)
    xnew[:,2] = x[:,2]

    return xnew

def modifypqr(inpqr, outpqr, xq):

    file_o = open(outpqr,'w')
    file1=open(inpqr,'r')
    for line in file1:
        line_split = line.split()

        if line_split[0] == 'ATOM':
            atm_nu = int(line_split[1])-1
            line_add = ' %3.3f  %3.3f  %3.3f '%(xq[atm_nu,0], xq[atm_nu,1], xq[atm_nu,2])
            line_new = line[:27] + line_add + line[55:]
            file_o.write(line_new)
        else:
            file_o.write(line)
    file_o.close()




inMesh = sys.argv[1]  #nombre_archivo_malla
inpqr  = sys.argv[2]  #nombre_archivo_pqr
alpha_z = float(sys.argv[3])*pi/180.	#alpha_rot
alpha_x = float(sys.argv[4])*pi/180.	#alpha_tilt
Dist = float(sys.argv[5])  #distancia_entre_proteina_sensor
if len(sys.argv)>6:
    name = sys.argv[6]
else:
    name = ''
if len(sys.argv)>7:
    if sys.argv[7] == 'verbose':
        verbose = True
else:
    verbose = False

#outMesh = inMesh+'_rot'+sys.argv[3]+'_til'+sys.argv[4]
#outpqr = inpqr+'_rot'+sys.argv[3]+'_til'+sys.argv[4]
outMesh = inMesh + name
outpqr = inpqr + name
X = loadtxt(inMesh+'.vert', float)
#vert = read_vertex(inMesh+'.vert', float)
vert = X[:,0:3]
xq, q = readpqr(inpqr+'.pqr', float)

#xq = array([[1.,0.,0.],[0.,0.,1.],[0.,1.,0.]])
#q = array([1.,-1.,1.])

#### Setup initial configuration
# Initial configuration: dipole parallel to z and outermost atom to center parallel to x
d = findDipole(xq,q)
normd = sqrt(sum(d*d))
normal  = array([0,0,1])
normal2 = array([0,1,0]) #modifique

angle = arccos(dot(d, normal)/normd)

## Align normal and dipole vectors
# Rotate y axis
angle_y = -atan2(d[0],d[2])     # Positive angle gets away from y, then negative to take it back
xq_aux = rotate_y(xq, angle_y)
vert_aux = rotate_y(vert, angle_y)

# Rotate x axis
d_aux = findDipole(xq_aux, q)
angle_x = atan2(d_aux[1],d_aux[2]) # Positive angle approaches y, then it's ok
xq_aux2 = rotate_x(xq_aux, angle_x)
vert_aux2 = rotate_x(vert_aux, angle_x)

d_aux2 = findDipole(xq_aux2,q)

## Align vector of atom furthest to center to x axis
# Pick atom
ctr = average(xq_aux2, axis=0)
r_atom = xq_aux2 - ctr
r_atom_norm = sqrt(xq_aux2[:,0]**2+xq_aux2[:,1]**2) # Distance in x-y plane
max_atom = where(r_atom_norm==max(r_atom_norm))[0][0]

# Rotate z axis
r_atom_max = r_atom[max_atom]
angle_z = atan2(r_atom_max[0], r_atom_max[1])
xq_0 = rotate_z(xq_aux2, angle_z)
vert_0 = rotate_z(vert_aux2, angle_z)

# Check if dipole and normal are parallel
d_0 = findDipole(xq_0, q)

# Check if furthest away atom vector and x axis are parallel
ctr = average(xq_0, axis=0)
ctr[2] = xq_0[max_atom,2]
r_atom = xq_0 - ctr
max_atom_vec = r_atom[max_atom]

check_dipole = dot(d_0,array([1,1,1]))
check_atom   = dot(max_atom_vec,array([1,1,1]))

if verbose:
    print('Initial configuration:')
if abs(check_dipole - abs(d_0[2]))<1e-10:
    if verbose: print('\tDipole is aligned with normal')
else: print('\tDipole NOT aligned!')
if abs(check_atom - abs(max_atom_vec[1]))<1e-10:
    if verbose: print('\tMax atom is aligned with x axis')
else: print('\tMax atom NOT aligned!')


### Move to desired configuration

## Rotate
# Rotate z axis
xq_aux = rotate_z(xq_0, alpha_z)
vert_aux = rotate_z(vert_0, alpha_z)

# Rotate x axis
xq_new = rotate_x(xq_aux, alpha_x)
vert_new = rotate_x(vert_aux, alpha_x)

## Translate
zmin = min(vert_new[:,2])
ctr = average(vert_new, axis=0)
translation = array([ctr[0], ctr[1], zmin-Dist]) # 2 Angs over the x-y plane

vert_new -= translation
xq_new -= translation

## Check
ctr = average(vert_new, axis=0)
d = findDipole(xq_new, q)
dx = array([0, d[1], d[2]])
dy = array([d[0], 0, d[2]])
dz = array([d[0], d[1], 0])
normd = sqrt(sum(d*d))
normdx = sqrt(sum(dx*dx))
normdz = sqrt(sum(dz*dz))
angle = arccos(dot(d, normal)/normd)
anglex = arccos(dot(dx, normal)/normdx)
anglez = arccos(dot(dz, normal)/normdz)

xq_check = rotate_x(xq_new, -alpha_x) #modifique
ctr_check = average(xq_check, axis=0)
atom_vec = array([xq_check[max_atom,0]-ctr_check[0], xq_check[max_atom,1]-ctr_check[1], 0]) #modifique
atom_vec_norm = sqrt(sum(atom_vec*atom_vec))
anglex = arccos(dot(atom_vec, normal2)/atom_vec_norm)


if alpha_x>pi:
    anglex = 2*pi-anglex    # Dot product finds the smallest angle!

if verbose:
    print('Desired configuration:')
if abs(ctr[0])<1e-10 and abs(ctr[1])<1e-10:
    if verbose:
        print('\tProtein is centered, %f angs over the surface'%(min(vert_new[:,1])))
else:
    print('\tProtein NOT well located!')

if abs(d[0])<1e-10:
    if verbose:
        print('\tDipole is on x-y plane, %f degrees from normal'%(angle*180/pi))
else:
    print('\tDipole is NOT well aligned')

if abs(angle-alpha_x)<1e-10:
    if verbose:
        print('\tMolecule was tilted correctly by %f deg'%(angle*180/pi))
else:
    print('\tMolecule was NOT tilted correctly!')

if abs(anglex-alpha_z)<1e-10:
    if verbose:
        print('\tMolecule was rotated correctly %f deg'%(anglex*180/pi))
else:
    print('\tMolecule was NOT rotated correctly!')

#### Save to file
savetxt(outMesh+'.vert', vert_new)
cmd = 'cp '+inMesh+'.face '+outMesh+'.face'
os.system(cmd)

modifypqr(inpqr+'.pqr', outpqr+'.pqr', xq_new)

if verbose:
    print('\nWritten to '+outMesh+'.vert(.face) and '+outpqr+'.pqr')

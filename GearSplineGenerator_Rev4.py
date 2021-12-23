# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 01:34:02 2021

@author: 2018
"""

# This is a gear generator that creates internal (hub) and external (shaft) 
# flank-centered gears in accordance with DIN 5480-1, Mar 2006. 

# The designation for these gears is:
    # Reference Diameter(dB) x Module(m) x Number of teeth(z1) x Tolerance Grade Number, Deviation Letter
    # Ex: 30 x 1 x 28 x 8j
    # All lengths are in mm and angles are in radians unless otherwise specified.
    
# To generate DXF files of the gear you'd like, simply run the code and input
# the parameters in your gear's designation. DXF files of an external spline and
# internal spline will be generated along with files of a single tooth of the 
# external spline and a single space width of the internal spline.

# DXF files can be imported into most CAD softwares. Once imported, just highlight the 2D profile 
# and extrude to create a 3D gear. DXF files can also be used to cut the 2D profile into a 3D stock
# of material on most EDMs.

# IMPORTANT: If you import a points file, the CAD software settings must be in mm.
# IMPORTANT: The DXF file won't generate if you don't have the ezdxf python library installed

import numpy as np
import matplotlib.pyplot as plt 
import ezdxf 

### Inputs

dB = float(input("Enter the Reference Diameter (d_B): "))
mod = float(input("Enter the Module (m): "))
z1 = int(input("Enter the number of teeth (z): "))
TolGrade_s = float(input("Enter the tolerance grade number for the shaft: "))
DevLetter_s = input("Enter the deviation grade letter for the shaft: ")
TolGrade_e = float(input("Enter the tolerance grade number for the hub: "))
DevLetter_e = input("Enter the deviation grade letter for the hub: ")
MachMethod = input("Enter the machining method (broaching, hobbing, gear shaping, or cold rolling): ")
FilletMethod = input("Enter the creation method for the root fillet (chip-removal or cold rolling): ")

points = 10 # Must be a whole number. Determines the number of points generated per spline. A higher number is more accurate, but harder on CAD software.
zcoord = 0 # This defines how far from the X-Y plane that the 2D involute profile will be

#Below is an example of input values
# dB = 30
# mod = 1
# z1 = 28
# TolGrade_s = 8
# DevLetter_s = "j"
# TolGrade_e = 9
# DevLetter_e = "H"
# MachMethod = "broaching"
# FilletMethod = "chip-removal"

### Gear Parameter Calculations
    # This section calculates all the required parameters necessary to build the gear from
    # the provided parameters
if MachMethod == "broaching": # This establishes the dedendum and form clearance coefficients
    hfp_coef = 0.55
    cFP_coef = 0.02
elif MachMethod == "hobbing":
    hfp_coef = 0.6
    cFP_coef = 0.07
elif MachMethod == "gear shaping":
    hfp_coef = 0.65
    cFP_coef = 0.12
elif MachMethod == "cold rolling":
    hfp_coef = 0.84
    cFP_coef = 0.12
else:
    print("Maching method input is invalid. Must be broaching, hobbing, gear shaping, or cold rolling.")

if FilletMethod == "chip-removal" or "chip-removal machining": # This establishes the fillet root radius coefficient
    rho_coef = 0.16
elif FilletMethod == "cold rolling":
    rho_coef = 0.54
else:
    print("Fillet creation method input is invalid. Must be chip-removal or cold rolling")

# Table 4 from 5480-1. Used to determine minimum form clearance (cFmin)
tab4 = np.zeros([7,3], dtype = float)
tab4[:, 0] = [25, 28, 30, 35, 40, None, None]
tab4[:, 1] = [None, 30, 35, 40, 45, 50, None]
tab4[:, 2] = [None, None, 40, 45, 50, 55, 65]
tab4 = tab4 * 0.001 # Converts values in the table from microns to mm

# The following two if statements determine the column and row of the cFmin in table 4
if mod >= 0.5 and mod <= 1.5:
    tab4_col = 0
elif mod >= 1.75 and mod <= 4:
    tab4_col = 1
elif mod >= 5 and mod <= 10:
    tab4_col = 2
else:
    print("invalid input for Module. Must be 0.5-1.5, 1.75-4, or 5-10")

if dB - round(dB) != 0:
    print("Invalid input for Reference Diameter. Must be a whole number")
elif dB > 0 and dB <= 12:
    tab4_row = 0
elif dB > 12 and dB <= 25:
    tab4_row = 1
elif dB > 25 and dB <= 50:
    tab4_row = 2
elif dB > 50 and dB <= 100:
    tab4_row = 3
elif dB > 100 and dB <= 200:
    tab4_row = 4
elif dB > 200 and dB <= 400:
    tab4_row = 5
elif dB > 400:
    tab4_row = 6
else:
    print("Invalid input for Reference Diameter, see table 1 in DIN 5480-1 for preferred values")

cFmin = tab4[tab4_row, tab4_col]

alpha = np.pi / 6 # Pressure angle. For all DIN 5480 gears, this is 30 degrees or pi/6 radians
pitch = mod * np.pi # Pitch value
z2 = -z1 # Teeth value representation for the hub
x1 = (dB / mod - z1 - 1.1) / 2 # Profile shift modification value for the shaft
x2 = -x1 # Profile shift modification value for the hub
hap = x1 * mod # Addendum
hfp = hfp_coef * mod # Dedendum
hP = hap + hfp # Tooth height
cP = hfp - hap # Bottom clearance
rho = rho_coef * mod # Root fillet radius
dp = mod*z1 # Pitch diameter
db = mod* z1 * np.cos(alpha) # Base diameter. This is what the involute profile is drawn from

da2 = abs(mod * (z2 + 2 * x2 + 0.9)) # Hub tip diameter
df2 = abs(mod * z2 + 2 * x2 * mod - 2 * hfp) # Hub root diameter

da1 = mod * (z1 + 2 * x1 + 0.9) # Shaft tip diameter
df1 = mod * z1 + 2 * x1 * mod - 2 * hfp # Shaft root diameter
dFf1 = da2 - 2 * cFmin # Shaft form circle diameter
dFf2 = da1 + 2 * cFmin # Hub form circle diameter
    
cFP = mod * cFP_coef

rb = db/2 # Radius of base circle.
rp = dp / 2 # Pitch radius
ra1 = da1 / 2 # Shaft tip radius
rf1 = df1 / 2 # Shaft root radius
rFf1 = dFf1 / 2 # Shaft form circle radius
ra2 = da2 / 2 # Hub tip radius
rf2 = df2 / 2 # Hub root radius
rFf2 = dFf2 / 2 # Hub form circle radius
 
### Tooth thickness and space width values and tolerances calculations
 # This section creates tables necessary for finding the shaft tooth thickness (s1)
 # and hub space width (e2) values and calculates those values and their associated
 # tolerances based on the inputted tolerance grade and deviation grade.

# The following is the first section of Table 7, which holds deviation space width (Ae) and 
# deviation tooth thickness (As) values
tab71 = np.zeros([18, 9], dtype = float)
tab71[0, :] = [200, 180, 160, 140, 125, 110, 100, 90, 80]
tab71[1, :] = [180, 162, 144, 126, 112, 99, 90, 81, 72]
tab71[2, :] = [160, 144, 128, 112, 100, 88, 80, 72, 64]
tab71[3, :] = [140, 126, 112, 98, 88, 77, 70, 63, 56]
tab71[4, :] = [120, 108, 96, 84, 75, 66, 60, 54, 48]
tab71[5, :] = [100, 90, 80, 70, 62, 55, 50, 45, 40]
tab71[6, :] = [80, 72, 64, 56, 50, 44, 40, 36, 32]
tab71[7, :] = [60, 54, 48, 42, 37, 33, 30, 27, 24]
tab71[8, :] = [40, 36, 32, 28, 25, 22, 20, 18, 16]
tab71[9, :] = [20, 18, 16, 14, 12, 11, 10, 9, 8]
tab71[11, :] = -tab71[9, :]
tab71[12, :] = -tab71[8, :]
tab71[13, :] = -tab71[7, :]
tab71[14, :] = -tab71[6, :] 
tab71[15, :] = -tab71[4, :]
tab71[16, :] = -tab71[2, :]
tab71[17, :] = -tab71[0, :]
tab71 = tab71 * 0.001 # Converts table values from microns to mm

# The following is the second section of Table 7, which provides actual and effective
# tolerance values for Ae and As
tab72 = np.zeros([30, 3], dtype = float)
tab72[:, 0] = [12, 14, 16, 18, 20, 22, 25, 28, 32, 36, 40, 45, 50, 56, 63, 71, 80, 90, 100, 112, 125, 140, 160, 180, 200, 224, 250, 280, 320, 360]
tab72[:, 1] = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 25, 28, 32, 36, 40, 45, 50, 56, 63, 71, 80, 90, 100, 112, 125, 140, 160, 175, 200, 225]
tab72[:, 2] = [4, 5, 6, 7, 8, 8, 9, 10, 12, 14, 15, 17, 18, 20, 23, 26, 30, 34, 37, 41, 45, 50, 60, 68, 75, 84, 90, 105, 120, 135]
tab72 = tab72 * 0.001 # Converts table values from microns to mm

# The following two if statments determine the rows and columns that Ae and As are
# on in Table 7
if dB > 0 and dB <= 12:
    if mod >= 0.5 and mod <= 1.5:
        tab71_col = 8
    elif mod >= 1.75 and mod <= 4:
        tab71_col = 7
    elif mod >= 5 and mod <= 10:
        tab71_col = 6
elif dB > 12 and dB <= 25:
    if mod >= 0.5 and mod <= 1.5:
        tab71_col = 7
    elif mod >= 1.75 and mod <= 4:
        tab71_col = 6
    elif mod >= 5 and mod <= 10:
        tab71_col = 5
elif dB > 25 and dB <= 50:
    if mod >= 0.5 and mod <= 1.5:
        tab71_col = 6
    elif mod >= 1.75 and mod <= 4:
        tab71_col = 5
    elif mod >= 5 and mod <= 10:
        tab71_col = 4
elif dB > 50 and dB <= 100:
    if mod >= 0.5 and mod <= 1.5:
        tab71_col = 5
    elif mod >= 1.75 and mod <= 4:
        tab71_col = 4
    elif mod >= 5 and mod <= 10:
        tab71_col = 3
elif dB > 100 and dB <= 200:
    if mod >= 0.5 and mod <= 1.5:
        tab71_col = 4
    elif mod >= 1.75 and mod <= 4:
        tab71_col = 3
    elif mod >= 5 and mod <= 10:
        tab71_col = 2
elif dB > 200 and dB <= 400:
    if mod >= 0.5 and mod <= 1.5:
        tab71_col = 3
    elif mod >= 1.75 and mod <= 4:
        tab71_col = 2
    elif mod >= 5 and mod <= 10:
        tab71_col = 1
elif dB > 400:
    if mod >= 0.5 and mod <= 1.5:
        tab71_col = 2
    elif mod >= 1.75 and mod <= 4:
        tab71_col = 1
    elif mod >= 5 and mod <= 10:
        tab71_col = 0
        
def tab71row(deviation_letter):    
    if deviation_letter == "v":
        tab71_row = 0
    elif deviation_letter == "u":
        tab71_row = 1
    elif deviation_letter == "t":
        tab71_row = 2
    elif deviation_letter == "s":
        tab71_row = 3
    elif deviation_letter == "r":
        tab71_row = 4
    elif deviation_letter == "p":
        tab71_row = 5
    elif deviation_letter == "n":
        tab71_row = 6
    elif deviation_letter == "m":
        tab71_row = 7
    elif deviation_letter == "k" or deviation_letter == "F":
        tab71_row = 8
    elif deviation_letter == "j" or deviation_letter == "G":
        tab71_row = 9
    elif deviation_letter == "h" or deviation_letter == "H":
        tab71_row = 10
    elif deviation_letter == "g" or deviation_letter == "J":
        tab71_row = 11
    elif deviation_letter == "f" or deviation_letter == "K":
        tab71_row = 12
    elif deviation_letter == "e" or deviation_letter == "M":
        tab71_row = 13
    elif deviation_letter == "d":
        tab71_row = 14
    elif deviation_letter == "c":
        tab71_row = 15
    elif deviation_letter == "b":
        tab71_row = 16
    elif deviation_letter == "a":
        tab71_row = 17
    else:
        print("Invalid deviation letter input, see table 9 for recommendations based on fit types.")
    return tab71_row

# The following if statement determines the row that the space width and tooth thickness deviations are
# on in Table 7
def tab72row(tolerance_grade):
    if tolerance_grade - round(tolerance_grade) != 0:
        print("Tolerance Grade Number input is invalid. Must be a whole number.")
    elif tolerance_grade == 5:
        if tab71_col == 8:
            tab72_row = 0
        elif tab71_col == 7:
            tab72_row = 1
        elif tab71_col == 6:
            tab72_row = 2
        elif tab71_col == 5:
            tab72_row = 3
        elif tab71_col == 4:
            tab72_row== 4
        elif tab71_col == 3:
            tab72_row = 5
        elif tab71_col == 2:
            tab72_row = 6
        elif tab71_col == 1:
            tab72_row = 7
        elif tab71_col == 0:
            tab72_row = 8
    elif tolerance_grade == 6:
        if tab71_col == 8:
            tab72_row = 3
        elif tab71_col == 7:
            tab72_row = 4
        elif tab71_col == 6:
            tab72_row = 5
        elif tab71_col == 5:
            tab72_row = 6
        elif tab71_col == 4:
            tab72_row = 7
        elif tab71_col == 3:
            tab72_row = 8
        elif tab71_col == 2:
            tab72_row = 9
        elif tab71_col == 1:
            tab72_row = 10
        elif tab71_col == 0:
            tab72_row = 11
    elif tolerance_grade == 7:
        if tab71_col == 8:
            tab72_row = 6
        elif tab71_col == 7:
            tab72_row = 7
        elif tab71_col == 6:
            tab72_row = 8
        elif tab71_col == 5:
            tab72_row = 9
        elif tab71_col == 4:
            tab72_row = 10
        elif tab71_col == 3:
            tab72_row = 11
        elif tab71_col == 2:
            tab72_row = 12
        elif tab71_col == 1:
            tab72_row = 13
        elif tab71_col == 0:
            tab72_row = 14
    elif tolerance_grade == 8:
        if tab71_col == 8:
            tab72_row = 9
        elif tab71_col == 7:
            tab72_row = 10
        elif tab71_col == 6:
            tab72_row = 11
        elif tab71_col == 5:
            tab72_row = 12
        elif tab71_col == 4:
            tab72_row = 13
        elif tab71_col == 3:
            tab72_row = 14
        elif tab71_col == 2:
            tab72_row = 15
        elif tab71_col == 1:
            tab72_row = 16
        elif tab71_col == 0:
            tab72_row = 17
    elif tolerance_grade == 9:
        if tab71_col == 8:
            tab72_row = 12
        elif tab71_col == 7:
            tab72_row = 13
        elif tab71_col == 6:
            tab72_row = 14
        elif tab71_col == 5:
            tab72_row = 15
        elif tab71_col == 4:
            tab72_row = 16
        elif tab71_col == 3:
            tab72_row = 17
        elif tab71_col == 2:
            tab72_row = 18
        elif tab71_col == 1:
            tab72_row = 19
        elif tab71_col == 0:
            tab72_row = 20
    elif tolerance_grade == 10:
        if tab71_col == 8:
            tab72_row = 15
        elif tab71_col == 7:
            tab72_row = 16
        elif tab71_col == 6:
            tab72_row = 17
        elif tab71_col == 5:
            tab72_row = 18
        elif tab71_col == 4:
            tab72_row = 19
        elif tab71_col == 3:
            tab72_row = 20
        elif tab71_col == 2:
            tab72_row = 21
        elif tab71_col == 1:
            tab72_row = 22
        elif tab71_col == 0:
            tab72_row = 23
    elif tolerance_grade == 11:
        if tab71_col == 8:
            tab72_row = 18
        elif tab71_col == 7:
            tab72_row = 19
        elif tab71_col == 6:
            tab72_row = 20
        elif tab71_col == 5:
            tab72_row = 21
        elif tab71_col == 4:
            tab72_row = 22
        elif tab71_col == 3:
            tab72_row = 23
        elif tab71_col == 2:
            tab72_row = 24
        elif tab71_col == 1:
            tab72_row = 25
        elif tab71_col == 0:
            tab72_row = 26
    elif tolerance_grade == 12:
        if tab71_col == 8:
            tab72_row = 21
        elif tab71_col == 7:
            tab72_row = 22
        elif tab71_col == 6:
            tab72_row = 23
        elif tab71_col == 5:
            tab72_row = 24
        elif tab71_col == 4:
            tab72_row = 25
        elif tab71_col == 3:
            tab72_row = 26
        elif tab71_col == 2:
            tab72_row = 27
        elif tab71_col == 1:
            tab72_row = 28
        elif tab71_col == 0:
            tab72_row = 29
    else:
        print("Tolerance Grade Number input is invalid. Must be 5-12")
    return tab72_row
    
# Tolerance calculations:
Ae = tab71[tab71row(DevLetter_e), tab71_col] # Space width deviation
T_act_e = tab72[tab72row(TolGrade_e), 1] # Space width actual tolerance
T_eff_e = tab72[tab72row(TolGrade_e), 2] # Space width effective tolerance

As = tab71[tab71row(DevLetter_s), tab71_col] # Tooth thickness deviation
T_act_s = tab72[tab72row(TolGrade_s), 1] # Tooth thickness actual tolerance
T_eff_s = tab72[tab72row(TolGrade_s), 2] # Tooth thickness effective tolerance

s1 = mod * np.pi / 2 + 2 * x1 * mod * np.tan(alpha) # Circular tooth thickness of the shaft measured on the pitch diameter
s_vmax = s1 + As # Max effective tolerance
s_max = s1 + As - T_eff_s # Max actual reference tolerance
s_min = s1 + As - T_act_s - T_eff_s # Min actual tolerance
s = s_min + (s_max - s_min) / 2 # Arbitrary nominal value that lies in the middle of the tolerance

e2 = s1 # Circular space width of the hub measured on the pitch diameter
e_max = e2 + Ae + T_act_e + T_eff_e # Max actual tolerance
e_min = e2 + Ae + T_eff_e # Min actual reference tolerance
e_vmin = e2 + Ae # Min effective tolerance
e = e_min + (e_max - e_min) / 2 # Arbitrary nominal value that lies in the middle of the tolerance

### Spline Generation Calculations:
    
# Shaft Involute Sides:
def inv(theta): # Involute function of an angle
    inv_angle = np.tan(theta) - theta
    return inv_angle

def invr(radius): # Involute angle outputted for a given radius relative to the base circle radius
    angle = np.arccos(rb/radius)
    inv_angle = inv(angle)
    return inv_angle

p_sector = 2*np.pi / z1 # Central angle of one pitch
sector_range = np.linspace(0, 2*np.pi - p_sector, z1) # Polar angle at the start of each pitch in the gear profile

# Below is a function that will return the involute profile x and y coordinates of one tooth side for every tooth 
# in the gear
def invcoord(RadRange, InvAng): 
    x_inva = []
    y_inva = []
    for angle in sector_range:
        x_inva.append(RadRange * np.cos(InvAng + angle))
        y_inva.append(RadRange * np.sin(InvAng + angle))
    x_inva = np.transpose(np.array(x_inva))
    y_inva = np.transpose(np.array(y_inva))
    return x_inva, y_inva

sector_s = s / rp # Central angle encompassing one tooth thickness
inva_tooth_s = invr(rp) # Polar angle to the involute profile on the tooth thickness

RadRange_s = np.linspace(rFf1, ra1, points) # Range of radii along involute profile of the shaft
inva1s = invr(RadRange_s) # Range of involute angles along the tooth side profile
inva_sector_s = 2 * (inva_tooth_s - inva1s[0]) + sector_s # Central angle between the base of two involute profiles of a tooth
inva1s = inva1s - inva1s[0] - inva_sector_s/2 # Centers the first tooth along the x axis

x_inva1s = invcoord(RadRange_s, inva1s)[0] # X coordinates for first side of involute profile
y_inva1s = invcoord(RadRange_s, inva1s)[1] # Y coordinates for first side of involute profile

inva2s = -inva1s

x_inva2s = invcoord(RadRange_s, inva2s)[0] # X coordinates for second side of involute profile
y_inva2s = invcoord(RadRange_s, inva2s)[1] # Y coordinates for second side of involute profile

# Hub Involute Sides:
sector_e = e / rp # Central angle encompassing one space width

RadRange_e = np.linspace(ra2, rFf2, points) # Range of radii along involute profile of the hub
inva1e = invr(RadRange_e) # Range of involute angles along the space width side profile
inva_sector_e = 2 * (inva_tooth_s - inva1e[0]) + sector_e # Central angle between the base of two involute profiles of a space width
inva1e = inva1e - inva1e[0] - inva_sector_e/2 # Centers the first space width along the x axis

x_inva1e = invcoord(RadRange_e, inva1e)[0] # X coordinates for first side of involute profile
y_inva1e = invcoord(RadRange_e, inva1e)[1] # Y coordinates for first side of involute profile

inva2e = -inva1e

x_inva2e = invcoord(RadRange_e, inva2e)[0] # X coordinates for second side of involute profile
y_inva2e = invcoord(RadRange_e, inva2e)[1] # Y coordinates for second side of involute profile

# Shaft Tooth Tip Generation

# Below is a function that generates tooth tip or root circle coordinates
def ArcCoord(TipRadius, AngRang):
    xa = []
    ya = []
    for angle in sector_range:
        xa.append(TipRadius * np.cos(AngRang + angle)) 
        ya.append(TipRadius * np.sin(AngRang + angle))
    xa = np.transpose(np.array(xa))
    ya = np.transpose(np.array(ya))
    return xa, ya

ra1_AngRang = np.linspace(inva1s[-1], inva2s[-1], points) # Range of polar angles along one tooth tip
xa1 = ArcCoord(ra1, ra1_AngRang)[0] # X coordinates for points along a tooth tip
ya1 = ArcCoord(ra1, ra1_AngRang)[1] # Y coordinates for points along a tooth tip

# Hub Tooth Tip Generation
ra2_AngRang1 = np.linspace(inva2e[0], p_sector / 2, points) # Range of polar angles along half of a hub tooth tip
xa2_1 = ArcCoord(ra2, ra2_AngRang1)[0] # X coordinates for points along half a hub tooth tip
ya2_1 = ArcCoord(ra2, ra2_AngRang1)[1] # Y coordinates for points along half a hub tooth tip

ra2_AngRang2 = -ra2_AngRang1 # Range of polar angles along another half of a hub tooth tip
xa2_2 = ArcCoord(ra2, ra2_AngRang2)[0] # X coordinates for points along half a hub tooth tip
ya2_2 = ArcCoord(ra2, ra2_AngRang2)[1] # Y coordinates for points along half a hub tooth tip

# Shaft Root Fillet Generation:

# Below is a function that generates the coordinates for the root fillet of one side of a gear tooth
def fillet(FormRad, RootRad, InvAng):
    if FormRad > RootRad: # Defining parameters for root fillet circle on the shaft
        H = (RootRad + rho) * np.cos(InvAng) # X coordinate of the center of the root fillet circle on shaft
        K = (RootRad + rho) * np.sin(InvAng) # Y coordinate of the center of the root fillet circle on shaft
    else: # Defining parameters for root fillet circle on the hub
        H = (RootRad - rho) * np.cos(InvAng) # X coordinate of the center of the root fillet circle on hub
        K = (RootRad - rho) * np.sin(InvAng) # Y coordinate of the center of the root fillet circle on hub
    
    aq = (K**2 / H**2) + 1 # "a" term of the quadratic equation
    bq = -(K / H**2) * (FormRad**2 - rho**2 + K**2 - H**2) - 2 * K # "b" term of the quadratic equation
    cq = ((FormRad**2 - rho**2 + K**2 - H**2) / (2 * H))**2 + K**2- rho**2 # "c" term of the quadratic equation
    
    y_int = (-bq + (bq**2 - 4 * aq * cq)**0.5) / (2 * aq) # Quadratic formula solving for y coordinate of root fillet circle and form circle intercept
    x_int = (FormRad**2 - y_int**2)**0.5 # x coordinate of root fillet circle and form circle intercept
    
    theta_int_Ff = np.arccos(x_int / FormRad) # Polar angle to fillet circle and form circle intercept from form circle center
    
    if FormRad > RootRad:
        thetaHK = theta_int_Ff
    else:
        thetaHK = InvAng - (theta_int_Ff - InvAng)
    
    # Now that thetaHK has been redefined, the lines of code solving for the intercept must be repeated to update the intercept point
    if FormRad > RootRad: # Defining parameters for root fillet circle on the shaft
        H = (RootRad + rho) * np.cos(thetaHK) # X coordinate of the center of the root fillet circle on shaft
        K = (RootRad + rho) * np.sin(thetaHK) # Y coordinate of the center of the root fillet circle on shaft
    else: # Defining parameters for root fillet circle on the hub
        H = (RootRad - rho) * np.cos(thetaHK) # X coordinate of the center of the root fillet circle on hub
        K = (RootRad - rho) * np.sin(thetaHK) # Y coordinate of the center of the root fillet circle on hub
   
    aq = (K**2 / H**2) + 1 # "a" term of the quadratic equation
    bq = -(K / H**2) * (FormRad**2 - rho**2 + K**2 - H**2) - 2 * K # "b" term of the quadratic equation
    cq = ((FormRad**2 - rho**2 + K**2 - H**2) / (2 * H))**2 + K**2- rho**2 # "c" term of the quadratic equation
   
    y_int = (-bq + (bq**2 - 4 * aq * cq)**0.5) / (2 * aq) # Quadratic formula solving for y coordinate of root fillet circle and form circle intercept
    x_int = (FormRad**2 - y_int**2)**0.5 # x coordinate of root fillet circle and form circle intercept
    theta_int_fillet = np.arccos((x_int - H) / rho) # Polar angle to fillet circle and form circle intercept on the fillet circle center
    
    def fillet2(thetaHK, theta_int_fillet, offset):
        x_fil = []
        y_fil = []
        for angle in sector_range:
            if FormRad > RootRad: # Defining parameters for root fillet circle on the shaft
                H = (RootRad + rho) * np.cos(thetaHK + angle) # X coordinate of the center of the root fillet circle on shaft
                K = (RootRad + rho) * np.sin(thetaHK + angle) # Y coordinate of the center of the root fillet circle on shaft
                FilletAngRang = np.linspace(thetaHK + offset + angle, (thetaHK + offset) + ((thetaHK + offset) - theta_int_fillet) + angle, points)
            else: # Defining parameters for root fillet circle on the hub
                H = (RootRad - rho) * np.cos(thetaHK + angle) # X coordinate of the center of the root fillet circle on hub
                K = (RootRad - rho) * np.sin(thetaHK + angle) # Y coordinate of the center of the root fillet circle on hub
                FilletAngRang = np.linspace(thetaHK + angle, theta_int_fillet + angle, points)
            x_fil.append(H + rho * np.cos(FilletAngRang))
            y_fil.append(K + rho * np.sin(FilletAngRang))

        x_fil = np.transpose(np.array(x_fil)) # X coordinates of root fillets on one side of the tooth
        y_fil = np.transpose(np.array(y_fil)) # Y coordinates of root fillets on one side of the tooth
        return x_fil, y_fil
    
    x_fil1 = fillet2(thetaHK, theta_int_fillet, np.pi)[0]
    y_fil1 = fillet2(thetaHK, theta_int_fillet, np.pi)[1]
    x_fil2 = fillet2(-thetaHK, -theta_int_fillet, -np.pi)[0]
    y_fil2 = fillet2(-thetaHK, -theta_int_fillet, -np.pi)[1]
    
    return x_fil1, y_fil1, x_fil2, y_fil2, thetaHK

fillet_s = fillet(rFf1, rf1, inva2s[0])
x_fil1_s = fillet_s[0] # Shaft root fillet x coordinates
y_fil1_s = fillet_s[1] # Shaft root fillet y coordinates
x_fil2_s = fillet_s[2] # Shaft root fillet x coordinates
y_fil2_s = fillet_s[3] # Shaft root fillet y coordinates

# Hub Root Fillet Generation:
fillet_e = fillet(rFf2, rf2, inva2e[-1])
x_fil1_e = fillet_e[0] # Hub root fillet x coordinates
y_fil1_e = fillet_e[1] # Hub root fillet y coordinates
x_fil2_e = fillet_e[2] # Hub root fillet x coordinates
y_fil2_e = fillet_e[3] # Hub root fillet y coordinates

# Shaft Root Circle Generation:
rf1_AngRang1 = np.linspace(p_sector/2, fillet_s[4], points)
xf1_1 = ArcCoord(rf1, rf1_AngRang1)[0]
yf1_1 = ArcCoord(rf1, rf1_AngRang1)[1]

rf1_AngRang2 = -rf1_AngRang1
xf1_2 = ArcCoord(rf1, rf1_AngRang2)[0]
yf1_2 = ArcCoord(rf1, rf1_AngRang2)[1]

# Hub Root Circle Generation:
rf2_AngRang = np.linspace(fillet_e[4], -fillet_e[4], points)
xf2 = ArcCoord(rf2, rf2_AngRang)[0]
yf2 = ArcCoord(rf2, rf2_AngRang)[1]

### Measurement Over Pins
    # This section calculates the pin diameter and length of the measurement across pins when
    # The are put on either side of the gear. This measurement can be used when performing
    # quality assurance on the gear, to insure the involute sides are within their tolerances

def pins(z, x):
    eta = (np.pi/(2*z) - inv(alpha)) - 2*x*np.tan(alpha)/z
    alpha_p = np.arccos(z * mod * np.cos(alpha) / ((z + 2 * x) * mod))
    phi = np.tan(alpha_p) + eta
    d_pin = z * mod * np.cos(alpha) * (inv(phi) + eta) # Ideal diameter of pins used to measure distance across the gear
    d_pin = round(2 * d_pin) / 2 # Rounded diameter to the nearest 0.5 that a gauge pin could match

    # inv_phi is the involute function of angle phi, which must be recalculated now that d_pin has changed
    inv_phi = d_pin/(z * mod * np.cos(alpha)) - np.pi / (2 * z) + inv(alpha) + 2 * x * np.tan(alpha) / z
    
    # Below, phi and the for loop under it calculate the perform the inverse involute function on inv_phi in order to find the angle phi.
    phi = 1.441 * inv_phi**(1 / 3) - 0.374 * inv_phi
    for n in range(0, 5):
        phi = phi + (inv_phi - inv(phi)) / (np.tan(phi))**2
        
    if z % 2 == 0: # The outer most if/else statement determines whether the number of teeth is even or odd
        if z1 > 0: # The two if statements embedded in the primary if statement determine if an internal or external (hub) is being measured
            MoP = z * mod * np.cos(alpha) / np.cos(phi) + d_pin
        elif z1 < 0:
            MoP = z * mod * np.cos(alpha) / np.cos(phi) - d_pin
    else:
        if z1 > 0:
            MoP = z * mod * np.cos(alpha) / (np.cos(phi)) * np.cos((np.pi / 2) / z1) + d_pin
        elif z1 < 0:
            MoP = z * mod * np.cos(alpha) / (np.cos(phi)) * np.cos((np.pi / 2) / z1) - d_pin
    return abs(MoP), d_pin # MoP is the Measurement over Pins. d_pin is the practical diameter of the pins
    
MoP_shaft = pins(z1, x1)[0]
d_pin_shaft = pins(z1, x1)[1]
print("")
print("The external spline measurement across pins is", round(MoP_shaft, 4), "mm", "using pins with a diameter of", d_pin_shaft, "mm")

MoP_hub = pins(z2, x2)[0]
d_pin_hub = pins(z2, x2)[1]
print("The internal spline measurement across pins is", round(MoP_hub, 4), "mm", "using pins with a diameter of", d_pin_hub, "mm")
print("The root fillet radius is", rho, "mm")
    
### Plot Reference Lines Generation
    # This section of the code was made to show important gear parameters their plots

def onearc(CircRad, AngRang):
    x = CircRad * np.cos(AngRang)
    y = CircRad * np.sin(AngRang)
    return x, y

PitchCircX = onearc(rp, np.linspace(-p_sector/2, p_sector/2, 2*points))[0] # Pitch circle x coordinates
PitchCircY = onearc(rp, np.linspace(-p_sector/2, p_sector/2, 2*points))[1] # Pitch circle y coordinates

RootCircX_s = onearc(rf1, np.linspace(-p_sector/2, p_sector/2, 2*points))[0] # Shaft Root circle x coordinates
RootCircY_s = onearc(rf1, np.linspace(-p_sector/2, p_sector/2, 2*points))[1] # Shaft Root circle y coordinates

FormCircX_s =onearc(rFf1, np.linspace(-p_sector/2, p_sector/2, 2*points))[0] # Shaft Form circle x coordinates
FormCircY_s = onearc(rFf1, np.linspace(-p_sector/2, p_sector/2, 2*points))[1] # Shaft Form circle y coordinates

ToothThickX = onearc(rp, np.linspace(-sector_s/2, sector_s/2, points))[0] # Shaft tooth thickness X coordinates
ToothThickY = onearc(rp, np.linspace(-sector_s/2, sector_s/2, points))[1] # Shaft tooth thickness Y coordinates

TipCircX_s = onearc(ra1, np.linspace(-p_sector/2, p_sector/2, 2*points))[0] # Shaft tip circle X coordinates
TipCircY_s = onearc(ra1, np.linspace(-p_sector/2, p_sector/2, 2*points))[1] # Shaft tip circle Y coordinates

RootCircX_e = onearc(rf2, np.linspace(-p_sector/2, p_sector/2, 2*points))[0] # Hub Root circle x coordinates
RootCircY_e = onearc(rf2, np.linspace(-p_sector/2, p_sector/2, 2*points))[1] # Hub Root circle y coordinates

FormCircX_e = onearc(rFf2, np.linspace(-p_sector/2, p_sector/2, 2*points))[0] # Hub Form circle x coordinates
FormCircY_e = onearc(rFf2, np.linspace(-p_sector/2, p_sector/2, 2*points))[1] # Hub Form circle y coordinates

SpaceWidX = onearc(rp, np.linspace(-sector_e/2, sector_e/2, points))[0] # Hub tooth thickness X coordinates
SpaceWidY = onearc(rp, np.linspace(-sector_e/2, sector_e/2, points))[1] # Hub tooth thickness Y coordinates

TipCircX_e = onearc(ra2, np.linspace(-p_sector * 0.65, p_sector * 0.65, 2*points))[0] # Hub tip circle X coordinates
TipCircY_e = onearc(ra2, np.linspace(-p_sector * 0.65, p_sector * 0.65, 2*points))[1] # Hub tip circle Y coordinates

#ToothAngRang = np.linspace(-sector_s / 2, sector_s / 2, points)
#xtooth = rp * np.cos(ToothAngRang)
#ytooth = rp * np.sin(ToothAngRang)
#plt.figure(1)
#plt.plot(xtooth, ytooth)

### Space width test
    # This section of the code was made to check the thickness of the space width so that the 
    # accuracy of the program can be verified.
#ToothAngRang2 = np.linspace(-sector_e / 2, sector_e / 2, points)
#xtooth2 = rp * np.cos(ToothAngRang2)
#ytooth2 = rp * np.sin(ToothAngRang2)
#plt.figure(3)
#plt.plot(xtooth2, ytooth2)


### Spline Profile Plots

# Shaft Plot of one tooth:
plt.figure(1)
plt.title("Plot of One Shaft Gear Tooth (mm)")
plt.plot(x_inva1s[:, 0], y_inva1s[:, 0], x_inva2s[:, 0], y_inva2s[:, 0]) # Involute Sides
plt.plot(xa1[:, 0], ya1[:, 0]) # Tooth Tip
plt.plot(x_fil1_s[:, 0], y_fil1_s[:, 0], x_fil2_s[:, 0], y_fil2_s[:, 0]) # Root Fillets
plt.plot(xf1_1[:, 0], yf1_1[:, 0], xf1_2[:, 0], yf1_2[:, 0]) # Root Circle

plt.plot(PitchCircX, PitchCircY, '--', label = 'Pitch Circle, d = ' + str(round(dp,2))) # Spline parameters for reference
plt.plot(RootCircX_s, RootCircY_s, '--', label = 'Root Circle, d_f1 = ' + str(round(df1,2))) 
plt.plot(TipCircX_s, TipCircY_s, '--', label = 'Tip Circle, d_a1 = ' + str(round(da1,2)))
plt.plot(FormCircX_s, FormCircY_s, '--', label = 'Form Circle, d_Ff1 = ' + str(round(dFf1,2)))
plt.plot(ToothThickX, ToothThickY, linewidth = 3, label = 'Tooth Thickness, s1 = ' + str(round(s_min,4)) + ' - ' +str(round(s_max,4))) 
plt.plot(ra1 * np.cos(-p_sector), ra1 * np.sin(-p_sector)) # Point to help position the plot to accomadate for the label
plt.legend(loc = 'lower right')

# Shaft Plot of the entire spline
plt.figure(2)
plt.title("Plot of the Shaft Involute Spline (mm)")
plt.plot(x_inva1s, y_inva1s, x_inva2s, y_inva2s)  # Involute Sides 
plt.plot(xa1, ya1) # Tooth Tip
plt.plot(x_fil1_s, y_fil1_s, x_fil2_s, y_fil2_s) # Root Fillets
plt.plot(xf1_1, yf1_1, xf1_2, yf1_2) # Root Circle
    
# Hub Plot of one space width
plt.figure(3)
plt.title("Plot of One Hub Gear Tooth (mm)")
plt.plot(x_inva1e[:, 0], y_inva1e[:, 0], x_inva2e[:, 0], y_inva2e[:, 0])  # Involute Sides 
plt.plot(xa2_1[:, 0], ya2_1[:, 0], xa2_2[:, 0], ya2_2[:, 0]) # Hub Tooth Tip (half of a tip on each side of the space width)
plt.plot(x_fil1_e[:, 0], y_fil1_e[:, 0], x_fil2_e[:, 0], y_fil2_e[:, 0]) # Root Fillets    
plt.plot(xf2[:, 0], yf2[:, 0]) # Root Circle

plt.plot(PitchCircX, PitchCircY, '--', label = 'Pitch Circle, d = ' + str(round(dp,2))) # Spline parameters for reference
plt.plot(RootCircX_e, RootCircY_e, '--', label = 'Root Circle, d_f2 = ' + str(round(df2,2))) 
plt.plot(TipCircX_e, TipCircY_e, '--', label = 'Tip Circle, d_a2 = ' + str(round(da2,2)))
plt.plot(FormCircX_e, FormCircY_e, '--', label = 'Form Circle, d_Ff2 = ' + str(round(dFf2,2)))
plt.plot(SpaceWidX, SpaceWidY, linewidth = 3, label = 'Space Width, e2 = ' + str(round(e_min,4)) + ' - ' +str(round(e_max,4))) 
plt.plot(rf2 * np.cos(-p_sector), rf2 * np.sin(-p_sector)) # Point to help position the plot to accomadate for the label
plt.legend(loc = 'lower right')

# Hub Plot of the entire spline
plt.figure(4)
plt.title("Plot of the Hub Involute Spline (mm)")
plt.plot(x_inva1e, y_inva1e, x_inva2e, y_inva2e) # Involute Sides
plt.plot(xa2_1, ya2_1, xa2_2, ya2_2) # Hub Tooth Tip
plt.plot(x_fil1_e, y_fil1_e, x_fil2_e, y_fil2_e) # Root Fillets 
plt.plot(xf2, yf2) # Root Circle

### Points File Generation:

# Shaft Tooth and Hub Space Width:
ToothListX = (x_inva1s[:, 0], x_inva2s[:, 0], xa1[:, 0], x_fil1_s[:, 0], x_fil2_s[:, 0], xf1_1[:, 0], xf1_2[:, 0])
ToothListY = (y_inva1s[:, 0], y_inva2s[:, 0], ya1[:, 0], y_fil1_s[:, 0], y_fil2_s[:, 0], yf1_1[:, 0], yf1_2[:, 0])
SpaceListX = (x_inva1e[:, 0], x_inva2e[:, 0], xa2_1[:, 0], xa2_2[:, 0], x_fil1_e[:, 0], x_fil2_e[:, 0], xf2[:, 0]) 
SpaceListY = (y_inva1e[:, 0], y_inva2e[:, 0], ya2_1[:, 0], ya2_2[:, 0], y_fil1_e[:, 0], y_fil2_e[:, 0], yf2[:, 0])

ToothX = []
ToothY = []
SpaceX = []
SpaceY = []
for m in range(0, len(ToothListX)):
    ToothX = np.append(ToothX, ToothListX[m])
    ToothY = np.append(ToothY, ToothListY[m])
    SpaceX = np.append(SpaceX, SpaceListX[m])
    SpaceY = np.append(SpaceY, SpaceListY[m])
    
ToothX = np.reshape(ToothX, (len(ToothX), 1))
ToothY = np.reshape(ToothY, (len(ToothY), 1))    
ZPoints = np.zeros((len(ToothX), 1), dtype = float)
ZPoints = zcoord + ZPoints  

ToothPoints = np.append(ToothX, ToothY, 1)
ToothPoints = np.append(ToothPoints, ZPoints, 1)

# np.savetxt("Tooth_PointsFile.asc", ToothPoints, delimiter = ",")

SpaceX = np.reshape(SpaceX, (len(SpaceX), 1))
SpaceY = np.reshape(SpaceY, (len(SpaceY), 1))    

SpacePoints = np.append(SpaceX, SpaceY, 1)
SpacePoints = np.append(SpacePoints, ZPoints, 1)

# np.savetxt("SpaceWidth_PointsFile.asc", SpacePoints, delimiter = ",")

# Full shaft and hub
def arrange(parameter, ShapeValue):
    NewArray = np.reshape(np.transpose(parameter), (z1 * ShapeValue, 1))
    return NewArray

ShaftListX = (arrange(x_inva1s, points), arrange(x_inva2s, points), arrange(xa1, points), arrange(x_fil1_s, points), arrange(x_fil2_s, points), arrange(xf1_1, points), arrange(xf1_2, points))
ShaftListY = (arrange(y_inva1s, points), arrange(y_inva2s, points), arrange(ya1, points), arrange(y_fil1_s, points), arrange(y_fil2_s, points), arrange(yf1_1, points), arrange(yf1_2, points))
HubListX = (arrange(x_inva1e, points), arrange(x_inva2e, points), arrange(xf2, points), arrange(xa2_1, points), arrange(xa2_2, points), arrange(x_fil1_e, points), arrange(x_fil2_e, points))
HubListY = (arrange(y_inva1e, points), arrange(y_inva2e, points), arrange(yf2, points), arrange(ya2_1, points), arrange(ya2_2, points), arrange(y_fil1_e, points), arrange(y_fil2_e, points))

ShaftX = []
ShaftY = []
HubX = []
HubY = []
for m in range(0, len(ShaftListX)):
    ShaftX = np.append(ShaftX, ShaftListX[m])
    ShaftY = np.append(ShaftY, ShaftListY[m])
    HubX = np.append(HubX, HubListX[m])
    HubY = np.append(HubY, HubListY[m])

ShaftX = np.reshape(ShaftX, (len(ShaftX), 1))
ShaftY = np.reshape(ShaftY, (len(ShaftY), 1))    
ZPoints = np.zeros((len(ShaftX), 1), dtype = float)  
ZPoints = zcoord + ZPoints  

ShaftPoints = np.append(ShaftX, ShaftY, 1)
ShaftPoints = np.append(ShaftPoints, ZPoints, 1)

# np.savetxt("Shaft_PointsFile.asc", ShaftPoints, delimiter = ",") 

HubX = np.reshape(HubX, (len(HubX), 1))
HubY = np.reshape(HubY, (len(HubY), 1))    

HubPoints = np.append(HubX, HubY, 1)
HubPoints = np.append(HubPoints, ZPoints, 1)

# np.savetxt("Hub_PointsFile.asc", HubPoints, delimiter = ",")   


### DXF File Generation

# Single Tooth and Single Space Width

from ezdxf import units
doc = ezdxf.new()
doc.units = units.MM

msp = doc.modelspace()
column1 = 0
column2 = points 
for m in range(0, len(ToothListX)):
    msp.add_polyline2d(ToothPoints[column1:column2]) 
    column1 = column1 + points
    column2 = column2 + points

doc.saveas('Shaft_Tooth.dxf')

from ezdxf import units
doc = ezdxf.new()
doc.units = units.MM

msp = doc.modelspace()
column1 = 0
column2 = points 
for m in range(0, len(SpaceListX)):
    msp.add_polyline2d(SpacePoints[column1:column2]) 
    column1 = column1 + points
    column2 = column2 + points

doc.saveas('Space_Width.dxf')

# Entire Spline
from ezdxf import units
doc = ezdxf.new()
doc.units = units.MM

msp = doc.modelspace()
column1 = 0
column2 = points 
for m in range(0, z1* len(ShaftListX)):
    msp.add_polyline2d(ShaftPoints[column1:column2]) 
    column1 = column1 + points
    column2 = column2 + points

doc.saveas('Shaft.dxf')


doc = ezdxf.new()
doc.units = units.MM

msp = doc.modelspace()
column1 = 0
column2 = points 
for m in range(0, z1* len(HubListX)):
    msp.add_polyline2d(HubPoints[column1:column2]) 
    column1 = column1 + points
    column2 = column2 + points

doc.saveas('Hub.dxf')

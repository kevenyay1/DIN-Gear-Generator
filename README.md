# DIN-Gear-Generator
Python Program that will generate DXF files of DIN 5480-1 internal and external gears

Required Python Libraries:

Numpy, matplotlib, and ezdxf. All of them (including ezdxf) can be installed using pip or conda.

Background:

This program will generate gears that are in accordance with the DIN 5480-1 (The document is one of the files in this repository). Many free gear generator softwares will only produce gears of a general shape that are not in accordance with a specific standard, or they won't give you the customization needed to hit the exact parameters of a given standard. The GearSplineGenerator_Rev4.py script will generate flank-centered gears (not diameter centered gears though) that meet all the possible customizable parameters within the DIN 5480-1.

DIN is a German metric (module) involute gear standard that is commonly used in Europe. The documentation on it is easy to find, which makes it a useful standard for manufacturing. DIN external and internal gears are defined by a designation with the following format: W/N (W for shaft, N for hub) Reference Diameter x Module x Number of Teeth x Tolerance Grade Number Deviation Grad Letter (ex: W30x1x28x8j indicates an external gear with a 30 mm reference diameter, 1 mm module, 28 teeth, tolerance grade of 8, and a deviation grade of "j"). The designation contains the majority of the parameters needed to  produce a gear. The other two parameters not listed are machining methods for the gear.

Recommended deviations/tolerance grades for a given fit type are available in table 9 of the DIN 5480-1.

How to Use:

When the script is run it will ask for the parameters in the gear designation and the machining methods. Once those are inputted, four DXF files will be generated (One for the Shaft, one for the Hub, one for a single shaft tooth, and one for a single hub space width) and plots will be made representing the four files. The plots will contain important dimensions of the gears that can be used on a GD&T drawing of the gear. The root fillet radius will be printed, and the measurement over pins data (useful for manufacturing purposes) will be printed.

The DXF files can be imported into other CAD softwares to make 3D models of the gears, and they can also be uploaded on to most EDMs (electric discharge machines) that can then cut the profile into a piece of stock (see the EDM cut jpg for an example). The usefulness with the EDM is that they can be operated with very little training. In other words, anyone with a proper DXF file can manufacture a gear with an EDM; a dedicated CNC programmer is not required.






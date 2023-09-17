# KSAM
Kinetic and Stress Analysis of N-bar Mechanisms

## Description
A mechanism is a device that transforms movement into a desired pattern. It's a medium to transmit, control or limit relative movement. Examples of mechanisms include: folding chairs, mechanical watches, and umbrellas [1]. 
This program is designed to analyze n-bar linkages that consist of four member vector loops like the one shown in the image below. <br><br>
![mechanism-powered-compresor](examples/powered_compresor.gif#center)

The construction of this machines is accomplished through the concatenation of one or more four-bar linkages and/or slider crank mechanisms. The systems created are of one degree of freedom, driven by the crank of the 1st mechanism of the configuration.
Once its solution is found the rest of the system is solved employing the outputs as the inputs to the corresponding mechanisms through a power graph. 

As well as solving the kinetics of the machine the program also determines the maximum Equivalent von Mises Stress on each of the links. This is accomplished solving *F=ma* in a system of equations to determine the forces on the joints, finding through 
numerical methods the centroids for each of the links (Figure 2) and analyzing slices of each link to establish the point of maximum stress. This requires to describe the profile of the links through single variable functions defined by parts. These links have 
therefore a variable cross section, which must be of constant thickness. Other than the change of area stress concentration is not taken into account and the average shear stress is used to calculate the Equivalent von Mises Stress (since shear stress effects tend
to be negligible [2]). To botain units in *__Pa__* the entries have to be in meters, rads/s, N-m, kg/m^3. N-m refers to the external moments which can be applied to either the coupler or output of each of the mechanism in the system, this external moments are applied 
on the same plane as the links and the stress analysis functionality is currently implemented only to four-bar linkages so any n-bar machine that is to be analyzed must take into consideration that all of its sub-mechanisms should be of this type.
![mechanism-mass-center](examples/mass_center.gif#center)

## Instalation
``` console
git clone https://github.com/FernandoLavarreda/KSAM
python -m pip install -r requirements.txt
cd src
python main.py
```

### Windows
Alternatively use the installer under *__Releases__*

## Usage
This is a GUI application although the code API is strongly recommended since it may be more intuitive to manipulate. The following explanation is centered on how to operate the GUI, to learn how to use the code API refer to *examples.py*.

### Structure
The GUI consists of a series of screens to define the components of the machine and ultimately to exact the analysis on it: Curves, Links, Mechanisms, Machines, Stresses.

#### Screen One: Curves
This screen is intended to define the functions and/or series of vectors that will be used to build a link. To create a new curve first click the button *__new__* which will populate the entries, give the function a name for example: quadratic. Then on the 
__Functions__ entry enter the following input: x**2{0, 2, 15}. Then press <kbd>Enter</kbd> this will draw a quadratic cuve x^2 from 0 to 2 (inclusive) with 15 linearly spaced inputs where dx = (2-0)/15 (f(2) will be always added). The press *__save__* and there you
have your fisrt function. Now lets create a vertical line. Press *__new__*, then type vertical on the name, and on the __Functions__ entry type 0{0, 4, 2} then type 90 in the Angle(°) and follow pressing *__rotate__* then press save. Finally create another horizontal
line using the function: 4{0, 2, 2}. The __Functions__ entry allows: constants (integers & floats), x, sin, tan and cos. You can define multiple functions as part of curve by simply entering a different value and pressing <kbd>Enter</kbd> again (All the functions will
be connected by a line that goes from the last function vector to the first vector in the next function entered) to clear the screen just press *__clear__*. Bear in mind that a rotation (always done around (0, 0)) and/or translation of a function will make it non 
suitable for stress analysis. Press *__delete__* to remove a selected curve. The Upload file functionality will be addressed in the next section.

![image](https://github.com/FernandoLavarreda/KSAM/assets/70668651/e8abfb8f-b0d8-4b54-af61-556c1cabd5b3)

#### Screen Two: Links
This screen is designed to build the links of a mechanism. If you click on the dropdown menu at the far right a series of links are already present, click them to see a preview. To create a new link press *__new__*. Then rename it to test_link, on the __Curves__ section
select each one of the curves previously created and add them to the link. Thickness is the thickness of the link (remember to work with meters if results in Pa are desired). Upper limits & Lower limits are used to define the functions that describe the shape of the link
if a stress analysis is desired. In this case enter 3 for upper limits and 1 for lower limits, since we desire the quadratic function to represent the lower boundary of the geometry and the horitzontal line to represent the upper boundary, press *__Set__*. Multiple 
curves can be used to define the upper and lower limits. If for example two functions are used to describe the upper limits (f1, and f2) and their respective domains are [0, 4] & [6, 10] the final function interpreted by the program will be from [0, 10] where the 
region (4, 6) a linear interpolation between the f1(4) and f2(6) will be performed. If there is any overlap the function with the smallest start will take presedence and override the behaviour of the other function. If multiple functions are entered they will be 
first ordered by start (lower limit of the domain) and then joined following the rules previously described. Save the link pressing *__save__*. The upper and lower limit functions should have the same domain and the connections of the link should be within the 
domain and range (otherwise inaccurate results will be presented). 

The connections are the joints of the link. To make it easier to place them select all the checkboxes, then select the *test_link* again in the dropdown. Enter x:0 y:0, then press add, then enter x:0 y:2, press *__save__* and select the link again. The connections should
appear as red dots on the preview. To see the values of each connection select them on the drowdown menu next to the button *__remove__*. The distance between the connections is the effective length of each link.

![image](https://github.com/FernandoLavarreda/KSAM/assets/70668651/d1563ef7-0087-4b04-98a9-3d991337dd05)

##### Upload file | Utils
Since the construction of visually appealing mechanisms is difficult using KSAM it has the ability to process csv files. In the utils directory in src an iLogic rule has been added to make it possible to generate the desired csv format through Inventor®. This tool 
expects an sketch in the XY plane (Use a negative number to reference the last sketch in the ipt) and a location to write the data to a csv. To create your own tools to integrate with KSAM, follow these conventions. The first line will be ignored. Then the entities 
that create a curve/curves should be stated followed by the x, y. An entity can have any name as long as it starts with __New__ + any_name. Then it should be followed by the x, y coordinates that describe it. A Point does not have the word __New__ next to it and it is
reserved to process a the next line as a connection of a link. When uploading a file to the section Links it will will load each entity as its own curve (but the curves will not be available in screen Curves, just available to be removed from the link itself) and the
points will be interpreted as the connections. If the uploading is done in the __Curves__ screen the user will be prompted to load all entities as one Curve (not recommended) and each entity will be connected to the next one with a line as the appear in the file 
with the name of the curve being the name of the file. Otherwise, each entity will be interpreted as its own curve with the name of the file and a counter starting from 1, Points will be ignored in this case. This allows to create visually complex mecanisms easier as
show in the image below.

![mechanism-mass-center](examples/detailed_piston.gif#center)

### Screen Three: Mechanisms
This screen is designed to build mechanisms, either four-bar mechanisms or slider-crank mechanisms. A few are placed in the dropdown menu to check their movement. Select *piston 1* and press *__Animate__*. Here __Inverion__ is used to describe either the open or cross
configuration of the mechanism not the inversion itself. Press the checkbox and run the animation again. Redraw is used to draw the desired configuration based on the __Input analge(°)__. Let's create a new mechanism, press *__new__*. In name place test, then select
the links that form part of the mechanism, for this example for the crank select *crank machine*, for the coupler and output select *test_link* and for the ground select *ground machine*. Then select the connection that will be used for each link. The connections are
presented by their location in the plane. The first connection of the crank is connected to (0, 0) the same for the ground, the first connection of the coupler is connected to the crank and the first connection of the output is connected to coupler. The same happens 
for the Slider-Crank option (which has no ground) but an offset of the slider from the crank first connection. __Mech. Rotation(°)__ refers to the rotation of the ground, for this situation enter 60° (this means that the actual angle of the mechanism is 24° since the
ground we copied from is rotated -36°, so the Mech rotation (°) is relative to the ground being copied). The __Stress Analysis__ option allows to perform a stress analysis on the mechanism, for this the lower and upper limits must be defined (as we did before). Select 
the option and save the mechanism. A differentials option will be presented, to get accurate and fast results 1e-4 is recommended, this is the size of the slices for the links. Then the density of the material is required to determine the mass of the links select 7850 
to simulate structural steel, again working in kg/m^3 to obtain the stress value in *Pa*. This may take some time. This creates the first mechanism. Now, an input function for the crank can be set in the __Input function__, by default it uses a linear set of 
radians [0, 2pi] (one hundred). This can be altered with a function just like the one presented in the Curves screen. now the variable is *time* instead of x. An example of 3.14159/2*sin(time){0, 6.28, 120} is presented below.

![mechanism-mass-center](examples/piston_sinusoidal_input.gif#center)

![image](https://github.com/FernandoLavarreda/KSAM/assets/70668651/aee77806-d6ab-4e0c-8f06-40ca5209960d)


### Screen Four: Machines
A machine was defined as one or more mechanisms that interact with each other. Again, like in the previuos screens: a series of examples are present to mess around with. Now lets create a new one, press *__new__* and rename it to *test_machine*. In the section 
__Available__ select *test* and add it. Then select *machine 1* and do the same. In the power graph enter *0{1, 2}*. What does this meean? The power graph presents the relationships between the input-output of each mechanism. In this case we are stating that the 
crank from the mechanism 1 (referenced as 0) powers both mechanism 1 and mechanism 2. The mechanisms are referenced in the order that they were added. In this case, 1 = *test* and 2 = *machine 1*. In the section __Inversion Array__ a series of 1s and 0s can be 
put in place to select the desired configuration of the mechanisms. If a single 0 or 1 is placed then all the mechanisms will be set to configuration 0 or 1 respectively. Otherwise, a configuration for each mechanism must be provided. For the example enter 01 
(*important* do not leave any space in between the numbers). The section __Background__ allows to place a series of links that will not rotate nor translate to make the visualization more visually apealing (like the chamber presented in the piston for the 
subsection __Upload file__). Now press *__save__*, then press *__Animate__*. The crank of *machine 1* wont appear in the animation this is because it is powered by the crank of *test*, grounds, couplers and outputs are always included. Now remove *machine 1*, 
enter 1 in the __Inversion Array__ and edit the power graph to be *0{1}* (*important* notice that mechanism 1 must always be powered by its crank). Then press *__save__*. Here the animation can be saved by selecting the checkbox before clicking 
*__Redraw__* | *__Animate__*. 

![image](https://github.com/FernandoLavarreda/KSAM/assets/70668651/869bba56-5b56-42ab-b146-8c76d22a09c6)

### Screen Five: Stresses
This screen determines the maximum Equivalent von Mises Stress for each link. Select *test_machine* enter an input angle of 10°, angular speed 1 (remember working rad/s to get *Pa*), angular acceleration of 0.5 (rad/s^2 to get *Pa*). Inversion array 1, External moments
couplers 2.5 (N-m to get *Pa*). Leave outputs empty. Then select both checkboxes and press *__Solve__*, you will be promted to select a location to save the report save it with the name report and wait for the solutions to be computed. This report can be later opened 
in the web browser. The green dots indicate the regions of max stress, the red dots are the mass centers for wich the accelerations are provided, the values of the report are in N, Pa, m/s^2 and rad/s^2 as long as the conventions for the other inputs have been followed.

![image](https://github.com/FernandoLavarreda/KSAM/assets/70668651/90986a9e-a312-4f82-bcbd-3ce8e3d8fc50)

## References
1. Norton, R. L. (2012). Design of machinery: An introduction to the synthesis and analysis of mechanisms and machines (5. ed). McGraw-Hill.
2. Budynas, R. G., Nisbett, J. K., & Shigley, J. E. (2015). Shigley’s mechanical engineering design (Tenth edition). McGraw-Hill Education.

# Using marker pen to apply support material contact surfaces for FDM printers
Hello! Here's a simple step-by-step guide:

Step 1: Buy a marker pen. We use the Zebra brand YYSS6-BK marker pen with an air-tight valve, which is sealing the pen when not pressed. If you have an i3 printer, you can print the fixer.stl directly; if not, find another way to fix it to the X-axis component of the printer (Note: avoid welding the marker pen too tightly as it would prevent incoming height adjustment and cause inconvenience during your installation; make sure it doesn't interfere with the X-axis endstop to avoid issues when homing).

Step 2: If you used the fixer.stl, just press the pen cap and raise the Z-axis of the printer until the pen tip touches the platform precisely, then record the Z height. If you fixed the pen by yourself, apply an A4 paper on the platform, move the axis, slightly lift the nozzle (e.g., Z2), press the pen cap, adjust the pen position up or down until the pen tip just touches the platform, then fix it and record the X, Y position. This step helps position the pen tip higher than the nozzle to reduce leakage.

Step 3: Skip this step if you used the fixer.stl. In the second step, the pen left a dot on the paper. Move the axis unitl the printer nozzle aligns with this dot. Record the X, Y position at this point and calculate the difference compared to the previous X, Y data.

Step 4: Print the trigger.stl. If it doesn't work, find an similar object and install it at a certain position on your Z-axis. When the pen rises to this position and hits the object, the pen cap will be pressed.

Step 5: Fill in the con.txt. Z-axis contact position is the height where the button can be pressed and held; X-axis contact trigger is still in development, so leave it at 0 for now. Is triggering structure only at Z axis, just leave it there. (I don't think there's anyone who wants to fix a bridge on his printer) Retraction length is the value for reducing leakage during application, fill in the desired retraction value. Retraction compensation is rarely used, so leave it at 0. Nozzle distance is the height of the nozzle when the pen tip just touches the platform. Enter the data based on the second step. Z-axis error compensation is not recommended. Leave it as 0 because the other tool is much better. Cooling for leak prevention is to reduce nozzle leakage, higher values for fast heating machines, or keep original data for slower ones. Force Z-axis home is better kept unchanged, but if you're sure that your machine is capable, you can change it to 0 to save time. Custom Deploy and Retract: If you want to use a stepper motor to press the pen cap, remove "undefined" and replace it with your GCODE.

Step 6: Open Prusa Slicer for slicing settings. Go to Print Settings -> Support Material. First-layer density: 100%; Top contact Z distance: 0 (soluble); Top interface layers: 1 or 2 (default) (we found two layers under a 0.2mm layer thickness works better for a 0.4mm nozzle); adjust the bottom interface layer as needed. XY separation distance between an object and its support, you can write a higher value for safety (we wrote 1.73).

Step 7: Slice the model and place the sliced Gcode in the same folder that Markpen.exe exists. Launch the program, and it will generate the _Output.Gcode and open the preview.

Step 8: Turn on the 3D printer and start printing happily.

Note: This project is still under development, and there might be unknown bugs. If you encounter any, please contact jhmodel01@outlook.com. The compressed package contains source code and needed files; it has no copyright, feel free to use.

Goodbye meow!

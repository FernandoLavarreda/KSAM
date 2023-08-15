#Fernando Lavarreda

import os
from gui.gui import GUI
from examples import examples

icon = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))+"\\Icon\\pistons.ico"
compresor = examples.build_compresor(3)
machine = examples.build_machine()
vline = examples.build_vline()
power_comp = examples.build_double_crank(5)
gui = GUI(links=compresor.mechanisms[0].links[:]+machine.mechanisms[0].links[:], mechanisms=compresor.mechanisms[:]+machine.mechanisms[:], machines=[compresor, machine, vline, power_comp], icon=icon)
gui.mainloop()

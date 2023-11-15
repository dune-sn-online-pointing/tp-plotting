# tp-plotting

This repo contains some simple functions to display Trigger Primitives.
It will be moved to `dune-daq`.

### Requirements

You just need matplotlib, numpy and dataclasses.

### Usage

The notebook should be self-explanatory.
`plot-tps.py` does the same thing, and the usage can be seen with `-h`. 
In short, you can give it a variable number of files with the flag `-f`, the number of tps to load and plot with `-n`.
You can decide to superimpose them on the same plot with the flag `-s`, default is `False`.

You can change some display options for each variable directly inside the pythons script.
Default location for output is `./output/`, you see the folder in the repo but its content is added to `.gitignore`.


### Include

All functions are in `include/PlottingUtils.py`. 
Definition of the TP dataclass is in `include/TriggerPrimitive.py`.
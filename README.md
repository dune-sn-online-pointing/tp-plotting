# tp-plotting

This repo contains some simple functions to display Trigger Primitives.
It will be moved to `dune-daq`.

### Requirements

You just need matplotlib, numpy and dataclasses.

### Input files
For textfiles, the idea is that the input files contain the TP variables in this order:
```
time_start, time_peak, time_over_threshold, channel, adc_integral, adc_peak, detid, type, algorithm, version, flags
```
If there are more variables after these (MC truth from offline), it's not a problem, they will just be ignored.

The example files in the repo come from offline, but are ok for testing.

### Usage

The notebook should be self-explanatory, and can be good for quick checks.

`plot-tps.py` does the same thing; the usage can be seen with `-h`. 
In short, you can give it a variable number of files with the flag `-f`, the number of tps to load and plot with `-n`.
You can decide to superimpose them on the same plot with the flag `-s`, default is `False`.

You can change some display options for each variable directly inside the pythons script.
Default location for output is `./output/`, you see the folder in the repo but its content is added to `.gitignore`.


### Include

All functions are in `include/PlottingUtils.py`. 
Definition of the TP dataclass is in `include/TriggerPrimitive.py`.
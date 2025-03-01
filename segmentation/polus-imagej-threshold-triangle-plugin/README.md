# ImageJ threshold triangle

This plugin implements the triangle threshold method. As described by [ImageJ](https://imagej.net/plugins/auto-threshold#triangle)
the Triangle algorithm, a geometric method, cannot tell whether the data is 
skewed to one side or another, but assumes a maximum peak (mode) near one end of 
the histogram and searches towards the other end. This causes a problem in the 
absence of information of the type of image to be processed, or when the maximum 
is not near one of the histogram extremes (resulting in two possible threshold 
regions between that max and the extremes). Here the algorithm was extended to 
find on which side of the max peak the data goes the furthest and searches for 
the threshold within that largest range.

Zack, G. W., Rogers, W. E., & Latt, S. A. (1977). Automatic measurement of 
sister chromatid exchange frequency. Journal of Histochemistry & Cytochemistry, 
25(7), 741–753. [doi:10.1177/25.7.70454](https://doi.org/10.1177/25.7.70454)


This WIPP plugin was automatically generated by a utility that searches for
ImageJ plugins and generates code to run them. For more information on what this
plugin does, contact one of the authors: Nick Schaub (nick.schaub@nih.gov), 
Anjali Taneja or Benjamin Houghton (benjamin.houghton@axleinfo.com).

For more information on WIPP, visit the [official WIPP page](https://isg.nist.gov/deepzoomweb/software/wipp).

## Building

Bump the version in the `VERSION` file.

Then to build the Docker image for the conversion plugin, run
`./build-docker.sh`.

## Install WIPP Plugin

If WIPP is running, navigate to the plugins page and add a new plugin.
Paste the contents of `plugin.json` into the pop-up window and submit.

## Options

This plugin takes one input argument and one output argument:

| Name       | Description                               | I/O    | Type       |
| ---------- | ----------------------------------------- | ------ | ---------- |
| `--inpDir` | Collection to be processed by this plugin | Input  | collection |
| `--opName` | Operation to perform                      | Input  | enum       |
| `--outDir` | Output collection                         | Output | collection |


#!/bin/bash

version=$(<VERSION)
datapath=$(readlink --canonicalize ../../data)

# Inputs
opName='ApplyThresholdMethod$Intermodes'
inpDir=/data/input

# Output paths
outDir=/data/output

docker run --mount type=bind,source=${datapath},target=/data/ \
            polusai/imagej-threshold-intermodes-plugin:${version} \
            --opName ${opName} \
            --inpDir ${inpDir} \
            --outDir ${outDir}
            
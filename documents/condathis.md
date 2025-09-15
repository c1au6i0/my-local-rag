#condathis




This repo it is an example of the use of using targets and condathis to create 
a pure R pipeline, system reproducibe, that tho uses other non-R command line interface tools (CLI).  Targets is a package that is used to run make-like pipeline.
Condathis is a CRAN package that allows to run CLI tools in Rmaintaing reproducibiliy and isoloration across systems.

# Motivation
As Bioinfarmatician working on omics data,  R it is extremelly and rich of packages, howver most of the tools used in the first phases of omics analysis are not r based.
Targets is great to create to create pipeline for R. Using targets + condathis we can create pipelines that integrate R tools and other CLI tools in an R enviroment maintaing reproducibility.


# [show-and-tell] {targets} and {condathis}: Pipelines Using R and Other CLI Tools

In our bioinformatics lab, we love using `targets` for omics analysis. One challenge we faced was that many upstream steps in the analysis require other, non-`R` command-line interface (CLI) tools. To allow us to create `targets` reproducible pipelines that integrate both `R` and other CLI tools, my friend @lucioqr created a CRAN package called `condathis`. This package was inspired by our experience with `targets`, and we wanted to share it here to show our appreciation for the work done on it. 
If you are curious, check out the [condathis repository](https://github.com/luciorq/condathis) for more details. Here’s also a **practical [example](https://github.com/c1au6i0/align-condathis-targets) of a bioinformatic reproducible pipeline** that employ `targets` and `condathis` to run common CLI tools for the in initial steps of an omics.
Best,

Check out the

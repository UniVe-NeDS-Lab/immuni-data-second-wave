## The code repository for the research paper: "On the Performance and Effectiveness of Contact Tracing Apps in the Second Wave of COVID-19 in Italy"

This repository contains the code and documentation to reproduce the results of the paper, yet to be published on IEEE Transactions on Computational Social Systems.


The folder contains a few data that are pre-downloaded and it will download more csv files from the Immuni github repository. There is also a zipfile named cahced-data.zip that contains all the data used for the paper, in case in the future the repositories may not work anymore. 

Run as:

`python3 monitor.py`

And then move in the `scripts` folder and run 

`gnuplot plot.gnuplot`

This will create all the figures present in the paper in the `images/` folder.

Please cite this paper as (I will update the citation as soon as the paper is assigned an issue):

```
@article{maccari2022performance,
   title = {{On the Performance and Effectiveness of Contact Tracing Apps in the Second Wave of COVID-19 in Italy}},
   author = {Maccari, Leonardo},
   journal = {{IEEE Transactions on Computational Social Sytstems}},
   year = "2022"
}
```

A work that is at the basis of this paper is the [ComCom](https://www.sciencedirect.com/science/article/pii/S0140366420319873) paper i wrote with Biologist Valeria Cagno:

```
@article{Maccari2020Need,
  title = {Do we need a contact tracing app?},
  journal = {Computer Communications},
  volume = {166},
  pages = {9-18},
  year = {2021},
  author = {Maccari, Leonardo and Cagno, Valeria},
  doi = {https://doi.org/10.1016/j.comcom.2020.11.007}
}
```


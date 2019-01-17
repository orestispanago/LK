# SCoSCo tracking absorber

### File types

- **.stinput** : SolTrace project - Contains all device elements and properties. Loading from the GUI is not necessary

- **.csi** :  spline file - Reflector shape

- **.lk** : scripts

### Scripts

- singletrace: runs trace for only one sun position
 
- sunpos_0_1000: test for multiple sun position simulations

- trace2csv: Runs simulation for each sun position and saves ray hit coordinates on flat absorber to csv

- plot_csv2gif: Reads csv files, plots and creates gif

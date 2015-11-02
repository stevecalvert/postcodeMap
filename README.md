# postcodeMap
postcodeMap.py generates a Google map .kml file which can be imported into Google MyMaps.  Here's a summary of the usage:-
 
(a) Create a customer / small cell usage spreadsheet mapping the usage to postcode region, as per smallcelldata.csv
(b) Run the python with three commands to specify the usage spreadsheet, the UK postcode boundary data .csv and the required output filename
 
$ python postcodeMap.py <small cell config.csv> < UK postcodes.csv> < output.kml>
 
(c)  Go to https://www.google.com/maps and select MyMaps from the options button top left.  You need to be signed in with your Google account for this
 
(d) Select 'Add Layer' and choose the import option to specify the generated .kml file

(note, the UK Postcode .csv file can be obtained from https://www.google.com/fusiontables/data?docid=1jgWYtlqGSPzlIa-is8wl1cZkVIWEm_89rWUwqFU#card:id=2.  Click on File / Download from the menu bar)
 
Hopefully you will see a map something like below
 
At the moment, the Python generates based on the column for the number of cells.  Update line 92 to specify row[2] to grab the 'number of customers' column or to tweak the scaling algorithm (currently based on the value as a proportion of the range of values to scale the intensity of the red colour)

![alt tag](https://raw.github.com/stevecalvert/postcodeMap/master/postcodeMap.png)
 

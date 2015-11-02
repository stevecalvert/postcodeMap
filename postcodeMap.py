
# coding: utf-8
import csv, sys
import struct
import os
from datetime import timedelta, datetime


# utilities to generate the postcode map based on Google.kml syntax
# https://developers.google.com/kml/documentation/kmlreference?hl=en
def writeKmlHeader():
    kml_file.write("""<?xml version='1.0' encoding='UTF-8'?>
<kml xmlns='http://www.opengis.net/kml/2.2'>
    <Document>
        <name>PostCodes</name>""")

# write the.kml header
def writeKmlFooter():
    kml_file.write("""
	</Document>
</kml>""")


def writePlacemarkHeader( postcode_name, num_small_cells, num_customers ):
    # first write the preamble
    kml_file.write("""
		<Placemark>
			<name>%s</name>
			<description>%u small cells, %u customers</description>
			<styleUrl>#%s_style</styleUrl>
			<ExtendedData></ExtendedData>
            """ % (postcode_name, num_small_cells, num_customers, postcode_name))


def writePlacemarkFooter( ):
    # first write the preamble
    kml_file.write("""
		</Placemark>""")


def writePlacemarkCoords( row ):
    # strip couple of unwanted preamble chars off beginning and end
    #print "Coords are <%s>" % row
    kml_file.write(row[2:-2])

    
def processSmallCellInfo():
    rowcount = 0
    sc_info = []
    sc_dict = {}
    with open(smallcell_file, 'rb') as scfile:
        smallcell_reader = csv.reader( scfile, delimiter=',', quotechar='|')
        
        # get the info into a list (of lists) but remove the header row
        sc_info = [x for x in smallcell_reader ]
        del sc_info[0]
    # get min and max values for APs and Customers
    min_AP = min( sc_info, key=lambda x: (int(x[1])))
    max_AP = max( sc_info, key=lambda x: (int(x[1])))
    min_cust = min( sc_info, key=lambda x: (int(x[2])))
    max_cust = max( sc_info, key=lambda x: (int(x[2])))
	
    print "min_cust %d max_cust %d min_AP %d max_AP %d" % (int(min_cust[2]), int(max_cust[2]), int(min_AP[1]), int(max_AP[1]))
        
    # for each postcode region, create a style for that postcode with a style colour
    # based on the number of cells or customers as a proportion of the maximum
    # use number of APs for now

    # cap to remove max peak
    max_cust_cap = (int(max_cust[2]) * 7) / 10
    max_AP_cap = (int(max_AP[1]) * 5) / 10

    # scale the colour from white to solid red to create a red-scale map ranging from ffffff to ff0000
    # red always remains at maximum hue
    # green and blue move together 
    red = 0xff
    cust_range = int(max_cust_cap) - int(min_cust[2])
    ap_range = int(max_AP_cap) - int(min_AP[1])

    for row in sc_info:
        rowcount+=1

        #print 'Writing style for %s' % row[0]
        #want the intensity of red to increase with increased cell/customer count
        #if the green/blue are both 0xff then the colour is white (RGB all at max)
        #with green/blue set to 0x0 then it is full red
        green_and_blue = 255 - (255 * (int(row[2]) - int(min_cust[2])) / cust_range)
        #green_and_blue = 255 - (255 * (int(row[1]) - int(min_AP[1])) / ap_range)
        if green_and_blue < 0:
           green_and_blue = 0

        #color comprises transparency:green:blue:red
        #fix the transparency at halfway, 0x80
        kml_file.write("""
    <Style id=\"%s_style\">""" % row[0])

        kml_file.write("""
        <LineStyle>
            <color>E0%02x%02x%02x</color>
            <width>1</width>
            <fill>1</fill>
        </LineStyle>
        <PolyStyle>
            <color>E0%02x%02x%02x</color>
            <fill>1</fill>
            <outline>1</outline>
        </PolyStyle>
    </Style>""" % (green_and_blue, green_and_blue, red, green_and_blue, green_and_blue, red))

        print 'Process small cell row %d' % rowcount
        sc_dict[row[0]] = (int(row[1]), int(row[2]))
        #print 'row[0]<%s>' % row[0]
        #print 'row[1]<%s>' % row[1]
        #print 'row[2]<%s>' % row[2]
        
    # need again to add postcode info to the <name> field
    return sc_dict


def processCsv():
    writeKmlHeader()
    
    # get a dictionary of the postcodes of interest
    sc_dict = processSmallCellInfo()

    rowcount = 0
    with open(postcode_file, 'rb') as csvfile:
        postcode_reader = csv.reader( csvfile, delimiter=',', quotechar='|')
        for row in postcode_reader:
            rowcount+=1
                       
            # row[0] is the postcode - if there's a match in the sc_dict then extract the boundary info
            try:
                if row[0] in sc_dict:
                    print 'Matched to %s %d %d' % (row[0], sc_dict[row[0]][0], sc_dict[row[0]][1] )
                    writePlacemarkHeader(row[0], sc_dict[row[0]][0], sc_dict[row[0]][1])
                    writePlacemarkCoords(str(row[1:]).replace(" '","").replace("'",""));
                    writePlacemarkFooter();
            except KeyError as e:
                print "Cannot find postcode %s" % row[0]
                #writePlacemarkHeader(row[0], 0, 0)
             
    writeKmlFooter()


if __name__ == "__main__":

    # Command line arguments are "small cell info .csv" "postcode info .csv" "output .kml file"
    if len(sys.argv) != 4:
        print 'usage: postcodeMap <small cell info .csv> <postcode boundaries .csv> <output .kml>'
        print sys.argv
        sys.exit(0)
        
    smallcell_file, postcode_file, kml_outfile = sys.argv[1:]

    kml_file = open(kml_outfile, 'w+')

    if os.path.isfile( smallcell_file ):
        print 'Checking Small cell data file'
    else:
        sys.exit(1)
    
    if os.path.isfile( postcode_file ):
        print 'Checking postcode file'
        processCsv()
    else:
        sys.exit(1)

    kml_file.close()


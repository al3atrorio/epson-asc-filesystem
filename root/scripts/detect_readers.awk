#!/usr/bin/awk -f

BEGIN {
	RS = ""
	FS = " "
}  

/Honeywell|Lunatron/{
	where = match($0, /event/)
    if (where != 0) {

    	split(substr($0, where), a, " ", seps)
    	if ($0 ~ "Honeywell") {
        	readers[++n] = "barcode"
        	devices[n] = a[1]
        }
        else if ($0 ~ "Lunatron") {
        	readers[++n] = "rfid"
        	devices[n] = a[1]
        }
    }

    where = match($0, /usb2\/2-/)

    if (where != 0) {
        port[n] = substr($0, where + 7,1)
    }
}

END{
	print "{"
	printf "\t\"devices\" : ["
	for (i=1; i<=n; i++) {
		printf "\n\t\t{\"type\" : \"%s\", \"input\" : \"%s\", \"port\" : \"%s\"}", readers[i], devices[i], "usb" port[i]
		if (i != n) printf ","
	}
	printf "\n\t],"

	printf "\n\t\"number_of_devices\" : \"%d\"", n

	print "\n}"
}
/*

Copyright (c) 2009 Jan Dittmer <jdi@l4x.org>

Run: gcc -o fugawi fugawi.c && ./fugawi Heide_rund.TRK 

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

*/
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define ph(t) if (!gpx) printf("        %02d: %02x%02x%02x%02x\n",t,r[t],r[t+1],r[t+2],r[t+3]);

#define LEAP_YEAR(year) ((!(year % 4) && (year % 100)) || !(year % 400))
     static const unsigned char days_in_month[] = {
	     31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31
     };

int month_days(unsigned int month, unsigned int year) {
	return days_in_month[month] + (LEAP_YEAR(year) && month == 1);
}

struct tm floatdate(double date) {
	struct tm t;
	int d = 30, m = 12, y = 1899;
	while(date > 1.0) {
		if (d == month_days(m-1,y)) {
			d = 0;
			m++;
		}
		if (m == 13) {
			m = 1;
			y++;
		}
		d++;
		date-=1.0;
	}
	//printf("%4d-%02d-%02d ",y,m,d);

	date *= 86400;
	date += 0.5;
	int hour,min,sec;
	sec = (int)date%60;
	date = date/60;
	min = (int)date%60;
	date = date/60;
	hour = (int)date;
	//printf("%02d:%02d:%02d\n",hour,min,sec);
	t.tm_sec = sec;
	t.tm_min = min;
	t.tm_hour = hour;
	t.tm_mday = d;
	t.tm_mon = m - 1;
	t.tm_year = y - 1900;
	return t;
}

void swap(unsigned char *r, int o, int n) {
	unsigned char tmp[n],k;
	for(k=0;k<n;k++) tmp[k] = r[o+k];
	for(k=0;k<n;k++) r[o+n-k-1] = tmp[k];
}

void swap_if_be(unsigned char *r, int o, int n) {
	unsigned char d[8] = {1,0,0,0,0,0,0,0};
	unsigned int *i = (unsigned int *)d;
	if ( *i != 1)
		swap(r,o,n);
}

int main(int argc, char *argv[]) {

	int s, p = 0, n = 0, ret = 0;
	unsigned char *d, *r, gpx = 0;
	if (argc < 2) {
		printf("No file specified\n");
	}
	if (argc >= 3) {
		if (!strcmp(argv[2],"gpx"))
			gpx = 1;
		if (!strcmp(argv[2],"kml"))
			gpx = 2;
	}
	if (!gpx)
		printf("File: %s\n", argv[1]);
	FILE *fh = fopen(argv[1], "r");
	if (!fh) {
		printf("Could not open file\n");
		return 1;
	}
	// get file size
	fseek(fh, 0, SEEK_END);
	s = ftell(fh);
	fseek(fh, 0, SEEK_SET);
	d = malloc(s); // this buffer has to be kept around...
	fread(d, s, 1, fh);
	fclose(fh);
	if (!gpx)
		printf("File size: %d Bytes\n", s);
	if ( (d[0] != 'F') || (d[1] != 'U') || (d[2] != 'G') ||
	     (d[3] != 'T') || (d[4] != 'R') || (d[5] != 'K') ) {
		printf("Invalid signature\n");
		r = d;
		ph(0);
		ret = 2;
		goto outfree;
	}

	if ((d[6] != 0xff) || (d[7] != 0xff)) {
		printf("Bytes 6+7 not 0xffff: 0x%02x%02x\n", d[6],d[7]);
		ret = 3;
		goto outfree;
	}
	if (!gpx)
		printf("\n");
	// 36 bytes header
	p = 36;
	n = 0;
	if (gpx == 1)
		printf("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\" ?>\n<gpx xmlns=\"http://www.topografix.com/GPX/1/1\" creator=\"fugawi.c jdi@l4x.org\" version=\"1.1\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd\"><trk><name>%s</name><desc></desc><trkseg>\n",argv[1]);
	if (gpx == 2)
		printf("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n\
				  <Document>\n\
				      <name>%s</name>\n\
				      <Placemark>\n\
				      <LineString>\n\
				      <tessellate>1</tessellate>\n\
				      <altitudeMode>absolute</altitudeMode>\n\
				                <coordinates>",argv[1]);


	while(p < s) {
		// each record has 48 bytes, little endian
		r = d + p;
		if (!gpx)
			printf("Pos: %05d, Record: %03d\n", p, n);

		// Bytes
		//  0- 3 ?
		//  4- 7 Hoehe
		//  8-11 Abstand
		// 12-15 ?
		// 16-19 Heading
		// 20-23 ?
		// 24-31 Breite
		// 32-39 Laenge
		// 40-47 ?
		ph(0);

		swap_if_be(r,4,4);
		float *height = (float *)(r + 4);

		swap_if_be(r,8,4);
		float *distance = (float *)(r + 8);

		ph(12);

		swap_if_be(r,16,4);
		float *heading = (float *)(r + 16);

		ph(20);

		swap_if_be(r,24,8);
		double *lat = (double *)(r + 24);
		swap_if_be(r,32,8);
		double *lng = (double *)(r + 32);

		swap_if_be(r,40,8);
		double *time = (double *)(r + 40);
		struct tm tmt = floatdate(*time);
		// 0 == 1889-12-30 00:00:00 UTC
		char stime[40];
		memset(stime,0,40);
		strftime(stime, 40, "%Y-%m-%dT%H:%M:%SZ", &tmt);
		stime[40] = 0;

		if (gpx == 1) {
			printf("<trkpt lat=\"%.8f\" lon=\"%.8f\">\n", *lat, *lng); // WGS84
			printf("    <ele>%f</ele>\n", *height);
			printf("    <time>%s</time>\n",stime);
			printf("</trkpt>\n");
		} else if (gpx == 2) {
			printf("%.8f,%.8f,%f\n", *lng, *lat, *height); // WGS84
		} else {
		printf("   Lat/Lng: %f / %f\n", *lat, *lng); // WGS84
		printf("    Height: %f m\n", *height);
		printf("  Distance: %f m\n", *distance);
		printf("   Heading: %f deg\n", *heading);
		printf(" Date/Time: %s\n",stime);
		printf("\n");
		}
		p += 48;
		n++;
	}
	if (gpx == 1)
		printf("</trkseg></trk></gpx>\n");
	if (gpx == 2)
		printf("</coordinates></LineString></Placemark></Document></kml>\n");
outfree:
	free(d);
	return ret;
}


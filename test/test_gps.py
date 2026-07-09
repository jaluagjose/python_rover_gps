from gps import GPSReader

gps = GPSReader("/dev/ttyUSB1", 9600)

gps.read_loop()

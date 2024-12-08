def get_location():
    latitude = 35.703798
    longitude = 51.221327
    return latitude, longitude



# import geocoder
# import gps

# def get_dynamic_location():
#     try:
#         session = gps.gps(mode=gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
#         report = session.next()
#         if report['class'] == 'TPV' and hasattr(report, 'lat') and hasattr(report, 'lon'):
#             latitude = report.lat
#             longitude = report.lon
#             print(f"GPS Location: Latitude={latitude}, Longitude={longitude}")
#             return latitude, longitude
#     except Exception as e:
#         print(f"GPS Error: {e}")
#     g = geocoder.ip('me')
#     if g.ok:
#         latitude, longitude = g.latlng
#         print(f"IP Location: Latitude={latitude}, Longitude={longitude}")
#         return latitude, longitude
#     else:
#         print("Error getting location")
#         return None, None





# import requests
# import serial
# import pynmea2

# def get_location_by_ip():
#     try:
#         response = requests.get('http://ipinfo.io/json')
#         data = response.json()
#         location = data['loc'].split(',')
#         latitude = location[0]
#         longitude = location[1]
#         print(f"IP Location: Latitude={latitude}, Longitude={longitude}")
#         return latitude, longitude
#     except Exception as e:
#         print(f"Error getting location by IP: {e}")
#         return None, None

# def get_gps_location():
#     try:
#         gps = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)
#         while True:
#             data = gps.readline().decode('ascii', errors='replace')
#             if data.startswith('$GPGGA'):
#                 msg = pynmea2.parse(data)
#                 latitude = msg.latitude
#                 longitude = msg.longitude
#                 print(f"GPS Location: Latitude={latitude}, Longitude={longitude}")
#                 return latitude, longitude
#     except Exception as e:
#         print(f"Error getting GPS location: {e}")
#         return None, None

# def get_dynamic_location():
#     # Try getting GPS location first, if not available, fall back to IP geolocation
#     gps_location = get_gps_location()
#     if gps_location != (None, None):
#         return gps_location
#     else:
#         print("GPS not available. Using IP location instead.")
#         return get_location_by_ip()

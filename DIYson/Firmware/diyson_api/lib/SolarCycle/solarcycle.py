"""
MIT License
Copyright (c) 2023 Joseph0M

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from datetime import datetime, timezone
from suntime import Sun, SunTimeException #pip install suntime
import numpy as np

class Solar:
    def __init__(self):
        ##LOCATION##
        self.latitude = 51.4934
        self.longitude = 0.0098 #Exampe Values
        ##LED VALUES##
        self.LED_Values = {
            'CCT': {
                'min_CCT': 1800,
                'max_CCT': 6500, #(Kelvin) Defalt Values, Change to suit your LED's

                'sunrise_CCT': 2000,
                'noon_CCT': 6000, #Kelvin, Values for sun tracking
                'sunset_CCT': 2000,
            },

            'BRIGHTNESS': {
                'min_BRT': 0,
                'max_BRT': 100, #Percentage

                'min_lux': None,
                'max_lux': None, #Values in Lux (Lumens/centre desk area)
            },

            'CRI': 90
        }
    def get_LED_Values(self,value):
        table = self.LED_Values
        for type in table:
            if value in table[type]:
                return table[type][value]
        return None

    def utc_to_local(self,utc_dt):
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

    def time(self):
        now = datetime.now()
        return int(now.strftime("%H")),int(now.strftime("%M")),int(now.strftime("%S"))
    
    def calculate_hourly_insolation(self,latitude,day_of_year,hour) -> float:
        elev = np.degrees(np.arcsin(np.sin(np.radians(latitude)) * np.sin(np.radians(23.45 * np.sin(np.radians(360 * (284 + day_of_year) / 365)))) + np.cos(np.radians(latitude)) * np.cos(np.radians(23.45 * np.sin(np.radians(360 * (284 + day_of_year) / 365)))) * np.cos(np.radians(15 * (hour - 12)))))
        return(max(0, np.sin(np.radians(elev))))
    
    def sunrise_sunset(self):
        sun = Sun(self.latitude, self.longitude)
        today_sr = self.utc_to_local(sun.get_sunrise_time())
        today_ss = self.utc_to_local(sun.get_sunset_time())
        return int(today_sr.strftime("%H"))+(int(today_sr.strftime("%M"))/60)+(int(today_sr.strftime("%S"))/3600), int(today_ss.strftime("%H"))+(int(today_ss.strftime("%M"))/60)+(int(today_ss.strftime("%S"))/3600)
    
    def cct(self,mincct,maxcct,ssn):
        sr,ss = self.sunrise_sunset()
        a1,b1,a2,b2,a3,b3 = sr,min(maxcct,max(mincct,ssn[0])),12,min(maxcct,max(mincct,ssn[1])),ss,min(maxcct,max(mincct,ssn[2]))
        hours,mins,secs = self.time()
        x = hours+(mins/60)+(secs/3600)
        cct = (b1*(((x-a2)*(x-a3))/((a1-a2)*(a1-a3))))+(b2*(((x-a1)*(x-a3))/((a2-a1)*(a2-a3))))+(b3*(((x-a1)*(x-a2))/((a3-a1)*(a3-a2))))
        return int(max(mincct,min(cct,maxcct))) #Kelvin
    
    def brightness(self,minbri,maxbri):
        h,m,s = self.time()
        time = h+(m/60)+(s/3600)
        insolation = self.calculate_hourly_insolation(self.latitude,datetime.now().timetuple().tm_yday,time)
        peak = self.calculate_hourly_insolation(self.latitude,datetime.now().timetuple().tm_yday,12)
        insolation = (insolation/peak)*100 #percentage
        return(max(minbri,min(insolation,maxbri)))
        
    def age_intensity_multiplier(self,age):
        return max(1,((1/382.5)*(min(age,100)**2))-1.4) #multiply by the intensity to get the correct value (percentage)
    
def example_code():
    srcct = 2000 #sunrise_cct
    sscct = 2000 #sunset_cct
    ncct = 6000 #noon_cct
    minbri = 0
    maxbri = 100
    mincct = 1800
    maxcct = 6500
    solar = Solar()
    print(f"Sunrise: {solar.sunrise_sunset()[0]}")
    print(f"Sunset: {solar.sunrise_sunset()[1]}")
    print(f"Time: {solar.time()[0]}:{solar.time()[1]}:{solar.time()[2]}")
    print(f"Sunlight Intensity: {solar.brightness(minbri=minbri,maxbri=maxbri)}%")
    print(f"CCT: {solar.cct(mincct=mincct,maxcct=maxcct,ssn=[srcct,ncct,sscct])}K")
    print(f"Age Intensity Multiplier: {solar.age_intensity_multiplier(50)}")
#example_code()
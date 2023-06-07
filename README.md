# DIYson-SolarCycle-Firmware
Firmware that adds support for solar tracking, WiFi Comaptibility and other Smart fetures to Steven Bennett's DIYson Lamp Project. The firmware is designed to be run on a Raspberry Pi Zero for it's high processing capability. Please see Releses for the most up-to-date verison

## Hardware Info

The repo is designed to be an on a Raspberry Pi Zero 2 W for its high processing capability and small form factor. this compatibility also extends to the Raspberry Pi 3/4B and Compute Module 3+/4

Limited support is availble for Raspberry Pi Pico and similar microcontrollers. Install Adafruit Circuitpython 8.0.0 or higher and Unzip lib.zip and dump contents in lib folder.

### Sensor Info
The algorithm uses the following sensors:
* VL53L1X Time of Flight(ToF) Sensor
    * Used For: 
        * Object Distance detection
        * Lamp Height detection
     * Applications:
        * Reading/Book Mode (Future Addition)
        * Brightness ajustment
* LTR-559 Ambient light and Proximity sensor (ALS)
    * Used For:
       * Finding Abient Light levels
       * Close object detection
    * Applications:
       * Brightness control
       * Touchless lamp activation
* Flick Zero 3D Gesture and Capacitive touch sensor (GCS) (Future addition)
    * Used For:
       * Detecting 3D Gestures and taps
    * Applications:
       * Touchless lamp operation
# Solar Tracking with the DIYson	
	
Please see `solarcycle.py` in the latest commit at the bottom for the main Algorithm.
The aim with this algorithm is to provide the capability of changing **CCT (Colour temperature)**  and **intensity** based on the sun's movement throughout the day. it also includes the age multiplier function that **varies the light intensity based on age**, replicating the feature from Dyson. Although the DIYson currently does not have a tuneable CCT LED, I hope this algorithm can spark a discussion about the addition of smarter features that Dyson offers, e.g., motion sensing and object distance sensing with a ToF sensor.	
	
## How the algorithm works	

Based on Dyson's advertised features, I have tried to replicate some of them in this algorithm. Currently, there are no APIs or publicly accessible data, nor are there any equations that can estimate the approximate CCT of the sun at a given location and time. Instead, I have gone through the mathematical route. Hopefully this explanation will demystify my completely unreadable code.	
	
### CCT Calculations	
	
I have used a quadratic formula to estimate the Colour temperature of the sun, in  the form: *y = ax + bx + c*, Where y = CCT and x = local time. The crucial element of this equation is the use of sunset and sunrise times. When the sun rises and sets, the CCT is often at its lowest point, usually around 2000K, while noon is around 5000–6500K. We can construct this equation so that the parabola intersects 2000 in the y and the sunrise/sunset time in the x. A parabola (quadratic graph) looks something like this:	
<img src="https://user-images.githubusercontent.com/75663305/222946110-aaaa3f06-0280-40e4-be06-ba75d90e5002.png" alt="Parabola Graph" width="200">
	
As the sunset and sunrise times change during the year, the module "Suntime" is used so that the parabola is constantly changing throughout the year. In the UK, the parabola would be at its widest in the summer, and in the winter, it would be at its narrowest To facilitate this, another equation is used to calculate the equation, as seen below:	

<img src="https://user-images.githubusercontent.com/75663305/222946274-996b23c5-067d-4818-8004-a21e3d07f086.png" alt="Equation by Dean Rubine" height="50">
	
### Where:	
	
* **f(x)** = Sun's CCT
 	
* **x** = local time	

* **a1**, **b1** = (Sunrise Time, Sunrise CCT)	

* **a2**, **b2** = (Noon, Noon CCT)	
	
* **a3**, **b3** = (Sunset Time, Sunset CCT)	
	
And finally, this is returned as a percentage of the minimum and maximum CCT that the LED can replicate.	
	
### Solar Insolation (Intensity)	
	
Compared to the CCT replication algorithm, there are many equations used to calculate the intensity of the sun given the location and time in the public domain. I will not cover most of this, as I am not a certified astrophysicist, nor could I verify that this equation is accurate based on the supplied readings. However I will briefly go through it.	

The algorithm takes into account the *Solar Constant* (1364 W/m^2), the *relative sun-earth distance* (1.1), and the *atmospheric turbidity factor* (0.6). It also takes in the latitude and longitude of the user. The intensity is then returned as a percentage and can be used in conjunction with the age multiplier function.	
	
### Final Thoughts	
	
Along with these features, values are always checked for violations of LED specs and user settings before being returned. As this algorithm is contained in a class, it can be imported or integrated into existing scripts fairly easily. This fork currently does not contain DIYson Express files or 3D parts for simplicity.


# WiFi Compatibility

the Latest commit includes Major changes and additions to Firmware. This is to support the addition of a locally hosted API for the Lamp. The firmware does not support manual inputs (buttons ect) at the moment.

Documentation will follow soon.

## How to use the API

* Make sure you are running Python 3.11 or Higher
* Type the following into Terminal/CMD Line
    * pip install fastapi
    * pip install "uvicorn[standard]"
    * pip install pydantic
* Navigate to DIYson/Firmware/diyson_api/lib/config.json
* Change the IP address under SERVER_DATA to the IP address of your device
* Run Main.py at DIYson/Firmware/main.py
* In your browser enter your IP address and Port.
    * It should look a bit like this: 127.0.0.1:8005/docs
* Authorize your browser by clicking "Authorize" at the top right
    * the defult Username is "app" and the Password is "test"

You can now play around with the API, it should display all the avalible Endpoints.

**Modifing the config.json and Hardware.py files are a MUST**. The values and code depend on your hardware and configuration.

If you want to use the SolarCycle module on its own, you can import it from DIYson/Firmware/diyson_api/lib/SolarCycle/solarcycle.py

### To-do list:
* Auto Mode (Graph Peak detection)
* Flick Zero 3D gesture support
* Easier to operate UI
* Manual input support
* a full Firmware Build

# API Documentation


## /v1/users

### **/v1/users/token/**
*login_for_access_token*

     Authorisation = False
     Method = Post
     Response = {"access_token": str,"token_type":"bearer"} -> json
     
**Application:**
```
import requests
form_data = {
  "username": "app",
  "password": "test"
}
url = "http://127.0.0.1:8005/v1/users/token"
response = requests.post(url,data=form_data)
token = response.json()['access_token']
```
### **/v1/users/get_user/**

*get_logged_in_user*

     Authorisation = True
     Method = Get
     Response = {'username': str, 'full_name': str, 'disabled': Bool} -> json

**Application:**
```
import requests
headers = {
    'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + token,
} 
url = "http://127.0.0.1:8005/v1/users/get_user"
response = requests.get(url, headers=headers)
print(response.json())
```

### **/v1/users/disable_user/**

*delete_user*

     Authorisation = True
     Method = Delete
     Response = {'username': str, 'full_name': str, 'disabled': Bool} -> json

**Application:**
```
import requests
headers = {
    'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + token,
} 
url = "http://127.0.0.1:8005/v1/users/disable_user"
response = requests.delete(url, headers=headers)
print(response.json())
```

##/v1/state

### **/v1/state/set_state/**

*set_lamp_status*

     Authorisation = True
     Method = Post
     Response = {'status': str, 'user': str} -> json
     Valid Data = "IDLE","READY","BUSY"

**Application:**
```
import requests
headers = {
    'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + token,
} 
url = "http://127.0.0.1:8005/v1/state/set_state/?"+state
response = requests.post(url, headers=headers)
print(response.json())
```

### **/v1/state/get_state/**

*get_lamp_status*

     Authorisation = True
     Method = Get
     Response = {'status': str, 'user': str} -> json

**Application:**
```
import requests
headers = {
    'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + token,
} 
url = "http://127.0.0.1:8005/v1/state/get_state/"
response = requests.get(url, headers=headers)
print(response.json())
```

## /v1/data

### **/v1/data/generate_cct/**

*generate_cct_value*

     Authorisation = True
     Method = Get
     Response = {'CCT VALUE': float, 'user': str} -> json

**Application:**
```
import requests
headers = {
    'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + token,
} 
url = "http://127.0.0.1:8005/v1/data/generate_cct/"
response = requests.get(url, headers=headers)
print(response.json())
```

### **/v1/data/generate_intensity/**

*generate_intensity*

     Authorisation = True
     Method = Get
     Response = {'INTENSITY VALUE': float, 'user': str} -> json

**Application:**
```
import requests
headers = {
    'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + token,
} 
url = "http://127.0.0.1:8005/v1/data/generate_intensity/"
response = requests.get(url, headers=headers)
print(response.json())
```

### **/v1/data/get_aim/**

*get_age_intensity_multiplier*

     Authorisation = True
     Method = Get
     Response = {'AIM': float, 'user': str} -> json

**Application:**
```
import requests
headers = {
    'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + token,
} 
url = "http://127.0.0.1:8005/v1/data/get_aim/"
response = requests.get(url, headers=headers)
print(response.json())
```

### **/v1/data/get_sss_sr/**

*get_sunrise_and_sunset*

     Authorisation = True
     Method = Get
     Response = {'SUNRISE': float, "SUNSET": float, 'user': str} -> json

**Application:**
```
import requests
headers = {
    'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + token,
} 
url = "http://127.0.0.1:8005/v1/data/get_sss_sr/"
response = requests.get(url, headers=headers)
print(response.json())
```

### **/v1/data/get_config/**

*get_config*

     Authorisation = True
     Method = Get
     Response = {'CONFIG': {json}, 'user': str} -> json

**Application:**
```
import requests
headers = {
    'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + token,
} 
url = "http://127.0.0.1:8005/v1/data/get_config/"
response = requests.get(url, headers=headers)
print(response.json())
```

## /v1/lamp

### **/v1/lamp/set_bri/**

*set_lamp_brightness*

     Authorisation = True
     Method = Post
     Response = {'CONFIG': {json}, 'user': str} -> json
     Parameters = {
     	bri: int = 100,
	incriment: int = 1
	}
	
**Application:**
```
import requests
headers = {
    'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + token,
} 
url = "http://127.0.0.1:8005/v1/lamp/set_bri/?bri="+str(brightness)+"&incriment="+str(incriment)
response = requests.post(url, headers=headers)
print(response.json())
```

### **/v1/lamp/get_intensity/**

*get_intensity*

     Authorisation = True
     Method = Get
     Response = {'INTENSITY': {json}, 'user': str} -> json

**Application:**
```
import requests
headers = {
    'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + token,
} 
url = "http://127.0.0.1:8005/v1/lamp/get_intensity/"
response = requests.get(url, headers=headers)
print(response.json())
```

### **/v1/lamp/get_distance/**

*get_intensity*

     Authorisation = True
     Method = Get
     Response = {'DISTANCE': float,'PROXIMITY': float, 'user': str} -> json
     Parameters = {
     	range: int = 1,2 or 3
	}

**Application:**
```
import requests
headers = {
    'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + token,
} 
url = "http://127.0.0.1:8005/v1/lamp/get_distance/?range="+str(range)
response = requests.post(url, headers=headers)
print(response.json())
```

### **/v1/lamp/get_ambient_light/**

*get_ambient_light*

     Authorisation = True
     Method = Get
     Response = {'AMBIENT_LIGHT': float, 'user': str} -> json

**Application:**
```
import requests
headers = {
    'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + token,
} 
url = "http://127.0.0.1:8005/v1/lamp/get_ambient_light/"
response = requests.post(url, headers=headers)
print(response.json())
```

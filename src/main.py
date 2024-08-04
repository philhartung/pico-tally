import network
import time
import ujson
import asyncio
from tinyweb import webserver as TinyWeb
from neopixel import NeoPixel
from machine import ADC

# init
app = TinyWeb(7413)
leds = NeoPixel()
sensor = ADC(4)

# load config
with open('config.json', 'r') as f:
    config = ujson.load(f)

# functions
def display_ip(addr):
    parts = addr.split('.')
    col = 12
    row = 2
    for part in parts:
        power=7
        intpart = int(part)
        while intpart != 0:
            rest = intpart - 2 ** power
            pixel = (row + (7 - power)) * 16 + col
            if rest >= 0:
                intpart = rest
                leds.pixels_set(pixel, (255, 255, 0))
            else:
                leds.pixels_set(pixel, (0, 0, 0))
            power -= 1
        col += 1
    leds.pixels_show()

def parse_query_string(query_string):
    params = {}
    pairs = query_string.split('&')
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            params[key] = value
    return params

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def init_display():
    global r, g, b, brightness
    r = 0
    g = 0
    b = 0
    brightness = 0
    leds.pixels_set(0, (0, 255, 0))
    leds.pixels_set(1, (255, 0, 0))
    leds.pixels_set(2, (255, 0, 0))

    # set name and display id
    if config['id'] < 10:
        config['name'] = config['name'] + '0' + str(config['id'])
    else:
        config['name'] = config['name'] + str(config['id'])
    
    for i in range(config['id'] % 10):
        leds.pixels_set(15 - i, (0, 0, 255))
        
    leds.pixels_show()

def connect_to_wifi(ssid, password):
    global wlan
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.config(hostname=config['name'])
    wlan.connect(ssid, password)

    while not wlan.isconnected():
        print("Connecting to network...")
        leds.pixels_set(1, (255, 0, 0))
        leds.pixels_show()
        time.sleep(0.5)
        leds.pixels_set(1, (0, 0, 0))
        leds.pixels_show()
        time.sleep(0.5)
    
    leds.pixels_set(1, (0, 255, 0))
    leds.pixels_show()
    
    print("Connected to", ssid)
    print("IP address:", wlan.ifconfig()[0])
    display_ip(wlan.ifconfig()[0])

    parts = wlan.ifconfig()[0].split('.')
    for part in parts:
        if len(part) < 3:
            part = ' ' * (3 - len(part)) + part
        leds.displayStringHorz(part, 0, 3, (255, 255, 0), (0, 0, 0))
        if config['displayIP']:
            time.sleep(1)
    
    return wlan.ifconfig()[0]

def displayConnectionStatus(duration):
    leds.pixels_fill((0, 0, 0), 0.5)
    for i in range(duration * 2):
        rssi = wlan.status('rssi')
        
        if rssi > -45:
            color = (0, 255, 0)
        elif rssi > -70:
            color = (255, 255, 0)
        else:
            color = (255, 0, 0)
            
        leds.displayStringHorz(str(rssi), 2, 2, color, (0, 0, 0))
        time.sleep(0.5)
    
    leds.pixels_fill((r, g, b), brightness)
    leds.pixels_show()

def readTemp():
    adc_value = sensor.read_u16()
    volt = (3.3/65535)*adc_value
    temperature = 27 - (volt - 0.706)/0.001721
    return round(temperature, 1)

# routes
@app.route("/connection")
async def connection(req, res):
    params = parse_query_string(req.query_string.decode('utf-8'))
    duration = int(params.get('duration', 30))
    await res.start_html()
    await res.send('Displaying connection status')
    await asyncio.sleep(0.2)
    displayConnectionStatus(duration)

@app.route("/id")
async def connection(req, res):
    await res.start_html()
    await res.send('Displaying ID')
    leds.pixels_fill((0, 0, 0), 0.4)
    leds.displayStringHorz(str(config['id']), 2, 2, (0, 255, 0), (0, 0, 0))
    

@app.route("/status")
async def status(req, res):
    status = {
        "hostname": config['name'],
        "id": config['id'],
        "address": address,
        "red": r,
        "green": g,
        "blue": b,
        "brightness": brightness,
        "rssi": wlan.status('rssi'),
        "temperature": readTemp(),
        "uptime": round(time.ticks_diff(time.ticks_ms(), startTime) / 1000)
    }
    
    await res.start_json()
    res.add_access_control_headers()
    await res.send(ujson.dumps(status))

@app.route("/set")
async def set(req, res):
    global r, g, b, brightness
    params = parse_query_string(req.query_string.decode('utf-8'))
    color = params.get('color', None)
    brightness = params.get('brightness', None)
    
    try:
        if color and brightness:
            r, g, b = hex_to_rgb(color)
            brightness = float(brightness)
            
            if 0 <= brightness <= 1:
                response = f"Color set to (R: {r}, G: {g}, B: {b}), brightness set to {brightness}"
                leds.pixels_fill((r, g, b), brightness)
                leds.pixels_show()
                time.sleep(0.05)
                leds.pixels_show()
            else:
                response = "Brightness must be between 0 and 1"
        else:
            response = "Invalid request"
    except ValueError:
        response = "Invalid color or brightness value"
        
    await res.start_html()
    await res.send(response)

@app.route("/setRGB")
async def set(req, res):
    global r, g, b, brightness
    params = parse_query_string(req.query_string.decode('utf-8'))
    
    try:
        r = int(params.get('r', 0))
        g = int(params.get('g', 0))
        b = int(params.get('b', 0))
        brightness = float(params.get('brightness', 0))
        
        if 0 <= brightness <= 1 and 0 <= r <= 255 and  0 <= g <= 255 and  0 <= b <= 255:
            response = f"Color set to (R: {r}, G: {g}, B: {b}), brightness set to {brightness}"
            leds.pixels_fill((r, g, b), brightness)
            leds.pixels_show()
            time.sleep(0.05)
            leds.pixels_show()
        else:
            response = "Brightness must be between 0 and 1"
    except ValueError:
        response = "Invalid color or brightness value"
        
    await res.start_html()
    await res.send(response)

# connect to wifi and start webserver
startTime = time.ticks_ms()
init_display()
address = connect_to_wifi(config['wifi_ssid'], config['wifi_password'])
leds.pixels_set(2, (0, 255, 0))
leds.pixels_show()
app.run(host='0.0.0.0', port=config['port'])


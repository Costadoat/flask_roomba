import serial
import time
import matplotlib.pyplot as plt
from bitstring import Bits

# Initialisation de la connexion avec le Roomba
ser = serial.Serial()
ser.baudrate = 115200
ser.port = "/dev/ttyUSB0"
# ser.timeout=1
ser
ser.open()
ser.isOpen()

# Mode safe
ser.write(bytearray([128,131]))
# time.sleep(.5)
# Play mario song 
#ser.write(bytearray([140,2,7,88,8,88,16,88,16,84,8,88,16,91,32,79,16]))
#ser.write(bytearray([141,2]))
# # Play Zelda song 
# ser.write(bytearray([140,3,7,65,8,70,8,70,8,72,8,74,8,75,8,77,32]))
# ser.write(bytearray([141,3]))
# Play song
#ser.write(bytearray([140,0,15,62,8,68,8,71,8,68,8,73,8,71,8,68,8,71,8,52,8,56,8,56,8,59,8,61,8,59,8,56,8]))
#ser.write(bytearray([141,0]))

ser.write(bytearray([140,0,12,69,17,69,17,74,17,71,34,69,17,65,68,65,17,65,17,71,17,69,17,65,17,62,68]))
ser.write(bytearray([141,2]))


def led(name,color,intensity,duration):
    l=['debris','spot','dock','check'].index(name)
    ser.write(bytearray([139,4,color,intensity]))
    time.sleep(duration)
    ser.write(bytearray([139,4,0,0]))

#while True:
#    for l in ['debris','spot','dock','check']:
#        led(l,255,255,4)

ser.write(bytearray([139,0,255,255]))
time.sleep(2)
ser.write(bytearray([139,0,255,0]))

duree=2
depart=0.5


vitd = 100
d = vitd.to_bytes(2,'big',signed=True)
vitg = 100
g = vitg.to_bytes(2,'big',signed=True)

# Direct Drive
# ser.write(bytearray([145,d[0],d[1],g[0],g[1]]))
# # Drive PWM 
# ser.write(bytearray([146,d[0],d[1],g[0],g[1]]))

start_move = True

x_time_f = []
res_list = []

t0 = time.time()
t = time.time()
while (t - t0) <= duree:
    t = time.time()
    if (t - t0) > depart and start_move:
        # # Drive PWM 
        ser.write(bytearray([146,d[0],d[1],g[0],g[1]]))
        start_move =  False
    
    if (t - t0) > duree:
        break   
    x_time_f.append(t-t0)
    ser.write(bytearray([149,4,43,44,54,55]))#Encoder+Current
    res_list.append(ser.read(8))  
ser.write(bytearray([137,0,0,1,244]))# stop 
 


y_reel_f = []
y_reel_f2 = []
y_reel_f3 = []
y_reel_f4 = []

#Conversion
for res_i in res_list:
#     y_reel_f.append(res_i[0]*16**2+res_i[1])
#     y_reel_f2.append(res_i[2]*16**2+res_i[3])   
    y_reel_f.append(Bits(res_i[0:2]).int)
    y_reel_f2.append(Bits(res_i[2:4]).int)
    y_reel_f3.append(Bits(res_i[4:6]).int)
    y_reel_f4.append(Bits(res_i[6:8]).int)

plt.plot(x_time_f,y_reel_f3)
plt.show()
# Stop

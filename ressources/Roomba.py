import serial
import time
import matplotlib.pyplot as plt


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




# Led Clean Rouge
ser.write(bytearray([139,0,255,255]))
# time.sleep(.5)

# Led
ser.write(bytearray([139,6,0,0]))
# time.sleep(.5)

# Bumper
ser.write(bytearray([149,1,7]))
res = ser.read(1)
print(res[0])

# Bumper
while True:
    ser.write(bytearray([149,1,7]))
    res = ser.read(1)
    print(res[0])
    time.sleep(0.1)



# Buttons
ser.write(bytearray([149,1,18]))
res = ser.read(1)
print(res)

while True:
    ser.write(bytearray([149,1,18]))
    res = ser.read(1)
    print(res[0])
    time.sleep(0.01)



# Encoders
ser.write(bytearray([149,1,44]))
res = ser.read(2)
print(res)
print(res[0]*16**2+res[1])

while True:
    ser.write(bytearray([149,1,44]))
    res = ser.read(2)
    print(res[0]*16**2+res[1])   



ser.write(bytearray([149,1,43]))
res = ser.read(2)
print(res)


# Charge 
ser.write(bytearray([149,1,21]))
res = ser.read(1)
print(res)

# Charge source
ser.write(bytearray([149,1,34]))
res = ser.read(1)
print(res)


# Recule
ser.write(bytearray([137,255,56,127,255]))
time.sleep(1)
ser.write(bytearray([137,0,0,1,244]))# stop

# Avance
ser.write(bytearray([137,0,200,127,255]))
time.sleep(1)
ser.write(bytearray([137,0,0,1,244]))


# Avance lente
ser.write(bytearray([137,0,20,127,255]))
time.sleep(5)
ser.write(bytearray([137,0,0,1,244]))





# Avance PWM 
ser.write(bytearray([145,0,50,0,50]))
time.sleep(2)
ser.write(bytearray([145,0,0,0,0]))

# Angle
ser.write(bytearray([149,1,20]))
res = ser.read(3)
print(res)
# Rotation PWM +
ser.write(bytearray([145,255,205,0,50]))
time.sleep(5)
ser.write(bytearray([145,0,0,0,0]))
# Rotation PWM -
ser.write(bytearray([145,0,50,255,205]))
time.sleep(5)
ser.write(bytearray([145,0,0,0,0]))


# Angle
ser.write(bytearray([149,1,20]))
res = ser.read(3)
print(res)


# Trajectoire carré (approx)
for i in range(4):
    # Rotation PWM +
    ser.write(bytearray([145,255,205,0,50]))
    time.sleep(3.5)
    ser.write(bytearray([145,0,0,0,0]))
    # Avance PWM 
    ser.write(bytearray([145,0,50,0,50]))
    time.sleep(5)
    ser.write(bytearray([145,0,0,0,0]))



# Affichage
ser.write(bytearray([164,65,66,67,68]))
time.sleep(0.2)
ser.write(bytearray([164,32,32,32,32]))


# Distance
ser.write(bytearray([149,1,19]))
res = ser.read(2)
print(res)

# Avance PWM 
ser.write(bytearray([145,0,50,0,50]))
time.sleep(1)
ser.write(bytearray([145,0,0,0,0]))

# Distance
ser.write(bytearray([149,1,19]))
res = ser.read(2)
print(res)

# Recule PWM 
ser.write(bytearray([145,255,205,255,205]))
time.sleep(1)
ser.write(bytearray([145,0,0,0,0]))

# Tension batterie
ser.write(bytearray([149,1,22]))
res = ser.read(2)
print(res)
print(res[0]*16**2+res[1])




def PWM_motor(speed_left,speed_right,t):
    if speed_left < 0:
        v10 = 255
        v11 = speed_left + v10
    else:
        v10 = 0
        v11 = speed_left      
    if speed_right < 0:
        v20 = 255
        v21 = speed_right + v20
    else:
        v20 = 0
        v21 = speed_right   
    # Avance PWM 
    ser.write(bytearray([145,v20,v21,v10,v11]))
    time.sleep(t)
    ser.write(bytearray([145,0,0,0,0]))# stop

# Essai declanchement action apres appui bouton
ser.write(bytearray([149,1,18]))
button = ser.read(1)

while button[0] == 0:
    ser.write(bytearray([149,1,18]))
    button = ser.read(1)
PWM_motor(20,-20,5)


PWM_motor(20,20,5)
PWM_motor(-255,-255,1)


# Essai Angle
ser.write(bytearray([149,1,20]))
res = ser.read(3)
print(res[1]-res[0])
PWM_motor(100,-100,4)
ser.write(bytearray([149,1,20]))
res = ser.read(3)
print(res[1]-res[0])



# Avance + Affichage encoders
ser.write(bytearray([145,255,240,0,15]))
# ser.write(bytearray([145,0,15,0,15]))
t1 = time.clock()
t2 = time.clock()
while t2-t1 < 5:
    t2 = time.clock()
    ser.write(bytearray([149,2,43,44]))
    res = ser.read(4)
#     time.sleep(0.005)
    print(res[0]*16**2+res[1],res[2]*16**2+res[3])
ser.write(bytearray([137,0,0,1,244]))



# Avance +stockage encoders
ser.write(bytearray([145,255,200,0,20]))
t1 = time.clock()
t2 = time.clock()
data = []
while t2-t1 < 15:
    t2 = time.clock()
    ser.write(bytearray([149,2,43,44]))
    res = ser.read(4)
    data.append([t2-t1,res])
#     time.sleep(0.001)
ser.write(bytearray([137,0,0,1,244]))

t = []
data1 = []
data2 = []
for i in range(len(data)):
    t.append(data[i][0])
    data1.append(data[i][1][0]*256 + data[i][1][1])
    data2.append(data[i][1][2]*256 + data[i][1][3])
    
    

plt.figure(1)
plt.plot(t,data1,color='r')
plt.plot(t,data2,color='b')
plt.show()



# IR 
ser.write(bytearray([149,1,17]))
res = ser.read()
print(res[0])



# PWM start
def PWM_motor_start(speed_left,speed_right):
    if speed_left < 0:
        v10 = 255
        v11 = speed_left + v10
    else:
        v10 = 0
        v11 = speed_left      
    if speed_right < 0:
        v20 = 255
        v21 = speed_right + v20
    else:
        v20 = 0
        v21 = speed_right   
    # Avance PWM 
    ser.write(bytearray([145,v20,v21,v10,v11]))

# PWM stop
def PWM_motor_stop():
    ser.write(bytearray([145,0,0,0,0]))# stop

# Test vitesse croissante
for i in range(155):
    PWM_motor_start(-i,i)
    time.sleep(0.1)
PWM_motor_stop()

# Stop
ser.write(bytearray([133]))



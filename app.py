import json
import os
import serial
import numpy as np
import time
from bitstring import Bits
from scipy.signal import savgol_filter

ser = serial.Serial()
inputs={}

from flask import Flask, render_template, request

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

def init():
    global ser
    # Initialisation de la connexion avec le Roomba
    ser.baudrate = 115200
    ser.port = "/dev/ttyUSB0"
    # ser.timeout=1
    ser
    ser.open()
    print(ser.isOpen())

    # Mode safe
    ser.write(bytearray([128,131]))
init()

def light_led(leds,clean):
    # Led Clean Rouge
    global ser
    ser.write(bytearray([139,leds[0]+2*leds[1]+4*leds[2],clean[0],clean[1]]))

def drive(speed,direction):
    global ser
    radius=20*direction-2000
    if direction==0:
        radius=32767
    elif direction>0:
        radius-=4000
    s = speed.to_bytes(2,'big',signed=True)
    r = radius.to_bytes(2,'big',signed=True)
    ser.write(bytearray([137,s[0],s[1],r[0],r[1]]))


def read_cliff():
    # Led Clean Rouge
    global ser
    ser.write(bytearray([149,4,9,10,11,12]))
    res=ser.read(4)
    return [i for i in res]

@app.route('/')
def index():
    global input, output
    gp1_sliders=[
        {'name':'clean_color','label':'Couleur (green->red)','convertpython': int(),'target': '#clean_color','convertjava':'parseInt','condition':'','hide':'','val': [i for i in range(256)],'set': [0]},
        {'name':'clean_intensity','label':'Intensité','convertpython': int(),'target': '#clean_intensity','convertjava':'parseInt','condition':'','hide':'','val': [i for i in range(256)],'set': [0]},
        {'name':'direction','label':'Direction','convertpython': int(),'target': '#direction','convertjava':'parseInt','condition':'','hide':'','val': [i for i in range(-100,101)],'set': [0]},
        {'name':'speed','label':'Vitesse','convertpython': int(),'target': '#speed','convertjava':'parseInt','condition':'','hide':'','val': [i for i in range(-500,501)],'set': [0]},
    ]
    gp2_sliders=[
        {'name':'consigne_vitesse','label':'Consigne Vitesse (mm/s)','convertpython': float(),'target': '#consigne_vitesse','convertjava':'parseFloat','hide':['pilotage','bo'],'val': [5*i for i in range(-10,11)],'set': [np.pi]},
        {'name':'consigne_position','label':'Consigne Position (mm)','convertpython': float(),'target': '#consigne_position','convertjava':'parseFloat','hide':['pilotage','bo'],'val': [5*i for i in range(-100,101)],'set': [0]},
        {'name':'tension','label':'Tension (V)','convertpython': float(),'target': '#tension','convertjava':'parseFloat','hide':['pilotage','bf'],'val': [i for i in range(0,100)],'set': [0]},
        {'name':'kp','label':'Gain Kp','convertpython': int(),'target': '#kp','convertjava':'parseInt','hide':['pilotage','bo'],'val': [i for i in range(101)],'set': [1]},
        {'name':'ki','label':'Gain Ki','convertpython': int(),'target': '#ki','convertjava':'parseInt','hide':['pilotage','bo'],'val': [i for i in range(101)],'set': [0]},
        {'name':'kd','label':'Gain Kd','convertpython': int(),'target': '#kd','convertjava':'parseInt','hide':['pilotage','bo'],'val': [i for i in range(101)],'set': [0]},
        {'name':'duree','label':'Durée (s)','convertpython': float(),'target': '#duree','convertjava':'parseFloat','hide':'','val': [i/10 for i in range(50)],'set': [2]},
    ]
    gp1_checks=[
         {'name':'dirt','label':'LED Dirt detect','convertpython': None,'hide':'','target': '#dirt','checked':True},
         {'name':'spot','label':'LED SPOT','convertpython': None,'hide':'','target': '#spot','checked':True},
         {'name':'dock','label':'LED DOCK','convertpython': None,'hide':'','target': '#dock','checked':True},
    ]
    gp1_radios=[
         {'name':'pilotage','label':'Pilotage BO/BF','convertpython': None,\
          'choices': [{'name':'bo','label':'BO','checked':True},{'name':'bf','label':'BF','checked':False}],'selected':'BO'},
    ]
    gp1_buttons=[
         {'name':'start','label':'Démarrer mesure','action':'send_exp();'},
    ]
    outputs=[[{'name':'currentg','label': 'Courant Gauche', 'color': '#bf4510','yaxe':'amp', 'borderDash':[5,5]},
              {'name':'tensiong','label': 'Tension Gauche', 'color': '#10bf4a','yaxe':'volt', 'borderDash':[5,5]},
              {'name':'encoderg','label': 'Encodeur Gauche', 'color': '#181fe6','yaxe':'nb', 'borderDash':[5,5]},
              {'name':'currentd','label': 'Courant Droit', 'color': '#bf4510','yaxe':'amp', 'borderDash':[10,0]},
              {'name':'tensiond','label': 'Tension Droit', 'color': '#10bf4a','yaxe':'volt', 'borderDash':[10,0]},
              {'name':'encoderd','label': 'Encodeur Droit', 'color': '#181fe6','yaxe':'nb', 'borderDash':[10,0]},
              {'name':'vitessed','label': 'Vitesse Droit', 'color': '#181fe6','yaxe':'mms', 'borderDash':[10,0]},
              {'name':'vitesseg','label': 'Vitesse Gauche', 'color': '#181fe6','yaxe':'mms', 'borderDash':[5,5]}
              ]
             ]
    inputs['sliders']=[gp1_sliders,gp2_sliders]
    inputs['radios']=[gp1_radios]
    inputs['checks']=[gp1_checks]
    buttons=[gp1_buttons]
    return render_template('line_chart.html', inputs=inputs, buttons=buttons, outputs=outputs)

@app.route('/process', methods=['POST', 'GET'])
def calculation():
    if request.method == "POST":
        data_input = request.get_json()
        variables={}
        for elts in inputs.values():
            for gp_elts in elts:
                for elt in gp_elts:
                    if elt['convertpython']:
                        variables[elt['name']]=elt['convertpython'](data_input[elt['name']])
                    else:
                        variables[elt['name']]=data_input[elt['name']]
        light_led([variables['dirt'],variables['spot'],variables['dock']],[variables['clean_color'],variables['clean_intensity']])
#        drive(speed,direction)
        return json.dumps('')

@app.route('/sensors', methods=['GET'])
def read_sensors():
    #result=[read_cliff()]
    result=[1,0,0,1]
    return json.dumps(result)

@app.route('/send_exp', methods=['POST', 'GET'])
def send_exp():
    global outputs
    if request.method == "POST":
        data_input = request.get_json()
        duree=float(data_input['duree'])
        depart=0.1
        if data_input['pilotage']=='bo':
            vit = int(data_input['tension']*2.55)
            v = vit.to_bytes(2,'big',signed=True)
            x_time = []
            res_list = []
            active = []
            t0 = time.time()
            t = time.time()
            while (t - t0) <= duree:
                t = time.time()
                active.append(0)
                x_time.append(t-t0)
                if (t - t0) > depart:
                    ser.write(bytearray([146,v[0],v[1],v[0],v[1]]))
                    active[-1]=1
                if (t - t0) > duree:
                    x_time.pop()
                    active.pop()
                    break
                ser.write(bytearray([149,5,43,44,54,55,22]))#Encoder+Current
                res_list.append(ser.read(10))
        else:
            posc = int(data_input['consigne_position']/((1/508.8)*2*np.pi*32.5))
            kp = int(data_input['kp'])
            ki = int(data_input['ki'])
            kd = int(data_input['kd'])
            x_time = []
            res_list = []
            active = []
            t0 = time.time()
            t = time.time()
            while (t - t0) <= duree:
                t = time.time()
                active.append(0)
                x_time.append(t-t0)
                ser.write(bytearray([149,5,43,44,54,55,22]))#Encoder+Current
                data=ser.read(10)
                res_list.append(data)
                posdr=Bits(data[0:2]).int
                posgr=Bits(data[2:4]).int

                if (t - t0) > depart:
                    sat=255
                    erreur=[int((posc-posdr)),int((posc-posgr))]
                    erreur=[int(kp*i) for i in erreur]
                    print(erreur,posc)
                    for i in range(2):
                        if erreur[i]>sat:
                            erreur[i]=sat
                        elif erreur[i]<-sat:
                            erreur[i]=-sat
                    print(erreur,posc)
                    vg = erreur[0].to_bytes(2,'big',signed=True)
                    vd = erreur[1].to_bytes(2,'big',signed=True)
                    print(erreur,posc,vd,vg)
                    ser.write(bytearray([146,vd[0],vd[1],vg[0],vg[1]]))
                    active[-1]=1
                if (t - t0) > duree:

                    break

        ser.write(bytearray([137,0,0,1,244]))# stop
        encoderd = []
        encoderg = []
        currentg = []
        currentd = []
        tensiond = []
        tensiong = []

        for res_i in res_list:
            encoderd.append(Bits(res_i[0:2]).int*(1/508.8)*2*np.pi*32.5)
            encoderg.append(Bits(res_i[2:4]).int*(1/508.8)*2*np.pi*32.5)
            currentg.append(Bits(res_i[4:6]).int*10**(-3))
            currentd.append(Bits(res_i[6:8]).int*10**(-3))
            tensiond.append(Bits(res_i[8:10]).int*10**(-3)*int(data_input['tension'])/100)
            tensiong.append(Bits(res_i[8:10]).int*10**(-3)*int(data_input['tension'])/100)
        active=np.array(active)
        tensiond=tensiond*active
        tensiong=tensiong*active
        vitesseg=[0]+[encoderg[i+1]-encoderg[i] for i in range(len(encoderg)-1)]
        vitesseg = savgol_filter(vitesseg, 15, 3)
        delta_t=[1]+[x_time[i+1]-x_time[i] for i in range(len(x_time)-1)]
        vitesseg=(vitesseg/delta_t)*(1/508.8)*2*np.pi*32.5
        vitessed=[0]+[encoderd[i+1]-encoderd[i] for i in range(len(encoderd)-1)]
        vitessed = savgol_filter(vitessed, 15, 3)
        vitessed=(vitessed/delta_t)*(1/508.8)*2*np.pi*32.5
        keys_list=['x_time','encoderd','encoderg','currentg','currentd','tensiond','tensiong','vitessed','vitesseg']
        result=[dict(zip(keys_list, [x_time[i],encoderd[i],encoderg[i],currentg[i],currentd[i],tensiond[i],tensiong[i],vitessed[i],vitesseg[i]])) for i in range(len(x_time)-1)]
        return json.dumps(result)

if __name__ == "__main__":
    app.run(debug=True)

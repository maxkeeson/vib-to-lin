#!/usr/bin/env python

import numpy as np
import json
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema

input_json_file = 'vib.json'
output_json_file = 'lin.json'

def open_fs(filename):
    t = []
    y = []
    with open(filename) as file:
        data = json.load(file)
        for dic in data['actions']:
            t.append(dic['at'])
            y.append(dic['pos'])

    t, y = np.array(t), np.array(y)
    return t, y

def interpolation(t,y, step = 5):
    ti = np.arange(t[0], t[-1], step, t[-1] + step)
    yi = np.interp(ti, t, y)
    return ti, yi
def pre_processing(t, y):
    '''
    The problem with some scripts is that the baseline is at 10%, this produces
    wayy too slow movement for the handy, its very jittery then. so maybe the 
    mapping should not be linear? i.e. baseline of 10% should be the minimum non jittery
    speed of
    '''

def to_sin(t, y, min_freq = 0, max_freq = 100):
    length = 11 #cm
    max = 40 #cm/s real max should be ~600 mm/s according to 99DM
    fmax = max/(11/2)/(2*np.pi)/1000 # in khz
    fmin = 0 
    dt = t[1] - t[0]
    
    f = fmax*y/100 #since time is in ms, this is in KHz
    ft_int = np.cumsum(f)*dt
    
    sin = 50 * np.sin(2*np.pi*ft_int) + 50
    #plt.plot(t/1E3, y, 'o-', markersize = 1.2, linewidth = 0.5)
    #plt.plot(t/1E3, sin-100, 'o-', markersize = 1.2, linewidth = 0.5)
    #plt.ylim(-100, 100)
    #plt.show()
    return t, sin

def reduce_points(ti, yconv, t_org ,y_org,mode = 'multiple'):

    if mode == 'minmax':
        minima = argrelextrema(yconv, np.less)
        maxima = argrelextrema(yconv, np.greater)
        trunc_t = np.concatenate([ti[minima], ti[maxima]])
        trunc_y = np.concatenate([yconv[minima], yconv[maxima]])
    
    #trunc_t = sorted(trunc_t)a
        trunc_y = trunc_y[trunc_t.argsort()]
        trunc_t = trunc_t[trunc_t.argsort()]

        return trunc_t, trunc_y
    elif mode == 'multiple':
        trunc_t, trunc_y = [], []
        "First i have to add the zero points at the start of the scirpt"
        for i, (t, y) in enumerate(zip(t_org, y_org)):
            if y > 5:
                print(i)
                print(y)
                start = t_org[i-1]
                break

        d = int(start / 10000)
        for i in np.linspace(0, start, d, endpoint = True):
            i = int(i)
            i = float(i)
            trunc_t.append(i)
            trunc_y.append(0.)


        points_at = [0, 10, 50, 90, 100]
        
        for p in points_at:
            func = np.abs(yconv - p)
            minima = argrelextrema(func, np.less)[0] # the abs diff is minimize i.e. crossing
            for i in minima:

                trunc_t.append(ti[i])
                trunc_y.append(p) #<- here maybe change to p
     
        trunc_t = np.array(trunc_t)
        trunc_y = np.array(trunc_y)

        trunc_y = trunc_y[trunc_t.argsort()]
        trunc_t = trunc_t[trunc_t.argsort()]
     
        return trunc_t, trunc_y


def write_json_output(trunc_t, trunc_y, output):
    'make dict of dicts'
    list_of_dic = []
    for t, y in zip(trunc_t, trunc_y):
        list_of_dic.append({"at": t, "pos": y})
    dic = {"actions": list_of_dic}
    print(dic)
    with open(output, 'w') as file:
        json.dump(dic, file)

t, y = open_fs(input_json_file)
ti, yi = interpolation(t, y)
ti, yconv = to_sin(ti, yi)
trunc_t, trunc_y = reduce_points(ti, yconv, t, y,'multiple')
write_json_output(trunc_t, trunc_y, output_json_file)


'''
fig, ax = plt.subplots(2,1, sharex='all', figsize = (6,4), dpi = 150)
ax[1].set_xlabel('Time (s)')
ax[0].set_ylabel('Pos %')
ax[1].set_ylabel('Pos %')
ax[0].plot(t/1E3, y, '-o', markersize=1.0, linewidth = 1.0)
#plt.plot(trunc_t, trunc_y, alpha = 0.4)
ax[1].plot(trunc_t/1E3, trunc_y, '-o', markersize=1.0, linewidth = 1.0)
ax[0].grid()
ax[1].grid()
#ax[0].set_xlim(1310, 1350)
plt.tight_layout()
plt.savefig('asd3.png', dpi = 500)
plt.show()
'''





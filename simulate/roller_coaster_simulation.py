"""
This code, created by Stijn Carelsbergh is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.

You are free to:
- Share: copy and redistribute the material in any medium or format
- Adapt: remix, transform, and build upon the material

Under the following terms:
- Attribution: You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
- NonCommercial: You may not use the material for commercial purposes.
- ShareAlike: If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.

For more details, see the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License:
https://creativecommons.org/licenses/by-nc-sa/4.0/
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import csv
import os

# step size and number of steps
dt = 0.005
t_tot = 24
steps = int(t_tot/dt)

# vector drawing
vectorspacing = int(steps/20)
vectorscale = 0.2

# physical properties
m = 6000
g = np.array([0, 0, -9.81])
rho = 1.3
Cd = 0.6
A = 4
mu = 0.02

# time since beginning
t = [dt * i for i in range(1, steps)]

# open discrete track
ps = np.loadtxt('trackpoints.txt', delimiter=',', encoding='utf-8-sig')/1000

# next trackpoint
p = 1

# upside down intervals
start1 = np.where(np.all(np.abs(ps - np.array([-55.107, 63.931, 17.965])) < 0.2, axis=1))[0][0]
stop1 = np.where(np.all(np.abs(ps - np.array([-34.879, 62.083, 18.183])) < 0.2, axis=1))[0][0]
start2 = np.where(np.all(np.abs(ps - np.array([-80.108, 54.990, 10.078])) < 0.2, axis=1))[0][0]
stop2 = np.where(np.all(np.abs(ps - np.array([-99.660, 67.021, 10.246])) < 0.2, axis=1))[0][0]
UD = np.array([[start1, stop1], [start2, stop2]])

# motion property lists
tussen = np.zeros(steps)
dp = np.zeros((steps, 3))
e_dp = np.zeros((steps, 3))
theta = np.zeros(steps)
phi = np.zeros(steps)
r = np.zeros(steps)
g_a = np.zeros((steps, 3))
g_N = np.zeros((steps, 3))
a_f = np.zeros((steps, 3))
a_d = np.zeros((steps, 3))
a = np.zeros(steps)
v = np.zeros(steps)
ds = np.zeros((steps, 3))
s = np.zeros((steps, 3))
R = np.zeros((steps, 3))
M = np.zeros((steps, 3))
a_eq = np.zeros((steps, 3))
G = np.zeros((steps, 3))
G_N = np.zeros((steps, 3))

# initial values
tussen[0] = 1
dp[0] = np.array([0, 0, 0])
e_dp[0] = np.array([-1, 0, 0])
theta[0] = np.pi/2
phi[0] = 0
r[0] = 0
g_a[0] = np.array([0, 0, 0])
g_N[0] = np.linalg.norm(g)
a_f[0] = np.array([0, 0, 0])
a_d[0] = np.array([0, 0, 0])
a[0] = 0
v[0] = 2
ds[0] = np.array([0, 0, 0])
s[0] = ps[0]
R[0] = np.array([np.inf, np.inf, np.inf])
M[0] = np.array([np.inf, np.inf, np.inf])
a_eq[0] = np.array([0, 0, 0])
G[0] = g
G_N[0] = g

for i in range(1, steps):
    # find next closest point
    min_distance = np.inf
    for j in range(p, p+5):
        distance = np.linalg.norm(s[i-1]-ps[j]) + np.linalg.norm(s[i-1]-ps[j-1])
        if distance < min_distance:
            min_distance = distance
            p = j

    tussen[i] = p

    # coordinates ISO 80000-2
    dp[i] = ps[p] - s[i-1]
    e_dp[i] = dp[i] / np.linalg.norm(dp[i])
    r[i] = np.linalg.norm(dp[i])
    theta[i] = np.arccos(dp[i][2] / r[i])
    phi[i] = np.arctan2(dp[i][1], dp[i][0])

    # gravity
    g_a[i] = np.dot(g, e_dp[i]) * e_dp[i]
    g_N[i] = g - g_a[i]

    # acceleration, velocity and position
    a_f[i] = np.linalg.norm(G_N[i-1])*mu * -1*e_dp[i]
    a_d[i] = 0.5*rho*v[i-1]**2*Cd*A/m * -1*e_dp[i]
    a[i] = np.sign(-1*np.cos(theta[i]))*np.linalg.norm(g_a[i]) - np.linalg.norm(a_f[i]) - np.linalg.norm(a_d[i])
    v[i] = v[i-1] + a[i]*dt
    ds[i] = v[i]*dt*e_dp[i] + 0.5*a[i]*dt**2*e_dp[i]
    s[i] = s[i-1] + ds[i]

    # https://itecnote.com/tecnote/python-find-arc-circle-equation-given-three-points-in-space-3d/

    # 3 points
    p1 = ps[p-1]
    p2 = ps[p]
    p3 = ps[p+1]

    # sides of triagle
    s1 = np.linalg.norm(p3 - p2)
    s2 = np.linalg.norm(p3 - p1)
    s3 = np.linalg.norm(p2 - p1)

    # collinearity check
    if (abs(s1 + s2 - s3) < 1e-15 or abs(s1 + s3 - s2) < 1e-15 or abs(s2 + s3 - s1) < 1e-15):
        M[i] = np.array([np.inf, np.inf, np.inf])
        R[i] = np.array([np.inf, np.inf, np.inf])
        a_eq[i] = np.array([0, 0, 0])
        G[i] = g
        G_N[i] = g_N[i]

    # find midpoint and radius and calculate G-force
    else:
        b1 = s1**2 * (s2**2 + s3**2 - s1**2)
        b2 = s2**2 * (s3**2 + s1**2 - s2**2)
        b3 = s3**2 * (s1**2 + s2**2 - s3**2)
        
        M[i] = np.dot(np.array([p1, p2, p3]).T, np.array([b1, b2, b3])) / (b1 + b2 + b3)
        R[i] = s[i] - M[i]
        e_R = R[i] / np.linalg.norm(R[i])
        a_eq[i] = v[i]**2/np.linalg.norm(R[i]) * e_R
        G[i] = g + a_f[i] + a_d[i] + a_eq[i]
        G_N[i] = g_N[i] + a_eq[i]

# matplotlib
fig = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.scatter(s[:,0], s[:,1], s[:,2], s=2, c="b")
ax.plot(ps[:,0], ps[:,1], ps[:,2], c="r")
ax.quiver(s[::vectorspacing, 0], s[::vectorspacing, 1], s[::vectorspacing, 2], v[::vectorspacing]*e_dp[::vectorspacing, 0], v[::vectorspacing]*e_dp[::vectorspacing, 1], v[::vectorspacing]*e_dp[::vectorspacing, 2], color='green', arrow_length_ratio=vectorscale)
ax.quiver(s[::vectorspacing, 0], s[::vectorspacing, 1], s[::vectorspacing, 2], a_eq[::vectorspacing, 0], a_eq[::vectorspacing, 1], a_eq[::vectorspacing, 2], color='red', arrow_length_ratio=vectorscale)
ax.quiver(s[::vectorspacing, 0], s[::vectorspacing, 1], s[::vectorspacing, 2], G[::vectorspacing, 0], G[::vectorspacing, 1], G[::vectorspacing, 2], color='yellow', arrow_length_ratio=vectorscale)
ax.quiver(s[::vectorspacing, 0], s[::vectorspacing, 1], s[::vectorspacing, 2], g_a[::vectorspacing, 0], g_a[::vectorspacing, 1], g_a[::vectorspacing, 2], color='black', arrow_length_ratio=vectorscale)
ax.quiver(s[::vectorspacing, 0], s[::vectorspacing, 1], s[::vectorspacing, 2], g_N[::vectorspacing, 0], g_N[::vectorspacing, 1], g_N[::vectorspacing, 2], color='orange', arrow_length_ratio=vectorscale)
ax.quiver(s[::vectorspacing, 0], s[::vectorspacing, 1], s[::vectorspacing, 2], g[0], g[1], g[2], color='grey', arrow_length_ratio=vectorscale)
ax.set_aspect('equal')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.show()

# make CSV
csv_GN = np.zeros(steps)

for i in range(steps):
    if not np.any((tussen[i] >= UD[:, 0]) & (tussen[i] <= UD[:, 1])) and G_N[i][2] > 0:
        csv_GN[i] = -1 * np.linalg.norm(G_N[i])/np.linalg.norm(g)
    else:
        csv_GN[i] = np.linalg.norm(G_N[i])/np.linalg.norm(g)
    
with open(os.path.splitext(__file__)[0] + ".csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile, delimiter=",")
    writer.writerow(["Time", "Tussen", "x", "y", "z", "v", "a", "g_N", "g_a", "R", "a_eq", "G_N"])
    for row in range(0, steps):
        writer.writerow([
                            row*dt,
                            str(int(tussen[row])-1) + " - " + str(int(tussen[row])),
                            s[row][0], s[row][1], s[row][2],
                            v[row],
                            a[row],
                            np.linalg.norm(g_N[i-1] + a_eq[i-1]),
                            g_a[row],
                            np.linalg.norm(R[row]),
                            np.linalg.norm(a_eq[row]),
                            csv_GN[row]
                        ])

# make XLSX
read_file = pd.read_csv(os.path.splitext(__file__)[0] + ".csv")
read_file.to_excel(os.path.splitext(__file__)[0] + ".xlsx", index = None, header=True)

# 2D plot
df = pd.read_csv(os.path.splitext(__file__)[0] + ".csv")
df.set_index('Time', inplace=True)
df['G_N'] = df['G_N'].astype(float)
df['v'] = df['v'].astype(float)
df['a'] = df['a'].astype(float)
df['z'] = df['z'].astype(float)

fig, ax = plt.subplots()
fig.subplots_adjust(right=0.75)

twin1 = ax.twinx()
twin2 = ax.twinx()
twin3 = ax.twinx()

twin2.spines.right.set_position(("axes", 1.1))
twin3.spines.right.set_position(("axes", 1.2))

p0, = ax.plot(df.index, df['G_N'], "k-", label="Normale G-kracht")
p1, = twin1.plot(df.index, df['v'], "r-", label="Snelheid")
p2, = twin2.plot(df.index, df['a'], "b-", label="Versnelling")
p3, = twin3.plot(df.index, df['z'], "g-", label="Hoogte")

ax.set_xlim(df.index.min(), df.index.max())
ax.set_ylim(df['G_N'].min() - 2, df['G_N'].max() + 2)
twin1.set_ylim(df['v'].min() - 3, df['v'].max() + 3)
twin2.set_ylim(df['a'].min() - 3, df['a'].max() + 3)
twin3.set_ylim(df['z'].min() - 3, df['z'].max() + 3)

ax.set_xlabel("t [s]")
ax.set_ylabel("G_N [x 9.81 m/s^2]")
twin1.set_ylabel("v [m/s]")
twin2.set_ylabel("a [m/s^2]")
twin3.set_ylabel("h [m]")

ax.yaxis.label.set_color(p0.get_color())
twin1.yaxis.label.set_color(p1.get_color())
twin2.yaxis.label.set_color(p2.get_color())
twin3.yaxis.label.set_color(p3.get_color())

tkw = dict(size=4, width=1.5)
ax.tick_params(axis='y', colors=p0.get_color(), **tkw)
twin1.tick_params(axis='y', colors=p1.get_color(), **tkw)
twin2.tick_params(axis='y', colors=p2.get_color(), **tkw)
twin3.tick_params(axis='y', colors=p3.get_color(), **tkw)
ax.tick_params(axis='x', **tkw)

handles = [p0, p1, p2, p3]
ax.legend(handles=handles)

plt.show()
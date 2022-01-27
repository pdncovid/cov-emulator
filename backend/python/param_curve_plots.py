import matplotlib.pyplot as plt
import numpy as np


def gaussian(x, mu, sig):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

plt.figure()
plt.hist(np.random.lognormal(1, 0.5, 100000), bins=1000, cumulative=True, density=True, histtype='step')
plt.xlabel("Contact duration (minutes)")
plt.ylabel("Transmission probability")
plt.tight_layout()
plt.savefig("images/transmission_contact_dur.png")

x = np.arange(0, 10, 0.1)
y = [np.exp(-d / 5) for d in x]
plt.figure()
plt.plot(x, y)
plt.xlabel("Distance (meters)")
plt.ylabel("Transmission probability")
plt.tight_layout()
plt.savefig("images/transmission_dist.png")

x = np.arange(0,30, 1)
y = np.array([gaussian(dt, 15, 10) for dt in x])
plt.figure()
plt.plot(x, y)
plt.xlabel("Infected duration (days)")
plt.ylabel("Transmission probability")
plt.tight_layout()
plt.savefig("images/transmission_infected_dur.png")

x = np.arange(0,30, 1)
y = np.array([gaussian(dt, 20, 5) for dt in x])
plt.figure()
plt.plot(x, y)
plt.xlabel("Infected duration (days)")
plt.ylabel("Recovery probability")
plt.tight_layout()
plt.savefig("images/recovery_infected_dur.png")

x = np.arange(0, 12, 0.1)
y = [(min(5,c) + (1 - (min(5,c)/20+0.5)) ** 2)/5 for c in x]
plt.figure()
plt.plot(x, y)
plt.xlabel("Contacts")
plt.ylabel("Transmission probability")
plt.tight_layout()
plt.savefig("images/transmission_contacts.png")


x = np.arange(0, 100, 1)
y = [(np.tanh((d-60)/20)+2)/3 for d in x]
plt.figure()
plt.plot(x, y)
plt.ylim([0,1])
plt.xlabel("Age")
plt.ylabel("Transmission probability")
plt.tight_layout()
plt.savefig("images/transmission_age.png")

x = np.arange(0, 100, 1)
y = [(np.tanh((d-60)/20)+1)/2 for d in x]
plt.figure()
plt.plot(x, y)
plt.ylim([0,1])
plt.xlabel("Age")
plt.ylabel("Disease worsen probability")
plt.tight_layout()
plt.savefig("images/disease_worsen_age.png")

import pandas as pd
V = pd.read_csv('data/p_go_4_LocPersonTime.csv')
V = V.loc[V['person']=='Student']
plt.figure(figsize=(12, 8))
plt.imshow(V.values[:,:1440].astype(float), interpolation='none', aspect='auto')
plt.yticks([i for i in range(len(V['location']))],V['location'].values)
plt.xlabel("Time (minutes)")
plt.colorbar()
plt.savefig("images/locationvisitprob_student.png")

V = pd.read_csv('data/p_dtLocPersonTime.csv')
V = V.loc[V['person']=='Student']
plt.figure(figsize=(12, 8))
plt.imshow(V.values[:,:1440].astype(float), interpolation='none', aspect='auto')
plt.yticks([i for i in range(len(V['location']))],V['location'].values)
plt.xlabel("Time (minutes)")
plt.colorbar()
plt.tight_layout()
plt.savefig("images/locationoccupancyprob_student.png")


plt.show()

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from scipy.stats import lognorm

def gaussian(x, mu, sig):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))


# ========================================================================================== transmission_contact_dur
plt.figure(figsize=(5, 3))
lg = lognorm([0.5], loc=1)
x = np.arange(0, 25, 0.1)
y = [lg.cdf(d) for d in x]
plt.plot(x, y)
plt.xlabel("Contact duration (minutes)")
plt.ylabel("Transmission probability")
plt.tight_layout()
plt.savefig("images/transmission_contact_dur.png")

# ========================================================================================== transmission_distance
x = np.arange(0, 10, 0.1)
y = [np.exp(-d / 5) for d in x]
plt.figure(figsize=(5, 3))
plt.plot(x, y)
plt.xlabel("Distance (meters)")
plt.ylabel("Transmission probability")
plt.tight_layout()
plt.savefig("images/transmission_dist.png")

# ========================================================================================== transmission_infected_dur
x = np.arange(0, 30, 1)
y = np.array([gaussian(dt, 0, 10) for dt in x])
plt.figure(figsize=(5, 3))
plt.plot(x, y)
plt.xlabel("Infected duration (days)")
plt.ylabel("Transmission probability")
plt.tight_layout()
plt.savefig("images/transmission_infected_dur.png")

# ========================================================================================== recovery_infected_dur
x = np.arange(0, 30, 1)
y = np.array([gaussian(dt, 20, 5) for dt in x])
plt.figure(figsize=(5, 3))
plt.plot(x, y)
plt.xlabel("Infected duration (days)")
plt.ylabel("Recovery probability")
plt.tight_layout()
plt.savefig("images/recovery_infected_dur.png")

# ========================================================================================== transmission_contacts
x = np.arange(0, 12, 0.1)
y = [(min(5, c) + (1 - (min(5, c) / 20 + 0.5)) ** 2) / 5 for c in x]
plt.figure(figsize=(5, 3))
plt.plot(x, y)
plt.xlabel("Contacts")
plt.ylabel("Transmission probability")
plt.tight_layout()
plt.savefig("images/transmission_contacts.png")

# ========================================================================================== transmission_age
x = np.arange(0, 100, 1)
y = [(np.tanh((d - 60) / 20) + 2) / 3 for d in x]
plt.figure(figsize=(5, 3))
plt.plot(x, y)
plt.ylim([0, 1])
plt.xlabel("Age")
plt.ylabel("Transmission probability")
plt.tight_layout()
plt.savefig("images/transmission_age.png")

# ========================================================================================== disease_worsen_age
x = np.arange(0, 100, 1)
y = [(np.tanh((d - 60) / 20) + 1) / 2 for d in x]
plt.figure(figsize=(5, 3))
plt.plot(x, y)
plt.ylim([0, 1])
plt.xlabel("Age")
plt.ylabel("Disease worsen probability")
plt.tight_layout()
plt.savefig("images/disease_worsen_age.png")

# ========================================================================================== locationvisitprob_student
import pandas as pd

V = pd.read_csv('data/p_go_4_LocPersonTime.csv')
V = V.loc[V['person'] == 'Student']
plt.figure(figsize=(12, 8))
plt.imshow(V.values[:, :1440].astype(float), interpolation='none', aspect='auto')
plt.yticks([i for i in range(len(V['location']))], V['location'].values)
plt.xlabel("Time (minutes)")
plt.colorbar()
plt.savefig("images/locationvisitprob_student.png")

# ======================================================================================= locationoccupancyprob_student
V = pd.read_csv('data/p_dtLocPersonTime.csv')
V = V.loc[V['person'] == 'Student']
plt.figure(figsize=(12, 8))
plt.imshow(V.values[:, :1440].astype(float), interpolation='none', aspect='auto')
plt.yticks([i for i in range(len(V['location']))], V['location'].values)
plt.xlabel("Time (minutes)")
plt.colorbar()
plt.tight_layout()
plt.savefig("images/locationoccupancyprob_student.png")

# ========================================================================================== severity change time
plt.figure()
from scipy.stats import lognorm

x = np.linspace(0, 20, 500)
dists = []
dists.append((lognorm([1.5], loc=4.5), "exposed -> infectious"))
dists.append((lognorm([0.9], loc=1.1), "infectious -> symptomatic (mild)"))
dists.append((lognorm([4.9], loc=6.6), "mild -> severe"))
dists.append((lognorm([2.0], loc=1.5), "severe-> critical"))
dists.append((lognorm([4.8], loc=10.7), "critical->death"))

for dist in dists:
    plt.plot(x, dist[0].pdf(x), label=dist[1])
plt.legend()
plt.show()

# ========================================================================================= kandy curve
plt.figure()
df = pd.read_csv('data/SL_covid.csv').drop(['District'], axis=1).set_index('Code')
# plt.plot(df.transpose()['KAN'])
kan = df.transpose()['KAN'].iloc[0:61]
# plt.plot(kan.index[1:], (kan.values[1:] - kan.values[:-1]))
sns.lineplot(x=kan.index, y=kan.values/kan.max(), label="Real data")
ax = plt.gca()
ax.xaxis.set_major_locator(plt.MaxNLocator(4))
plt.xlabel('Date')
plt.ylabel("Normalized total infected cases")

df_sim = pd.read_csv('../../app/src/data/timeline.csv')
df_sim = df_sim.loc[df_sim['Parameter'] == 'TOTAL INFECTED CASES']
df_sim["Value"] = df_sim["Value"].astype(int)
df_sim["Value"] /= df_sim["Value"].max()
df_sim["Value"] /= 1
df_sim["Value"] += 0.05
df_sim["Time"] = df_sim["Time"].astype(int)
tot = df_sim['Value'].astype(int)
print(len(kan.index), len(tot), df_sim)
sns.lineplot(data=df_sim, x="Time", y="Value", label="Simulation")
# sns.lineplot(x=kan.index,y=tot.values), label="Simulation")

plt.legend()

plt.savefig("images/kandy_sim_compare.svg")
plt.show()

# ========================================================================================= king county curve
plt.figure()
df = pd.read_csv('data/King_covid.csv').set_index('Collection_Date')
plt.plot(df.index, (df.values))
ax = plt.gca()
ax.xaxis.set_major_locator(plt.MaxNLocator(4))
plt.xlabel('Date')
plt.ylabel("New cases in King county")
plt.savefig("images/newcases_king.png")
plt.show()

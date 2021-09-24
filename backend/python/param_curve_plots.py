import matplotlib.pyplot as plt
import numpy as np

from backend.python.Time import Time

plt.figure()
plt.hist(np.random.lognormal(1, 0.5, 100000), bins=100, cumulative=True, density=True)
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

x = np.arange(0, 1000, 0.1)
y = [
    ((np.tanh((dt - (24 * 5)*60) / (24 * 5)*60) + 0.2) * (np.tanh((-dt + (24 * 8)*60) / (24 * 8)*60) + 0.5) + 1.19987) / 2.6683940 for dt in x]
plt.figure()
plt.plot(x, y)
plt.xlabel("Infected duration (hours)")
plt.ylabel("Transmission probability")
plt.tight_layout()
plt.savefig("images/transmission_infected_dur.png")


x = np.arange(0, 12, 0.1)
y = [min(10,c) + (1 - (min(10,c)/20+0.5)) ** 2 for c in x]
plt.figure()
plt.plot(x, y)
plt.xlabel("Contacts")
plt.ylabel("Transmission probability")
plt.tight_layout()
plt.savefig("images/transmission_contacts.png")

plt.show()

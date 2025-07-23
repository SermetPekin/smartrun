
#!/usr/bin/env python3
"""Plot a sine curve and save to file."""
import numpy as np
import matplotlib.pyplot as plt
x = np.linspace(0, 2 * np.pi, 500)
y = np.sin(x)
plt.plot(x, y)
plt.title("Sine wave")
plt.xlabel("x")
plt.ylabel("sin(x)")
plt.tight_layout()
plt.savefig("sine.png")
print("Saved plot to sine.png")

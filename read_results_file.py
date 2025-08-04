import pickle
from classPosTest import posTest  # Ensure this file is in the same directory
import matplotlib.pyplot as plt
import os
import numpy as np

# Path to the pickle file

POSID = 25 # CHANGE POSITIONER HERE!
TEMP = -20 # CHANGE TEMPERATURE HERE!

def path_to_results_dir(posID: int = None, temp: float = None):

    script_dir = os.path.dirname(__file__)
    # results_dir_path = os.path.join(script_dir, 'Results_examples/')
    results_dir_path = os.path.join(script_dir, 'Results/')

    # Creates a subfolder corresponding to the project name in Results/
    if posID is not None: 
        results_dir_path = os.path.join(results_dir_path, f'Positioner {posID}' + '/')

    if temp is not None:
        results_dir_path = os.path.join(results_dir_path, f'{temp} degrees' + '/')
    
    return results_dir_path

base_directory = path_to_results_dir(POSID, TEMP)

filepath = None
filename = None
for filename in os.listdir(base_directory):
    print(os.listdir(base_directory))
    if filename.endswith(f'pos{POSID}'):
        filepath = os.path.join(base_directory, filename)
        break

# Load the object
# with open(filepath, "rb") as f:
print(f"Reading file {filename}...")
data = posTest.loadFromFile(filepath)
x,y,r = data.getCircle()
xa,ya,ra = data.getAlphaArm()
print(x,y,r)
print(xa,ya,ra)
# Print basic metadata
print(f"ID: {data.id}")
print(f"Filename: {data.filename}")
print(f"Temperature: {data.temperature}")

# Optional: display the size of each list-type attribute
attributes = [
    "alphaPos", "betaPos",
    "circleAlphaXs", "circleAlphaYs",
    "circleBetaXs", "circleBetaYs",
    "datumAlphaXs", "datumAlphaYs",
    "datumBetaXs", "datumBetaYs",
    "betaHighXs", "betaHighYs",
    "betaLowXs", "betaLowYs",
    "alphaHighXs", "alphaHighYs",
    "alphaLowXs", "alphaLowYs",
    "betaNLXs", "betaNLYs",
    "alphaNLXs", "alphaNLYs"
]

for attr in attributes:
    val = getattr(data, attr)
    print(f"{attr}: {len(val)} entries")

# Plot circleAlphaXs/Ys
plt.figure(figsize=(8, 6))
for i, (xs, ys) in enumerate(zip(data.circleAlphaXs, data.circleAlphaYs)):
    plt.scatter(xs, ys, marker='o', label=f'circleAlpha {i}')
plt.title(f'circleAlphaXs / Ys - pos {data.id}')
plt.xlabel("X")
plt.ylabel("Y")
plt.axis("equal")
plt.grid(True)
plt.legend()
plt.tight_layout()

# Plot circleBetaXs/Ys
plt.figure(figsize=(8, 6))
for i, (xs, ys) in enumerate(zip(data.circleBetaXs, data.circleBetaYs)):
    plt.scatter(xs, ys, marker='o', label=f'circleBeta {i}')
plt.title(f'circleBetaXs / Ys - pos {data.id}')
plt.xlabel("X")
plt.ylabel("Y")
plt.axis("equal")
plt.grid(True)
plt.legend()
plt.tight_layout()

# Plot alphaNL path
plt.figure(figsize=(6, 6))
plt.plot(data.alphaNLXs, data.alphaNLYs, marker='o', color='blue')
plt.title(f'Alpha Non-Linearity Path - pos {data.id}')
plt.xlabel("X")
plt.ylabel("Y")
plt.axis("equal")
plt.grid(True)
plt.tight_layout()

# Plot betaNL path
plt.figure(figsize=(6, 6))
plt.plot(data.betaNLXs, data.betaNLYs, marker='o', color='green')
plt.title(f'Beta Non-Linearity Path - pos {data.id}')
plt.xlabel("X")
plt.ylabel("Y")
plt.axis("equal")
plt.grid(True)
plt.tight_layout()


# Plot Alpha Highs and Lows
plt.figure(figsize=(6, 6))
plt.plot(data.alphaHighXs, data.alphaHighYs, 'o-', label="Alpha Highs", color="red")
plt.plot(data.alphaLowXs, data.alphaLowYs, 'o-', label="Alpha Lows", color="blue")
plt.title(f'Alpha High vs Low Trajectories - pos {data.id}')
plt.xlabel("X")
plt.ylabel("Y")
plt.axis("equal")
plt.grid(True)
plt.legend()
plt.tight_layout()

# Plot Beta Highs and Lows
plt.figure(figsize=(6, 6))
plt.plot(data.betaHighXs, data.betaHighYs, 'o-', label="Beta Highs", color="green")
plt.plot(data.betaLowXs, data.betaLowYs, 'o-', label="Beta Lows", color="purple")
plt.title(f'Beta High vs Low Trajectories - pos {data.id}')
plt.xlabel("X")
plt.ylabel("Y")
plt.axis("equal")
plt.grid(True)
plt.legend()
plt.tight_layout()

# --- 1. Compute center of alpha circle ---
# Flatten all alpha X/Y coordinates
alphaXs_all = np.concatenate(data.circleAlphaXs)
alphaYs_all = np.concatenate(data.circleAlphaYs)
centerX, centerY, _ = fit_circle(alphaXs_all, alphaYs_all)

# Helper function to center and plot data
def plot_centered(x_list, y_list, title, labels, colors):
    plt.figure(figsize=(6, 6))
    for xs, ys, label, color in zip(x_list, y_list, labels, colors):
        xs = np.array(xs) - centerX
        ys = np.array(ys) - centerY
        plt.plot(xs, ys, 'o-', label=label, color=color)
    plt.title(title)
    plt.xlabel("X (centered)")
    plt.ylabel("Y (centered)")
    plt.axis("equal")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

# --- 2. Plot centered circleAlpha and circleBeta ---
plot_centered(
    x_list=data.circleAlphaXs + data.circleBetaXs,
    y_list=data.circleAlphaYs + data.circleBetaYs,
    title=f"Centered Circle Alpha & Beta - pos {data.id}",
    labels=[f"circleAlpha {i}" for i in range(len(data.circleAlphaXs))] +
           [f"circleBeta {i}" for i in range(len(data.circleBetaXs))],
    colors=['blue']*len(data.circleAlphaXs) + ['green']*len(data.circleBetaXs)
)

# --- 3. Plot centered AlphaNL and BetaNL ---
plot_centered(
    x_list=[data.alphaNLXs, data.betaNLXs],
    y_list=[data.alphaNLYs, data.betaNLYs],
    title=f"Centered Non-Linearity Paths - pos {data.id}",
    labels=["Alpha NL", "Beta NL"],
    colors=["blue", "green"]
)

# --- 4. Plot centered Alpha Highs/Lows ---
plot_centered(
    x_list=[data.alphaHighXs, data.alphaLowXs],
    y_list=[data.alphaHighYs, data.alphaLowYs],
    title=f"Centered Alpha High/Low Paths - pos {data.id}",
    labels=["Alpha High", "Alpha Low"],
    colors=["red", "blue"]
)

# --- 5. Plot centered Beta Highs/Lows ---
plot_centered(
    x_list=[data.betaHighXs, data.betaLowXs],
    y_list=[data.betaHighYs, data.betaLowYs],
    title=f"Centered Beta High/Low Paths - pos {data.id}",
    labels=["Beta High", "Beta Low"],
    colors=["green", "purple"]
)
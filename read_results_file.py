#%%
import pickle
from classPosTest import posTest  # Ensure this file is in the same directory
import matplotlib.pyplot as plt
import os
import numpy as np
from miscmath import fit_circle
import pandas as pd

# Path to the pickle file

POSID = 26 # CHANGE POSITIONER HERE!
TEMP = 30 # CHANGE TEMPERATURE HERE!
SAVE_FIGURES = False  # Set to False to disable figure saving

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

def flip_x_coordinates(data):
    """
    Flips all x coordinates in the posTest data object by negating them.
    
    Args:
        data: posTest object containing coordinate data
    
    Returns:
        None (modifies data object in place)
    """
    # List of all x-coordinate attributes to flip
    x_attributes = [
        "circleAlphaXs", "circleBetaXs",
        "datumAlphaXs", "datumBetaXs", 
        "betaHighXs", "betaLowXs",
        "alphaHighXs", "alphaLowXs",
        "betaNLXs", "alphaNLXs"
    ]
    
    for attr in x_attributes:
        if hasattr(data, attr):
            values = getattr(data, attr)
            if isinstance(values, list):
                if len(values) > 0 and isinstance(values[0], list):
                    # Nested list: multiple groups
                    flipped_values = [[-x for x in group] for group in values]
                else:
                    # Flat list
                    flipped_values = [-x for x in values]
                setattr(data, attr, flipped_values)
            else:
                print(f"Warning: {attr} is not a list, skipping...")
    
    print("All x coordinates have been flipped (negated)")

def save_figure(filename, base_dir=None, dpi=300, format='png', enable_saving=None):
    """
    Save the current matplotlib figure to the specified directory.
    
    Args:
        filename (str): Name of the file (without extension)
        base_dir (str): Directory to save to. If None, uses current directory
        dpi (int): Resolution for saving (default 300)
        format (str): File format (default 'png')
        enable_saving (bool): Override for SAVE_FIGURES global flag. If None, uses global flag
    """
    # Use global flag if enable_saving is not specified
    should_save = SAVE_FIGURES if enable_saving is None else enable_saving
    
    if not should_save:
        print(f"Figure saving disabled for: {filename}")
        return
    
    if base_dir is None:
        base_dir = os.getcwd()
    
    # Ensure the directory exists
    os.makedirs(base_dir, exist_ok=True)
    
    # Add extension if not present
    if not filename.endswith(f'.{format}'):
        filename = f"{filename}.{format}"
    
    filepath = os.path.join(base_dir, filename)
    plt.savefig(filepath, dpi=dpi, bbox_inches='tight')
    print(f"Figure saved: {filepath}")

def getAlphaCircle(self):
    Xs = []
    Ys = []
    radii = []
    for i in range(len(self.circleBetaXs)):
        x, y, radius = fit_circle(np.array(self.circleBetaXs[i]), np.array(self.circleBetaYs[i]))
        Xs.append(x)
        Ys.append(y)
        radii.append(radius)
        # print(f'X: {x}..3f, Y: {y}.3f, radius: {radius}.3f')
    x, y, radius = fit_circle(np.array(Xs), np.array(Ys))
    # print(f'alpha X: {x}..3f, Y: {y}.3f, radius: {radius}.3f')
    return x, y, radius, Xs, Ys, radii

base_directory = path_to_results_dir(POSID, TEMP)
plots_directory = os.path.join(base_directory, 'Plots')
if not os.path.exists(plots_directory):
    os.makedirs(plots_directory)

filepath = None
filename = None
for filename in os.listdir(base_directory):
    print(os.listdir(base_directory))
    if filename.endswith(f'pos{POSID}'):
        filepath = os.path.join(base_directory, filename)
        break

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

data = posTest.loadFromFile(filepath)
flip_x_coordinates(data)  # Flip x coordinates

# Load the object
# with open(filepath, "rb") as f:
print(f"Reading file {filename}...")
xb,yb,rb = fit_circle(np.array(data.betaNLXs), np.array(data.betaNLYs))
xa,ya,ra = data.getAlphaArm()
print(xb,yb,rb)
print(xa,ya,ra)
# Print basic metadata
print(f"ID: {data.id}")
print(f"Filename: {data.filename}")
# print(f"Temperature: {data.temperature}")

def data2Dataframe(list_attributes):
    # Flatten and label all data
    records = []
    for attr in list_attributes:
        values = getattr(data, attr)
        if isinstance(values[0], list):  # Nested list: multiple groups
            for group_idx, group in enumerate(values):
                for point_idx, val in enumerate(group):
                    records.append({
                        "source": attr,
                        "group": group_idx,
                        "index": point_idx,
                        "value": val
                    })
        else:  # Flat list
            for point_idx, val in enumerate(values):
                records.append({
                    "source": attr,
                    "group": None,
                    "index": point_idx,
                    "value": val
                })

    # Convert to DataFrame
    df = pd.DataFrame(records)
    return df
for attr in attributes:
    val = getattr(data, attr)
    print(f"{attr}: {len(val)} entries")

def circleResidualBeta(betaXs, betaYs, start=0, end=-1):
        centerX, centerY, radius = fit_circle(np.array(betaXs[start:end]), np.array(betaYs[start:end]))
        normalizedXs = np.array(betaXs[start:end]) - centerX
        normalizedYs = np.array(betaYs[start:end]) - centerY
        NLAngles = np.rad2deg(np.arctan2(normalizedXs, normalizedYs))
        for i in range(len(NLAngles)-1):
            if NLAngles[i+1] - NLAngles [i] > 180 :
                NLAngles[i+1] = NLAngles[i+1] - 360
            elif NLAngles[i+1] - NLAngles[i] < -180:
                NLAngles[i+1] = NLAngles[i+1] + 360
        target_angles = NLAngles.astype(np.int64)
        if len(NLAngles) != len(target_angles):
            raise ValueError("NLAngles and target_angles must have the same length")
        else:
            residuals = NLAngles - target_angles
        # print(f"residuals: {residuals}")
        # print(f"NLAngles: {NLAngles}")
        # print(f"target_angles: {target_angles}")
        return residuals, target_angles, radius
#%%

# Plot circleAlphaXs/Ys

xa, ya ,ra = fit_circle(np.array(data.circleAlphaXs), np.array(data.circleAlphaYs))
normalizedXs = np.array(data.circleAlphaXs) - xa
normalizedYs = np.array(data.circleAlphaYs) - ya
print(f"Normalized Xs: {normalizedXs}")
print(f"Normalized Ys: {normalizedYs}")
print(data.alphaPos)
angle = np.rad2deg(np.arctan2(np.array(normalizedYs), np.array(normalizedXs)))+90
angle = np.round(angle, 2)  # Round to 2 decimal places
diff_angle = np.diff(angle, prepend=angle[0])  # Calculate angle differences
diff_angle = np.abs(diff_angle)  # Take absolute values
print("Angle differences:", diff_angle)
angle_start = np.arctan2(normalizedYs[0], normalizedXs[0]) * 180 / np.pi
print("angle", angle)
print("angle_start", angle_start)

plt.figure(figsize=(8, 6))
for aPos, xs, ys in zip(angle, normalizedXs, normalizedYs):
    plt.scatter(xs,  ys, marker='o', label=f'Alpha Pos: {aPos}°')
plt.title(f'circleAlphaXs / Ys - pos {data.id}')
plt.xlabel("X [mm]")
plt.ylabel("Y [mm]")
plt.axis("equal")
plt.grid(True)
plt.legend()
plt.tight_layout()
save_figure(f'circleAlphaXs_Ys_pos{data.id}', plots_directory)

# Plot circleBetaXs/Ys
x, y, radius, Xs, Ys, radii = getAlphaCircle(data)
plt.figure(figsize=(8, 6))
for i, (xs, ys) in enumerate(zip(data.circleBetaXs, data.circleBetaYs)):
    plt.scatter(xs-xa, ys-ya, marker='o')
plt.scatter(x-xa, y-ya, marker='*', color='red', label=f'Alpha center')
plt.scatter(Xs-xa, Ys-ya, marker='D', color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
 '#8c564b'], label=f'Beta centers')
plt.title(f'circleBetaXs / Ys - pos {data.id}')
plt.xlabel("X [mm]")
plt.ylabel("Y [mm]")
plt.axis("equal")
plt.grid(True)
plt.legend()
plt.tight_layout()
save_figure(f'circleBetaXs_Ys_pos{data.id}', plots_directory)

plt.figure(figsize=(8, 6))
for i, (xs, ys) in enumerate(zip(data.datumAlphaXs, data.datumAlphaYs)):
    plt.scatter(xs-xa, ys-ya, marker='o', label=f'iter {i}')
plt.title(f'hardStopsAlpha Xs / Ys - pos {data.id}')
plt.xlabel("X [mm]")
plt.ylabel("Y [mm]")
plt.axis("equal")
plt.grid(True)
plt.legend()
plt.tight_layout()
save_figure(f'hardStopsAlpha_Xs_Ys_pos{data.id}', plots_directory)

plt.figure(figsize=(8, 6))
for i, (xs, ys) in enumerate(zip(data.datumBetaXs, data.datumBetaYs)):
    plt.scatter(xs-xa, ys-ya, marker='o', label=f'iter {i}')
plt.title(f'hardStopsBeta Xs / Ys - pos {data.id}')
plt.xlabel("X [mm]")
plt.ylabel("Y [mm]")
plt.axis("equal")
plt.grid(True)
plt.legend()
plt.tight_layout()
save_figure(f'hardStopsBeta_Xs_Ys_pos{data.id}', plots_directory)


# Plot alphaNL path
plt.figure(figsize=(6, 6))
plt.plot(data.alphaNLXs-xa, data.alphaNLYs-ya, marker='o', color='blue')
plt.plot(data.alphaNLXs[0]-xa, data.alphaNLYs[0]-ya, marker='o', color='red', label='Start')
plt.plot(data.alphaNLXs[-1]-xa, data.alphaNLYs[-1]-ya, marker='o', color='black', label='End')
plt.xlabel("X [mm]")
plt.ylabel("Y [mm]")
plt.title(f'Alpha Non-Linearity Path - pos {data.id}')
plt.legend()
plt.axis("equal")
plt.grid(True)
plt.tight_layout()
save_figure(f'alphaNL_path_pos{data.id}', plots_directory)

# Plot betaNL path
plt.figure(figsize=(6, 6))
plt.plot(data.betaNLXs-xb, data.betaNLYs-yb, marker='o', color='green')
plt.plot(data.betaNLXs[0]-xb, data.betaNLYs[0]-yb, marker='o', color='red', label='Start')
plt.plot(data.betaNLXs[-1]-xb, data.betaNLYs[-1]-yb, marker='o', color='black', label='End')
plt.title(f'Beta Non-Linearity Path - pos {data.id}')
plt.xlabel("X [mm]")
plt.ylabel("Y [mm]")
plt.title(f'Beta Non-Linearity Path - pos {data.id}')
plt.legend()
plt.axis("equal")
plt.grid(True)
plt.tight_layout()
save_figure(f'betaNL_path_pos{data.id}', plots_directory)

start_beta = 15
residuals, target_angles, radius = circleResidualBeta(data.betaNLXs, data.betaNLYs, start=start_beta)
plt.figure(figsize=(6, 6))
plt.plot(target_angles, residuals, 'o-', label="Beta Res", color="red")
plt.title(f'Beta arc residuals - pos {data.id}')
plt.xlabel("X [mm]")
plt.ylabel("Y [mm]")
plt.grid(True)
plt.legend()
plt.tight_layout()
save_figure(f'beta_arc_residuals_pos{data.id}', plots_directory)


# Plot Alpha Highs and Lows
plt.figure(figsize=(6, 6))
plt.plot(data.alphaHighXs, data.alphaHighYs, 'o-', label="Alpha Highs", color="red")
plt.plot(data.alphaLowXs, data.alphaLowYs, 'o-', label="Alpha Lows", color="blue")
plt.title(f'Alpha High vs Low Trajectories - pos {data.id}')
plt.xlabel("X [mm]")
plt.ylabel("Y [mm]")
plt.axis("equal")
plt.grid(True)
plt.legend()
plt.tight_layout()
save_figure(f'alpha_high_low_trajectories_pos{data.id}', plots_directory)

# Plot Beta Highs and Lows
plt.figure(figsize=(6, 6))
plt.plot(data.betaHighXs, data.betaHighYs, 'o-', label="Beta Highs", color="green")
plt.plot(data.betaLowXs, data.betaLowYs, 'o-', label="Beta Lows", color="purple")
plt.title(f'Beta High vs Low Trajectories - pos {data.id}')
plt.xlabel("X [mm]")
plt.ylabel("Y [mm]")
plt.axis("equal")
plt.grid(True)
plt.legend()
plt.tight_layout()
save_figure(f'beta_high_low_trajectories_pos{data.id}', plots_directory)

# --- 1. Compute center of alpha circle ---
# Flatten all alpha X/Y coordinates
print(data.circleAlphaXs)

# Helper function to center and plot data
def plot_centered(x_list, y_list, title, labels, colors, Xcenter=0, Ycenter=0, save_filename=None):
    plt.figure(figsize=(6, 6))
    for xs, ys, label, color in zip(x_list, y_list, labels, colors):
        xs = np.array(xs) - Xcenter
        ys = np.array(ys) - Ycenter
        plt.plot(xs, ys, 'o-', label=label, color=color)
    plt.title(title)
    plt.xlabel("X [mm]")
    plt.ylabel("Y [mm]")
    plt.axis("equal")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    save_figure(save_filename, plots_directory)

# --- 2. Plot centered circleAlpha and circleBeta ---
plot_centered(
    x_list=data.circleAlphaXs + data.circleBetaXs,
    y_list=data.circleAlphaYs + data.circleBetaYs,
    Xcenter=xa, Ycenter=ya,
    title=f"Centered Circle Alpha & Beta - pos {data.id}",
    labels=[f"circleAlpha {i}" for i in range(len(data.circleAlphaXs))] +
           [f"circleBeta {i}" for i in range(len(data.circleBetaXs))],
    colors=['blue']*len(data.circleAlphaXs) + ['green']*len(data.circleBetaXs),
    save_filename=f'centered_circle_alpha_beta_pos{data.id}'
)

# --- 3. Plot centered AlphaNL and BetaNL ---
plot_centered(
    x_list=[data.alphaNLXs, data.betaNLXs, data.alphaNLXs[0], data.betaNLXs[0]],
    y_list=[data.alphaNLYs, data.betaNLYs, data.alphaNLYs[0], data.betaNLYs[0]],
    Xcenter=xa, Ycenter=ya,
    title=f"Centered Non-Linearity Paths - pos {data.id}",
    labels=["Alpha NL", "Beta NL"],
    colors=["blue", "green", "red", "red"],
    save_filename=f'centered_non_linearity_paths_pos{data.id}'
)
# plt.scatter(data.alphaNLXs[0] - xa, data.alphaNLYs[0] - ya, color='red', label='Alpha NL Start')
# plt.scatter(data.alphaNLXs[-1] - xa, data.alphaNLYs[-1] - ya, color='black', label='Alpha NL End')

# --- 4. Plot centered Alpha High/Low Paths ---
plot_centered(
    x_list=[data.alphaHighXs, data.alphaLowXs],
    y_list=[data.alphaHighYs, data.alphaLowYs],
    Xcenter=xa, Ycenter=ya,
    title=f"Centered Alpha High/Low Paths - pos {data.id}",
    labels=["Alpha High", "Alpha Low"],
    colors=["red", "blue"],
    save_filename=f'centered_alpha_high_low_paths_pos{data.id}'
)

# --- 5. Plot centered Beta Highs/Lows ---
plot_centered(
    x_list=[data.betaHighXs, data.betaLowXs],
    y_list=[data.betaHighYs, data.betaLowYs],
    Xcenter=xb, Ycenter=yb,
    title=f"Centered Beta High/Low Paths - pos {data.id}",
    labels=["Beta High", "Beta Low"],
    colors=["green", "purple"],
    save_filename=f'centered_beta_high_low_paths_pos{data.id}'
)

plt.show()


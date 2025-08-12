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
SAVE_FIGURES = True  # Set to False to disable figure saving

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

def getAlphaCircle(data):
    Xs = []
    Ys = []
    radii = []
    for i in range(len(data.circleBetaXs)):
        x, y, radius = fit_circle(np.array(data.circleBetaXs[i]), np.array(data.circleBetaYs[i]))
        Xs.append(x)
        Ys.append(y)
        radii.append(radius)
        # print(f'X: {x}..3f, Y: {y}.3f, radius: {radius}.3f')
    x, y, radius = fit_circle(np.array(Xs), np.array(Ys))
    # print(f'alpha X: {x}..3f, Y: {y}.3f, radius: {radius}.3f')
    return x, y, radius, Xs, Ys, radii

def nonLinearityAlpha(data, start = None, end = None, centerX = 0, centerY = 0):
    normalizedXs = np.array(data.alphaNLXs[start:end]) - centerX
    normalizedYs = np.array(data.alphaNLYs[start:end]) - centerY
    NLAngles = np.rad2deg(np.arctan2(normalizedXs, normalizedYs))
    for i in range(len(NLAngles)-1):
        if NLAngles[i+1] - NLAngles [i] > 180 :
            NLAngles[i+1] = NLAngles[i+1] - 360
        elif NLAngles[i+1] - NLAngles[i] < -180:
            NLAngles[i+1] = NLAngles[i+1] + 360
    if NLAngles[4] < NLAngles[1]:
        NLAngles = NLAngles * (-1)
    NLAngles = NLAngles - NLAngles[0]
    return NLAngles

def nonLinearityBeta(data, start = None, end = None, centerX = 0, centerY = 0):
    normalizedXs = np.array(data.betaNLXs[start:end]) - centerX
    normalizedYs = np.array(data.betaNLYs[start:end]) - centerY
    NLAngles = np.rad2deg(np.arctan2(normalizedXs, normalizedYs))
    for i in range(len(NLAngles)-1):
        if NLAngles[i+1] - NLAngles [i] > 180 :
            NLAngles[i+1] = NLAngles[i+1] - 360
        elif NLAngles[i+1] - NLAngles[i] < -180:
            NLAngles[i+1] = NLAngles[i+1] + 360
    if NLAngles[4] < NLAngles[1]:
        NLAngles = NLAngles * (-1)
    NLAngles = NLAngles - NLAngles[0]
    return NLAngles
    
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

base_directory = path_to_results_dir(POSID, TEMP)
plots_directory = os.path.join(base_directory, 'Plots')
if not os.path.exists(plots_directory):
    os.makedirs(plots_directory)

filepaths = []
for filename in os.listdir(base_directory):
    if filename.endswith(f'pos{POSID}'):
        filepath = os.path.join(base_directory, filename)
        with open(filepath, "rb") as f:
            header = f.read(2)  # read first two bytes
        if header in (b"\x80\x04", b"\x80\x05"):  # pickle protocol 4 or 5
            filepaths.append(filepath)

datas = []
NLangles_alphas = []
ref_angles_alphas = []
NLangles_betas = []
ref_angles_betas = []
for filepath in filepaths:
    with open(filepath, "rb") as f:
        data = pickle.load(f)
        datas.append(data)

    xa, ya, ra, _, _, _ = getAlphaCircle(data)
    NLangles_alpha = nonLinearityAlpha(data, start=15, end=-15, centerX=xa, centerY=ya)
    ref_angles_alpha = np.linspace(0, len(NLangles_alpha)-1, len(NLangles_alpha))
    NLangles_alpha = NLangles_alpha - ref_angles_alpha
    NLangles_alphas.append(NLangles_alpha)
    ref_angles_alphas.append(ref_angles_alpha)

    xb, yb, rb = data.getBetaArm()
    NLangles_beta = nonLinearityBeta(data, start=15, end=-15, centerX=xb, centerY=yb)
    ref_angles_beta = np.linspace(0, len(NLangles_beta)-1, len(NLangles_beta))
    NLangles_beta = NLangles_beta - ref_angles_beta
    NLangles_betas.append(NLangles_beta)
    ref_angles_betas.append(ref_angles_beta)

# Plotting
plt.figure(figsize=(10, 6))
plt.title(f'Alpha Non-linearities of Positioner {POSID} at {TEMP}°C')
plt.xlabel('Reference Angle (degrees)')
plt.ylabel('Non-linearity (degrees)')
for i, (NLangles_alpha, ref_angles_alpha) in enumerate(zip(NLangles_alphas, ref_angles_alphas)):
    plt.plot(ref_angles_alpha, NLangles_alpha, label=f'iter {i+1}')
plt.grid()
plt.legend()
plt.tight_layout()
save_figure("alpha_non_linearities", base_dir=plots_directory)

plt.figure(figsize=(10, 6))
plt.title(f'Beta Non-linearities of Positioner {POSID} at {TEMP}°C')
plt.xlabel('Reference Angle (degrees)')
plt.ylabel('Non-linearity (degrees)')
for i, (NLangles_beta, ref_angles_beta) in enumerate(zip(NLangles_betas, ref_angles_betas)):
    plt.plot(ref_angles_beta, NLangles_beta, label=f'iter {i+1}')
plt.grid()
plt.legend()
plt.tight_layout()
save_figure("beta_non_linearities", base_dir=plots_directory)
plt.show()
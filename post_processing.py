#%%
import os
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
# from docx import Document
from miscmath import fit_circle
## Make sure to search for: # CHANGE POSITIONER HERE! to be able to change the positioner!
## Make sure to search for: # CHANGE MODULE HERE! to be able to change the module!

POSID = 24 # CHANGE POSITIONER HERE!
TEMP = 20 # [°C] CHANGE TEMPERATURE HERE

def path_to_results_dir(posID: int = None, temp: float = None):

    script_dir = os.path.dirname(__file__)
    # results_dir_path = os.path.join(script_dir, 'Results_examples/')
    results_dir_path = os.path.join(script_dir, 'Results/')

    # Creates a subfolder corresponding to the project name in Results/
    if posID is not None: 
        results_dir_path = os.path.join(results_dir_path, f'Positioner {posID}' + '/')

    if temp is not None:
        results_dir_path = os.path.join(results_dir_path, f'{temp} degrees' + '/')

    # Checks if the directory exists, if not creates it
    if not os.path.isdir(results_dir_path):
        os.makedirs(results_dir_path)
    
    return results_dir_path
#base_directory3 = "D:/My Work/Testing of Modules/MPS Prototype - Module 1/Plots"

results_dir_path = path_to_results_dir(POSID, TEMP)

base_directory3_alpha = results_dir_path + "Plots/Repeatability Alpha" 
base_directory3_beta = results_dir_path +  "Plots/Repeatability Beta"

base_directory3_NLalpha = results_dir_path + "Plots/NL Alpha"
base_directory3_NLbeta = results_dir_path + "Plots/NL Beta"

base_directory2 = results_dir_path
base_directory = results_dir_path

class posTest():
    def __init__(self, id = '19', module=1, stamp = '20200101_121212', temperature: float = None):
        self.id = id
        self.filename = (f'{stamp}_module_{module}_pos{id}')
        #circle positions and coordinates
        self.alphaPos =  [0, 60, 120, 180, 240, 300]
        self.betaPos = [0, 30, 60, 90, 120, 150]
        self.circleAlphaXs = []
        self.circleAlphaYs = []
        self.circleBetaXs = []
        self.circleBetaYs = []
        self.datumAlphaXs = []
        self.datumAlphaYs = []
        self.datumBetaXs = []
        self.datumBetaYs = []
        # repeatability testing
        self.testPosition = 30
        self.deltaMove = 10  # delta
        self.repeatabilityIterations = 20 # amount of iterations

        self.hardStopIterations =  100 # amount og iteration

        self.betaHighXs = []    # when going higher angle
        self.betaHighYs = []
        self.betaLowXs = []    # when going lower anglew
        self.betaLowYs = []

        self.alphaHighXs = []    # when going higher angle
        self.alphaHighYs = []
        self.alphaLowXs = []    # when going lower anglew
        self.alphaLowYs = []

                # repeatability testing
        self.alphaNLRange = 380
        self.betaNLRange = 200
        self.betaNLXs = []    # when going higher angle
        self.betaNLYs = []

        self.alphaNLXs = []    # when going higher angle
        self.alphaNLYs = []

    def saveToFile(self):
        try:
            with open(self.filename, "wb") as f:
                pickle.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as ex:
            print("Error during pickling object (Possibly unsupported):", ex)

    def getCircle(self):
        centerX, centerY, radius = fit_circle(np.array(self.betaNLXs), np.array(self.betaNLYs))
        return centerX, centerY, radius

    def getAlphaArm(self):
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
        return x, y, radius
    
    def getBetaArm(self):
        x, y, radius = fit_circle(np.array(self.betaNLXs), np.array(self.betaNLYs))
        # print(f' beta X: {x}..3f, Y: {y}.3f, radius: {radius}.3f')
        return x, y, radius
    
    def plotRepeatabilityBetaXY(self, folder_path=base_directory3_beta):
        normalizedX = self.betaHighXs - np.mean(self.betaHighXs)
        normalizedX = normalizedX * 1000
        normalizedY = self.betaHighYs - np.mean(self.betaHighYs)
        normalizedY = normalizedY * 1000
        plt.scatter(normalizedX, normalizedY)
        plt.title('Repeatability beta XY of pos ' + str(self.id))
        plt.xlabel('x [um]')
        plt.ylabel('y [um]')
        plt.grid()
        #filename = (f'images/{self.filename}_betaXY.png')
        #plt.savefig(filename, bbox_inches = 'tight')
        #plt.show()
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        filename = os.path.join(folder_path, f'{self.filename}_betaXY.png')
        plt.savefig(filename, bbox_inches='tight')
        plt.clf()
        #plt.show()

    def plotRepeatabilityAlphaXY(self, folder_path=base_directory3_alpha):
        normalizedX = self.alphaHighXs - np.mean(self.alphaHighXs)
        normalizedX = normalizedX * 1000
        normalizedY = self.alphaHighYs - np.mean(self.alphaHighYs)
        normalizedY = normalizedY * 1000
        plt.scatter(normalizedX, normalizedY)
        plt.title('Repeatability alpha XY of pos ' + str(self.id))
        plt.xlabel('x [um]')
        plt.ylabel('y [um]')
        plt.grid()
        #filename = (f'images/{self.filename}_alphaXY.png')
        #plt.savefig(filename, bbox_inches = 'tight')
        #plt.show()
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        filename = os.path.join(folder_path, f'{self.filename}_alphaXY.png')
        plt.savefig(filename, bbox_inches='tight')
        plt.clf()
        #plt.show()

    def repeatabilityBetaXY(self):
        meanX = np.mean(np.array(self.betaHighXs))
        meanY = np.mean(np.array(self.betaHighYs))
        distanceX = np.array(self.betaHighXs) - meanX
        distanceY = np.array(self.betaHighYs) - meanY
        distances = np.sqrt(distanceX **2 + distanceY ** 2)
        return np.std(distances)
    
    def repeatabilityAlphaXY(self):
        meanX = np.mean(np.array(self.alphaHighXs))
        meanY = np.mean(np.array(self.alphaHighYs))
        distanceX = np.array(self.alphaHighXs) - meanX
        distanceY = np.array(self.alphaHighYs) - meanY
        distances = np.sqrt(distanceX **2 + distanceY ** 2)
        return np.std(distances)
    
    def backlashBeta(self):
        centerX, centerY, radius = self.getCircle()
        print(self.betaHighXs)
        print(centerX)
        normalizedXs = np.array(self.betaHighXs) - centerX
        normalizedYs = np.array(self.betaHighYs) - centerY
        anglesHigh = np.rad2deg(np.arctan2(normalizedXs, normalizedYs))
        normalizedXs = np.array(self.betaLowXs) - centerX
        normalizedYs = np.array(self.betaLowYs) - centerY
        anglesLow = np.rad2deg(np.arctan2(normalizedXs, normalizedYs))
        backlashes = anglesHigh - anglesLow
        return np.mean(backlashes)
    
    def nonLinearity_alpha(self):
        centerX, centerY, radius = self.getCircle()
        normalizedXs = np.array(self.alphaNLXs) - centerX
        normalizedYs = np.array(self.alphaNLYs) - centerY
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
    
    def plotNonLinearity_alpha(self, folder_path=base_directory3_NLalpha):
        NL = self.nonLinearity_alpha()
        NL = NL - np.linspace(0, len(NL)-1, len(NL))
        plt.plot(NL)
        plt.title(f'Nonlinearity alpha of pos {self.id}')
        plt.xlabel('Position at output [°]')
        plt.ylabel('Nonlinearity [°] at output')
        plt.grid()
        #filename = (f'images/{self.filename}alpha_NL.png')
        #plt.savefig(filename, bbox_inches = 'tight')
        #plt.show()
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        filename = os.path.join(folder_path, f'{self.filename}alpha_NL.png')
        plt.savefig(filename, bbox_inches='tight')
        plt.clf()
        #plt.show()
    
    def nonLinearity_beta(self):
        centerX, centerY, radius = self.getCircle()
        normalizedXs = np.array(self.betaNLXs) - centerX
        normalizedYs = np.array(self.betaNLYs) - centerY
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
    
    def plotNonLinearity_beta(self, folder_path=base_directory3_NLbeta):
        NL = self.nonLinearity_beta()
        NL = NL - np.linspace(0, len(NL)-1, len(NL))
        plt.plot(NL)
        plt.title(f'Nonlinearity beta of pos {self.id}')
        plt.xlabel('Position at output [°]')
        plt.ylabel('Nonlinearity [°] at output')
        plt.grid()
        #filename = (f'images/{self.filename}alpha_NL.png')
        #plt.savefig(filename, bbox_inches = 'tight')
        #plt.show()
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        filename = os.path.join(folder_path, f'{self.filename}beta_NL.png')
        plt.savefig(filename, bbox_inches='tight')
        plt.clf()
        #plt.show()
    
    def getResults(self):
        centerX, centerY, radius = self.getCircle()
        repeatabilityBetaXY = self.repeatabilityBetaXY()
        self.plotRepeatabilityBetaXY()
        repeatabilityAlphaXY = self.repeatabilityAlphaXY()
        self.plotRepeatabilityAlphaXY()
        backlash = self.backlashBeta()
        self.plotNonLinearity_alpha()
        self.plotNonLinearity_beta()

        #print(self.id)
        #print(f'Repeatability alpha XY is {repeatabilityAlphaXY*1000:.3f} um rms')
        #print(f'Repeatability beta XY is {repeatabilityBetaXY*1000:.3f} um rms')
        #print(f'Mean backlash is {backlash:.3f}Â°')

    def scaleResults(self):
        scaleFactor = 4.0 / 2.2
        for i in range(len(self.circleAlphaXs)):
            self.circleAlphaXs[i] *= scaleFactor
        for i in range(len(self.circleAlphaYs)):
            self.circleAlphaYs[i] *= scaleFactor
        for i in range(len(self.circleBetaXs)):
            for ii in range(len(self.circleBetaXs[i])):
                self.circleBetaXs[i][ii] *= scaleFactor
        for i in range(len(self.circleBetaYs)):
            for ii in range(len(self.circleBetaYs[i])):
                self.circleBetaYs[i][ii] *= scaleFactor
        for i in range(len(self.datumAlphaXs)):
            self.datumAlphaXs[i] *= scaleFactor
        for i in range(len(self.datumAlphaYs)):
            self.datumAlphaYs[i] *= scaleFactor
        for i in range(len(self.datumBetaXs)):
            self.datumBetaXs[i] *= scaleFactor
        for i in range(len(self.datumBetaYs)):
            self.datumBetaYs[i] *= scaleFactor

        for i in range(len(self.betaHighXs)):
            self.betaHighXs[i] *= scaleFactor
        for i in range(len(self.betaHighYs)):
            self.betaHighYs[i] *= scaleFactor
        for i in range(len(self.betaLowXs)):
            self.betaLowXs[i] *= scaleFactor
        for i in range(len(self.betaLowYs)):
            self.betaLowYs[i] *= scaleFactor

        for i in range(len(self.alphaHighXs)):
            self.alphaHighXs[i] *= scaleFactor
        for i in range(len(self.alphaHighYs)):
            self.alphaHighYs[i] *= scaleFactor
        for i in range(len(self.alphaLowXs)):
            self.alphaLowXs[i] *= scaleFactor
        for i in range(len(self.alphaLowYs)):
            self.alphaLowYs[i] *= scaleFactor

        for i in range(len(self.betaNLXs)):
            self.betaNLXs[i] *= scaleFactor
        for i in range(len(self.betaNLYs)):
            self.betaNLYs[i] *= scaleFactor
        for i in range(len(self.alphaNLXs)):
            self.alphaNLXs[i] *= scaleFactor
        for i in range(len(self.alphaNLYs)):
            self.alphaNLYs[i] *= scaleFactor
    
    @classmethod
    def loadFromFile(cls, fileName):
        try:
            with open(fileName, "rb") as f:
                data = pickle.load(f)
            return  data
        except Exception as ex:
            print("Error during unpickling object (Possibly unsupported):", ex)


class posResults():
        
    def __init__(self, filepath):
        self.data = posTest.loadFromFile(filepath)
        self.centerX = 0.0
        self.centerY = 0.0
        self.centerX_beta = 0.0
        self.centerY_beta = 0.0
        self.alphaArm = 0.0
        self.betaArm = 0.0
        self.filename = os.path.basename(filepath)

    def calculateResults(self):
        x, y, radius = self.data.getAlphaArm()
        self.centerX = x
        self.centerY = y
        self.alphaArm = radius
        x, y, radius = self.data.getBetaArm()
        self.centerX_beta = x
        self.centerY_beta = y
        self.betaArm = radius

    def repeatabilityDatumAlphaXY(self):
        meanX = np.mean(np.array(self.data.datumAlphaXs))
        meanY = np.mean(np.array(self.data.datumAlphaYs))
        distanceX = np.array(self.data.datumAlphaXs) - meanX
        distanceY = np.array(self.data.datumAlphaYs) - meanY
        distances = np.sqrt(distanceX ** 2 + distanceY ** 2)
        return np.std(distances)

    def repeatabilityDatumAlpha(self):
        normalizedXs = np.array(self.data.datumAlphaXs) - self.centerX
        normalizedYs = np.array(self.data.datumAlphaYs) * (-1) - self.centerY * (-1)
        Xs = normalizedYs
        Ys = normalizedXs * (-1)
        scara = Scara(self.alphaArm, self.betaArm)
        angles = scara.inverse_kinematics(Xs[0], Ys[0])
        DatumAngles = np.rad2deg(np.arctan2(Xs[1:], Ys[1:]))
        return DatumAngles

    def repeatabilityDatumBetaXY(self):
        meanX = np.mean(np.array(self.data.datumBetaXs))
        meanY = np.mean(np.array(self.data.datumBetaYs))
        distanceX = np.array(self.data.datumBetaXs) - meanX
        distanceY = np.array(self.data.datumBetaYs) - meanY
        distances = np.sqrt(distanceX ** 2 + distanceY ** 2)
        return np.std(distances)

    def repeatabilityDatumBeta(self):
        normalizedXs = np.array(self.data.datumAlphaXs) - self.centerX
        normalizedYs = np.array(self.data.datumAlphaYs) * (-1) - self.centerY * (-1)
        Xs = normalizedYs
        Ys = normalizedXs * (-1)
        scara = Scara(self.alphaArm, self.betaArm)
        angles = scara.inverse_kinematics(Xs[0], Ys[0])
        DatumAngles = np.rad2deg(np.arctan2(normalizedXs[1:], normalizedYs[1:]))
        return DatumAngles

    def nonLinearityAlpha(self, start=None, end=None):
        centerX, centerY, radius = fit_circle(np.array(self.data.alphaNLXs[start:end]), np.array(self.data.alphaNLYs[start:end]))
        normalizedXs = np.array(self.data.alphaNLXs[start:end]) - centerX
        normalizedYs = np.array(self.data.alphaNLYs[start:end]) - centerY
        NLAngles = np.rad2deg(np.arctan2(normalizedXs, normalizedYs))
        for i in range(len(NLAngles)-1):
            if NLAngles[i+1] - NLAngles[i] > 180:
                NLAngles[i+1] = NLAngles[i+1] - 360
            elif NLAngles[i+1] - NLAngles[i] < -180:
                NLAngles[i+1] = NLAngles[i+1] + 360
        if NLAngles[4] < NLAngles[1]:
            NLAngles = NLAngles * (-1)
        NLAngles = NLAngles - NLAngles[0]
        return NLAngles

    def nonLinearityBeta(self, start=None, end=None):
        centerX, centerY, radius = fit_circle(np.array(self.data.betaNLXs[start:end]), np.array(self.data.betaNLYs[start:end]))
        normalizedXs = np.array(self.data.betaNLXs[start:end]) - centerX
        normalizedYs = np.array(self.data.betaNLYs[start:end]) - centerY
        NLAngles = np.rad2deg(np.arctan2(normalizedXs, normalizedYs))
        for i in range(len(NLAngles)-1):
            if NLAngles[i+1] - NLAngles[i] > 180:
                NLAngles[i+1] = NLAngles[i+1] - 360
            elif NLAngles[i+1] - NLAngles[i] < -180:
                NLAngles[i+1] = NLAngles[i+1] + 360
        if NLAngles[4] < NLAngles[1]:
            NLAngles = NLAngles * (-1)
        NLAngles = NLAngles - NLAngles[0]
        return NLAngles

    def plotNonLinearityAlpha(self, start=None, end=None, folder_path=None):
        NL = self.nonLinearityAlpha(start, end)
        NL = NL - np.linspace(0, len(NL)-1, len(NL))
        plt.plot(NL)
        plt.title(f'Nonlinearity alpha of pos {self.data.id}')
        plt.xlabel('Position at output [°]')
        plt.ylabel('Nonlinearity [°] at output')
        #plt.show()
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        filename = os.path.join(folder_path, f'{self.filename}alpha_NL.png')
        plt.savefig(filename, bbox_inches='tight')
        plt.clf()


    def plotNonLinearityBeta(self, start=None, end=None,folder_path=None):
        NL = self.nonLinearityBeta(start, end)
        NL = NL - np.linspace(0, len(NL)-1, len(NL))
        plt.plot(NL)
        plt.title(f'Nonlinearity beta of pos {self.data.id}')
        plt.xlabel('Position at output [°]')
        plt.ylabel('Nonlinearity [°] at output')
        #plt.show()
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        filename = os.path.join(folder_path, f'{self.filename}beta_NL.png')
        plt.savefig(filename, bbox_inches='tight')
        plt.clf()

    def backlashAlpha(self):
        normalizedXs = np.array(self.data.alphaHighXs) - self.centerX
        normalizedYs = np.array(self.data.alphaHighYs) - self.centerY
        anglesHigh = np.rad2deg(np.arctan2(normalizedXs, normalizedYs))
        normalizedXs = np.array(self.data.alphaLowXs) - self.centerX
        normalizedYs = np.array(self.data.alphaLowYs) - self.centerY
        anglesLow = np.rad2deg(np.arctan2(normalizedXs, normalizedYs))
        backlashes = anglesHigh - anglesLow
        return np.mean(backlashes)
    
    def backlashBeta(self):
        normalizedXs = np.array(self.data.betaHighXs) - self.centerX_beta
        normalizedYs = np.array(self.data.betaHighYs) - self.centerY_beta
        anglesHigh = np.rad2deg(np.arctan2(normalizedXs, normalizedYs))
        normalizedXs = np.array(self.data.betaLowXs) - self.centerX_beta
        normalizedYs = np.array(self.data.betaLowYs) - self.centerY_beta
        anglesLow = np.rad2deg(np.arctan2(normalizedXs, normalizedYs))
        backlashes = anglesHigh - anglesLow
        return np.mean(backlashes)

    def get_results(self):
        self.calculateResults()
        repeatabilityAlphaXY = self.data.repeatabilityAlphaXY()
        repeatabilityBetaXY = self.data.repeatabilityBetaXY()
        datumAlpha = self.repeatabilityDatumAlphaXY()
        datumBeta = self.repeatabilityDatumBetaXY()
        backlashAlpha = self.backlashAlpha()
        backlashBeta = self.backlashBeta()
        self.plotNonLinearityAlpha(start=8, end=350, folder_path=base_directory3_NLalpha)
        self.plotNonLinearityBeta(start=8, end=150, folder_path=base_directory3_NLbeta)

        return {
            'Repeatability alpha XY': repeatabilityAlphaXY * 1000,  # Convert to um
            'Repeatability beta XY': repeatabilityBetaXY * 1000,   # Convert to um
            'Datum alpha XY': datumAlpha * 1000,                   # Convert to um
            'Datum beta XY': datumBeta * 1000,                     # Convert to um
            'Mean backlash alpha': backlashAlpha,
            'Mean backlash beta': backlashBeta
        }

# Define the base directory where the files are located
# base_directory = "C:/Users/astrobots/Desktop/Astrobots Work/Thermal Test/TESTING/Positioner 24/5 degrees" # CHANGE MODULE HERE! Only by commenting and uncommenting!
# base_directory2 = "C:/Users/astrobots/Desktop/Astrobots Work/Thermal Test/TESTING/Positioner 24/5 degrees" # CHANGE MODULE HERE! Only by commenting and uncommenting!


# for filename in os.listdir(base_directory):
#     if filename.endswith(f'pos{POSID}'):  # CHANGE POSITIONER HERE! Check for files ending with 'pos__'
#         filepath = os.path.join(base_directory, filename)
        
#         # Load the data using the loadFromFile method from the posTest class
#         pos_data = posTest.loadFromFile(filepath)
#         print(pos_data)
        
#         # Check if the file was loaded successfully
#         if pos_data is None:
#             print(f"Skipping file {filename} due to loading issues.")
#             continue
        
#         # Call the getResults() method on the loaded posTest object
#         print(f"Running getResults() for file {filename}...")
#         pos_data.getResults()

#%%
# Create an empty DataFrame to store the results
df = pd.DataFrame()

for filename in os.listdir(base_directory):
    if filename.endswith(f'pos{POSID}'):
        filepath = os.path.join(base_directory, filename)
        
        pos_data = posTest.loadFromFile(filepath)
        if pos_data is None:
            print(f"Skipping file {filename} due to loading issues.")
            continue
        print(f"Running getResults() for file {filename}...")
        pos_data.getResults()
        results = posResults(filepath)
        file_results = results.get_results()
        # file_results = pos_data.getResults()
        
        # Convert dict to DataFrame
        file_results_df = pd.DataFrame([file_results])
        
        # Concatenate to df
        df = pd.concat([df, file_results_df], ignore_index=True)

#%%    
def calculate_and_append_stats(df):
    """
    Calculates the mean, max, and min for each parameter in a DataFrame,
    and appends them to the DataFrame with descriptive rows.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame: The DataFrame with appended mean, max, and min rows.
    """

    # Calculate statistics
    mean_values = df.mean()
    max_values = df.max()
    min_values = df.min()

    # Create empty rows (dtype float64)
    empty_row_mean = pd.Series([np.nan] * len(mean_values), index=mean_values.index, dtype='float64')
    empty_row_max = pd.Series([np.nan] * len(max_values), index=max_values.index, dtype='float64')
    empty_row_min = pd.Series([np.nan] * len(min_values), index=min_values.index, dtype='float64')

    # Create descriptive rows (dtype object)
    desc_row_mean = pd.Series(['Mean Value'] * len(mean_values), index=mean_values.index, dtype='object')
    desc_row_max = pd.Series(['Max Value'] * len(max_values), index=max_values.index, dtype='object')
    desc_row_min = pd.Series(['Min Value'] * len(min_values), index=min_values.index, dtype='object')

    # Combine all rows using pd.concat
    df = pd.concat([
        df,
        pd.DataFrame([empty_row_mean]),
        pd.DataFrame([desc_row_mean]),
        pd.DataFrame([mean_values]),
        pd.DataFrame([empty_row_max]),
        pd.DataFrame([desc_row_max]),
        pd.DataFrame([max_values]),
        pd.DataFrame([empty_row_min]),
        pd.DataFrame([desc_row_min]),
        pd.DataFrame([min_values])
    ], ignore_index=True)

    return df
# Calculate the mean for each parameter and append it to the DataFrame
#mean_values = df.mean()
#mean_values.name = 'Mean'

# Create an empty row with NaN values
#empty_row = pd.Series([np.nan] * len(mean_values), index=mean_values.index)
#empty_row2 = pd.Series(['Mean Value'] * len(mean_values), index=mean_values.index)

# Append the empty row and then the mean values
#df = df.append(empty_row, ignore_index=True)
#df = df.append(empty_row2, ignore_index=True)
#df = df.append(mean_values, ignore_index=True)

# Save the data to an Excel file
output_path = os.path.join(base_directory2, f'results_pos{POSID}.xlsx')
df = calculate_and_append_stats(df)
df.to_excel(output_path, index=False)

print(f"Data saved to {output_path}")

import os
import time
import numpy as np
import pickle
from datetime import datetime
import matplotlib.pyplot as plt
from miscmath import fit_circle
#from docx import Document

class posTest():
    def __init__(self, id = '19', module=1, stamp = '20200101_121212', temperature: float = None):
        self.id = id
        self.filename = (f'{stamp}_module_{module}_pos{id}')
        self.temperature = temperature #test temperature [°C]
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
        self.repeatabilityIterations = 10 # amount of iterations

        self.hardStopIterations =  10 # amount of iteration

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

        self.results_dir_path = None

    def saveToFile(self, posID: int = None, temp: float = None):

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

        filepath = os.path.join(results_dir_path, self.filename)

        try:
            with open(filepath, "wb") as f:
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
    
    def plotRepeatabilityBetaXY(self, folder_path = None):
        normalizedX = self.betaHighXs - np.mean(self.betaHighXs)
        normalizedX = normalizedX * 1000
        normalizedY = self.betaHighYs - np.mean(self.betaHighYs)
        normalizedY = normalizedY * 1000
        plt.scatter(normalizedX, normalizedY)
        plt.title('Repeatability beta XY of pos ' + str(self.id))
        plt.xlabel('x [um]')
        plt.ylabel('y [um]')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        filename = os.path.join(folder_path, f'{self.filename}_betaXY.png')
        plt.savefig(filename, bbox_inches = 'tight')
        plt.show()

    def plotRepeatabilityAlphaXY(self, folder_path = None):
        normalizedX = self.alphaHighXs - np.mean(self.alphaHighXs)
        normalizedX = normalizedX * 1000
        normalizedY = self.alphaHighYs - np.mean(self.alphaHighYs)
        normalizedY = normalizedY * 1000
        plt.scatter(normalizedX, normalizedY)
        plt.title('Repeatability alpha XY of pos ' + str(self.id))
        plt.xlabel('x [um]')
        plt.ylabel('y [um]')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        filename = os.path.join(folder_path, f'{self.filename}_betaXY.png')
        plt.savefig(filename, bbox_inches = 'tight')
        plt.show()

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
        normalizedXs = np.array(self.betaHighXs) - centerX
        normalizedYs = np.array(self.betaHighYs) - centerY
        anglesHigh = np.rad2deg(np.arctan2(normalizedXs, normalizedYs))
        normalizedXs = np.array(self.betaLowXs) - centerX
        normalizedYs = np.array(self.betaLowYs) - centerY
        anglesLow = np.rad2deg(np.arctan2(normalizedXs, normalizedYs))
        backlashes = anglesHigh - anglesLow
        return np.mean(backlashes)
    
    def nonLinearity(self):
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
    
    def plotNonLinearity(self):
        NL = self.nonLinearity()
        NL = NL - np.linspace(0, len(NL)-1, len(NL))
        plt.plot(NL)
        plt.title(f'Non linearity beta of pos {self.id}')
        plt.xlabel('Position at output[°]')
        plt.ylabel('Non Linearity [°] at output')
        filename = (f'images/{self.filename}alpha_NL.png')
        plt.savefig(filename, bbox_inches = 'tight')
        plt.show()
    
    def getResults(self):
        centerX, centerY, radius = self.getCircle()
        repeatabilityBetaXY = self.repeatabilityBetaXY()
        self.plotRepeatabilityBetaXY(folder_path = './Plots/Repeatability Beta')
        repeatabilityAlphaXY = self.repeatabilityAlphaXY()
        self.plotRepeatabilityAlphaXY(folder_path = './Plots/Repeatability Alpha')
        backlash = self.backlashBeta()
        # self.plotNonLinearity()

        print(self.id)
        print(f'Repeatability alpha XY is {repeatabilityAlphaXY*1000:.3f} um rms')
        print(f'Repeatability beta XY is {repeatabilityBetaXY*1000:.3f} um rms')
        print(f'Mean backlash is {backlash:.3f}°')

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
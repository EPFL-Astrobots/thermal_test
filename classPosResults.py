import os
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
# from docx import Document
from miscmath import fit_circle
## Make sure to search for: # CHANGE POSITIONER HERE! to be able to change the positioner!
## Make sure to search for: # CHANGE MODULE HERE! to be able to change the module!
from classPosTest import posTest


class posResults():
        
    def __init__(self, filepath):
        self.data = posTest.loadFromFile(filepath)
        self.posID = self.data.id
        self.temp = self.data.temperature
        self.centerX = 0.0
        self.centerY = 0.0
        self.centerX_beta = 0.0
        self.centerY_beta = 0.0
        self.alphaArm = 0.0
        self.betaArm = 0.0
        self.filename = os.path.basename(filepath)

        self.results_folder_path = self.path_to_results_folder()
        self.rep_alpha_path = os.joint(self.results_folder_path, "Plots/Repeatability Alpha")
        self.rep_beta_path = os.joint(self.results_folder_path, "Plots/Repeatability Alpha")
        self.NL_alpha_path = os.joint(self.results_folder_path, "Plots/NL Alpha")
        self.NL_beta_path = os.joint(self.results_folder_path, "Plots/NL Beta")

    def path_to_results_folder(self):

        script_dir = os.path.dirname(__file__)
        # results_dir_path = os.path.join(script_dir, 'Results_examples/')
        results_folder_path = os.path.join(script_dir, 'Results/')

        # Creates a subfolder corresponding to the project name in Results/
        if self.posID is not None: 
            results_folder_path = os.path.join(results_folder_path, f'Positioner {self.posID}' + '/')

        if self.temp is not None:
            results_folder_path = os.path.join(results_folder_path, f'{self.temp} degrees' + '/')

        # Checks if the directory exists, if not creates it
        if not os.path.isdir(results_folder_path):
            os.makedirs(results_folder_path)
        
        return results_folder_path

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

    def plotNonLinearityAlpha(self, start=None, end=None):
        NL = self.nonLinearityAlpha(start, end)
        NL = NL - np.linspace(0, len(NL)-1, len(NL))
        plt.plot(NL)
        plt.title(f'Nonlinearity alpha of pos {self.data.id}')
        plt.xlabel('Position at output [°]')
        plt.ylabel('Nonlinearity [°] at output')
        #plt.show()
        if not os.path.exists(self.NL_alpha_path):
            os.makedirs(self.NL_alpha_path)

        filename = os.path.join(self.NL_alpha_path, f'{self.filename}alpha_NL.png')
        plt.savefig(filename, bbox_inches='tight')
        plt.clf()


    def plotNonLinearityBeta(self, start=None, end=None):
        NL = self.nonLinearityBeta(start, end)
        NL = NL - np.linspace(0, len(NL)-1, len(NL))
        plt.plot(NL)
        plt.title(f'Nonlinearity beta of pos {self.data.id}')
        plt.xlabel('Position at output [°]')
        plt.ylabel('Nonlinearity [°] at output')
        #plt.show()

        if not os.path.exists(self.NL_beta_path):
            os.makedirs(self.NL_beta_path)

        filename = os.path.join(self.NL_beta_path, f'{self.filename}beta_NL.png')
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
        self.plotNonLinearityAlpha(start=8, end=350)
        self.plotNonLinearityBeta(start=8, end=150)

        return {
            'Repeatability alpha XY': repeatabilityAlphaXY * 1000,  # Convert to um
            'Repeatability beta XY': repeatabilityBetaXY * 1000,   # Convert to um
            'Datum alpha XY': datumAlpha * 1000,                   # Convert to um
            'Datum beta XY': datumBeta * 1000,                     # Convert to um
            'Mean backlash alpha': backlashAlpha,
            'Mean backlash beta': backlashBeta
        }
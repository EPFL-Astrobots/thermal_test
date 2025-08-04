#%% Snippet for left PC (Ctrl + Enter to run cell)
import os
import time
import numpy as np
import pickle
from datetime import datetime
import matplotlib.pyplot as plt
from miscmath import fit_circle
#from docx import Document


#%% hardware related stuff
import bench as bench


#%% configuration info for the test run
manufacturer = 'MPS'
#%%manufacturer = 'Maxon'
module = 1
posID = 24 # CHANGE POS NUMBER HERE
temperature = 20 # [°C] CHANGE TEMPERATURE HERE
now = datetime.now()
testStamp = now.strftime('%Y%m%d_%H%M%S')
comment = 'Test with chamber off'

class posTest():
    def __init__(self, id = '19', module=1, stamp = '20200101_121212', temperature: float = None, comment: str = None):
        self.id = id
        self.filename = (f'{stamp}_module_{module}_pos{id}')
        self.temperature = temperature #test temperature [°C]
        self.comment = comment 
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
    
    def plotRepeatabilityBetaXY(self):
        normalizedX = self.betaHighXs - np.mean(self.betaHighXs)
        normalizedX = normalizedX * 1000
        normalizedY = self.betaHighYs - np.mean(self.betaHighYs)
        normalizedY = normalizedY * 1000
        plt.scatter(normalizedX, normalizedY)
        plt.title('Repeatability beta XY of pos ' + str(self.id))
        plt.xlabel('x [um]')
        plt.ylabel('y [um]')
        filename = (f'images/{self.filename}_betaXY.png')
        plt.savefig(filename, bbox_inches = 'tight')
        plt.show()

    def plotRepeatabilityAlphaXY(self):
        normalizedX = self.alphaHighXs - np.mean(self.alphaHighXs)
        normalizedX = normalizedX * 1000
        normalizedY = self.alphaHighYs - np.mean(self.alphaHighYs)
        normalizedY = normalizedY * 1000
        plt.scatter(normalizedX, normalizedY)
        plt.title('Repeatability alpha XY of pos ' + str(self.id))
        plt.xlabel('x [um]')
        plt.ylabel('y [um]')
        filename = (f'images/{self.filename}_alphaXY.png')
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
        self.plotRepeatabilityBetaXY()
        repeatabilityAlphaXY = self.repeatabilityAlphaXY()
        self.plotRepeatabilityAlphaXY()
        backlash = self.backlashBeta()
        self.plotNonLinearity()

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


class posResults():
    def __init__(self, filename):
        self.data  = posTest.loadFromFile(filename)
        # self.data.scaleResults()
        
        self.centerX = 0.0
        self.centerY = 0.0
        self.alphaArm = 0.0
        self.betaArm = 0.0

    def calculateResults(self):
        x, y, radius = self.data.getAlphaArm()
        self.centerX = x
        self.centerY = y
        self.alphaArm = radius
        _, _, radius = self.data.getBetaArm()
        self.betaArm = radius

    def repeatabilityDatumAlphaXY(self):
        meanX = np.mean(np.array(self.data.datumAlphaXs))
        meanY = np.mean(np.array(self.data.datumAlphaYs))
        distanceX = np.array(self.data.datumAlphaXs) - meanX
        distanceY = np.array(self.data.datumAlphaYs) - meanY
        distances = np.sqrt(distanceX **2 + distanceY ** 2)
        return np.std(distances)
    
    def repeatabilityDatumAlpha(self):
        normalizedXs = np.array(self.data.datumAlphaXs) - self.centerX
        normalizedYs = np.array(self.data.datumAlphaYs) * (-1) - self.centerY * (-1)
        #rotate scara 90° CW
        Xs = normalizedYs
        Ys = normalizedXs * (-1)
        scara = Scara(self.alphaArm, self.betaArm)
        angles = scara.inverse_kinematics(Xs[0], Ys[0])
        print(angles)
        DatumAngles = np.rad2deg(np.arctan2(Xs[1:], Ys[1:]))
        return DatumAngles

    def repeatabilityDatumBetaXY(self):
        meanX = np.mean(np.array(self.data.datumBetaXs))
        meanY = np.mean(np.array(self.data.datumBetaYs))
        distanceX = np.array(self.data.datumBetaXs) - meanX
        distanceY = np.array(self.data.datumBetaYs) - meanY
        distances = np.sqrt(distanceX **2 + distanceY ** 2)
        return np.std(distances)

    def repeatabilityDatumBeta(self):
        normalizedXs = np.array(self.data.datumAlphaXs) - self.centerX
        normalizedYs = np.array(self.data.datumAlphaYs) * (-1) - self.centerY * (-1)
        #rotate scara 90° CW
        Xs = normalizedYs
        Ys = normalizedXs * (-1)

        scara = Scara(self.alphaArm, self.betaArm)
        angles = scara.inverse_kinematics(Xs[0], Ys[0])
        print(angles)

        DatumAngles = np.rad2deg(np.arctan2(normalizedXs[1:], normalizedYs[1:]))
        return DatumAngles
    
    def nonLinearityAlpha(self, start = None, end = None):
        centerX, centerY, radius = fit_circle(np.array(self.data.alphaNLXs[start:end]), np.array(self.data.alphaNLYs[start:end]))
        normalizedXs = np.array(self.data.alphaNLXs[start:end]) - centerX
        normalizedYs = np.array(self.data.alphaNLYs[start:end]) - centerY
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
    
    def nonLinearityBeta(self, start = None, end = None):
        centerX, centerY, radius = fit_circle(np.array(self.data.betaNLXs[start:end]), np.array(self.data.betaNLYs[start:end]))
        normalizedXs = np.array(self.data.betaNLXs[start:end]) - centerX
        normalizedYs = np.array(self.data.betaNLYs[start:end]) - centerY
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
    
    def plotNonLinearityAlpha(self, start = None, end = None):
        NL = self.nonLinearityAlpha(start, end)
        NL = NL - np.linspace(0, len(NL)-1, len(NL))
        plt.plot(NL)
        plt.title(f'Non linearity alpha of pos {self.data.id}')
        plt.xlabel('Position at output[°]')
        plt.ylabel('Non Linearity [°] at output')
        filename = (f'images/{self.data.filename}_alphaNL_.png')
        plt.savefig(filename, bbox_inches = 'tight')
        plt.show()

    def plotNonLinearityBeta(self,  start = None, end = None):
        NL = self.nonLinearityBeta(start, end)
        NL = NL - np.linspace(0, len(NL)-1, len(NL))
        plt.plot(NL)
        plt.title(f'Non linearity beta of pos {self.data.id}')
        plt.xlabel('Position at output[°]')
        plt.ylabel('Non Linearity [°] at output')
        filename = (f'images/{self.data.filename}_beta_NL_XY.png')
        plt.savefig(filename, bbox_inches = 'tight')
        plt.show()
    
    def backlashAlpha(self):
        normalizedXs = np.array(self.data.alphaHighXs) - self.centerX
        normalizedYs = np.array(self.data.alphaHighYs) - self.centerY
        anglesHigh = np.rad2deg(np.arctan2(normalizedXs, normalizedYs))
        normalizedXs = np.array(self.data.alphaLowXs) - self.centerX
        normalizedYs = np.array(self.data.alphaLowYs) - self.centerY
        anglesLow = np.rad2deg(np.arctan2(normalizedXs, normalizedYs))
        backlashes = anglesHigh - anglesLow
        return np.mean(backlashes)
    
    def generateReport(self):
        self.calculateResults()
        print (f'{self.data.filename}')
        repeatabilityBetaXY = self.data.repeatabilityBetaXY()
        self.data.plotRepeatabilityBetaXY()
        repeatabilityAlphaXY = self.data.repeatabilityAlphaXY()
        self.data.plotRepeatabilityAlphaXY()
        backlash = self.backlashAlpha()
        self.plotNonLinearityAlpha(20, -20)
        self.plotNonLinearityBeta(20, -20)
        datumAlpha = self.repeatabilityDatumAlphaXY()
        datumBeta = self.repeatabilityDatumBetaXY()

        print(self.data.id)
        print(f'Repeatability alpha XY is {repeatabilityAlphaXY*1000:.3f} um rms')
        print(f'Repeatability beta XY is {repeatabilityBetaXY*1000:.3f} um rms')
        print(f'Repeatability datum alpha XY is {datumAlpha*1000:.3f} um rms')
        print(f'Repeatability datum beta XY is {datumBeta*1000:.3f} um rms')
        print(f'Mean backlash is {backlash:.3f}°')


#%%
def perform_test():
    # %% Initialize communication (run cell once is enough)
    cam, allpos, pos21, pos22, pos23, pos24, pos25, pos26 = bench.bench_init()

    pos_dict = {"21": pos21, "22": pos22, "23": pos23, "24": pos24, "25": pos25, "26": pos26}
    
    pos = pos_dict[f'{posID}']
    print(f"pos set to pos{posID}")

    if temperature is not None:

        test = posTest(posID, module, testStamp, temperature, comment)
    
    else:

        test = posTest(posID, module, testStamp)
#%%
    # Early check for NaNs in positions given by camera
    [xtest, ytest] = cam.getCentroid()
    if np.any(np.isnan(np.array([xtest, ytest]))):
        raise("Camera returns at least one Nan; stopping test")

    #%% Move around positioner
    pos.set_current(60, 60)
    # make sure we are at hardstops
    print('going to hardstops')
    waitTime, waitTime2 = pos.goto_relative(-200, -180)
    time.sleep(max(waitTime, waitTime2) + 0.1)
    waitTime, waitTime2 = pos.goto_relative(-200, -90)
    time.sleep(max(waitTime, waitTime2) + 0.1)

    pos.set_position(0, 0)

    #%% beta circles detect center and circle
    for posAlpha in test.alphaPos:
        print(f'testing beta at alpha pos {posAlpha}')
        waitTime, waitTime2 = pos.goto_absolute(posAlpha, 0)
        time.sleep(max(waitTime, waitTime2) + 0.1)
        betaXs = []
        betaYs = []

        for target in test.betaPos:
            print(f'testing beta at pos {target}')
            waitTime, waitTime2 = pos.goto_absolute(posAlpha, target)
            time.sleep(max(waitTime, waitTime2) + 0.1)
            x, y = cam.getCentroid()
            print(f"centroid at {x}, {y}")
            betaXs.append(x)
            betaYs.append(y)
        
        test.circleBetaXs.append(betaXs)
        test.circleBetaYs.append(betaYs)
        # centerX, centerY, radius = fit_circle(np.asarray(test.circleBetaXs), np.asarray(test.circleBetaYs))

    waitTime, waitTime2 = pos.goto_absolute(0,0)
    time.sleep(max(waitTime, waitTime2) + 0.1)

    #%% alpha circles detect center and circle
    for target in test.alphaPos:
        waitTime, waitTime2 = pos.goto_absolute(target, 180)
        time.sleep(max(waitTime, waitTime2) + 0.1)
        x, y = cam.getCentroid()
        test.circleAlphaXs.append(x)
        test.circleAlphaYs.append(y)
    
    waitTime, waitTime2 = pos.goto_absolute(0,0)
    time.sleep(max(waitTime, waitTime2) + 0.1)

    #%% testing alpha hard stops
    print("Testing alpha hard stops")
    for i in range(test.hardStopIterations):
        waitTime, waitTime2 = pos.goto_absolute(20, 180)
        time.sleep(max(waitTime, waitTime2) + 0.1)
        waitTime, waitTime2 = pos.goto_relative(-30, 0)
        time.sleep(max(waitTime, waitTime2) + 0.1)

        x, y = cam.getCentroid()
        test.datumAlphaXs.append(x)
        test.datumAlphaYs.append(y)        

    waitTime, waitTime2 = pos.goto_absolute(0,0)
    time.sleep(max(waitTime, waitTime2) + 0.1)

    #%% testing beta hard stops
    print("Testing beta hard stops")
    for i in range(test.hardStopIterations):
        waitTime, waitTime2 = pos.goto_absolute(0, 20)
        time.sleep(max(waitTime, waitTime2) + 0.1)
        waitTime, waitTime2 = pos.goto_relative(0, -30)
        time.sleep(max(waitTime, waitTime2) + 0.1)

        x, y = cam.getCentroid()
        test.datumBetaXs.append(x)
        test.datumBetaYs.append(y)        

    waitTime, waitTime2 = pos.goto_absolute(0,0)
    time.sleep(max(waitTime, waitTime2) + 0.1)

    #%% repeatability testing
    print("Testing beta repeatability")
    for i in range(test.repeatabilityIterations):
        print(f'Repeatability: iteration beta {i} out of {test.repeatabilityIterations} ')
        waitTime, waitTime2 = pos.goto_absolute(0, test.testPosition + test.deltaMove)
        time.sleep(max(waitTime, waitTime2) + 0.1)
        waitTime, waitTime2 = pos.goto_absolute(0, test.testPosition)
        time.sleep(max(waitTime, waitTime2) + 0.1)
        x, y = cam.getCentroid()
        test.betaHighXs.append(x)
        test.betaHighYs.append(y)
        waitTime, waitTime2 = pos.goto_absolute(0, test.testPosition - test.deltaMove)
        time.sleep(max(waitTime, waitTime2) + 0.1)
        waitTime, waitTime2 = pos.goto_absolute(0, test.testPosition)
        time.sleep(max(waitTime, waitTime2) + 0.1)
        x, y = cam.getCentroid()
        test.betaLowXs.append(x)
        test.betaLowYs.append(y)

    waitA, waitB = pos.goto_absolute(0,0)
    wait = max(waitA, waitB)
    time.sleep(wait + 0.1)

    print("Testing alpha repeatability")
    for i in range(test.repeatabilityIterations):
        print(f'Repeatability: iteration alpha {i} out of {test.repeatabilityIterations} ')
        waitTime, waitTime2 = pos.goto_absolute(test.testPosition + test.deltaMove, 180)
        time.sleep(max(waitTime, waitTime2) + 0.1)
        waitTime, waitTime2 = pos.goto_absolute(test.testPosition, 180)
        time.sleep(max(waitTime, waitTime2) + 0.1)
        x, y = cam.getCentroid()
        test.alphaHighXs.append(x)
        test.alphaHighYs.append(y)
        waitTime, waitTime2 = pos.goto_absolute(test.testPosition - test.deltaMove, 180)
        time.sleep(max(waitTime, waitTime2) + 0.1)
        waitTime, waitTime2 = pos.goto_absolute(test.testPosition, 180)
        time.sleep(max(waitTime, waitTime2) + 0.1)
        x, y = cam.getCentroid()
        test.alphaLowXs.append(x)
        test.alphaLowYs.append(y)

    waitA, waitB = pos.goto_absolute(0,0)
    wait = max(waitA, waitB)
    time.sleep(wait + 0.1)

    for i in range(test.alphaNLRange):
        print(f'NL alpha  at angle {i}')
        waitTime, waitTime2 = pos.goto_absolute(i, 180)
        time.sleep(max(waitTime, waitTime2) + 0.1)
        x, y = cam.getCentroid()
        test.alphaNLXs.append(x)
        test.alphaNLYs.append(y)

    waitA, waitB = pos.goto_absolute(0,0)
    wait = max(waitA, waitB)
    time.sleep(wait + 0.1)

    for i in range(test.betaNLRange):
        print(f'NL beta  at angle {i}')
        waitTime, waitTime2 = pos.goto_absolute(0, i)
        time.sleep(max(waitTime, waitTime2) + 0.1)
        x, y = cam.getCentroid()
        test.betaNLXs.append(x)
        test.betaNLYs.append(y)

    test.saveToFile(posID, temperature)


if __name__ == '__main__':
    perform_test()

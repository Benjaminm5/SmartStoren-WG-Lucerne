import RPi.GPIO as GPIO
import time
import sys

direction = 17
step = 4
relay = 27

rpm = float(25)
rpmFast = float(60)
stepsperrotation = float(200)
rps = float(0)      #rotations per second
sps = float(0)      #steps per second
dps = float(0)      #delay per half step (in seconds)
delays = float(0)   #delay per half step (in seconds)
delaysFast = float(0)
transmission = float(5.18) #Getriebeubersetzung
spm = 60            #seconds per minute

readLastDirection = " "
readLastOpening = " "

fileNameDirection = "/home/pi/stepper/lastDirection"
fileNameOpening = "/home/pi/stepper/opening"

operation = "NONE"

def whichOperation():
    global operation
    input = sys.argv[1]
    operation = input
    print("Operation:")
    print(operation)

def calculateDelay(rotationsperminute):
    global delays
    global delaysFast
    global rps
    global sps
    global dps

    rps = float((rotationsperminute * transmission) / spm)
    sps = float(rps * stepsperrotation)
    dps = float(1) / (float(2) * sps)       #for miliseconds 1000000 anstatt 1

    if rotationsperminute == rpm:
        delays = dps
    elif rotationsperminute == rpmFast:
        delaysFast = dps

def readFile(file):
    global readLastOpening
    global readLastDirection

    fileName = file + ".txt"
    f = open(fileName, 'r')
    data = f.readlines()

    if file == fileNameOpening:
        readLastOpening = data[0]
        print("LastOpening:")
        print(readLastOpening)
    else:
        readLastDirection = data[0]
        print("LastDirection:")
        print(readLastDirection)

    f.close()

def calculateMaxSteps(maxRot):
    resultAsInt = int(maxRot * transmission * stepsperrotation)
    return resultAsInt

def safeToTextfile(file, value):
    fileName = file + ".txt"
    data = value

    with open(fileName, 'wb') as saveFile:
        saveFile.write(data)

def moveStepper(moveDirection, steps, pause):
    #moveDirection: 1=UP, 0=DOWN
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(0)
    GPIO.setup(direction, GPIO.OUT)
    GPIO.setup(step, GPIO.OUT)
    GPIO.setup(relay, GPIO.OUT)
    GPIO.output(relay, GPIO.LOW)
    time.sleep(0.2)
    GPIO.output(direction, moveDirection)

    for i in range(0, steps):
      GPIO.output(step, 1)
      time.sleep(pause)
      GPIO.output(step, 0)
      time.sleep(pause)

    GPIO.output(direction, 0)
    GPIO.output(step, 0)
    GPIO.output(relay, GPIO.HIGH)
    #GPIO.output(relay, GPIO.HIGH)
    #GPIO.cleanup()

def moveUp():
    print("up")

    maxSteps = (calculateMaxSteps(float(24))) #0.2 = rotations
    moveStepper(0, maxSteps, delays)

    safeToTextfile(fileNameDirection, "UP")

def moveDown():
    print("down")

    maxSteps = (calculateMaxSteps(float(24))) #0.2 = rotations
    moveStepper(1, maxSteps, delaysFast)

    safeToTextfile(fileNameDirection, "DOWN")

def middleFromDown():
    print("to middle from down")

    maxSteps = (calculateMaxSteps(float(1.1))) #0.2 = rotations
    moveStepper(0, maxSteps, delays)

    safeToTextfile(fileNameOpening, "MIDDLE")

def closeFromMiddle():
    print("to close from middle")

    maxSteps = (calculateMaxSteps(float(1.1))) #0.2 = rotations
    moveStepper(1, maxSteps, delays)

    safeToTextfile(fileNameOpening, "CLOSED")

def move():

    if operation == "dark":
        if readLastDirection == "UP":
            moveDown()
        elif readLastDirection == "DOWN":
            if readLastOpening == "MIDDLE":
                closeFromMiddle()
    elif operation == "light":
        if readLastDirection == "UP":
            moveDown()
            time.sleep(1)
            middleFromDown()
        elif readLastDirection == "DOWN":
            if readLastOpening == "CLOSED":
                middleFromDown()
    elif operation == "up":
        if readLastDirection == "DOWN":
            if readLastOpening == "MIDDLE":
                closeFromMiddle()
                time.sleep(1)
                moveUp()
            elif readLastOpening == "CLOSED":
                moveUp()
    elif operation == "down":
        if readLastDirection == "UP":
            moveDown()
        elif readLastDirection == "DOWN":
            if readLastOpening == "MIDDLE":
                closeFromMiddle()

calculateDelay(rpm)
calculateDelay(rpmFast)
whichOperation()

readFile(fileNameDirection)
readFile(fileNameOpening)

move()

sys.exit()

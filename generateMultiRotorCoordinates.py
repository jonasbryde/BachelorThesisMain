import numpy as np

def generateMultiRotorCoordinates(centers, sector, turbineDiameter, turbineTipClearence, Collumns, rows):

    Heights = []
    DistanceTurbinesSameRow = turbineDiameter + turbineTipClearence
    DistanceTurbineNeighbouringRow = (turbineDiameter + turbineTipClearence) / 2

    #define the wind direction sector from 0 to 11
    angle = 360 / 12 * sector + 15
    angleFromZero = np.radians(angle)

    xCoordinates = list()
    yCoordinates = list()
    zCoordinates = list()

    #initiate heights in multirotor
    for i in range(rows):
        Heights.append(40 + i * np.sin(np.pi/3)*(turbineDiameter + turbineTipClearence))


    #For every center loop through the following code 
    for center in centers:
        #loop through rows
        for i in range(0,len(Heights),1):
            #check if row is even or odd
            if i % 2 == 0:
                #Define a list of the x,y and z coordinates 
                x = np.linspace((center[0] - DistanceTurbinesSameRow*(Collumns - 1)/2*np.cos(2*np.pi-angleFromZero)),(center[0] + DistanceTurbinesSameRow*(Collumns - 1)/2*np.cos(2*np.pi-angleFromZero)),(Collumns))
                y = np.linspace((center[1] - DistanceTurbinesSameRow*(Collumns - 1)/2*np.sin(2*np.pi-angleFromZero)),(center[1] + DistanceTurbinesSameRow*(Collumns - 1)/2*np.sin(2*np.pi-angleFromZero)),(Collumns))
                for coordinate in x:
                    xCoordinates.append(round(coordinate,0))
                for coordinate in y:
                    yCoordinates.append(round(coordinate,0))
                    zCoordinates.append(Heights[i])
            elif i % 2 == 1:
                #Define a list of the x,y and z coordinates 
                x = np.linspace((center[0] - DistanceTurbinesSameRow*(Collumns - 1)/2*np.cos(2*np.pi-angleFromZero) + DistanceTurbineNeighbouringRow*np.cos(2*np.pi-angleFromZero)),(center[0] + DistanceTurbinesSameRow*(Collumns - 1)/2*np.cos(2*np.pi-angleFromZero) + DistanceTurbineNeighbouringRow*np.cos(2*np.pi-angleFromZero)),(Collumns))
                y = np.linspace((center[1] - DistanceTurbinesSameRow*(Collumns - 1)/2*np.sin(2*np.pi-angleFromZero) + DistanceTurbineNeighbouringRow*np.sin(2*np.pi-angleFromZero)),(center[1] + DistanceTurbinesSameRow*(Collumns - 1)/2*np.sin(2*np.pi-angleFromZero) + DistanceTurbineNeighbouringRow*np.sin(2*np.pi-angleFromZero)),(Collumns))
                for coordinate in x:
                    xCoordinates.append(round(coordinate,0))
                for coordinate in y:
                    yCoordinates.append(round(coordinate,0))
                    zCoordinates.append(Heights[i])
    return {"xCoordinates": xCoordinates, "yCoordinates": yCoordinates, "zCoordinates": zCoordinates}
      

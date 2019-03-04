import src.yoloAnnotator

myFM=src.yoloAnnotator.FileManager()
myYA=src.yoloAnnotator.GUI(myFM)
myYA.mainLoop()
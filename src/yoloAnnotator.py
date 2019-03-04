try:
    import cv2
except ImportError:
    print("This program requires opencv-python to be installed")
    print("Install the module by: ")
    print("python -m pip install opencv-python")
    input("Press any key to close")

class TrackBar:
    def __init__(self,trackBarName,windowName,trackBarRange,changeResponder):
        self.trackBarName=trackBarName
        self.windowName=windowName
        self.trackBarRange=trackBarRange
        self.changeResponder=changeResponder
        cv2.createTrackbar(trackBarName,windowName,
                       trackBarRange[0],trackBarRange[1],self.__trackBarListener)
        
    def __trackBarListener(self,position):
        self.changeResponder(self.trackBarName,position)
        
    def progressTrackBar(self):
        pos=cv2.getTrackbarPos(self.trackBarName,self.windowName)
        if(pos+1<=self.trackBarRange[1]):
            cv2.setTrackbarPos(self.trackBarName, self.windowName, pos+1)
        else:
            cv2.setTrackbarPos(self.trackBarName, self.windowName, 0)
            
    def revertTrackBar(self):
        pos=cv2.getTrackbarPos(self.trackBarName,self.windowName)
        if(pos-1>=self.trackBarRange[0]):
            cv2.setTrackbarPos(self.trackBarName, self.windowName, pos-1)
        else:
            cv2.setTrackbarPos(self.trackBarName, self.windowName,self.trackBarRange[1]) 

class GUI:
                
    def __init__(self,fileManager):
        self.mousePosition=(0,0)
        self.fileManager=fileManager
        self.currentLabelIndex=0
        self.labels=self.fileManager.getLabelsList()
        #generate random number
        numberOfLabel=len(self.labels)
        self.labelsColor=[[i*255/numberOfLabel,
                           abs(125-i*255/numberOfLabel)
                           ,abs(255-i*255/numberOfLabel)]for i in range(numberOfLabel)]
        self.objectParams={"pose":" ","truncated":str(0),"difficult":str(0)}
        self.__displayNewImage()
        #makeWindow
        cv2.namedWindow("yolo annotator")      
    
        #set mouse listener
        cv2.setMouseCallback('yolo annotator',self.__mouseListener)
        
        #make image track bar
        numberOfImage=fileManager.getNumberOfImages()
        self.imageTrackBar=TrackBar("Image","yolo annotator",(0,numberOfImage-1),self.__trackChangeResponder)
        #make label track bar if there are more than one labels

        if(numberOfLabel>1):
            self.labelTrackBar=TrackBar("Label","yolo annotator",(0,numberOfLabel-1),self.__trackChangeResponder)
    
    #deals with any change in track bar
    def __trackChangeResponder(self,trackBarName,position):
        #when Image track bar is changed
        if(trackBarName=="Image"):
            self.fileManager.writeNewAnnotationFile(self.size,self.listOfBoundingBoxes)
            self.fileManager.selectImageByIndex(position)
            self.__displayNewImage()
        #deals with label change
        elif(trackBarName=="Label"):
            self.currentLabelIndex=position
            
    def __mouseListener(self,event,x,y,flags,param):
        self.mousePosition=(x,y)
        #onClick
        if event == cv2.EVENT_LBUTTONDOWN:
            if(self.drawingBB==False):
                self.firstClick = (x,y)
            else:
                self.secondClick = (x,y)
                boundingBox= self.__makeBoundingBoxFromMouseInput()
                #append to list of bb
                self.listOfBoundingBoxes.append(boundingBox)
            self.drawingBB = not(self.drawingBB)

    def __drawCrossLine(self):
        x=self.mousePosition[0]
        y=self.mousePosition[1]
        cv2.line(self.editedImage,(0,y),(self.size["x"],y), (255,5,0))
        cv2.line(self.editedImage,(x,0),(x,self.size["y"]), (255,5,0))

    #make a new bounding box from the mouse input
    def __makeBoundingBoxFromMouseInput(self):
        xs=[self.firstClick[0],self.secondClick[0]]
        ys=[self.firstClick[1],self.secondClick[1]]
        objectName=self.labels[self.currentLabelIndex]
        boundingBox={"name":objectName,"xmin":min(xs),"xmax":max(xs),"ymin":min(ys),"ymax":max(ys)}
        boundingBox={**boundingBox,**self.objectParams}
        return boundingBox
    
    #takes two corners as input
    def __drawSingleBoundingBox(self,corner1,corner2,name):
        #setColor
        if(name in self.labels):
            color=self.labelsColor[self.labels.index(name)]
        else:
            color=[0,255,0]
        #find lines to draw
        xs=[int(corner1[0]),int(corner2[0])]
        ys=[int(corner1[1]),int(corner2[1])]
        linesToPlot=[((xs[0],ys[0]),(xs[1],ys[0])),
                     ((xs[1],ys[0]),(xs[1],ys[1])),
                     ((xs[0],ys[1]),(xs[1],ys[1])),
                     ((xs[0],ys[0]),(xs[0],ys[1])),
                     ]
        #draw lines
        for points in linesToPlot:
            cv2.line(self.editedImage,points[0],points[1], color)
        #draw object name
        font = cv2.FONT_HERSHEY_COMPLEX
        bottomLeftCornerOfText = (min(xs),min(ys))
        fontScale = 1
        lineType  = 2
        cv2.putText(self.editedImage,str(name), bottomLeftCornerOfText, font, 
        fontScale, color, lineType)
            
    def __drawAllBoundingBoxes(self):
        for boundingBox in self.listOfBoundingBoxes:
            self.__drawSingleBoundingBox([boundingBox["xmin"],boundingBox["ymin"]],
                                   [boundingBox["xmax"],boundingBox["ymax"]],boundingBox["name"])
        
    def __displayNewImage(self):
        self.firstClick=(0,0)
        self.secondClick=(0,0)
        self.drawingBB=False
        self.listOfBoundingBoxes=self.fileManager.getObjectList()
        self.rawImage=cv2.imread("img/"+self.fileManager.getImgToDisplay())
        self.editedImage=self.rawImage.copy()
        self.size={"x":self.rawImage.shape[1],"y":self.rawImage.shape[0],"depth":self.rawImage.shape[2]}
    
    #deals with key inputs
    def __keyInPutManager(self,keyInput):
        #quit the program
        if keyInput & 0xFF == ord("q"):
            self.fileManager.writeNewAnnotationFile(self.size,self.listOfBoundingBoxes)
            print("quit")
            self.continueLoop=False
        #to next image
        elif keyInput & 0xFF == ord("d"):
            #update track bar position
            #this method deals with interacting with fileManager,display image and saving annotation file
            self.imageTrackBar.progressTrackBar()

        #to previous image
        elif keyInput & 0xFF == ord("a"):
            #update track bar position
            #this method deals with interacting with fileManager,display image and saving annotation file
            #update track bar position
            self.imageTrackBar.revertTrackBar()
        #delete a bounding box if there is any
        elif keyInput & 0xFF == ord("k"):
            if(len(self.listOfBoundingBoxes)>0):
                del self.listOfBoundingBoxes[-1]
        
                
    def __newFrameDrawer(self):
        #clearRawImage
        self.editedImage=self.rawImage.copy()
        #drawcrossLine
        self.__drawCrossLine()
        #drawBoundingBoxs
        self.__drawAllBoundingBoxes()
        #display currently drawing bounding box
        if(self.drawingBB):
            objectName=self.labels[self.currentLabelIndex]
            self.__drawSingleBoundingBox(self.firstClick,self.mousePosition,objectName)
        cv2.imshow("yolo annotator",self.editedImage)
    
    def mainLoop(self):
        self.continueLoop=True
        while self.continueLoop:
            self.__newFrameDrawer()
            
            keyInput=cv2.waitKey(25)
            self.__keyInPutManager(keyInput)
        cv2.destroyAllWindows()
        
####CLASS MANAGER
import os
import re
import xml.etree.ElementTree as elementTree
#minimal implementation of the Document Object Model interface
import xml.dom.minidom as minidom
class FileManager:
    def __init__(self):        
        self.cwd=os.getcwd()
        #find where cwd is
        if(os.getcwd()[-len("\\yoloAnnotator"):]!="\\yoloAnnotator"):
            self.__printErrorMsg("the currently working directory needs to be set at yoloAnnotator directory")            
        #get image names
        fileFormatToAccept=re.compile(r".*([j,J][p,P][g,G]|[j,J][p,P][e,E][g,G]|[p,P][n,N][g,G])$")
        self.images=[imgList for imgList in self.__listDir("img") if fileFormatToAccept.match(imgList)]
        if len(self.images)==0:
            self.__printErrorMsg("requires at least one jpeg or png image in yoloAnnotator/img directory")

        #getAnnotations
        self.__getAnnotationsList()
        self.currentImagePosition=0
        
    def __listDir(self,path):
        #e.g.Path: img
        try:
            imageList=os.listdir(path)
        except FileNotFoundError:
            self.__printErrorMsg("requires directory yoloAnnotator/"+path)
        finally:
            return imageList

    def __getAnnotationsList(self):
        #get annotation names
        fileFormatToAccept=re.compile(r".*[x,X][m,M][l,L]$")
        self.annotations=[imgList for imgList in self.__listDir("annotations") if fileFormatToAccept.match(imgList)]
    
    def __printErrorMsg(self,errorMsg):
        print(errorMsg)
        input("Press any key to close")
        exit(1)
    
    
    def getNumberOfImages(self):
        return len(self.images)
    
    def getImgToDisplay(self):
        return self.images[self.currentImagePosition]
    
    def selectImageByIndex(self,index):
        self.currentImagePosition=index
        
    #reads object parameter from annotation file and returns it
    def getObjectList(self):
        objectParamList=[]
        #check if annotation file exist
        xmlNameToMatch=re.compile(self.getImgToDisplay()+".[x,X][m,M][l,L]")
        xmlFileName=list(filter(xmlNameToMatch.match,self.annotations))
        if(len(xmlFileName)!=0):
            xmlFileName=xmlFileName[0]
            #annotationFileExists
            thisElementTree=elementTree.parse("annotations/"+xmlFileName)
            #parseObjects
            thisObjects=thisElementTree.findall("object")
            for anObject in thisObjects:
               name=anObject.find("name").text
               pose=anObject.find("pose").text
               truncated=anObject.find("truncated").text
               difficult=anObject.find("difficult").text
               
               bndbox=anObject.find("bndbox")
               xmin=bndbox.find("xmin").text
               ymin=bndbox.find("ymin").text
               xmax=bndbox.find("xmax").text
               ymax=bndbox.find("ymax").text
               objectParam={
                       "name":name,
                       "pose":pose,
                       "truncated":truncated,
                       "difficult":difficult,
                       "xmin":xmin,
                       "ymin":ymin,
                       "xmax":xmax,
                       "ymax":ymax}
               objectParamList.append(objectParam)
        return objectParamList
        
    #size e.g. {"x":100,"y":100,"depth"3}
    """objectElementList e.g. 
    [{"name":"a",
    "pose":" ",
    "truncated":"0",
    "difficult":"0",
    "xmin":"10",
	"ymin""10",
	"xmax""20",
    "ymax":"20"}]
    """
    def writeNewAnnotationFile(self,size,objectElementList):    
        #formingXML
        annotationSubXML=[]
        #annotation
        annotationXML=elementTree.Element("annotation")
        #folder
        folderElement=elementTree.Element("folder")
        folderElement.text="yoloAnnotator/img"
        #filename
        filenameElement=elementTree.Element("filename")
        filenameElement.text=self.getImgToDisplay()
        #size
        sizeElement=elementTree.Element("size")
        elementTree.SubElement(sizeElement,"width").text=str(size["x"])
        elementTree.SubElement(sizeElement,"height").text=str(size["y"])
        elementTree.SubElement(sizeElement,"depth").text=str(size["depth"])
        annotationSubXML=[folderElement,filenameElement,sizeElement]
        #object
        for objectParam in objectElementList:
            objectElement=elementTree.Element("object")
            elementTree.SubElement(objectElement,"name").text=objectParam["name"]
            elementTree.SubElement(objectElement,"pose").text=objectParam["pose"]
            elementTree.SubElement(objectElement,"truncated").text=str(objectParam["truncated"])
            elementTree.SubElement(objectElement,"difficult").text=str(objectParam["difficult"])
            boundBoxElement=elementTree.SubElement(objectElement,"bndbox")
            elementTree.SubElement(boundBoxElement,"xmin").text=str(objectParam["xmin"])
            elementTree.SubElement(boundBoxElement,"ymin").text=str(objectParam["ymin"])
            elementTree.SubElement(boundBoxElement,"xmax").text=str(objectParam["xmax"])
            elementTree.SubElement(boundBoxElement,"ymax").text=str(objectParam["ymax"])
            annotationSubXML.append(objectElement)
        
        for element in annotationSubXML:
            annotationXML.append(element)
        #turn element tree element into string
        xmlString=elementTree.tostring(annotationXML).decode()
        #make string pretty (add indentation)
        xmlString=minidom.parseString(xmlString).toprettyxml()
        print("Saved an annotation file")
        #save it to file
        try:
           fileHandle = open("annotations/"+self.getImgToDisplay()+".xml","w")
           fileHandle.write(xmlString)
           fileHandle.close()
        except:
           self.__printErrorMsg("could not save "+self.getImgToDisplay()+".xml file")
        #load all annotations file again incase you saved a new file   
        self.__getAnnotationsList()
      
    def getLabelsList(self):
        try:
            fileHandle = open("labels.txt","r")
            lableText=fileHandle.read()
            fileHandle.close()
        except:
            self.__printErrorMsg("could not read labels.txt file")
        listOfLables=lableText.split("\n")
        #deleate all empty balue
        while "" in listOfLables:
            listOfLables.remove("")
        if(len(listOfLables)<=0):
            self.__printErrorMsg("you must add a label in labels.txt file")
        return listOfLables
    
if __name__=="__main__":
    print("This program is not designed to be executed as a main program")
    print("Please execute the main.py file in the prgram directory")
    input("Press any key to close")
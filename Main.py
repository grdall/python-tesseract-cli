import sys
import os
from myutil.Util import *
from myutil.DateTimeObject import DateTimeObject
from myutil.FilePathObject import FilePathObject
import pytesseract
import cv2
import base64
from dotenv import load_dotenv
load_dotenv()
from Util import Util1

apiKeyHeaderName = "apiKey"
apiKey = os.environ.get("API_KEY")
apiBaseUrl = "https://grd-tesseract-api.herokuapp.com/tesseract"
apiLocalBaseUrl = "http://localhost:8080/tesseract"
batchOutputDir = "text" # Relative or absolute path. Note that the parent of this directory must exist, but the directory itself will be made if there are none.
apiMaxBytes = 512000
pageSegMode = 6
engineMode = 3

os.system("") # Needed to "trigger" coloured text
helpFlags = ["-help", "-h"]
testFlags = ["-test", "-t"]
tessScanFlags = ["-scan", "-s"]
localApiSwitches = ["local", "l"]
apiRawSwitches = ["raw", "r"]
apiCleanedSwitches = ["cleaned", "c"]
localTesseractSwitches = ["program", "exe"]
scaleImageForApiSwitches = ["scale", "s"]
tessLangFlags = ["-tesseractlanguage", "-tesslang", "-tl"]
tessLang = ["english (\"eng\")", 
"norwegian (\"nor\")", 
"swedish (\"swe\")", 
"danish (\"dan\")", 
"german (\"deu\")", 
"french (\"fra\")", 
"spanish (\"spa\")", 
"italian (\"ita\")", 
"russian (\"rus\")", 
"polish (\"pol\")", 
"japanese (\"jpn\")",
"latin (\"lat\")",  
"math equation (\"equ\")"] # https://github.com/tesseract-ocr/tessdoc/blob/master/Data-Files-in-different-versions.md
pytesseract.pytesseract.tesseract_cmd = r"c:\\Program Files\\Tesseract-OCR\\tesseract.exe"

class Main:
    def main():
        argC = len(sys.argv)
        argV = sys.argv
        argIndex = 1

        if(argC < 2): # Default
            Main.PrintHelp()
            response = requestCall(apiBaseUrl, "/health", HttpVerb.GET, headers = { apiKeyHeaderName: apiKey })
            print("API Uptime: " + response.json()["data"]["message"])

        while argIndex < argC:
            arg = sys.argv[argIndex].lower()

            if(arg in helpFlags):
                Main.PrintHelp()

            elif(arg in testFlags):
                args = extractArgs(argIndex, argV)
                print("test")
                # pathSplit = os.path.splitext(os.path.basename(args[0]))

                # outFilename = pathSplit[0] + getDatetime(True) + ".txt"
                # print(f"Scanning directory, writing to file {outFilename}")
                # print(pathSplit)
                # print(os.listdir(args[0]))

                # outFile = open("test.txt", "w")
                # outFile.write("working")
                # outFile.close()

                obj = FilePathObject(args[0])
                print(vars(obj))

                quit()

            elif(arg in tessScanFlags):
                args = Util1.ExtractArgs(argIndex, argV)
                print(args)

                sourceInput = args[0]
                sourceIsDir = False
                files = []
                if(not os.path.exists(sourceInput)):
                    print(sourceInput)
                    print("File or directory does not exist.")
                    argIndex += len(args)
                    continue
                elif(os.path.isfile(sourceInput)):
                    files.append(FilePathObject(sourceInput))
                else:
                    sourceIsDir = True
                    for path in os.listdir(sourceInput):
                        if(path.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".tif", ".tiff"))):
                            files.append(FilePathObject(os.path.join(sourceInput, path)))
                        else:
                            print(f"File {path} was not an image, will not process.")

                # Dumb variables can't be global for some unknown reason, works fine with apiMaxBytes
                pageSegMode = 6
                engineMode = 3

                if(len(args) > 2 and isNumber(args[2], True)):
                    pageSegMode = args[2]
                if(len(args) > 3 and isNumber(args[3], True)):
                    engineMode = args[3]

                for fileObject in files:
                    imageFile = cv2.imread(fileObject.fullPath)
                    print(f"Scanning file {fileObject.filename}")

                    if(arrayContains(args, localTesseractSwitches)):
                        text = pytesseract.image_to_string(imageFile, lang=args[1])
                        print(text)
                        # TODO save text for array of images

                        argIndex += len(args)
                        continue

                    # imageFile = cv2.set
                    imageFile = cv2.cvtColor(imageFile, cv2.COLOR_BGR2GRAY)

                    if(arrayContains(args, scaleImageForApiSwitches)):
                        originalDimensions = (imageFile.shape[1], imageFile.shape[0])
                        bufferSize = len(cv2.imencode(fileObject.extensionWithDot, imageFile)[1])
                        apiMaxBytesTolerance = (apiMaxBytes/10)
                        scalePercentage = (bufferSize / (apiMaxBytes - apiMaxBytesTolerance)) ** 0.5 # sqrt([current value]/[wanted value])
                        newDimensions = (int(imageFile.shape[1] / scalePercentage), int(imageFile.shape[0] / scalePercentage))
                        imageFile = cv2.resize(imageFile, newDimensions, interpolation = cv2.INTER_CUBIC)
                        printS("Scaling image from ", originalDimensions, " to ", newDimensions)
                        cv2.imwrite(fileObject.directory + "\\!latest-scaled.jpg", imageFile)

                    buffer = cv2.imencode(fileObject.extensionWithDot, imageFile)[1]
                    apiBase = apiLocalBaseUrl if arrayContains(args, localApiSwitches) else apiBaseUrl
                    imageBase64 = base64.b64encode(buffer)
                    body = imageBase64
                    params = { "languageKey": args[1], "pageSegmentationMode": pageSegMode, "engineMode": engineMode } 
                    response = requestCall(apiBase, "/scanImageBase64IntParams", HttpVerb.POST, params = params, body = body, headers = { apiKeyHeaderName: apiKey })
                    
                    if(response == None or response.json()["data"] == None or response.json()["data"]["contentRaw"] == None):
                        if(response != None and response.json() != None):
                            printS("Error in API call: ")
                            printS("\t", response.json()["message"])
                        continue

                    if(sourceIsDir):
                        outPath = batchOutputDir
                        if(not os.path.isabs(batchOutputDir)):
                            outPath = os.path.join(fileObject.directory, batchOutputDir)
                        if(not os.path.isdir(outPath)):
                            os.mkdir(outPath)

                        outputFilename = f"{fileObject.fileroot}-{DateTimeObject().isoWithMilliAsNumber}.txt"
                        outFileFullName = os.path.join(outPath, outputFilename)

                        outFile = open(outFileFullName, "w")
                        outFile.write(response.json()["data"]["contentCleaned"])
                        outFile.close
                        print(f"Scan complete, output written in {outputFilename}")
                    else:
                        if(arrayContains(args, apiRawSwitches)):
                            print(response.json()["data"]["contentRaw"])
                        elif(arrayContains(args, apiCleanedSwitches)):
                            print(response.json()["data"]["contentCleaned"])
                        else:
                            print(response.json())

                argIndex += len(args)

            elif(arg in tessLangFlags):
                print("Locally Installed Tesseract languages:")
                print(tessLang)

                print("API installed Tesseract languages:")
                response = requestCall(apiBaseUrl, "/languages", HttpVerb.GET, headers = { apiKeyHeaderName: apiKey })
                print(response.json()["data"])

            # Invalid, inform and quit
            else:
                print("Argument not recognized: \"" + arg + "\", please see documentation or run with \"-help\" for help.")

            argIndex += 1

    def PrintHelp():
        """
        A simple console print that informs user of program arguments.
        """

        print("--- Help ---")
        print("Arguments marked with ? are optional.")
        print("All arguments that triggers a function start with dash(-).")
        print("All arguments must be separated by space only.")
        print("\n")

        print(str(helpFlags) + ": prints this information about input arguments.")
        print(str(testFlags) + ": a method of calling experimental code (when you want to test if something works).")
        print(str(tessScanFlags) + " + [path to image] + [language] + [page segment mode as int]? + [tesseract engine mode]?: scan an image with Tesseract and get the text.")
        print("\t" + str(localApiSwitches) + f": when scanning with API, use local at {apiLocalBaseUrl}.")
        print("\t" + str(apiRawSwitches) + ": when scanning with API, only print the raw string from Tesseract.")
        print("\t" + str(apiCleanedSwitches) + ": when scanning with API, only print the cleaned string from Tesseract.")
        print("\t" + str(localTesseractSwitches) + ": when scanning, use the local .exe program, not the API.")
        print("\t" + str(localTesseractSwitches) + ": when scanning, use the local .exe program, not the API.")
        print("\t" + str(scaleImageForApiSwitches) + ": scale the image to best fit the API treshold of {apiMaxBytes}.")
        print(str(tessLangFlags) + ": print the available languages for Tesseract.")

if __name__ == "__main__":
    Main.main()
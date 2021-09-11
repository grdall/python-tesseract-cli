import sys
import os
import pytesseract
import cv2
import base64

from Util import *

apiKeyHeaderName = "apiKey"
apiKey = ""
apiBaseUrl = "https://grd-tesseract-api.herokuapp.com/tesseract"
apiLocalBaseUrl = "localhost:8080/tesseract"
batchOutputDir = "text"

os.system("") # Needed to "trigger" coloured text
helpFlags = ["-help", "-h"]
testFlags = ["-test", "-t"]
tessScanFlags = ["-scan", "-s"]
localApiSwitches = ["local", "l"]
apiRawSwitches = ["raw", "r"]
apiCleanedSwitches = ["cleaned", "c"]
localTesseractSwitches = ["program", "exe"]
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
            response = Util.apiCall(apiBaseUrl, "/health", HttpVerb.GET, headers = { apiKeyHeaderName: apiKey })
            print("API Uptime: " + response.json()["data"]["message"])

        while argIndex < argC:
            arg = sys.argv[argIndex].lower()

            if(arg in helpFlags):
                Main.PrintHelp()

            elif(arg in testFlags):
                args = Util.ExtractArgs(argIndex, argV)
                print("test")
                # pathSplit = os.path.splitext(os.path.basename(args[0]))

                # outFilename = pathSplit[0] + Util.getDatetime(True) + ".txt"
                # print(f"Scanning directory, writing to file {outFilename}")
                # print(pathSplit)
                # print(os.listdir(args[0]))

                # outFile = open("test.txt", "w")
                # outFile.write("working")
                # outFile.close()

                obj = FileObject(args[0])
                print(vars(obj))

                quit()

            elif(arg in tessScanFlags):
                args = Util.ExtractArgs(argIndex, argV)
                image = cv2.imread(args[0])

                if(Util.arrayContains(args, localTesseractSwitches)):
                    text = pytesseract.image_to_string(image, lang=args[1])
                    argIndex += len(args)
                    continue

                response = None
                if(Util.arrayContains(args, localApiSwitches)):
                    response = ""
                else:
                    dotSplit = args[0].split(".")
                    extension = "." + str(dotSplit[len(dotSplit) - 1])
                    buffer = cv2.imencode(extension, image)[1]
                    imageBase64 = base64.b64encode(buffer)

                    body = imageBase64
                    params = { "languageKey": args[1] } 
                    response = Util.apiCall(apiBaseUrl, "/scanImageBase64", HttpVerb.POST, params = params, body = body, headers = { apiKeyHeaderName: apiKey })

                if(response == None):
                    print("Failed to get data from API.")
                    argIndex += len(args)
                    continue
                elif(Util.arrayContains(args, apiRawSwitches)):
                    print(response.json()["data"]["contentRaw"])
                elif(Util.arrayContains(args, apiCleanedSwitches)):
                    print(response.json()["data"]["contentCleaned"])
                else:
                    print(response.json())

                argIndex += len(args)

            elif(arg in tessLangFlags):
                print("Locally Installed Tesseract languages:")
                print(tessLang)

                # TODO print for API
                print("API installed Tesseract languages:")
                response = Util.apiCall(apiBaseUrl, "/languages", HttpVerb.GET, headers = { apiKeyHeaderName: apiKey })
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
        print(str(tessScanFlags) + " + [path to image] + [language]: scan an image with Tesseract and get the text.")
        print("\t" + str(localApiSwitches) + f": when scanning with API, use local at {apiLocalBaseUrl}.")
        print("\t" + str(apiRawSwitches) + ": when scanning with API, only print the raw string from Tesseract.")
        print("\t" + str(apiCleanedSwitches) + ": when scanning with API, only print the cleaned string from Tesseract.")
        print("\t" + str(localTesseractSwitches) + ": when scanning, use the local .exe program, not the API.")
        print(str(tessLangFlags) + ": print the available languages for Tesseract.")

if __name__ == "__main__":
    Main.main()
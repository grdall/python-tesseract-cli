import sys
import os
import pytesseract
import cv2
import base64

from Util import *

os.system("") # Needed to "trigger" coloured text
helpFlags = ["-help", "-h"]
testFlags = ["-test", "-t"]
tessScanFlags = ["-scan", "-s"]
localApiSwitches = ["local", "l"]
apiJsonSwitches = ["json", "j"]
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

        while argIndex < argC:
            arg = sys.argv[argIndex].lower()

            if(arg in helpFlags):
                Main.PrintHelp()

            elif(arg in testFlags):
                print("test")
                quit()

            elif(arg in tessScanFlags):
                args = Util.ExtractArgs(argIndex, argV)
                img = cv2.imread(args[0])

                if(set(args).issubset(set(localTesseractSwitches))):
                    text = pytesseract.image_to_string(img, lang=args[1])
                    argIndex += len(args)
                    continue

                apiResponse = None
                if(set(args).issubset(set(localApiSwitches))):
                    apiResponse = ""
                else:
                    apiResponse = ""

                if(apiResponse == None):
                    print("Failed to get data from API.")
                    argIndex += len(args)
                    continue
                elif(set(args).issubset(set(apiJsonSwitches))):
                    print(2) #(apiResponse.json)
                elif(set(args).issubset(set(apiRawSwitches))):
                    print(3) #(apiResponse["data"]["contentRaw"])
                elif(set(args).issubset(set(apiCleanedSwitches))):
                    print(4) #(apiResponse["data"]["contentCleaned"])

                argIndex += len(args)

            elif(arg in tessLangFlags):
                print("Installed Tesseract languages:")
                print(tessLang)

                # TODO print for API

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
        print("\t" + str(localApiSwitches) + ": TODO.")
        print("\t" + str(apiJsonSwitches) + ": TODO.")
        print("\t" + str(apiRawSwitches) + ": TODO.")
        print("\t" + str(apiCleanedSwitches) + ": TODO.")
        print("\t" + str(localTesseractSwitches) + ": TODO.")
        print(str(tessLangFlags) + ": print the available languages for Tesseract.")

if __name__ == "__main__":
    Main.main()
import sys
import os
from enum import Enum
import requests
import time

class Util:
    def DisablePrint():
        """
        Disable usage of print().
        """
        sys.stdout = open(os.devnull, 'w')

    def EnablePrint():
        """
        Restore usage of print().
        """
        sys.stdout = sys.__stdout__

    def ExtractArgs(currentArgsIndex, args, numbersOnly = False, pathsOnly = False, urlsOnly = False):
        """
        Extract non-flag arguments from array of args, options to only accept numbers, paths, urls.\n\n
        int currentArgsIndex
        array of strings args
        bool numbersOnly
        bool pathsOnly
        bool urlsOnly
        """
        _args = []
        for arg in args[currentArgsIndex + 1:]:
            if(arg[0] == "-"):
                break
            if(numbersOnly and not Util.IsNumber(arg)):
                Util.PrintS("Argument ", arg, " is not a number.")
                continue
            if(pathsOnly and not os.path.exists(arg)):
                Util.PrintS("Argument ", arg, " is not a file path.")
                continue
            if(urlsOnly and not validators.url(arg)):
                Util.PrintS("Argument ", arg, " is not a url.")
                continue

            _args.append(arg)
        return _args

    def PrintS(*args):
        """
        Concats all arguments and prints them as string (delim not included).\n\n
        any *args
        """
        res = ""
        for e in args:
            res += str(e)
        print(res)

    def WrapColor(text, color):
        """
        Wraps text in ASCI colours for terminal usage.
        see colours in Util.colors for simple selection, argument accepts ANCI code like "\\x1b[0;34;42m".
            See Util project Main class' printAllColours function for most or all styles.
        string text
        string/int color
        """
        colorArg = ""

        if(Util.IsNumber(str(color))):
            colorList = list(Util.colors)
            if(int(color) < 0 or int(color) > len(colorList) - 1):
                return "Color index out of range (0 - " + str(len(colorList) - 1) + ")"

            colorArg = Util.colors[colorList[int(color)]]
        elif(str(color[0]) == "\x1b"):
            colorArg = color
        else:
            colorArg = Util.colors[str(color).upper()]

        return colorArg + str(text) + Util.colors["ENDC"]

    # https://note.nkmk.me/en/python-check-int-float/
    def IsNumber(n, intOnly = False):
        """
        Try parse n as float or inter, return true/false.\n\n
        any n
        """
        try:
            float(n)
        except ValueError:
            return False
        else:
            if(intOnly):
                return float(n).is_integer
            else:
                return True

    def AsTableRow(dataArray, labels = None, minColWidth = 6, delim = " | ", startingDelim = False):
        """
        Returns a string row of values as a row in tables.\n\n

        Array of any dataArray (1D)
        Array of any labels (1D)
        int minColWidth
        string delim
        bool startingDelim
        """

        row = delim if startingDelim else ""
        for i in range(0, len(dataArray)):
            _minColWidth = minColWidth
            if(len(labels) > 0 and len(labels[i]) > 0):
                _minColWidth = len(str(labels[i])) if len(str(labels[i])) > minColWidth else minColWidth

            spacePadding = " " * (_minColWidth - len(str(dataArray[i])))
            row += str(dataArray[i]).replace("\n", "") + spacePadding + delim
            
        return row

    def AsTable(dataArray, labels = None, minColWidth = 6, delim = " | ", startingDelim = False):
        """
        Returns a string formatted as a table.\n\n

        Array of any dataArray (2D)
        Array of any labels (1D)
        int minColWidth
        string delim
        bool startingDelim
        """

        tableString = ""
        if(len(labels) > 0):
            labelRow = Util.AsTableRow(labels, labels, minColWidth, delim, startingDelim)
            tableString += labelRow + "\n"
            tableString += ("-" * len(labelRow)) + "\n"
            
        for i in range(0, len(dataArray)):
            line = Util.AsTableRow(dataArray[i], labels, minColWidth, delim, startingDelim) + "\n"
            tableString += line if i % 2 != 0 else Util.WrapColor(line, "gray")
            
        return tableString  

    def apiCall(baseUrl, endpoint, verb, params, body, headers, retries = 4, timeout = 4):
        """
        Make an API call to {baseUrl}{endpoint}, using verb. Format params, header, and body like params = {"key": "value"}, 
        or body as just value. Retries default 4 times, waiting default 4 seconds after fail.
        """

        print(f"Making a web request to {baseUrl}{endpoint}...")

        response = None
        for i in range(retries):
            if(verb == HttpVerb.GET):
                response = requests.get(f"{baseUrl}{endpoint}", params = params, data = body, headers = headers)
            if(verb == HttpVerb.POST):
                response = requests.post(f"{baseUrl}{endpoint}", params = params, data = body, headers = headers)

            if(response.status_code == 200 or response.status_code == 500):
                return response
            else:
                print(f"Request to {baseUrl}{endpoint} failed with code: {response.status_code}. Codes 408 and 503 are common for websites warming up...")
                time.sleep(timeout)

        print(f"Web request to {baseUrl}{endpoint} failed all {retries} retries, after a minimum of {retreis * timeout} seconds...")
        return response        


    colors = {
        "GRAY": "\x1b[1;30;40m",
        "HEADER": "\x1b[95m",
        "OKBLUE": "\x1b[94m",
        "OKGREEN": "\x1b[92m",
        "WARNING": "\x1b[93m",
        "FAIL": "\x1b[91m",
        "ENDC": "\x1b[0m",
        "BOLD": "\x1b[1m",
        "UNDERLINE": "\x1b[4m",
    }

class HttpVerb(Enum):
    GET = 0,
    POST = 1,
    PUT = 2,
    PATCH = 3,
    DELETE = 4
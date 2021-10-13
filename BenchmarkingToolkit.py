import line_profiler
import os
import pickle
import json
import numpy as np
from time import time

class LineProfile:

    def __init__(self, line_tuple):

        self.line_no = line_tuple[0]
        self.hits = line_tuple[1]
        self.total_time = line_tuple[2]
        self.time_per_hit = self.total_time / self.hits
        self.time_percent_func = None
        self.time_percent_total = None


class FunctionProfile:

    def __init__(self, timed_element, line_list):

        # Lines hit in the function
        self.lines = []
        # Name of function
        self.name = timed_element[2]
        # Line number of function definition
        self.line_no = line_list[0][1]
        # Number of times the function was hit
        self.hits = None
        # Total time for function
        self.total_time = 0
        # Total time as percentage of main
        self.time_percent_total = None
        # For each line in the function
        for line in line_list:
            # Create a line object and append to lines
            self.lines.append(LineProfile(line))
        # Set the line percentages
        self.setLineInFuncPercentages()

    def setLineInFuncPercentages(self):
        # For each line
        for line in self.lines:
            # Add the time to the total
            self.total_time += line.total_time
        # For each line
        for line in self.lines:
            # Put in the percent total
            line.time_percent_func = line.total_time / (self.total_time / 100)

    def setLineOverallPercentages(self, total_time):
        # Number of lines
        line_count = len(self.lines)
        # For each line
        for line in self.lines:
            # Get the percentage of the whole script's time
            line.time_percent_total = line.total_time / (total_time / 100)
        # Set the function's overall time percentage
        self.time_percent_total = self.total_time / (total_time / 100)


class Profiler:

    def __init__(self, timings_dict):

        # Reference to "main" function
        self.main_func = None
        # Functions called by the main function
        self.called_functions = {}
        # Line number of "main" function
        self.main_func_line_no = None
        # Total time of all lines
        self.total_time = 0
        # For each timing element
        for timed_element in timings_dict:
            # Create a function profiler
            currProfiler = FunctionProfile(timed_element, timings_dict[timed_element])
            # If it is the 'main' function
            if currProfiler.name == "main":
                # Store as main function
                self.main_func = FunctionProfile(timed_element, timings_dict[timed_element])
                # Store line number
                self.line_no = currProfiler.line_no
            # Otherwise (not "main")
            else:
                # Add to called functions with its name as key
                self.called_functions[currProfiler.name] = currProfiler
        # Set the function and their lines' percentage time usages
        self.setFuncPercentages()

    def setFuncPercentages(self):
        # For each called function
        for funcName in self.called_functions.keys():
            # Add the function's total time
            self.total_time += self.called_functions[funcName].total_time
        # For each called function
        for funcName in self.called_functions.keys():
            # Get the function to set its line's percentages
            self.called_functions[funcName].setLineOverallPercentages(self.total_time)
        # Set main function's overall percentages
        self.main_func.setLineOverallPercentages(self.total_time)
        # # For each function called in the main
        # for line in self.main_func.lines:
        #     # Get the function corresponding to the line number
        #     currFuncSD = support_dict[line.line_no]
        #     # Get the function's stripped name
        #     funcName = currFuncSD["line"].replace("def ", "").strip("():")
        #     # Reference the function corresponding to the name
        #     currFunc = self.called_functions[funcName]
        #

    # Get the list of lines to print as the report
    def getReportLines(self, support_dict):
        # Line list
        line_list = []
        # For each operational line number in the support dictionary
        print(sorted(list(support_dict.keys()), key=int))
        for line_no in sorted(list(support_dict.keys()), key=int):
            # For each preceding blank line
            for blank in range(0, support_dict[line_no]["preceding blanks"]):
                # Add a blank line
                line_list.append("\n")
            # If the line is a function
            if support_dict[line_no]["type"] == "function":
                # Get the function's stripped name
                funcName = support_dict[line_no]["line"].replace("def ", "").replace("():", "").strip()
                # If it's the main function
                if funcName == "main":
                    # Reference the function
                    currFunc = self.main_func
                    # Update the line with its stats as a comment
                    commented_line = support_dict[line_no][
                                         "line"].strip() + f"#<> Func. Total time: {np.around(currFunc.total_time * 1e-07, decimals=2)}s\n"
                # Otherwise (not main)
                else:
                    # Reference the function
                    currFunc = self.called_functions[funcName]
                    # Update the line with its stats as a comment
                    commented_line = support_dict[line_no]["line"].strip() + f"#<> Func. Total time: {np.around(currFunc.total_time * 1e-07, decimals=2)}s, % of main: {np.around(currFunc.time_percent_total, decimals=2)}\n"
                # Add the line
                line_list.append(commented_line)
            # Otherwise
            else:
                # If it's import
                if "import" in support_dict[line_no]["line"]:
                    # Add the line
                    line_list.append(support_dict[line_no]["line"])
                # Otherwise
                else:
                    # Line match
                    line_match = False
                    # Look for the line's number
                    for funcName in self.called_functions.keys():
                        for line in self.called_functions[funcName].lines:
                            if int(line_no) == line.line_no:
                                # Assemble the commented line
                                commented_line = support_dict[line_no]["line"].strip("\n") + f"#<> Line Total time: {np.around(line.total_time * 1e-07, decimals=2)}s, % of func.: {np.around(line.time_percent_func, decimals=2)}, % of main: {np.around(line.time_percent_total, decimals=2)}\n"
                                # Add the line
                                line_list.append(commented_line)
                                # Set line match
                                line_match = True
                    # If there's still no match
                    if line_match is False:
                        # Try in the main lines
                        for line in self.main_func.lines:
                            # If the line number matches
                            if int(line_no) == line.line_no:
                                # Assemble the commented line
                                commented_line = support_dict[line_no]["line"].strip("\n") + f"#<> Line Total time: {np.around(line.total_time * 1e-07, decimals=2)}s, % of main: {np.around(line.time_percent_func, decimals=2)}\n"
                                # Add the line
                                line_list.append(commented_line)
                                # Set line match
                                line_match = True
                    # If there's still no match
                    if line_match is False:
                        # Transfer the line
                        line_list.append(support_dict[line_no]["line"])
        # Return the line list
        return line_list


def addDecorators(target_file):

    # Line dictionary for operational lines of code
    line_dict = {}
    with open(target_file, 'r') as f:
        # Line count
        line_count = 0
        # Blank line counter
        blank_count = 0
        # Added decorator counter
        decorator_count = 0
        # Previous line store
        prev_line = None
        # Output list
        output_list = []
        # For each line in the target file
        for line in f:
            # Add to line count
            line_count += 1
            if "def" in line:
                # Extract function name
                functionName = line.replace('def', '')
                print(f"Function {functionName} identified.")
                # If there is a previous line (i.e. this is not the first line)
                if prev_line is not None:
                    # If the previous line does not contain the decorator
                    if "@profile" not in prev_line:
                        # Append a decorator line to the output
                        output_list.append("@profile\n")
                        # Print notification
                        print(f"Adding decorator to profile function {line.replace('def', '').strip(' ')}")
                        # Add to decorator count
                        decorator_count += 1
                # Append line to output list
                output_list.append(line)
                # Add line to line dictionary
                line_dict[line_count + decorator_count] = {"type": "function",
                                                             "line": line,
                                                             "preceding blanks": blank_count,
                                                             "preceding decorators": decorator_count}
                # Reset blank and decorator counts
                blank_count = 0
                # Update previous line
                prev_line = line
            # Otherwise, if the line is empty
            elif line == "\n":
                output_list.append(line)
                # Add to blank count
                blank_count += 1
            # Otherwise
            else:
                # Append line
                output_list.append(line)
                # Add line to line dictionary
                line_dict[line_count + decorator_count] = {"type": "other",
                                                           "line": line,
                                                           "preceding blanks": blank_count,
                                                           "preceding decorators": decorator_count}
                # Reset blank and decorator counts
                blank_count = 0
                # Update previous line
                prev_line = line
        # Open an output file and add to the file name for "profiler ready"
        with open(target_file.replace(".py", "_pr.py"), 'w') as of:
            for line in output_list:
                of.write(line)
        # Open an output file for the support dictionary
        with open(target_file.replace(".py", "_sd.json"), 'w') as of:
            json.dump(line_dict, of, indent=4)


def fullService(target_file):

    # Add decorators to the target file if needed
    addDecorators(target_file)
    # Get profiler-ready name of file
    pr_filepath = target_file.replace(".py", "_pr.py")
    # Get support dictionary name of file
    sd_filepath = target_file.replace(".py", "_sd.json")
    # Call the line profiler (writes the output *.lprof file)
    os.system(f"kernprof -l {pr_filepath}")
    # Get the lprof file path
    lprof_filepath = pr_filepath.replace(".py", ".py.lprof")
    # Open the *.lprof file
    lprof = pickle.load(open(lprof_filepath, 'rb'))
    # Retrieve the timings dictionary
    timings_dict = lprof.__dict__['timings']
    # Create a profiler object
    currProfiler = Profiler(timings_dict)
    # Open the support dictionary
    with open(f"{sd_filepath}", 'r') as f:
        # Support dictionary
        support_dict = json.load(f)
    # Update all the function-level timing percentages
    currProfiler.setFuncPercentages()
    # Get report filepath
    report_filepath = target_file.replace(".py", "_report.py")
    # Open an output file and add to the file name for "report"
    with open(report_filepath, 'w') as of:
        for line in currProfiler.getReportLines(support_dict):
            of.write(line)

    # # For each timing element
    # for timed_element in timings_dict:
    #     # If
    #
    #     print(timed_element)
    #     print(timings_dict[timed_element])
        #print(f"Function: {timed_element[2]} on line {timed_element[1]}")
        #print(f"Hit {timings_dict[timed_element][0][1]} times.")



    #with open(lprof_filepath, 'r', encoding="UTF-8") as f:
    #    for line in f:
    #        print(line)



#addDecorators("F:/USRA/BMHDTools/BenchmarkTarget2.py")
stime = time()
fullService("F:/USRA/BMHDTools/BenchmarkTarget2.py")
print(time() - stime)
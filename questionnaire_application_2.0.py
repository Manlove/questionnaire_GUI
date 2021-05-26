# Gapps questionnaire application
# Version 2.0
# Logan Manlove
# 9/10/2019


import tkinter as tk                                                            # tkinter builds the application
import re                                                                       # regular expressions are used to remove any tabs or returns from any input boxes
import os                                                                       # OS allows the application to save temporary files while the application is running, creates an error log, allows user to choose location of output
import shutil                                                                   # allows the application to remove the temporary files once the application has completed successfully
from tkinter import messagebox, filedialog, W, NW, E, EW, SW, NE, NS
from functools import partial                                                   # Adds functions to the radiobuttons to allow them to expand and collapse fields in the gui
title_font = "Helvetica 26 bold"
header_font = "Helvetica 18 bold"
label_font = "Helvetica 18"

class gui(tk.Frame):
    def __init__(self, testing = False, master = None):
        self.testing = testing
        self.current = False
        self.root = tk.Tk()
        self.root.grid_propagate(False)
        self.root.title("GAPPS Questionnaire")
        self.path = os.getcwd()
        self.temp_path = self.path + "/temp"
        try:
            os.mkdir(self.temp_path)
        except:
            pass
        super().__init__(self.root)



        ### The template class names and the page names are fed to the builder to set up all pages in a loop
        self.templates = [page_one, page_two, page_three, page_four, page_five, page_six, page_seven, page_eight, page_nine, page_ten,
                   page_eleven, page_twelve, page_thirteen, page_fourteen, page_fifteen, page_sixteen, page_seventeen, page_eighteen]
        self.names = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen',
                    'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen']

        ### For expanding the window. The top row will hold the navigation panel which we do not want to expand. The second holds the page frame which should
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0,weight=1)
        self.root.columnconfigure(1,weight=0) # <= this holds the scrollbar if it is included on this level

        self.build_main_page()
        self.setup_questionnaire()

        self.root.configure(height = self.current.layout.frame.winfo_reqheight() + self.navigation_frame.winfo_reqheight() + 35, width = self.current.layout.frame.winfo_reqwidth() + 30)
        self.height = self.root.winfo_height()
        self.width = self.root.winfo_width()
        self.root.bind('<Configure>', self.window_resize)

    def build_main_page(self):
        ### Creates two containers on the root. The navigation_frame holds the forward and back buttons. The page_frame will hold the frames from each page.
        ###       I did this without these two frames originally but had trouble with positioning. This was intended to change that.
        self.page_frame = tk.Canvas(self.root)#, bd = 3, relief = "ridge")
        self.navigation_frame = tk.Frame(self.root)#, bd = 3, relief = "ridge")
        self.scrollbar = tk.Scrollbar(self.root, orient = "vertical", command = self.page_frame.yview)

        self.page_frame.grid(row = 1, column = 0, sticky = NW, padx = (10,10), pady = (0,10))
        self.navigation_frame.grid(row = 0, column = 0, sticky = NW , columnspan = 2, padx = (10,10), pady = (10,0)) # <= columnspan is only needed if the scrollbar is included on this level
        self.page_frame.configure(yscrollcommand=self.scrollbar.set)

        ### For expanding the window
        self.page_frame.rowconfigure(0, weight=1)
        self.page_frame.columnconfigure(0, weight=1)
        self.navigation_frame.rowconfigure(0, weight=1)
        self.navigation_frame.columnconfigure(0,weight=1)
        self.navigation_frame.columnconfigure(1,weight=1)

        ### Sets up the navigation buttons on the top level (inside the navigation_frame). Removes the back button from the grid as the first page wont use it.
        #tk.Label(self.root, text = "", font = "Helvetica 3").grid(row = 1, column = 0)
        self.next_button = tk.Button(self.navigation_frame, text = "Next", command = self.next_page, bd = 5, relief = "raised", font = header_font)
        self.back_button = tk.Button(self.navigation_frame, text = "Back", command = self.last_page, bd = 5, relief = "groove", font = header_font, state = "disabled")
        self.back_button.grid(row = 0, column = 0, pady = (0,10))
        self.next_button.grid(row = 0, column = 1, pady = (0,10))
        # self.back_button.grid_remove() # Could look to disable instead, might look cleaner without it popping in and out

    def setup_questionnaire(self):
        ### sets up the first page as the starting page
        self.start = page(self, self.page_frame, self.templates[0], self.names[0])
        self.current = self.start

        ### Walks through and creates the remaining pages by first creating the next page in a temporary variable
        ###     assigning that page to the next pointer on the current page
        ###     moving the current page to the next page
        ###     repeating for remaining page_sixteen
        for name, template in zip(self.names[1:], self.templates[1:]):
            next = page(self,self.page_frame, template, name, self.current)
            self.current.next = next
            self.current = next

        ### Moves the current page pointer back to the start and starts the questionnaire
        self.current = self.start
        self.build_page()
        if self.testing:
            self.next_page()

    def build_page(self):
        self.current.build_page()

        self.window = self.page_frame.create_window(0,0,anchor=NW, window = self.current.layout.frame)
        self.page_frame.update_idletasks()
        self.page_frame.configure(height = self.root.winfo_height() - self.navigation_frame.winfo_reqheight(), width = self.current.layout.frame.winfo_reqwidth(), scrollregion=self.page_frame.bbox('all'))
        self.scrollbar.grid(row = 1, column = 1, sticky = NS)
        if self.current.layout.frame.winfo_reqwidth() > self.root.winfo_width():
            self.root.configure(width = self.current.layout.frame.winfo_reqwidth() + 10)

    def next_page(self):
        if self.testing:
            self.current.layout.testing()

        ### Clears the current layout by removing the frame that the page was built on. This frame is built within the top level page_frame.
        self.page_frame.delete(self.window)

        ### Saves the current page to a temporary file. This prevents loss of too much data in the event of a crash
        self.current.layout.write_summary(path = self.temp_path)

        ### If a next page exists: Moves the current page pointer to the next page and builds that page
        ###     otherwise runs the finish function
        if self.current.next:
            self.current = self.current.next
            self.build_page()
        else:
            self.finish()

        ### Checks to see if a previous page exists. If it does it adds the back button.
        ###     If not it removes the back button
        ###  Maybe this should just activate/ deactivate the button
        if self.current.last:
            self.back_button.configure(relief = "raised", state = "active")
        else:
            self.back_button.configure(relief = "groove", state = "disabled")
        if self.testing:
            self.next_page()

    def last_page(self):
        ### Clears the current layout by removing the frame that the page was built on. This frame is built within the top level page_frame.
        self.page_frame.delete(self.window)

        ### Saves the current page to a temporary file. This prevents loss of too much data in the event of a crash
        self.current.layout.write_summary(path = self.temp_path)

        ### If a previous page exists: Moves the current page pointer to the previous page and builds that page
        ###     otherwise runs the finish function
        if self.current.last:
            self.current = self.current.last
            self.build_page()

        ### If the new current page has a previous page: show the back button
        ###     Otherwise, remove the back button
        if self.current.last:
            self.back_button.configure(relief = "raised", state = "active")
        else:
            self.back_button.configure(relief = "groove", state = "disabled")

    def finish(self):
        ### Retrieves the patient_id and the patients year of birth from the first page.  The year of birth will be used to calculate age of onset
        patient_id = self.start.layout.widgets['patient_id'].get()
        self.year_of_birth = self.start.layout.widgets['year_of_birth'].get()

        ### Creates the titles for the two output files from the patient ID and continues to check_name
        self.summary_title = self.path + '/{}_GAPPS_Questionnaire_Response.txt'.format(patient_id)
        self.output_title = self.path + '/{}_GAPPS_Questionnaire_database.txt'.format(patient_id)
        self.check_name()

    def check_name(self):
        ### Checks both the summary title and the output title to see if either file already exists. If it does it asks if the user wants to overwrite the file
        ###     If they do it saves the file with the given filename
        ###     If not it asks the user to give a new name
        ### Proceeds to write_to_file
        while os.path.exists(self.summary_title):
            if messagebox.askokcancel("Save", "'{}' Already exists. Do you want to over write?".format(self.summary_title)):
                os.remove(self.summary_title)
            else:
                self.summary_title = filedialog.asksaveasfilename(initialdir = self.path, title = "Save file")

        while os.path.exists(self.output_title):
            if messagebox.askokcancel("Save", "'{}' Already exists. Do you want to over write?".format(self.output_title)):
                os.remove(self.output_title)
            else:
                self.output_title = filedialog.asksaveasfilename(initialdir = self.path, title = "Save file")
        self.write_to_file()

    def write_to_file(self):
        ### Sets the current page back to the start page and opens the summary, output, and error_log files
        current_page = self.start
        summary_file = open(self.summary_title, 'w')
        database_file = open(self.output_title, 'w')
        error_file = open('error_log', 'w')

        ### Steps through each page in the questionnaire and runs the write_summary and write_ouput functions for those pages before moving to the next page
        while current_page:
            current_page.layout.write_summary(file = summary_file)
            current_page.layout.write_output(database_file, error_file, self.year_of_birth)
            current_page = current_page.next

        ### Closes the summary file..... output file may never be closed.... and removes the temporary files
        summary_file.close()
        shutil.rmtree(self.temp_path)

        ### Checks to see if the error log is empty and removes it if it is. Destroys and root and quits the application
        if os.stat('error_log').st_size == 0:
            os.remove('error_log')
        self.root.destroy()
        quit()

    def window_resize(self, event):
        ### Frame size can't be larger than the window st_size
        ### Just need to set the scrollbar to the requested height
        if self.current and (self.height != self.root.winfo_height() or self.width != self.root.winfo_width()):
            self.height = self.root.winfo_height()
            self.width = self.root.winfo_width()
            # self.window = self.page_frame.create_window(0,0,anchor=NW,window = self.current.layout.frame)
            self.page_frame.update_idletasks()
            self.page_frame.configure(height = self.root.winfo_height() - self.navigation_frame.winfo_reqheight(), width = self.current.layout.frame.winfo_reqwidth(), scrollregion=self.page_frame.bbox('all'))

        # if self.current.layout.frame.winfo_reqheight() + self.navigation_frame.winfo_reqheight() > self.root.winfo_height():
        #     self.page_frame.configure(width = self.root.winfo_width(), height = self.root.winfo_height() - self.navigation_frame.winfo_reqheight(), scrollregion=(0,0,self.current.layout.frame.winfo_reqwidth(), self.current.layout.frame.winfo_reqheight()))
        #     self.current.layout.frame.configure(width = self.root.winfo_width(), height = self.root.winfo_height() - self.navigation_frame.winfo_reqheight())
        #
        #
        # print("Width: {}\t{}\t{}".format(self.root.winfo_width(), self.current.layout.frame.winfo_reqwidth(), self.current.layout.frame.winfo_reqwidth() == self.page_frame.winfo_reqwidth()))
        # print("Height: {}\t{}\t{}\n".format(self.root.winfo_height(), self.current.layout.frame.winfo_reqheight() + self.navigation_frame.winfo_reqheight(), self.current.layout.frame.winfo_reqheight() == self.page_frame.winfo_reqheight()))

class page():
    def __init__(self, main_app, frame_page, setup, name, previous_page = None):
        self.page_name = name
        self.frame_page = frame_page
        self.last = previous_page
        self.next = None
        self.setup = setup
        self.main_app = main_app
        self.layout = setup(self.main_app, self, self.frame_page)

    def build_page(self):
        self.layout.build()

class pages():
    def __init__(self, main_app, page, page_frame):
        self.main_app = main_app
        self.page = page
        self.page_frame = page_frame
        self.frame = tk.Frame(self.page_frame)#, bd = 3, relief = "ridge")
        # self.scrollbar = tk.Scrollbar(self.frame, orient = "vertical", command = self.frame.yview)
        # self.frame.configure(yscrollcommand=self.scrollbar.set)
        self.widgets = {}

    def clear(self):
        self.frame.grid_remove()

    def retrieve(self):
        pass

    def write_summary(self, file, path, file_name):
        if path != None:
            self.file_name = path + "/page_{}_temp.txt".format(self.page.page_name)
            self.file = open(self.file_name, 'w')
        else:
            self.file = file

    def write_entry(self, description, variable, file, error_file, tabs = 1):
        try:
            file.write("{}{}".format(variable, "\t" * tabs))
        except:
            file.write("{}".format("\t" * tabs))
            error_file.write("Failed to write {}\n".format(description))

class page_one(pages):                                                          # Survey ID; Patient ID; Birthday/ Age; GAPPS diagnosis; Gastrctomy
    # Survey ID
    # Patient ID
    # A1. Year of Birth
    # A2. Diagnosed with Gapps (Y/N)
    #       Year/ Age
    #       How were you diagnosed (Upper GI endoscopy/ Genetic testing)
    # A3. Had a gastrectomy (Y/N)
    #       Year/ Age
    def __init__(self, main_app, page, frame_page):
        super().__init__(main_app, page, frame_page)
        self.widgets['survey_id'] = tk.Entry(self.frame, bg = 'light grey', font = header_font)
        self.widgets['patient_id'] = tk.Entry(self.frame, bg = 'light grey', font = header_font)
        self.widgets['year_of_birth'] = tk.Entry(self.frame, bg = 'light grey', font = header_font)
        self.widgets['gapps_diagnosis'] = radiobutton(['Yes', 'No'], self.frame)
        self.widgets['gapps_diagnosis'].var.set(1)
        self.widgets['gapps_year'] = tk.Entry(self.frame, bg = 'light grey', font = header_font)
        self.widgets['gapps_method'] = radiobutton(['Upper GI colonoscopy', 'Genetic testing'], self.frame)
        self.widgets['gastrectomy'] = radiobutton(['Yes', 'No'], self.frame)
        self.widgets['gastrectomy'].var.set(1)
        self.widgets['gastrectomy_year'] = tk.Entry(self.frame, bg = 'light grey', font = header_font)
    def build(self):
        # Field Labels
        self.frame.grid(row = 0, column = 0, columnspan = 2, sticky = NW)
        # self.scrollbar.grid(row = 0, column = 4, rowspan = 11, sticky = NS)
        tk.Label(self.frame, text = "Survey ID:", font = label_font).grid(row = 0,column = 0, sticky = W, pady = 1, columnspan = 2)
        tk.Label(self.frame, text = "Patient ID:", font = label_font).grid(row = 1,column = 0, sticky = W, pady = 1, columnspan = 2)
        tk.Label(self.frame, text = "A1", font = title_font).grid(row = 2,column = 0, sticky = W, pady = 1)
        tk.Label(self.frame, text = "Age or Year of birth: ", font = label_font).grid(row = 3,column = 1, sticky = W, pady = 1)
        tk.Label(self.frame, text = "A2", font = title_font).grid(row = 4,column = 0, sticky = W, pady = 1)
        tk.Label(self.frame, text = "Diagnosed with GAPPS", font = label_font).grid(row = 5,column = 1, sticky = W, pady = 1)
        tk.Label(self.frame, text = "\tYear or Age Diagnosed", font = label_font).grid(row = 6,column = 1, sticky = W, pady = 1)
        tk.Label(self.frame, text = "\tMethod of Diagnosis", font = label_font).grid(row = 7,column = 1, sticky = W, pady = 1)
        tk.Label(self.frame, text = "A3", font = title_font).grid(row = 8,column = 0, sticky = W, pady = 1)
        tk.Label(self.frame, text = "Gastrectomy?", font = label_font).grid(row = 9,column = 1, sticky = W, pady = 1)
        tk.Label(self.frame, text = "\tGastrectomy Year or Age", font = label_font).grid(row = 10,column = 1, sticky = W, pady = 1)

        self.widgets['survey_id'].grid(row = 0,column = 2, sticky = W, columnspan = 2)
        self.widgets['patient_id'].grid(row = 1,column = 2, sticky = W, columnspan = 2)
        self.widgets['year_of_birth'].grid(row = 3,column = 2, sticky = W, columnspan = 2)
        self.widgets['gapps_diagnosis'].place(rows = [5,5], columns = [2,3])
        self.widgets['gapps_year'].grid(row = 6,column = 2, sticky = W, columnspan = 2)
        self.widgets['gapps_method'].place(rows = [7,7], columns = [2,3])
        self.widgets['gastrectomy'].place(rows = [9,9], columns = [2,3])
        self.widgets['gastrectomy_year'].grid(row = 10,column = 2, sticky = W, columnspan = 2)
    def write_summary(self, file = None, path = None, file_name = None):
        super().write_summary(file = file, path = path, file_name = file_name)
        try: # ~~~~~~ From page one ~~~~~~
            self.file.write("Survey ID: {}\tPatient ID: {}\n".format(self.widgets['survey_id'].get(), self.widgets['patient_id'].get()))
            self.file.write("A. GAPPS\n\tA1. What is your year of birth? {}\n".format(self.widgets['year_of_birth'].get()))
            self.file.write("\tA2. Have you ever been diagnosed with GAPPS? {}\n".format("Yes" if not self.widgets['gapps_diagnosis'].get() else "No"))
            if not self.widgets['gapps_diagnosis'].get():
                self.file.write("{}".format("\t\tWhen were you diagnosed? {}\n".format(self.widgets['gapps_year'].get()) if self.widgets['gapps_year'].get() != "" else ""))
                self.file.write("\t\tHow were you diagnosed? {}\n".format('Upper GI colonoscopy' if not self.widgets['gapps_method'].get() else 'Genetic testing'))
            self.file.write("\tA3. Have you had a gastrectomy? {}\n".format("Yes" if not self.widgets['gastrectomy'].get() else "No"))
            if not self.widgets['gastrectomy'].get() and self.widgets['gastrectomy_year'].get() != "":
                self.file.write("\t\tWhen did it happen? {}\n".format(self.widgets['gastrectomy_year'].get()))
        except:
            print("Error during writing of page one")
        if path != None:
            self.file.close()
    def write_output(self, file, error_file, year_of_birth):
        for i in ['patient_id', 'year_of_birth']:                                                                               # Patient ID, Birth year (2)
            self.write_entry(i, self.widgets[i].get(), file, error_file)
        self.write_entry('GAPPS diagnosis', "yes" if not self.widgets['gapps_diagnosis'].get() else "no", file, error_file)
        if not self.widgets['gapps_diagnosis'].get():                                                                           # If the GAPPS diagnosis is yes:
            if self.widgets['gapps_year'].get() != "":
                try:
                    if len(self.widgets['gapps_year'].get()) < 4:                                                                           # If the year length is less than 4:
                        self.write_entry('GAPPS year', int(self.widgets['year_of_birth'].get()) + int(self.widgets['gapps_year'].get()) if self.widgets['year_of_birth'].get() != "" else "", file, error_file)
                        self.write_entry('GAPPS year', self.widgets['gapps_year'].get(), file, error_file)
                    elif len(self.widgets['gapps_year'].get()) == 4:                                                                        # If the year length is equal to 4:
                        self.write_entry('GAPPS year', self.widgets['gapps_year'].get(), file, error_file)
                        self.write_entry('GAPPS year', int(self.widgets['gapps_year'].get()) - int(self.widgets['year_of_birth'].get()) if self.widgets['year_of_birth'].get() != "" else "", file, error_file)
                    else:
                        self.write_entry('GAPPS year', self.widgets['gapps_year'].get(), file, error_file, tabs = 2)
                except:
                    file.write("\t\t")
            self.write_entry('GAPPS diagnosis method', 'Upper GI colonoscopy' if not self.widgets['gapps_method'].get() else 'Genetic testing', file, error_file)
        else:
            file.write("\t\t\t")
        self.write_entry('gastrectomy test response', "yes" if not self.widgets['gastrectomy'].get() else "no", file, error_file)

        if not self.widgets['gastrectomy'].get():                                                                               # If gastrectomy response is yes
            if len(self.widgets['gastrectomy_year'].get()) < 4:                                                                           # If the year length is less than 4:
                self.write_entry('gastrectomy year', int(self.widgets['year_of_birth'].get()) + int(self.widgets['gastrectomy_year'].get()) if self.widgets['year_of_birth'].get() != "" else "", file, error_file)
                self.write_entry('gastrectomy year', self.widgets['gastrectomy_year'].get(), file, error_file)
            elif len(self.widgets['gastrectomy_year'].get()) == 4:                                                                        # If the year length is equal to 4:
                self.write_entry('gastrectomy year', self.widgets['gastrectomy_year'].get(), file, error_file)
                self.write_entry('gastrectomy year', int(self.widgets['gastrectomy_year'].get()) - int(self.widgets['year_of_birth'].get()) if self.widgets['year_of_birth'].get() != "" else "", file, error_file)
            else:
                self.write_entry('gastrectomy year', self.widgets['gastrectomy_year'].get(), file, error_file, tabs = 2)
        else:
            file.write("\t\t")
    def testing(self):
        self.widgets['survey_id'].insert(0, 'survey_id - 1')
        self.widgets['patient_id'].insert(0, 'patient_id - 2')
        self.widgets['year_of_birth'].insert(0, '3000')
        self.widgets['gapps_diagnosis'].var.set(0)
        self.widgets['gapps_year'].insert(0, '100')
        self.widgets['gapps_method'].var.set(1)
        self.widgets['gastrectomy'].var.set(0)
        self.widgets['gastrectomy_year'].insert(0, '200')
class page_two(pages):                                                          # Upper GI endoscopy
    # Has the subject had an upper GI endoscopy? (Y/N)
    #       Age of First GI endoscopy
    #       Results of First GI endoscopy
    #       Specialists
    #       Clinic Locations
    def __init__(self, main_app, page, frame_page):
        super().__init__(main_app, page, frame_page)
        self.widgets['endoscopy'] = radiobutton(['Yes', 'No'], self.frame)
        self.widgets['endoscopy'].add_command(self.expand_page, 'Yes')
        self.widgets['endoscopy'].add_command(self.minimize_page, 'No')
        self.widgets['endoscopy'].var.set(1)

        self.subframe = tk.Frame(self.frame)

        for i in ["First", "Second", "Third", "Fourth", "Last"]:
            self.widgets['{}_endoscopy_age'.format(i)] = tk.Entry(self.subframe, bg = 'light grey', font = header_font)
            self.widgets['{}_endoscopy_results'.format(i)] = text(self.subframe, height = 2, bg = 'light grey', font = header_font)

        self.widgets['endoscopy_specialists'] = text(self.subframe, height = 2, bg = 'light grey', font = header_font)
        self.widgets['endoscopy_clinics'] = text(self.subframe, height = 2, bg = 'light grey', font = header_font)
    def build(self):
        self.frame.grid(row = 0, column = 0, columnspan = 2)
        #self.scrollbar.grid(row = 0, column = 4, rowspan = 11, sticky = NS)
        tk.Label(self.frame, text = "B1: Upper GI endoscopy", font = title_font).grid(row = 0,column = 0, sticky = W, pady = 1)
        tk.Label(self.frame, text = "\tHas subject had an upper GI endoscopy?", font = label_font).grid(row = 1,column = 0, sticky = W, pady = 1)

        self.widgets['endoscopy'].place(rows = [1,1], columns = [1,2])

        self.subframe.grid(row = 2, column = 0, columnspan = 3)

        for i, label in zip([0,4,8,12,16], ["First", "Second", "Third", "Fourth", "Last"]):
            tk.Label(self.subframe, text = "{} upper GI endoscopy".format(label), font = header_font).grid(row = i,column = 0, sticky = W, pady = 1, columnspan = 2)
            tk.Label(self.subframe, text = "\tYear/ Age", font = label_font).grid(row = i + 1,column = 0, sticky = W, pady = 1)
            tk.Label(self.subframe, text = "\tResults", font = label_font).grid(row = i + 2,column = 0, sticky = W, pady = 1)
            self.widgets['{}_endoscopy_age'.format(label)].grid(row = i + 1,column = 1, sticky = W, pady = 1, columnspan = 2)
            self.widgets['{}_endoscopy_results'.format(label)].grid(row = i + 2,column = 1, sticky = W, pady = 1, padx = (0, 0), columnspan = 2)

        tk.Label(self.subframe, text = "Specialist(s) name(s)", font = header_font).grid(row = 20,column = 0, sticky = W, pady = 1)
        tk.Label(self.subframe, text = "Clinic location(s)", font = header_font).grid(row = 22,column = 0, sticky = W, pady = 1)

        # Specialists and clinics
        self.widgets['endoscopy_specialists'].grid(row = 21,column = 0, sticky = W, pady = 1, columnspan = 2)
        self.widgets['endoscopy_clinics'].grid(row = 23,column = 0, sticky = W, pady = 1, columnspan = 2)
        if self.widgets['endoscopy'].get() == 1:
            self.subframe.grid_remove()
    def expand_page(self):
        self.subframe.grid()
        self.page_frame.update_idletasks()
        self.page_frame.configure(height = self.main_app.root.winfo_height() - self.main_app.navigation_frame.winfo_reqheight(), width = self.frame.winfo_reqwidth(), scrollregion=self.page_frame.bbox('all'))
        if self.frame.winfo_reqwidth() > self.main_app.root.winfo_width():
            self.main_app.root.configure(width = self.frame.winfo_reqwidth() + 20)
    def minimize_page(self):
        self.subframe.grid_remove()
        self.page_frame.update_idletasks()
        self.page_frame.configure(height = self.main_app.root.winfo_height() - self.main_app.navigation_frame.winfo_reqheight(), width = self.frame.winfo_reqwidth(), scrollregion=self.page_frame.bbox('all'))
    def write_summary(self, file = None, path = None, file_name = None):
        super().write_summary(file = file, path = path, file_name = file_name)
        try: # ~~~~~~ From page two ~~~~~~
            self.file.write("\nB. Procedures\n")
            self.file.write("\tB1. Have you ever had an upper GI endoscopy? {}\n".format("Yes" if not self.widgets['endoscopy'].get() else "No"))
            if not self.widgets['endoscopy'].get():
                for procedure in ["First", "Second", "Third", "Fourth", "Last"]:
                    if self.widgets['{}_endoscopy_age'.format(procedure)].get() != "" or self.widgets['{}_endoscopy_results'.format(procedure)].get() != "":
                        self.file.write("\t\t{} procedure year: {}\tResults: {}\n".format(procedure, self.widgets['{}_endoscopy_age'.format(procedure)].get(), self.widgets['{}_endoscopy_results'.format(procedure)].get()))

                if self.widgets['endoscopy_specialists'].get() != "":
                    self.file.write("\t\tSpecialist(s) name(s): {}\n".format(self.widgets['endoscopy_specialists'].get()))
                if self.widgets['endoscopy_clinics'].get() != "":
                    self.file.write("\t\tClinic locations: {}\n".format(self.widgets['endoscopy_clinics'].get()))
        except:
            print("Error during writing of page two")
        if path != None:
            self.file.close()
    def write_output(self, file, error_file, year_of_birth):
        self.write_entry('endoscopy response', "yes" if not self.widgets['endoscopy'].get() else "no", file, error_file)
        for i in ["First", "Second", "Third", "Fourth", "Last"]:
            if self.widgets['{}_endoscopy_age'.format(i)].get() != "":
                try:
                    if len(self.widgets['{}_endoscopy_age'.format(i)].get()) < 4:
                        self.write_entry("{} endoscopy age".format(i), int(year_of_birth) + int(self.widgets['{}_endoscopy_age'.format(i)].get()) if year_of_birth != "" else "", file, error_file)
                        self.write_entry("{} endoscopy age".format(i), self.widgets['{}_endoscopy_age'.format(i)].get(), file, error_file)
                    elif len(self.widgets['{}_endoscopy_age'.format(i)].get()) == 4:
                        self.write_entry("{} endoscopy age".format(i), self.widgets['{}_endoscopy_age'.format(i)].get(), file, error_file)
                        self.write_entry("{} endoscopy age".format(i), int(self.widgets['{}_endoscopy_age'.format(i)].get()) - int(year_of_birth) if year_of_birth != "" else "", file, error_file)
                    else:
                        self.write_entry("{} endoscopy age".format(i), self.widgets['{}_endoscopy_age'.format(i)].get(), file, error_file, tabs = 2)
                except:
                    try:
                        self.write_entry("{} endoscopy age".format(i), self.widgets['{}_endoscopy_age'.format(i)].get(), file, error_file, tabs = 2)
                    except:
                        file.write("\t\t")
            else:
                file.write("\t\t")
            self.write_entry("{} endoscopy results".format(i), self.widgets['{}_endoscopy_results'.format(i)].get(), file, error_file)
        self.write_entry("endoscopy specialists".format(i), self.widgets['endoscopy_specialists'].get(), file, error_file)
        self.write_entry("endoscopy clinics".format(i), self.widgets['endoscopy_clinics'].get(), file, error_file)
    def testing(self):
        self.widgets['endoscopy'].var.set(0)
        for i in ["First", "Second", "Third", "Fourth", "Last"]:
            self.widgets['{}_endoscopy_age'.format(i)].insert(0, '{} endoscopy age'.format(i))
            self.widgets['{}_endoscopy_results'.format(i)].insert(0, '{} endoscopy results'.format(i))
        self.widgets['endoscopy_specialists'].insert(0, 'endoscopy specialists')
        self.widgets['endoscopy_clinics'].insert(0, 'endoscopy clinics')
class page_three(pages):                                                        # Colonoscopy
    # Has the subject had a colonoscopy? (Y/N)
    #       Age of colonoscopy
    #       Results of colonoscopy
    #       Specialists
    #       Clinic Locations
    def __init__(self, main_app, page, frame_page):
        super().__init__(main_app, page, frame_page)
        self.widgets['colonoscopy'] = radiobutton(['Yes', 'No'], self.frame)
        self.widgets['colonoscopy'].add_command(self.expand_page, 'Yes')
        self.widgets['colonoscopy'].add_command(self.minimize_page, 'No')
        self.widgets['colonoscopy'].var.set(1)

        self.subframe = tk.Frame(self.frame)

        for i in ["First", "Second", "Third", "Fourth", "Last"]:
            self.widgets['{}_colonoscopy_age'.format(i)] = tk.Entry(self.subframe, bg = 'light grey', font = header_font)
            self.widgets['{}_colonoscopy_results'.format(i)] = text(self.subframe, height = 2, bg = 'light grey', font = header_font)

        self.widgets['colonoscopy_specialists'] = text(self.subframe, height = 2, bg = 'light grey', font = header_font)
        self.widgets['colonoscopy_clinics'] = text(self.subframe, height = 2, bg = 'light grey', font = header_font)
    def build(self):
        self.frame.grid(row = 0, column = 0, columnspan = 2)
        tk.Label(self.frame, text = "B2: Colonoscopy", font = title_font).grid(row = 0,column = 0, sticky = W, pady = 1)
        tk.Label(self.frame, text = "\tHas subject had a colonoscopy?", font = label_font).grid(row = 1,column = 0, sticky = W, pady = 1)

        self.widgets['colonoscopy'].place(rows = [1,1], columns = [1,2])

        self.subframe.grid(row = 2, column = 0, columnspan = 3)

        for i, label in zip([0,4,8,12,16], ["First", "Second", "Third", "Fourth", "Last"]):
            tk.Label(self.subframe, text = "{} colonoscopy".format(label), font = header_font).grid(row = i,column = 0, sticky = W, pady = 1)
            tk.Label(self.subframe, text = "\tYear/ Age", font = label_font).grid(row = i + 1,column = 0, sticky = W, pady = 1)
            tk.Label(self.subframe, text = "\tResults", font = label_font).grid(row = i + 2,column = 0, sticky = W, pady = 1)
            self.widgets['{}_colonoscopy_age'.format(label)].grid(row = i + 1,column = 1, sticky = W, pady = 1, columnspan = 2)
            self.widgets['{}_colonoscopy_results'.format(label)].grid(row = i + 2,column = 1, sticky = W, pady = 1, padx = (0, 0), columnspan = 2)

        tk.Label(self.subframe, text = "Specialist(s) name(s)", font = header_font).grid(row = 20,column = 0, sticky = W, pady = 1)
        tk.Label(self.subframe, text = "Clinic location(s)", font = header_font).grid(row = 22,column = 0, sticky = W, pady = 1)

        # Specialists and clinics
        self.widgets['colonoscopy_specialists'].grid(row = 21,column = 0, sticky = W, pady = 1, columnspan = 2)
        self.widgets['colonoscopy_clinics'].grid(row = 23,column = 0, sticky = W, pady = 1, columnspan = 2)
        if self.widgets['colonoscopy'].get() == 1:
            self.subframe.grid_remove()
    def expand_page(self):
        self.subframe.grid()
        self.page_frame.update_idletasks()
        self.page_frame.configure(height = self.main_app.root.winfo_height() - self.main_app.navigation_frame.winfo_reqheight(), width = self.frame.winfo_reqwidth(), scrollregion=self.page_frame.bbox('all'))
        if self.frame.winfo_reqwidth() > self.main_app.root.winfo_width():
            self.main_app.root.configure(width = self.frame.winfo_reqwidth() + 20)
    def minimize_page(self):
        self.subframe.grid_remove()
        self.page_frame.update_idletasks()
        self.page_frame.configure(height = self.main_app.root.winfo_height() - self.main_app.navigation_frame.winfo_reqheight(), width = self.frame.winfo_reqwidth(), scrollregion=self.page_frame.bbox('all'))
    def write_summary(self, file = None, path = None, file_name = None):
        super().write_summary(file = file, path = path, file_name = file_name)
        try: # ~~~~~~ From page two ~~~~~~
            self.file.write("\tB2. Have you ever had a colonoscopy? {}\n".format("Yes" if not self.widgets['colonoscopy'].get() else "No"))
            if not self.widgets['colonoscopy'].get():
                for procedure in ["First", "Second", "Third", "Fourth", "Last"]:
                    if self.widgets['{}_colonoscopy_age'.format(procedure)].get() != "" or self.widgets['{}_colonoscopy_results'.format(procedure)].get() != "":
                        self.file.write("\t\t{} procedure year: {}\tResults: {}\n".format(procedure, self.widgets['{}_colonoscopy_age'.format(procedure)].get(), self.widgets['{}_colonoscopy_results'.format(procedure)].get()))

                if self.widgets['colonoscopy_specialists'].get() != "":
                    self.file.write("\t\tSpecialist(s) name(s): {}\n".format(self.widgets['colonoscopy_specialists'].get()))
                if self.widgets['colonoscopy_clinics'].get() != "":
                    self.file.write("\t\tClinic locations: {}\n".format(self.widgets['colonoscopy_clinics'].get()))
        except:
            print("Error during writing of page three")
        if path != None:
            self.file.close()
    def write_output(self, file, error_file, year_of_birth):
        self.write_entry('colonoscopy response', "yes" if not self.widgets['colonoscopy'].get() else "no", file, error_file)
        for i in ["First", "Second", "Third", "Fourth", "Last"]:
            if self.widgets['{}_colonoscopy_age'.format(i)].get() != "":
                try:
                    if len(self.widgets['{}_colonoscopy_age'.format(i)].get()) < 4:
                        self.write_entry("{} colonoscopy age".format(i), int(year_of_birth) + int(self.widgets['{}_colonoscopy_age'.format(i)].get()) if year_of_birth != "" else "", file, error_file)
                        self.write_entry("{} colonoscopy age".format(i), self.widgets['{}_colonoscopy_age'.format(i)].get(), file, error_file)
                    elif len(self.widgets['{}_colonoscopy_age'.format(i)].get()) == 4:
                        self.write_entry("{} colonoscopy age".format(i), self.widgets['{}_colonoscopy_age'.format(i)].get(), file, error_file)
                        self.write_entry("{} colonoscopy age".format(i), int(self.widgets['{}_colonoscopy_age'.format(i)].get()) - int(year_of_birth) if year_of_birth != "" else "", file, error_file)
                    else:
                        self.write_entry("{} colonoscopy age".format(i), self.widgets['{}_colonoscopy_age'.format(i)].get(), file, error_file, tabs = 2)
                except:
                    try:
                        self.write_entry("{} colonoscopy age".format(i), self.widgets['{}_colonoscopy_age'.format(i)].get(), file, error_file, tabs = 2)
                    except:
                        file.write("\t\t")
            else:
                file.write("\t\t")
            self.write_entry("{} colonoscopy results".format(i), self.widgets['{}_colonoscopy_results'.format(i)].get(), file, error_file)
        self.write_entry("colonoscopy specialists".format(i), self.widgets['colonoscopy_specialists'].get(), file, error_file)
        self.write_entry("colonoscopy clinics".format(i), self.widgets['colonoscopy_clinics'].get(), file, error_file)
    def testing(self):
        self.widgets['colonoscopy'].var.set(0)
        for i in ["First", "Second", "Third", "Fourth", "Last"]:
            self.widgets['{}_colonoscopy_age'.format(i)].insert(0, '{} colonoscopy age'.format(i))
            self.widgets['{}_colonoscopy_results'.format(i)].insert(0, '{} colonoscopy results'.format(i))
        self.widgets['colonoscopy_specialists'].insert(0, 'colonoscopy specialists')
        self.widgets['colonoscopy_clinics'].insert(0, 'colonoscopy clinics')
class page_four(pages):                                                         # Additional Procedures
    def __init__(self, main_app, page, frame_page):
        super().__init__(main_app, page, frame_page)
        self.subframes = {}
        for procedure in ["Abdominal MRI", "CT", "Ultrasound", "Capsule Endoscopy", "Other"]:
            self.subframes[procedure] = tk.Frame(self.frame)
            for field in ["Procedure", "Year", "Results", "Notes"]:
                for time in ['First', 'Second', 'Third']:
                    self.widgets['{}_{}_{}'.format(time, procedure, field)] = tk.Entry(self.subframes[procedure], bg = 'light grey', font = header_font)
    def build(self):
        self.frame.grid(row = 0, column = 0, columnspan = 2)
        tk.Label(self.frame, text = "B3: Additional Procedures", font = title_font).grid(row = 0,column = 0, sticky = W, columnspan = 3)
        for i, procedure in enumerate(["Abdominal MRI", "CT", "Ultrasound", "Capsule Endoscopy", "Other"]):
            self.subframes[procedure].grid(row = i + 2, column = 0, columnspan = 5, sticky = W)
            tk.Label(self.subframes[procedure], text = "{}".format(procedure), font = header_font).grid(row = 0, column = 0, sticky = W, columnspan = 1)
            if i == 0:
                for j, label in enumerate(["Procedure", "Year", "Results", "Notes"]):
                    tk.Label(self.subframes[procedure], text = label, font = header_font).grid(row = 0, column = j + 1, sticky = W, pady = 1, columnspan = 1)

            for j, time in enumerate(['First', 'Second', 'Third']):
                tk.Label(self.subframes[procedure], text = str(j + 1) + "\t\t", font = header_font).grid(row = j + 1,column = 0, sticky = W, pady = 1, columnspan = 1)
                for k, field in enumerate(["Procedure", "Year", "Results", "Notes"]):
                    self.widgets['{}_{}_{}'.format(time, procedure, field)].grid(row = j + 1, column = k + 1, sticky = W, pady = 1, columnspan = 1)
                tk.Label(self.subframes[procedure], text = "", font = 'Helvetica 3').grid(row = j + 2, column = 0)
    def write_summary(self, file = None, path = None, file_name = None):
        super().write_summary(file = file, path = path, file_name = file_name)
        try:
            self.file.write("\tB3. List any other procedures\n")
            for procedure in ["Abdominal MRI", "CT", "Ultrasound", "Capsule Endoscopy", "Other"]:
                for time in ['First', 'Second', 'Third']:
                    if self.widgets['{}_{}_Procedure'.format(time, procedure)].get() != "" or self.widgets['{}_{}_Year'.format(time, procedure)].get() != "" or self.widgets['{}_{}_Results'.format(time, procedure)].get() != "" or self.widgets['{}_{}_Notes'.format(time, procedure)].get() != "":
                        self.file.write("\t\tProcedure: {}\tYear: {}\tResults: {}\n".format(self.widgets['{}_{}_Procedure'.format(time, procedure)].get(), self.widgets['{}_{}_Year'.format(time, procedure)].get(), self.widgets['{}_{}_Results'.format(time, procedure)].get()))
                        self.file.write("{}".format("\t\t\tNotes:{}\n".format(self.widgets['{}_{}_Notes'.format(time, procedure)].get())) if self.widgets['{}_{}_Notes'.format(time, procedure)].get() != "" else "")
        except:
            print("Error during writing of page four")
        if path != None:
            self.file.close()
    def write_output(self, file, error_file, year_of_birth):
        for procedure in ["Abdominal MRI", "CT", "Ultrasound", "Capsule Endoscopy", "Other"]:
            for time in ['First', 'Second', 'Third']:
                self.write_entry('{} {} Procedure'.format(procedure, time), self.widgets['{}_{}_Procedure'.format(time, procedure)].get(), file, error_file)
                self.write_entry('{} {} Year'.format(procedure, time), self.widgets['{}_{}_Year'.format(time, procedure)].get(), file, error_file)
                self.write_entry('{} {} Results'.format(procedure, time), '{}{}'.format(self.widgets['{}_{}_Results'.format(time, procedure)].get(), "{}Notes: {}".format("; " if self.widgets['{}_{}_Results'.format(time, procedure)].get() != "" else "", self.widgets['{}_{}_Notes'.format(time, procedure)].get()) if self.widgets['{}_{}_Notes'.format(time, procedure)].get() != "" else ""), file, error_file)
            file.write("\t\t\t")
    def testing(self):
        for procedure in ["Abdominal MRI", "CT", "Ultrasound", "Capsule Endoscopy", "Other"]:
            for field in ["Procedure", "Year", "Results", "Notes"]:
                for time in ['First', 'Second', 'Third']:
                    self.widgets['{}_{}_{}'.format(time, procedure, field)].insert(0, '{}_{}_{}'.format(time, procedure, field))
class symptoms_class(pages):
    def __init__(self, main_app, page, frame_page , symptoms, numbering):
        self.numbering = numbering
        self.symptoms = symptoms
        super().__init__(main_app, page, frame_page)
        self.subframes = {}
        self.response_frames = {}
        for symptom in self.symptoms:
            self.subframes['{}'.format(symptom)] = tk.Frame(self.frame)
            self.response_frames['{}'.format(symptom)] = tk.Frame(self.subframes['{}'.format(symptom)])
            self.widgets['{}'.format(symptom)] = radiobutton(['Yes', 'No'], self.subframes['{}'.format(symptom)])
            self.widgets['{}'.format(symptom)].var.set(1)
            self.widgets['{}'.format(symptom)].add_command(partial(self.expand_field, self.response_frames['{}'.format(symptom)]), 'Yes')
            self.widgets['{}'.format(symptom)].add_command(partial(self.collapse_field, self.response_frames['{}'.format(symptom)]), 'No')
            if symptom == 'loss of appetite':
                self.widgets['{}_frequency'.format(symptom)] = radiobutton(['Occasional', 'Regular'], self.response_frames['{}'.format(symptom)])
            else:
                self.widgets['{}_frequency'.format(symptom)] = radiobutton(['Occasional', 'Weekly', 'Daily or near daily'], self.response_frames['{}'.format(symptom)])
            self.widgets['{}_age'.format(symptom)] = tk.Entry(self.response_frames['{}'.format(symptom)], bg = 'light grey', font = header_font)
            self.widgets['{}_triggers'.format(symptom)] = text(self.response_frames['{}'.format(symptom)], height = 2, bg = 'light grey', font = header_font)
            self.widgets['{}_reliefs'.format(symptom)] = text(self.response_frames['{}'.format(symptom)], height = 2, bg = 'light grey', font = header_font)
            self.widgets['{}_symptoms_stopped'.format(symptom)] = radiobutton(['Stopped', 'Still Experiencing'], self.response_frames['{}'.format(symptom)])
            self.widgets['{}_age_last_occured'.format(symptom)] = tk.Entry(self.response_frames['{}'.format(symptom)], bg = 'light grey', font = header_font)
    def build(self):
        self.frame.grid(row = 0, column = 0, columnspan = 2)
        tk.Label(self.frame, text = "C1: Health", font = title_font).grid(row = 0,column = 0, sticky = W, columnspan = 2)

        for i, symptom in enumerate(self.symptoms):
            self.subframes['{}'.format(symptom)].grid(row = i + 1, column = 0, sticky = W, columnspan = 2)
            tk.Label(self.subframes['{}'.format(symptom)], text = "{}) Has subject experienced {}?".format(i + self.numbering, symptom), font = header_font).grid(row = 0,column = 0, sticky = W, pady = 1, columnspan = 1)
            self.widgets['{}'.format(symptom)].place(rows = [0, 0], columns = [1,2])
            self.response_frames['{}'.format(symptom)].grid(row = 1, column = 0, columnspan = 3)
            for j, label in zip([0, 1, 2, 4, 6, 7], ["Frequency:", "Age symptoms started", "Symptom triggers", "Symptom reliefs", "Did symptoms stop or improve?", "Age of last occurance"]):
                tk.Label(self.response_frames['{}'.format(symptom)], text = '\t{}'.format(label), font = label_font).grid(row = j, column = 0, sticky = W)
            if symptom == "loss of appetite":
                self.widgets['{}_frequency'.format(symptom)].place(rows = [0,0], columns = [1,2])
            else:
                self.widgets['{}_frequency'.format(symptom)].place(rows = [0,0,0], columns = [1,2,3])
            self.widgets['{}_age'.format(symptom)].grid(row = 1, column = 1, columnspan = 3, sticky = W)
            self.widgets['{}_triggers'.format(symptom)].grid(row = 2, column = 1, padx = (0, 0), columnspan = 3, rowspan = 2, sticky = W)
            self.widgets['{}_reliefs'.format(symptom)].grid(row = 4, column = 1, padx = (0, 0), columnspan = 3, rowspan = 2, sticky = W)
            self.widgets['{}_symptoms_stopped'.format(symptom)].place(rows = [6,6], columns = [1,2])
            self.widgets['{}_age_last_occured'.format(symptom)].grid(row = 7, column = 1, columnspan = 3, sticky = W)
            tk.Label(self.response_frames['{}'.format(symptom)], text = " ", font = "Helvetica 12").grid(row = 8, column = 0, sticky = W)
            if self.widgets['{}'.format(symptom)].get() == 1:
                self.response_frames['{}'.format(symptom)].grid_remove()
    def expand_field(self, frame):
        frame.grid()
        self.page_frame.update_idletasks()
        self.page_frame.configure(height = self.main_app.root.winfo_height() - self.main_app.navigation_frame.winfo_reqheight(), width = self.frame.winfo_reqwidth(), scrollregion=self.page_frame.bbox('all'))
        if self.frame.winfo_reqwidth() > self.main_app.root.winfo_width():
            self.main_app.root.configure(width = self.frame.winfo_reqwidth() + 20)
    def collapse_field(self, frame):
        frame.grid_remove()
        self.page_frame.update_idletasks()
        self.page_frame.configure(height = self.main_app.root.winfo_height() - self.main_app.navigation_frame.winfo_reqheight(), width = self.frame.winfo_reqwidth(), scrollregion=self.page_frame.bbox('all'))
    def write_summary(self, file = None, path = None, file_name = None):
        super().write_summary(file = file, path = path, file_name = file_name)
        for i, symptom in enumerate(self.symptoms):
            try:
                if symptom == 'heartburn':
                    self.file.write("\nC. Health\n")
                self.file.write("\tC1.{}. Have you experienced {}? {}\n".format(i + self.numbering, symptom, "Yes" if not self.widgets['{}'.format(symptom)].get() else "No"))
                if not self.widgets['{}'.format(symptom)].get():
                    if symptom == "loss of appetite":
                        self.file.write("\t\tHow often do you experience {}? {}\n".format(symptom, "Occasional" if not self.widgets['{}_frequency'.format(symptom)].get() else "Regular"))
                    else:
                        self.file.write("\t\tHow often do you experience {}? {}\n".format(symptom, "Occasional" if self.widgets['{}_frequency'.format(symptom)].get() == 0 else "Weekly" if self.widgets['{}_frequency'.format(symptom)].get() == 1 else "Daily or nearly daily"))
                    self.file.write("{}".format("\t\tWhen did your symptoms start? {}\n".format(self.widgets['{}_age'.format(symptom)].get()) if self.widgets['{}_age'.format(symptom)].get() != "" else ""))
                    self.file.write("{}".format("\t\tIs there anything that triggers your symptoms?\n\t\t{}\n".format(self.widgets['{}_triggers'.format(symptom)].get()) if self.widgets['{}_triggers'.format(symptom)].get() != "" else ""))
                    self.file.write("{}".format("\t\tIs there anything that relieves your symptoms?\n\t\t{}\n".format(self.widgets['{}_reliefs'.format(symptom)].get() ) if self.widgets['{}_reliefs'.format(symptom)].get()  != "" else ""))
                    self.file.write("\t\tDid your symptoms stop or improve? {}\n".format("Stopped" if not self.widgets['{}_symptoms_stopped'.format(symptom)].get() else "Still Experiencing"))
                    self.file.write("{}".format("\t\tWhen did you last experience these symptoms? {}\n".format(self.widgets['{}_age_last_occured'.format(symptom)].get()) if self.widgets['{}_age_last_occured'.format(symptom)].get() != "" else ""))
            except:
                print("Error while writing: {}".format(symptom))
        if path != None:
            self.file.close()
    def write_output(self, file, error_file, year_of_birth):
        for symptom in self.symptoms:
            if not self.widgets['{}'.format(symptom)].get():
                try:
                    if symptom == 'loss of appetite':
                        file.write("{}\t".format('Occasional' if not self.widgets['{}_frequency'.format(symptom)].get() else 'Regular'))
                    else:
                        file.write("{}\t".format('Occasional' if not self.widgets['{}_frequency'.format(symptom)].get() == 0 else 'Weekly' if self.widgets['{}_frequency'.format(symptom)].get() == 1 else 'Daily or near daily'))
                except:
                    write("\t")
                    error_file.write("Failed to write {} frequency".format(symptom))
                self.write_entry('{} age'.format(symptom), self.widgets['{}_age'.format(symptom)].get(), file, error_file)
                self.write_entry('{} triggers'.format(symptom), self.widgets['{}_triggers'.format(symptom)].get(), file, error_file)
                self.write_entry('{} reliefs'.format(symptom), self.widgets['{}_reliefs'.format(symptom)].get(), file, error_file)
                self.write_entry('{} stop status'.format(symptom), 'Stopped' if not self.widgets['{}_symptoms_stopped'.format(symptom)].get() else 'Still experiencing', file, error_file)
                self.write_entry('{} age last occured'.format(symptom), self.widgets['{}_age_last_occured'.format(symptom)].get(), file, error_file)
            else:
                file.write("Never\t\t\t\t\t\t")
    def testing(self):
        for symptom in self.symptoms:
            self.widgets['{}'.format(symptom)].var.set(0)
            self.widgets['{}_frequency'.format(symptom)].var.set(1)
            self.widgets['{}_age'.format(symptom)].insert(0, '{} age'.format(symptom))
            self.widgets['{}_triggers'.format(symptom)].insert(0, '{} triggers'.format(symptom))
            self.widgets['{}_reliefs'.format(symptom)].insert(0, '{}_reliefs'.format(symptom))
            self.widgets['{}_symptoms_stopped'.format(symptom)].var.set(1)
            self.widgets['{}_age_last_occured'.format(symptom)].insert(0, '{} age last occurred'.format(symptom))
class page_five(symptoms_class):                                                # Heartburn; Nausea; Vomiting
    def __init__(self, main_app, page, frame_page):
        super().__init__(main_app, page, frame_page , ['heartburn', 'nausea', 'vomiting'], 1)
class page_six(symptoms_class):                                                 # Stomach Pain; Regurgitation; Loss of appetite
    def __init__(self, main_app, page, frame_page):
        super().__init__(main_app, page, frame_page , ["stomach pain", "regurgitation", "loss of appetite"], 4)
class page_seven(symptoms_class):                                               # Abdominal Pain; Rectal Bleeding
    def __init__(self, main_app, page, frame_page):
        super().__init__(main_app, page, frame_page , ["abdominal pain", "rectal bleeding"], 7)
class conditions_class(pages):
    def __init__(self, main_app, page, frame_page , conditions, numbering):
        self.numbering = numbering
        self.conditions = conditions
        super().__init__(main_app, page, frame_page)
        self.subframes = {}
        self.response_frames = {}
        self.med_frames = {}
        for condition in self.conditions:
            self.subframes['{}'.format(condition)] = tk.Frame(self.frame)
            self.response_frames['{}'.format(condition)] = tk.Frame(self.subframes['{}'.format(condition)])
            self.med_frames['{}'.format(condition)] = tk.Frame(self.response_frames['{}'.format(condition)])
            self.widgets['{}'.format(condition)] = radiobutton(['Yes', 'No'], self.subframes['{}'.format(condition)])
            self.widgets['{}'.format(condition)].var.set(1)
            self.widgets['{}'.format(condition)].add_command(partial(self.expand_field, self.response_frames['{}'.format(condition)]), 'Yes')
            self.widgets['{}'.format(condition)].add_command(partial(self.collapse_field, self.response_frames['{}'.format(condition)]), 'No')
            self.widgets['{}_age'.format(condition)] = tk.Entry(self.response_frames['{}'.format(condition)], bg = 'light grey', font = header_font)

            if condition == 'anemia':
                for label in ["Iron-deficiency Anemia", "Aplastic Anemia", "Pernicious Anemia", "Hemolytic Anemia", "Not sure"]:
                    self.widgets[label] = checkbutton(label, self.response_frames['{}'.format(condition)])
                self.widgets['anemia_treatments'] = text(self.response_frames['{}'.format(condition)],  height = 2,bg = 'light grey', font = header_font)
            else:
                if condition == "inflammatory bowel disease":
                    self.widgets['{}_colectomy'.format(condition)] = radiobutton(['Yes', 'No'], self.response_frames['{}'.format(condition)])
                    self.widgets['{}_colectomy'.format(condition)].var.set(1)
                self.widgets['{}_medication'.format(condition)] = radiobutton(['Yes', 'No'], self.response_frames['{}'.format(condition)])
                self.widgets['{}_medication'.format(condition)].var.set(1)
                self.widgets['{}_medication'.format(condition)].add_command(partial(self.expand_field, self.med_frames['{}'.format(condition)]), 'Yes')
                self.widgets['{}_medication'.format(condition)].add_command(partial(self.collapse_field, self.med_frames['{}'.format(condition)]), 'No')

                self.widgets['{}_medication_length'.format(condition)] = tk.Entry(self.med_frames['{}'.format(condition)], bg = 'light grey', font = header_font)
                self.widgets['{}_medication_frequency'.format(condition)] = tk.Entry(self.med_frames['{}'.format(condition)], bg = 'light grey', font = header_font)
                self.widgets['{}_medication_list'.format(condition)] = text(self.med_frames['{}'.format(condition)], height = 2, bg = 'light grey', font = header_font)
                if condition == "helicobacter pylori":
                    self.widgets['{}_success'.format(condition)] = radiobutton(['Yes', 'No'], self.med_frames['{}'.format(condition)])
                    self.widgets['{}_success'.format(condition)].var.set(1)
                    self.widgets['{}_follow-up'.format(condition)] = radiobutton(['Yes', 'No'], self.med_frames['{}'.format(condition)])
                    self.widgets['{}_follow-up'.format(condition)].var.set(1)
    def build(self):
        self.frame.grid(row = 0, column = 0, columnspan = 2)
        tk.Label(self.frame, text = "C2: Health", font = title_font).grid(row = 0,column = 0, sticky = W, columnspan = 2)
        for i, condition in enumerate(self.conditions):
            self.subframes['{}'.format(condition)].grid(row = i + 1, column = 0, columnspan = 2, sticky = EW)
            tk.Label(self.subframes['{}'.format(condition)], text = "{}) Has subject been diagnosed with {}?".format(i + self.numbering, condition), font = header_font).grid(row = 0,column = 0, sticky = W, pady = 1, columnspan = 1)
            self.widgets['{}'.format(condition)].place(rows = [0,0], columns = [1,2])
            self.response_frames['{}'.format(condition)].grid(row = 1, column = 0, columnspan = 3, sticky = EW)
            tk.Label(self.response_frames['{}'.format(condition)], text = "\tAge diagnosed:", font = label_font).grid(row = 0, column = 0, sticky = W)
            self.widgets['{}_age'.format(condition)].grid(row = 0, column = 1, columnspan = 3, sticky = W)
            if condition == 'anemia':
                tk.Label(self.response_frames['{}'.format(condition)], text = "\tType of anemia", font = label_font).grid(row = 1, column = 0, sticky = W, columnspan = 2)
                self.widgets["Iron-deficiency Anemia"].place(row = 2, column = 0, padx = (100, 0))
                self.widgets["Aplastic Anemia"].place(row = 2, column = 1)
                self.widgets["Pernicious Anemia"].place(row = 2, column = 2)
                self.widgets["Hemolytic Anemia"].place(row = 3, column = 0, padx = (100, 0))
                self.widgets["Not sure"].place(row = 3, column = 1)

                tk.Label(self.response_frames['{}'.format(condition)], text = "\tList treatments:", font = label_font).grid(row = 4, column = 0, sticky = W, columnspan = 2)
                self.widgets['anemia_treatments'].grid(row = 5, column = 0, padx = (100, 0), columnspan = 3, sticky = W)
            else:
                if condition == "inflammatory bowel disease":
                    tk.Label(self.response_frames['{}'.format(condition)], text = "\tDid they have a colectomy or proctocolectomy?", font = label_font).grid(row = 1, column = 0, sticky = W)
                    self.widgets['{}_colectomy'.format(condition)].place(rows = [1,1], columns = [1,2])
                tk.Label(self.response_frames['{}'.format(condition)], text = "\tWas medication taken?", font = label_font).grid(row = 2, column = 0, sticky = W)
                self.widgets['{}_medication'.format(condition)].place(rows = [2,2], columns = [1,2])
                self.med_frames['{}'.format(condition)].grid(row = 3, column = 0, columnspan = 3)
                tk.Label(self.med_frames['{}'.format(condition)], text = "\tHow long was medication taken?", font = label_font).grid(row = 0, column = 0, sticky = W)
                tk.Label(self.med_frames['{}'.format(condition)], text = "\tHow often was medication taken?", font = label_font).grid(row = 1, column = 0, sticky = W)
                self.widgets['{}_medication_length'.format(condition)].grid(row = 0, column = 1, sticky = W, columnspan = 2)
                self.widgets['{}_medication_frequency'.format(condition)].grid(row = 1, column = 1, sticky = W, columnspan = 2)
                tk.Label(self.med_frames['{}'.format(condition)], text = "\tList Medications", font = label_font).grid(row = 2, column = 0, sticky = W)
                self.widgets['{}_medication_list'.format(condition)].grid(row = 3, column = 0, padx = (95, 0), columnspan = 3, sticky = W)
                if condition == "helicobacter pylori":
                    tk.Label(self.med_frames['{}'.format(condition)], text = "\tWas the treatment successful?", font = label_font).grid(row = 4, column = 0, sticky = W)
                    tk.Label(self.med_frames['{}'.format(condition)], text = "\tWas this confirmed through a follow-up test?", font = label_font).grid(row = 5, column = 0, sticky = W)
                    self.widgets['{}_success'.format(condition)].place(rows = [4,4], columns = [1,2])
                    self.widgets['{}_follow-up'.format(condition)].place(rows = [5,5], columns = [1,2])
                if self.widgets['{}_medication'.format(condition)].get() == 1:
                    self.med_frames['{}'.format(condition)].grid_remove()
            if self.widgets['{}'.format(condition)].get() ==1:
                self.response_frames['{}'.format(condition)].grid_remove()
    def expand_field(self, frame):
        frame.grid()
        self.page_frame.update_idletasks()
        self.page_frame.configure(height = self.main_app.root.winfo_height() - self.main_app.navigation_frame.winfo_reqheight(), width = self.frame.winfo_reqwidth(), scrollregion=self.page_frame.bbox('all'))
        if self.frame.winfo_reqwidth() > self.main_app.root.winfo_width():
            self.main_app.root.configure(width = self.frame.winfo_reqwidth() + 20)
    def collapse_field(self, frame):
        frame.grid_remove()
        self.page_frame.update_idletasks()
        self.page_frame.configure(height = self.main_app.root.winfo_height() - self.main_app.navigation_frame.winfo_reqheight(), width = self.frame.winfo_reqwidth(), scrollregion=self.page_frame.bbox('all'))
    def write_summary(self, file = None, path = None, file_name = None):
        super().write_summary(file = file, path = path, file_name = file_name)
        for i, condition in enumerate(self.conditions):
            try:
                self.file.write("\tC2.{}. Have you ever been diagnosed with {}: {}\n".format(i + self.numbering, condition, "Yes" if not self.widgets['{}'.format(condition)].get() else "No"))
                if not self.widgets['{}'.format(condition)].get():
                    self.file.write("{}".format("\t\tHow old were you when you were diagnosed? {}\n".format(self.widgets['{}_age'.format(condition)].get()) if self.widgets['{}_age'.format(condition)].get() != "" else ""))
                    if condition != "anemia":
                        if condition == "inflammatory bowel disease":
                            self.file.write("\t\tDid you ever have a colectomy or proctocolectomy? {}\n".format("Yes" if not self.widgets['{}_colectomy'.format(condition)].get() else "No"))
                        self.file.write("\t\tDid you take any medication for this? {}\n".format("Yes" if not self.widgets['{}_medication'.format(condition)].get() else "No"))
                        if not self.widgets['{}_medication'.format(condition)].get():
                            self.file.write("{}".format("\t\t\tHow long did you take the medication? {}\n".format(self.widgets['{}_medication_length'.format(condition)].get()) if self.widgets['{}_medication_length'.format(condition)].get() != "" else ""))
                            self.file.write("{}".format("\t\t\tHow often did you take them? {}\n".format(self.widgets['{}_medication_frequency'.format(condition)].get()) if self.widgets['{}_medication_frequency'.format(condition)].get() != "" else ""))
                            self.file.write("{}".format("\t\t\tList medications taken: {}\n".format(self.widgets['{}_medication_list'.format(condition)].get()) if self.widgets['{}_medication_list'.format(condition)].get() != "" else ""))
                            if condition == "helicobacter pylori":
                                self.file.write("\t\t\tWas the treatment successful? {}\n".format("Yes" if not self.widgets['{}_success'.format(condition)].get() else "No"))
                                self.file.write("\t\t\tWas this confirmed through a follow-up test? {}\n".format("Yes" if not self.widgets['{}_follow-up'.format(condition)].get() else "No"))
                    else:
                        anemia_check = []
                        for label in ["Iron-deficiency Anemia", "Aplastic Anemia", "Pernicious Anemia", "Hemolytic Anemia", "Not sure"]:
                            anemia_check.append(self.widgets[label].get())
                        if any(anemia_check):
                            self.file.write("\t\tWhat type of anemia were you diagnosed with? ")
                            for label in ["Iron-deficiency Anemia", "Aplastic Anemia", "Pernicious Anemia", "Hemolytic Anemia", "Not sure"]:
                                self.file.write("{}".format('\t{}'.format(label) if self.widgets[label].get() else ""))
                            self.file.write("\n")
                        self.file.write("{}".format("\t\tList treatments recieved: {}\n".format(self.widgets['anemia_treatments'].get()) if self.widgets['anemia_treatments'].get() != "" else ""))
            except:
                print("Error while writing: {}".format(condition))
        if path != None:
            self.file.close()
    def write_output(self, file, error_file, year_of_birth):
        # Gastric Reflux = 6
        # Gatric Ulcer = 6
        # Anemia = 6
        # IBS = 6
        # IBD = 7
        # Helicobacter pylori infection = 8
        for condition in self.conditions:
            if not self.widgets['{}'.format(condition)].get():
                file.write("yes\t")
                self.write_entry("{} age".format(condition), self.widgets['{}_age'.format(condition)].get(), file, error_file)
                if condition == "anemia":
                    try:
                        for label in ["Iron-deficiency Anemia", "Aplastic Anemia", "Pernicious Anemia", "Hemolytic Anemia", "Not sure"]:
                            file.write(" {}".format(" {}".format(label) if self.widgets[label].get() else ""))
                        file.write("\t\t\t")
                    except:
                        file.write("\t\t\t")
                        error_file.write("Failed to write anemia type")
                    self.write_entry("anemia treatments", self.widgets['anemia_treatments'].get(), file, error_file)
                else:
                    self.write_entry('{} medication response'.format(condition), "yes" if not self.widgets['{}_medication'.format(condition)].get() else 'no', file, error_file)
                    self.write_entry('{} medication length'.format(condition), self.widgets['{}_medication_length'.format(condition)].get(), file, error_file)
                    self.write_entry('{} medication frequency'.format(condition), self.widgets['{}_medication_frequency'.format(condition)].get(), file, error_file)
                    self.write_entry('{} medication list'.format(condition), self.widgets['{}_medication_list'.format(condition)].get(), file, error_file)
                    if condition == "inflammatory bowel disease":
                        self.write_entry('{} colectomy'.format(condition), "yes" if not self.widgets['{}_colectomy'.format(condition)].get() else 'no', file, error_file)
                    if condition == "helicobacter pylori":
                        self.write_entry('{} treatment outcome'.format(condition), "yes" if not self.widgets['{}_success'.format(condition)].get() else 'no', file, error_file)
                        self.write_entry('{} follow up'.format(condition), "yes" if not self.widgets['{}_follow-up'.format(condition)].get() else 'no', file, error_file)
            else:
                file.write("no\t\t\t\t\t\t")
                if condition == "inflammatory bowel disease":
                    file.write("\t")
                if condition == "helicobacter pylori":
                    file.write("\t\t")
    def testing(self):
        for condition in self.conditions:
            self.widgets['{}'.format(condition)].var.set(0)
            self.widgets['{}_age'.format(condition)].insert(0, '{}_age'.format(condition))
            if condition == 'anemia':
                self.widgets['anemia_treatments'].insert(0, 'anemia treatments')
            else:
                if condition == "inflammatory bowel disease":
                    self.widgets['{}_colectomy'.format(condition)].var.set(0)
                self.widgets['{}_medication'.format(condition)].var.set(0)
                self.widgets['{}_medication_length'.format(condition)].insert(0, '{} medication length'.format(condition))
                self.widgets['{}_medication_frequency'.format(condition)].insert(0, '{} medication frequency'.format(condition))
                self.widgets['{}_medication_list'.format(condition)].insert(0, '{} medication list'.format(condition))
                if condition == "helicobacter pylori":
                    self.widgets['{}_success'.format(condition)].var.set(0)
                    self.widgets['{}_follow-up'.format(condition)].var.set(0)
class page_eight(conditions_class):                                             # Gastric Reflux; Gastric Ulcer; Anemia
    def __init__(self, main_app, page, frame_page):
        super().__init__(main_app, page, frame_page , ["gastric reflux", "gastric ulcer", "anemia"], 1)
class page_nine(conditions_class):                                              # IBS; IBD; Helicobacter pylori
    def __init__(self, main_app, page, frame_page):
        super().__init__(main_app, page, frame_page , ["irritable bowel syndrome", "inflammatory bowel disease", "helicobacter pylori"], 4)
class page_ten(pages):                                                          # Additional Diagnosis
    def __init__(self, main_app, page, frame_page):
        super().__init__(main_app, page, frame_page)
        for label in ["Desmoid tumours", "Osteomas", "Dental abnormalities", "Benign cutaneous lesions", "Congenital hypertrophy and retinal pigment epithelium"]:
            self.widgets[label] = checkbutton(label, self.frame)
            self.widgets['{}_expanded'.format(label)] = tk.Entry(self.frame, bg = 'light grey', font = header_font)
            self.widgets[label].add_command(partial(self.expand_field, self.widgets[label], self.widgets['{}_expanded'.format(label)]))
    def build(self):
        self.frame.grid(row = 0, column = 0, columnspan = 2)
        tk.Label(self.frame, text = "C3: Has subject been diagnosed with any of the following?", font = title_font).grid(row = 0,column = 0, columnspan = 2, sticky = W, pady = 1)
        for i, label in enumerate(["Desmoid tumours", "Osteomas", "Dental abnormalities", "Benign cutaneous lesions", "Congenital hypertrophy and retinal pigment epithelium"]):
            self.widgets[label].place(row = i + 1, column = 0, padx = (20,0))
            self.widgets['{}_expanded'.format(label)].grid(row = i + 1, column = 1)
            if self.widgets[label].get() == 0:
                self.widgets['{}_expanded'.format(label)].grid_remove()
    def expand_field(self, checkbutton, entry):
        if checkbutton.get() == 1:
            entry.grid()
        else:
            entry.grid_remove()
        self.page_frame.update_idletasks()
        self.page_frame.configure(height = self.main_app.root.winfo_height() - self.main_app.navigation_frame.winfo_reqheight(), width = self.frame.winfo_reqwidth(), scrollregion=self.page_frame.bbox('all'))
        if self.frame.winfo_reqwidth() > self.main_app.root.winfo_width():
            self.main_app.root.configure(width = self.frame.winfo_reqwidth() + 20)
    def write_summary(self, file = None, path = None, file_name = None):
        super().write_summary(file = file, path = path, file_name = file_name)
        try:
            self.file.write("\tC3. Have you been diagnosed with any of the following?\n")
            for label in ["Desmoid tumours", "Osteomas", "Dental abnormalities", "Benign cutaneous lesions", "Congenital hypertrophy and retinal pigment epithelium"]:
                self.file.write("\t\t{}: {} {}\n".format(label, "Yes" if self.widgets[label].get() else "No", "-{}".format(self.widgets['{}_expanded'.format(label)].get()) if self.widgets['{}_expanded'.format(label)].get() != "" else ""))
        except:
            print("Error during writing of page ten")
        if path != None:
            self.file.close()
    def write_output(self, file, error_file, year_of_birth):
        try:
            for label in ["Desmoid tumours", "Osteomas", "Dental abnormalities", "Benign cutaneous lesions", "Congenital hypertrophy and retinal pigment epithelium"]:
                file.write("{}".format("{}{};".format(label, " - {}".format(self.widgets['{}_expanded'.format(label)].get()) if self.widgets['{}_expanded'.format(label)].get() != "" else "") if self.widgets[label].get() else ""))
        except:
            error_file.write("Failed to write additional conditions")
        file.write("\t")
    def testing(self):
        self.widgets["Desmoid tumours"].var.set(1)
        self.widgets['Desmoid tumours_expanded'].insert(0, "Desmoid tumours")
class page_eleven(pages):                                                       # Cancer Diagnosis
    def __init__(self, main_app, page, frame_page):
        super().__init__(main_app, page, frame_page)
        self.subframes = {}
        self.subframe = tk.Frame(self.frame, bg = 'grey')
        for i in range(10):
            self.subframes[i] = tk.Frame(self.subframe)
            for label in ['cancer', 'age', 'treatment']:
                self.widgets['{}_{}'.format(label, i)] = tk.Entry(self.subframes[i], bg = 'light grey', font = header_font)
            for label in ['Surgery', 'Chemotherapy', 'Radiation', 'Other']:
                self.widgets['{}_{}'.format(label, i)] = checkbutton(label, self.subframes[i])
    def build(self):
        self.frame.grid(row = 0, column = 0, columnspan = 2)
        tk.Label(self.frame, text = "C4: Cancer diagnosis", font = title_font).grid(row = 0,column = 0, sticky = W, columnspan = 2)
        for i, label in enumerate(['\tCancer', '\tAge at diagnosis', 'Treatment received']):
            tk.Label(self.frame, text = label, font = header_font).grid(row = 1,column = i, sticky = W, pady = 1, columnspan = 1)
        self.subframe.grid(row = 2, column = 0, columnspan = 4)
        for i in range(10):
            self.subframes[i].grid(row = i, column = 0, columnspan = 1, pady = (5,5), padx = 5)
            tk.Label(self.subframes[i], text = str(i + 1), font = header_font).grid(row = 0, column = 0, sticky = W, pady = 1, columnspan = 1, rowspan = 2)
            self.widgets['cancer_{}'.format(i)].grid(row = 0, column = 1, sticky = NW, pady = 1, columnspan = 1, rowspan = 2)
            self.widgets['age_{}'.format(i)].grid(row = 0, column = 2, sticky = NW, pady = 1, columnspan = 1, rowspan = 2)
            self.widgets['treatment_{}'.format(i)].grid(row = 1, column = 4, sticky = NW, pady = 1, columnspan = 2)
            for j, label in enumerate(['Surgery', 'Chemotherapy', 'Radiation']):
                self.widgets['{}_{}'.format(label, i)].place(row = 0, column = j + 3)
            self.widgets['Other_{}'.format(i)].place(row = 1, column = 3)
    def write_summary(self, file = None, path = None, file_name = None):
        super().write_summary(file = file, path = path, file_name = file_name)
        try:
            self.file.write("\tC4. List any cancer diagnosis?\n")
            for i in range(10):
                if self.widgets['cancer_{}'.format(i)].get() != "" or self.widgets['age_{}'.format(i)].get() != "" or self.widgets['treatment_{}'.format(i)].get() != "" or self.widgets['Surgery_{}'.format(i)].get() == 1 or self.widgets['Chemotherapy_{}'.format(i)].get() == 1 or self.widgets['Radiation_{}'.format(i)].get() == 1 or self.widgets['Other_{}'.format(i)].get() == 1:
                    self.file.write("\t\tCancer type: {}\tAge at diagnosis: {}".format(self.widgets['cancer_{}'.format(i)].get(), self.widgets['age_{}'.format(i)].get()))
                    self.file.write("\tTreatment received: {} {} {} {} {}\n".format("Surgery" if self.widgets['Surgery_{}'.format(i)].get() else "", "Chemotherapy" if self.widgets['Chemotherapy_{}'.format(i)].get() else "","Radiation" if self.widgets['Radiation_{}'.format(i)].get() else "","Other:" if self.widgets['Other_{}'.format(i)].get() else "", self.widgets['treatment_{}'.format(i)].get()))
        except:
            print("Error during writing of page eleven")
        if path != None:
            self.file.close()
    def write_output(self, file, error_file, year_of_birth):
        for i in range(5):
            if self.widgets['cancer_{}'.format(i)].get() != "" or self.widgets['age_{}'.format(i)].get() != "":
                self.write_entry("cancer type {}".format(i), self.widgets['cancer_{}'.format(i)].get(), file, error_file)
                self.write_entry("cancer age {}".format(i), self.widgets['age_{}'.format(i)].get(), file, error_file)
                self.write_entry("Surgery treatment {}".format(i), self.widgets['Surgery_{}'.format(i)].get(), file, error_file)
                self.write_entry("chemotherapy treatment {}".format(i), self.widgets['Chemotherapy_{}'.format(i)].get(), file, error_file)
                self.write_entry("radiation treatment {}".format(i), self.widgets['Radiation_{}'.format(i)].get(), file, error_file)
                self.write_entry("other treatment {}".format(i), self.widgets['treatment_{}'.format(i)].get() if self.widgets['Other_{}'.format(i)].get() else "None", file, error_file)
            else:
                file.write("\t\t\t\t\t\t")
    def testing(self):
        for i in [1,2,4]:
            for label in ['cancer', 'age', 'treatment']:
                self.widgets['{}_{}'.format(label, i)].insert(0, '{}_{}'.format(label, i + 1))
            for label in ['Surgery', 'Other']:
                self.widgets['{}_{}'.format(label, i)].var.set(1)
class page_twelve(pages):                                                       # Stool Test; Other heart, gastric, abnominal conditions
    def __init__(self, main_app, page, frame_page):
        super().__init__(main_app, page, frame_page)
        self.stoolFrame = tk.Frame(self.frame)
        self.conditionFrame = tk.Frame(self.frame)
        self.widgets['stool test'] = radiobutton(['Yes','No'], self.frame)
        self.widgets['stool test'].var.set(1)
        self.widgets['stool test'].add_command(self.expand_field, 'Yes')
        self.widgets['stool test'].add_command(self.collapse_field, 'No')
        self.widgets['stool test age'] = tk.Entry(self.stoolFrame, bg = 'light grey', font = header_font)
        self.widgets['stool test number'] = tk.Entry(self.stoolFrame, bg = 'light grey', font = header_font)
        temp = {'{}_{}'.format(label, i + 1): tk.Entry(self.conditionFrame, bg = 'light grey', font = header_font) for label in ['condition', 'age', 'treatment'] for i in range(4)}
        self.widgets.update(temp)
    def build(self):
        self.frame.grid(row = 0, column = 0, columnspan = 2)
        tk.Label(self.frame, text = "C5: Has subject ever had a stool test?", font = header_font).grid(row = 0,column = 0, sticky = W, pady = 1, columnspan = 1)
        self.widgets['stool test'].place(rows = [0, 0], columns = [1,2])
        self.stoolFrame.grid(row = 1, column = 0, columnspan = 3)
        tk.Label(self.stoolFrame, text = "Age/Year of first test", font = label_font).grid(row = 0, column = 0, sticky = W)
        tk.Label(self.stoolFrame, text = "Number of tests", font = label_font).grid(row = 1, column = 0, sticky = W)
        self.widgets['stool test age'].grid(row = 0, column = 1, sticky = W)
        self.widgets['stool test number'].grid(row = 1, column = 1, sticky = W)
        tk.Label(self.frame, text = "C6: Any other heart, gastric or abdominal conditions", font = header_font).grid(row = 2,column = 0, sticky = W, pady = 1, columnspan = 3)
        self.conditionFrame.grid(row = 3, column = 0, columnspan = 3)
        tk.Label(self.conditionFrame, text = "Condition", font = header_font).grid(row = 0,column = 1, sticky = W, pady = 1, columnspan = 1)
        tk.Label(self.conditionFrame, text = "Age at diagnosis", font = header_font).grid(row = 0,column = 2, sticky = W, pady = 1, columnspan = 1)
        tk.Label(self.conditionFrame, text = "Treatment received", font = header_font).grid(row = 0,column = 3, sticky = W, pady = 1, columnspan = 1)
        for i in range(4):
            tk.Label(self.conditionFrame, text = str(i + 1), font = header_font).grid(row = i + 1, column = 0, sticky = W, pady = 1, columnspan = 1, rowspan = 1)
            self.widgets['condition_{}'.format(i+1)].grid(row = i + 1, column = 1, sticky = W)
            self.widgets['age_{}'.format(i+1)].grid(row = i + 1, column = 2, sticky = W)
            self.widgets['treatment_{}'.format(i+1)].grid(row = i + 1, column = 3, sticky = W)
        if self.widgets['stool test'].get() == 1:
            self.stoolFrame.grid_remove()
    def expand_field(self):
        self.stoolFrame.grid()
        self.page_frame.update_idletasks()
        self.page_frame.configure(height = self.main_app.root.winfo_height() - self.main_app.navigation_frame.winfo_reqheight(), width = self.frame.winfo_reqwidth(), scrollregion=self.page_frame.bbox('all'))
        if self.frame.winfo_reqwidth() > self.main_app.root.winfo_width():
            self.main_app.root.configure(width = self.frame.winfo_reqwidth() + 20)
    def collapse_field(self):
        self.stoolFrame.grid_remove()
        self.page_frame.update_idletasks()
        self.page_frame.configure(height = self.main_app.root.winfo_height() - self.main_app.navigation_frame.winfo_reqheight(), width = self.frame.winfo_reqwidth(), scrollregion=self.page_frame.bbox('all'))
    def write_summary(self, file = None, path = None, file_name = None):
        super().write_summary(file = file, path = path, file_name = file_name)
        try: # ~~~~~~ From page twelve ~~~~~~
            self.file.write("\tC5. Have you ever had a stool test? {}\n".format("Yes" if not self.widgets['stool test'].get() else "No"))
            if not self.widgets['stool test'].get():
                self.file.write("{}".format("\t\tWhen was your first stool test? {}\n".format(self.widgets['stool test age'].get()) if self.widgets['stool test age'].get() != "" else ""))
                self.file.write("{}".format("\t\tHow many tests have you had? {}\n".format(self.widgets['stool test number'].get()) if self.widgets['stool test number'].get() != "" else ""))
            self.file.write("\tC6. Please list any other diagnosed heart problems or other gastric or abdominal problems\n")
            for i in range(4):
                if self.widgets['condition_{}'.format(i + 1)].get() != "" or self.widgets['age_{}'.format(i + 1)].get() != "" or self.widgets['treatment_{}'.format(i + 1)].get() != "":
                    self.file.write("\t\tCondition: {}\tAge at diagnosis: {}\tTreatment received: {}\n".format(self.widgets['condition_{}'.format(i + 1)].get(), self.widgets['age_{}'.format(i + 1)].get(), self.widgets['stool test number'].get()))
        except:
            print("Error during writing of page twelve")
        if path != None:
            self.file.close()
    def write_output(self, file, error_file, year_of_birth):
        self.write_entry("stool test response", 'Yes' if not self.widgets['stool test'].get() else 'No', file, error_file)
        if not self.widgets['stool test'].get():
            if self.widgets['stool test age'].get() != "":
                try:
                    if len(self.widgets['stool test age'].get()) < 4 and self.widgets['stool test age'].get():
                        self.write_entry('stool test age', int(year_of_birth) + int(self.widgets['stool test age'].get()) if year_of_birth != "" else "", file, error_file)
                        self.write_entry('stool test age', self.widgets['stool test age'].get(), file, error_file)
                    elif len(self.widgets['stool test age'].get()) == 4:
                        self.write_entry('stool test age', self.widgets['stool test age'].get(), file, error_file)
                        self.write_entry('stool test age', int(self.widgets['stool test age'].get()) - int(year_of_birth) if year_of_birth != "" else "", file, error_file)
                    else:
                        self.write_entry('stool test age', self.widgets['stool test age'].get(), file, error_file, tabs = 2)
                except:
                    try:
                        self.write_entry('stool test age', self.widgets['stool test age'].get(), file, error_file, tabs = 2)
                    except:
                        file.write('\t\t')
            self.write_entry("number of stool tests", self.widgets['stool test number'].get(), file, error_file)
        else:
            file.write('\t\t')

        for i in range(4):
            self.write_entry("condition {}".format(i + 1), self.widgets['condition_{}'.format(i + 1)].get(), file, error_file)
            self.write_entry("age {}".format(i + 1), self.widgets['age_{}'.format(i + 1)].get(), file, error_file)
            self.write_entry("treatment {}".format(i + 1), self.widgets['treatment_{}'.format(i + 1)].get(), file, error_file)
    def testing(self):
        self.widgets['stool test'].var.set(0)
        self.widgets['stool test age'].insert(0, 'stool test age')
        self.widgets['stool test number'].insert(0, 'number of tests')
        for i in [1,4]:
            for label in ['condition', 'age', 'treatment']:
                self.widgets['{}_{}'.format(label, i)].insert(0, '{}_{}'.format(label, i + 1))
class page_thirteen(pages):                                                     # Medications for reflux heartburn
    def __init__(self, main_app, page, frame_page):
        super().__init__(main_app, page, frame_page)
        self.subframe = tk.Frame(self.frame, bg = 'grey')
        self.subframes = {}
        for i in range(6):
            self.subframes[i] = tk.Frame(self.subframe)
            temp = {'{}_{}'.format(label, i + 1):tk.Entry(self.subframes[i], bg = 'light grey', font = header_font) for label in ['Name', 'Dose', 'age', 'Length']}
            self.widgets.update(temp)
            self.widgets['frequency_{}'.format(i + 1)] = radiobutton(['Daily', 'Occasionally', 'Rarely'], self.subframes[i])
    def build(self):
        self.frame.grid(row = 0, column = 0, columnspan = 2)
        tk.Label(self.frame, text = "D1: Medications for reflux heartburn", font = title_font).grid(row = 0,column = 0, sticky = W, pady = 1, columnspan = 6)
        for i, label in enumerate(['Name', 'Dose', 'Frequency', 'Start year/ age', 'Length of use']):
            tk.Label(self.frame, text = label, font = header_font).grid(row = 1, column = i + 1, sticky = W, pady = 1, columnspan = 1)
        self.subframe.grid(row = 2, column = 0, columnspan = 6)
        for i in range(6):
            self.subframes[i].grid(row = i, column = 0, pady = (5,5), padx = 5)
            tk.Label(self.subframes[i], text = str(i + 1), font = header_font).grid(row = 0, column = 0, sticky = W, pady = 1, columnspan = 1, rowspan = 2)
            for j, label in enumerate(['Name', 'Dose', 'age', 'Length']):
                self.widgets['{}_{}'.format(label, i + 1)].grid(row = 0, column = j + 1 if j < 2 else j + 2, sticky = W, rowspan = 3)
            self.widgets['frequency_{}'.format(i + 1)].place(rows = [0,1,2], columns = [3,3,3])
    def write_summary(self, file = None, path = None, file_name = None):
        super().write_summary(file = file, path = path, file_name = file_name)
        try: # ~~~~~~ From page thirteen ~~~~~~
            self.file.write("\nD. Medication Use\n")
            self.file.write("\tD.1.1 Give any medications taken for heartburn\n")
            for i in range(6):
                if self.widgets['Name_{}'.format(i + 1)].get() != "" or self.widgets['Dose_{}'.format(i + 1)].get() != "" or self.widgets['age_{}'.format(i + 1)].get() != "" or self.widgets['Length_{}'.format(i + 1)].get() != "":
                    self.file.write("\t\tName: {}\tDose: {}".format(self.widgets['Name_{}'.format(i + 1)].get(), self.widgets['Dose_{}'.format(i + 1)].get()))
                    self.file.write("\tHow often do you take it? {}".format("Daily" if self.widgets['frequency_{}'.format(i + 1)].get() == 0 else "Occasionally" if self.widgets['frequency_{}'.format(i + 1)].get() == 1 else "Rarely"))
                    self.file.write("\tWhen did you start taking it? {}\tHow long did you take it? {}\n".format(self.widgets['age_{}'.format(i + 1)].get(), self.widgets['Length_{}'.format(i + 1)].get()))
        except:
            print("Error during writing of page thirteen")
        if path != None:
            self.file.close()
    def write_output(self, file, error_file, year_of_birth):
        for i in range(6):
            if self.widgets['Name_{}'.format(i + 1)].get() != "":
                self.write_entry("heartburn medication name {}".format(i + 1), '{}{}'.format(self.widgets['Name_{}'.format(i + 1)].get(), ', {}'.format(self.widgets['Dose_{}'.format(i + 1)].get())), file, error_file)
                self.write_entry("heartburn medication frequency {}".format(i + 1), 'Daily' if self.widgets['frequency_{}'.format(i + 1)].get() == 0 else 'Occasionally' if self.widgets['frequency_{}'.format(i + 1)].get() == 1 else 'Rarely', file, error_file)
                self.write_entry("heartburn medication age started {}".format(i + 1), self.widgets['age_{}'.format(i + 1)].get(), file, error_file)
                self.write_entry("heartburn medication duration {}".format(i + 1), self.widgets['Length_{}'.format(i + 1)].get(), file, error_file)
            else:
                file.write('\t\t\t\t')
    def testing(self):
        for i in [0,5]:
            for label in ['Name', 'Dose', 'age', 'Length']:
                self.widgets['{}_{}'.format(label, i + 1)].insert(0, '{}_{}'.format(label, i + 1))
            self.widgets['frequency_{}'.format(i + 1)].var.set(1)
class page_fourteen(pages):                                                     # Medications for heart or blood pressure
    def __init__(self, main_app, page, frame_page):
        super().__init__(main_app, page, frame_page)
        self.subframe = tk.Frame(self.frame, bg = 'grey')
        self.subframes = {}
        for i in range(6):
            self.subframes[i] = tk.Frame(self.subframe)
            temp = {'{}_{}'.format(label, i + 1):tk.Entry(self.subframes[i], bg = 'light grey', font = header_font) for label in ['Name', 'Dose', 'age', 'Length']}
            self.widgets.update(temp)
            self.widgets['frequency_{}'.format(i + 1)] = radiobutton(['Daily', 'Occasionally', 'Rarely'], self.subframes[i])
    def build(self):
        self.frame.grid(row = 0, column = 0, columnspan = 2)
        tk.Label(self.frame, text = "D1: Medications for heart or blood pressure", font = title_font).grid(row = 0,column = 0, sticky = W, pady = 1, columnspan = 6)
        for i, label in enumerate(['Name', 'Dose', 'Frequency', 'Start year/ age', 'Length of use']):
            tk.Label(self.frame, text = label, font = header_font).grid(row = 1, column = i + 1, sticky = W, pady = 1, columnspan = 1)
        self.subframe.grid(row = 2, column = 0, columnspan = 6)
        for i in range(6):
            self.subframes[i].grid(row = i, column = 0, pady = (5,5), padx = 5)
            tk.Label(self.subframes[i], text = str(i + 1), font = header_font).grid(row = 0, column = 0, sticky = W, pady = 1, columnspan = 1, rowspan = 2)
            for j, label in enumerate(['Name', 'Dose', 'age', 'Length']):
                self.widgets['{}_{}'.format(label, i + 1)].grid(row = 0, column = j + 1 if j < 2 else j + 2, sticky = W, rowspan = 3)
            self.widgets['frequency_{}'.format(i + 1)].place(rows = [0,1,2], columns = [3,3,3])
    def write_summary(self, file = None, path = None, file_name = None):
        super().write_summary(file = file, path = path, file_name = file_name)
        try:
            self.file.write("\tD.1.2 Give any medications taken for heart or blood pressure\n")
            for i in range(6):
                if self.widgets['Name_{}'.format(i + 1)].get() != "" or self.widgets['Dose_{}'.format(i + 1)].get() != "" or self.widgets['age_{}'.format(i + 1)].get() != "" or self.widgets['Length_{}'.format(i + 1)].get() != "":
                    self.file.write("\t\tName: {}\tDose: {}".format(self.widgets['Name_{}'.format(i + 1)].get(), self.widgets['Dose_{}'.format(i + 1)].get()))
                    self.file.write("\tHow often do you take it? {}".format("Daily" if self.widgets['frequency_{}'.format(i + 1)].get() == 0 else  "Occasionally" if self.widgets['frequency_{}'.format(i + 1)].get() == 1 else "Rarely"))
                    self.file.write("\tWhen did you start taking it? {}\tHow long did you take it? {}\n".format(self.widgets['age_{}'.format(i + 1)].get(), self.widgets['Length_{}'.format(i + 1)].get()))
        except:
            print("Error during writing of page fourteen")
        if path != None:
            self.file.close()
    def write_output(self, file, error_file, year_of_birth):
        for i in range(6):
            if self.widgets['Name_{}'.format(i + 1)].get() != "":
                self.write_entry("heart or blood pressure medication name {}".format(i + 1), '{}, {}'.format(self.widgets['Name_{}'.format(i + 1)].get(), self.widgets['Dose_{}'.format(i + 1)].get()), file, error_file)
                self.write_entry("heart or blood pressure medication frequency {}".format(i + 1), 'Daily' if self.widgets['frequency_{}'.format(i + 1)].get() == 0 else 'Occasionally' if self.widgets['frequency_{}'.format(i + 1)].get() == 1 else 'Rarely', file, error_file)
                self.write_entry("heart or blood pressure medication age started {}".format(i + 1), self.widgets['age_{}'.format(i + 1)].get(), file, error_file)
                self.write_entry("heart or blood pressure medication duration {}".format(i + 1), self.widgets['Length_{}'.format(i + 1)].get(), file, error_file)
            else:
                file.write('\t\t\t\t')
    def testing(self):
        for i in [0,5]:
            for label in ['Name', 'Dose', 'age', 'Length']:
                self.widgets['{}_{}'.format(label, i + 1)].insert(0, '{}_{}'.format(label, i + 1))
            self.widgets['frequency_{}'.format(i + 1)].var.set(1)
class page_fifteen(pages):                                                      # Aspirin; Other anti-inflammatory medications
    def __init__(self, main_app, page, frame_page):
        super().__init__(main_app, page, frame_page)
        self.aspirin_subframe = tk.Frame(self.frame, bg = 'grey')
        self.subframes = {}
        for i in range(6):
            self.subframes['aspirin_{}'.format(i)] = tk.Frame(self.aspirin_subframe)
            temp = {'aspirin_{}_{}'.format(label, i + 1):tk.Entry(self.subframes['aspirin_{}'.format(i)], bg = 'light grey', font = header_font) for label in ['Name', 'Dose', 'age', 'Length']}
            self.widgets.update(temp)
            self.widgets['aspirin_frequency_{}'.format(i + 1)] = radiobutton(['Daily', 'Occasionally', 'Rarely'], self.subframes['aspirin_{}'.format(i)])

        self.meds_subframe = tk.Frame(self.frame, bg = 'grey')
        for i in range(2):
            self.subframes['meds_{}'.format(i)] = tk.Frame(self.meds_subframe)
            temp = {'meds_{}_{}'.format(label, i + 1):tk.Entry(self.subframes['meds_{}'.format(i)], bg = 'light grey', font = header_font) for label in ['Name', 'Dose', 'age', 'Length']}
            self.widgets.update(temp)
            self.widgets['meds_frequency_{}'.format(i + 1)] = radiobutton(['Daily', 'Occasionally', 'Rarely'], self.subframes['meds_{}'.format(i)])
    def build(self):
        self.frame.grid(row = 0, column = 0, columnspan = 2)
        tk.Label(self.frame, text = "D1: Aspirin", font = title_font).grid(row = 0,column = 0, sticky = W, pady = 1, columnspan = 6)
        for i, label in enumerate(['Name', 'Dose', 'Frequency', 'Start year/ age', 'Length of use']):
            tk.Label(self.frame, text = label, font = header_font).grid(row = 1, column = i + 1, sticky = W, pady = 1, columnspan = 1)
        self.aspirin_subframe.grid(row = 2, column = 0, columnspan = 6)
        for i in range(6):
            self.subframes['aspirin_{}'.format(i)].grid(row = i, column = 0, pady = (5,5), padx = 5)
            tk.Label(self.subframes['aspirin_{}'.format(i)], text = str(i + 1), font = header_font).grid(row = 0, column = 0, sticky = W, pady = 1, columnspan = 1, rowspan = 2)
            for j, label in enumerate(['Name', 'Dose', 'age', 'Length']):
                self.widgets['aspirin_{}_{}'.format(label, i + 1)].grid(row = 0, column = j + 1 if j < 2 else j + 2, sticky = W, rowspan = 3)
            self.widgets['aspirin_frequency_{}'.format(i + 1)].place(rows = [0,1,2], columns = [3,3,3])

        tk.Label(self.frame, text = '').grid(row = 3, column = 0)
        tk.Label(self.frame, text = "D1: Other anti-inflammatory medications", font = title_font).grid(row = 4,column = 0, sticky = W, pady = 1, columnspan = 6)
        for i, label in enumerate(['Name', 'Dose', 'Frequency', 'Start year/ age', 'Length of use']):
            tk.Label(self.frame, text = label, font = header_font).grid(row = 5, column = i + 1, sticky = W, pady = 1, columnspan = 1)
        self.meds_subframe.grid(row = 6, column = 0, columnspan = 6)
        for i in range(2):
            self.subframes['meds_{}'.format(i)].grid(row = i, column = 0, pady = (5,5), padx = 5)
            tk.Label(self.subframes['meds_{}'.format(i)], text = str(i + 1), font = header_font).grid(row = 0, column = 0, sticky = W, pady = 1, columnspan = 1, rowspan = 2)
            for j, label in enumerate(['Name', 'Dose', 'age', 'Length']):
                self.widgets['meds_{}_{}'.format(label, i + 1)].grid(row = 0, column = j + 1 if j < 2 else j + 2, sticky = W, rowspan = 3)
            self.widgets['meds_frequency_{}'.format(i + 1)].place(rows = [0,1,2], columns = [3,3,3])
    def write_summary(self, file = None, path = None, file_name = None):
        super().write_summary(file = file, path = path, file_name = file_name)
        try:
            self.file.write("\tD.1.3 Give any aspirin taken\n")
            for i in range(6):
                if self.widgets['aspirin_Name_{}'.format(i + 1)].get() != "" or self.widgets['aspirin_Dose_{}'.format(i + 1)].get() != "" or self.widgets['aspirin_age_{}'.format(i + 1)].get() != "" or self.widgets['aspirin_Length_{}'.format(i + 1)].get() != "":
                    self.file.write("\t\tName: {}\tDose: {}".format(self.widgets['aspirin_Name_{}'.format(i + 1)].get(), self.widgets['aspirin_Dose_{}'.format(i + 1)].get()))
                    self.file.write("\tHow often do you take it? {}".format("Daily" if self.widgets['aspirin_frequency_{}'.format(i + 1)].get() == 0 else  "Occasionally" if self.widgets['aspirin_frequency_{}'.format(i + 1)].get() == 1 else "Rarely"))
                    self.file.write("\tWhen did you start taking it? {}\tHow long did you take it? {}\n".format(self.widgets['aspirin_age_{}'.format(i + 1)].get(), self.widgets['aspirin_Length_{}'.format(i + 1)].get()))

            self.file.write("\tD.1.4 Give any anti-inflammatory medications taken\n")
            for i in range(2):
                if self.widgets['meds_Name_{}'.format(i + 1)].get() != "" or self.widgets['meds_Dose_{}'.format(i + 1)].get() != "" or self.widgets['meds_age_{}'.format(i + 1)].get() != "" or self.widgets['meds_Length_{}'.format(i + 1)].get() != "":
                    self.file.write("\t\tName: {}\tDose: {}".format(self.widgets['meds_Name_{}'.format(i + 1)].get(), self.widgets['meds_Dose_{}'.format(i + 1)].get()))
                    self.file.write("\tHow often do you take it? {}".format("Daily" if self.widgets['meds_frequency_{}'.format(i + 1)].get() == 0 else  "Occasionally" if self.widgets['meds_frequency_{}'.format(i + 1)].get() == 1 else "Rarely"))
                    self.file.write("\tWhen did you start taking it? {}\tHow long did you take it? {}\n".format(self.widgets['meds_age_{}'.format(i + 1)].get(), self.widgets['meds_Length_{}'.format(i + 1)].get()))
        except:
            print("Error during writing of page fifteen")
        if path != None:
            self.file.close()
    def write_output(self, file, error_file, year_of_birth):
        for i in range(6):
            if self.widgets['aspirin_Name_{}'.format(i + 1)].get() != "":
                self.write_entry("aspirin medication name {}".format(i + 1), '{}, {}'.format(self.widgets['aspirin_Name_{}'.format(i + 1)].get(), self.widgets['aspirin_Dose_{}'.format(i + 1)].get()), file, error_file)
                self.write_entry("aspirin medication frequency {}".format(i + 1), 'Daily' if self.widgets['aspirin_frequency_{}'.format(i + 1)].get() == 0 else 'aspirin_Occasionally' if self.widgets['aspirin_frequency_{}'.format(i + 1)].get() == 1 else 'Rarely', file, error_file)
                self.write_entry("aspirin medication age started {}".format(i + 1), self.widgets['aspirin_age_{}'.format(i + 1)].get(), file, error_file)
                self.write_entry("aspirin medication duration {}".format(i + 1), self.widgets['aspirin_Length_{}'.format(i + 1)].get(), file, error_file)
            else:
                file.write('\t\t\t\t')
        for i in range(2):
            if self.widgets['meds_Name_{}'.format(i + 1)].get() != "":
                self.write_entry("other anti-inflammatory medication name {}".format(i + 1), '{}, {}'.format(self.widgets['meds_Name_{}'.format(i + 1)].get(), self.widgets['meds_Dose_{}'.format(i + 1)].get()), file, error_file)
                self.write_entry("other anti-inflammatory medication frequency {}".format(i + 1), 'Daily' if self.widgets['meds_frequency_{}'.format(i + 1)].get() == 0 else 'Occasionally' if self.widgets['meds_frequency_{}'.format(i + 1)].get() == 1 else 'Rarely', file, error_file)
                self.write_entry("other anti-inflammatory medication age started {}".format(i + 1), self.widgets['meds_age_{}'.format(i + 1)].get(), file, error_file)
                self.write_entry("other anti-inflammatory medication duration {}".format(i + 1), self.widgets['meds_Length_{}'.format(i + 1)].get(), file, error_file)
            else:
                file.write('\t\t\t\t')
    def testing(self):
        for i in [0,5]:
            for label in ['Name', 'Dose', 'age', 'Length']:
                self.widgets['aspirin_{}_{}'.format(label, i + 1)].insert(0, 'aspirin_{}_{}'.format(label, i + 1))
            self.widgets['aspirin_frequency_{}'.format(i + 1)].var.set(1)
        for i in [0,1]:
            for label in ['Name', 'Dose', 'age', 'Length']:
                self.widgets['meds_{}_{}'.format(label, i + 1)].insert(0, '{}_{}'.format(label, i + 1))
            self.widgets['meds_frequency_{}'.format(i + 1)].var.set(1)
class page_sixteen(pages):                                                      # Other Medications
    def __init__(self, main_app, page, frame_page):
        super().__init__(main_app, page, frame_page)
        self.subframe = tk.Frame(self.frame, bg = 'grey')
        self.subframes = {}
        for i in range(6):
            self.subframes[i] = tk.Frame(self.subframe)
            temp = {'{}_{}'.format(label, i + 1):tk.Entry(self.subframes[i], bg = 'light grey', font = header_font) for label in ['Name', 'Dose', 'age', 'Length']}
            self.widgets.update(temp)
            self.widgets['frequency_{}'.format(i + 1)] = radiobutton(['Daily', 'Occasionally', 'Rarely'], self.subframes[i])
    def build(self):
        self.frame.grid(row = 0, column = 0, columnspan = 2)
        tk.Label(self.frame, text = "D1: Other Medications", font = title_font).grid(row = 0,column = 0, sticky = W, pady = 1, columnspan = 6)
        for i, label in enumerate(['Name', 'Dose', 'Frequency', 'Start year/ age', 'Length of use']):
            tk.Label(self.frame, text = label, font = header_font).grid(row = 1, column = i + 1, sticky = W, pady = 1, columnspan = 1)
        self.subframe.grid(row = 2, column = 0, columnspan = 6)
        for i in range(6):
            self.subframes[i].grid(row = i, column = 0, pady = (5,5), padx = 5)
            tk.Label(self.subframes[i], text = str(i + 1), font = header_font).grid(row = 0, column = 0, sticky = W, pady = 1, columnspan = 1, rowspan = 2)
            for j, label in enumerate(['Name', 'Dose', 'age', 'Length']):
                self.widgets['{}_{}'.format(label, i + 1)].grid(row = 0, column = j + 1 if j < 2 else j + 2, sticky = W, rowspan = 3)
            self.widgets['frequency_{}'.format(i + 1)].place(rows = [0,1,2], columns = [3,3,3])
    def write_summary(self, file = None, path = None, file_name = None):
        super().write_summary(file = file, path = path, file_name = file_name)
        try:
            self.file.write("\tD.1.4 Give any other medications taken\n")
            for i in range(6):
                if self.widgets['Name_{}'.format(i + 1)].get() != "" or self.widgets['Dose_{}'.format(i + 1)].get() != "" or self.widgets['age_{}'.format(i + 1)].get() != "" or self.widgets['Length_{}'.format(i + 1)].get() != "":
                    self.file.write("\t\tName: {}\tDose: {}".format(self.widgets['Name_{}'.format(i + 1)].get(), self.widgets['Dose_{}'.format(i + 1)].get()))
                    self.file.write("\tHow often do you take it? {}".format("Daily" if self.widgets['frequency_{}'.format(i + 1)].get() == 0 else  "Occasionally" if self.widgets['frequency_{}'.format(i + 1)].get() == 1 else "Rarely"))
                    self.file.write("\tWhen did you start taking it? {}\tHow long did you take it? {}\n".format(self.widgets['age_{}'.format(i + 1)].get(), self.widgets['Length_{}'.format(i + 1)].get()))
        except:
            print("Error during writing of page sixteen")
        if path != None:
            self.file.close()
    def write_output(self, file, error_file, year_of_birth):
        for i in range(6):
            if self.widgets['Name_{}'.format(i + 1)].get() != "":
                self.write_entry("other medication name {}".format(i + 1), '{}, {}'.format(self.widgets['Name_{}'.format(i + 1)].get(), self.widgets['Dose_{}'.format(i + 1)].get()), file, error_file)
                self.write_entry("other medication frequency {}".format(i + 1), 'Daily' if self.widgets['frequency_{}'.format(i + 1)].get() == 0 else 'Occasionally' if self.widgets['frequency_{}'.format(i + 1)].get() == 1 else 'Rarely', file, error_file)
                self.write_entry("other medication age started {}".format(i + 1), self.widgets['age_{}'.format(i + 1)].get(), file, error_file)
                self.write_entry("other medication duration {}".format(i + 1), self.widgets['Length_{}'.format(i + 1)].get(), file, error_file)
            else:
                file.write('\t\t\t\t')
    def testing(self):
        for i in [0,5]:
            for label in ['Name', 'Dose', 'age', 'Length']:
                self.widgets['{}_{}'.format(label, i + 1)].insert(0, '{}_{}'.format(label, i + 1))
            self.widgets['frequency_{}'.format(i + 1)].var.set(1)
class page_seventeen(pages):                                                    # Diet; Meat; Vitamins; Smoking; Alcohol
    def __init__(self, main_app, page, frame_page):
        super().__init__(main_app, page, frame_page)

        self.subframes = {}
        self.subframes['alcohol'] = tk.Frame(self.frame)
        self.subframes['smoking'] = tk.Frame(self.frame)

        for label in ['Dietary intolerances', 'specific diet', 'smoking', 'alcohol', 'vitamins']:
            self.widgets[label] = radiobutton(['Yes', 'No'], self.frame)
            self.widgets[label].var.set(1)
            if label not in ['smoking', 'alcohol']:
                self.widgets['{}_expanded'.format(label)] = tk.Entry(self.frame, bg = 'light grey', font = header_font)
                self.widgets[label].add_command(partial(self.expand_field,   self.widgets['{}_expanded'.format(label)]), 'Yes')
                self.widgets[label].add_command(partial(self.collapse_field, self.widgets['{}_expanded'.format(label)]), 'No')

        self.widgets['smoking'].add_command(partial(self.expand_field,   self.subframes['smoking']), 'Yes')
        self.widgets['smoking'].add_command(partial(self.collapse_field, self.subframes['smoking']), 'No')
        self.widgets['alcohol'].add_command(partial(self.expand_field,   self.subframes['alcohol']), 'Yes')
        self.widgets['alcohol'].add_command(partial(self.collapse_field, self.subframes['alcohol']), 'No')

        self.widgets['unprocessed_meat'] = radiobutton(["Never", "1-3", "4-7", "More often:"], self.frame)
        self.widgets['unprocessed_meat'].var.set(0)

        self.widgets['unprocessed_meat_entry'] = tk.Entry(self.frame, bg = 'light grey', font = header_font)

        self.widgets['unprocessed_meat'].add_command(partial(self.expand_field,   self.widgets['unprocessed_meat_entry']), 'More often:')
        self.widgets['unprocessed_meat'].add_command(partial(self.collapse_field, self.widgets['unprocessed_meat_entry']), 'Never')
        self.widgets['unprocessed_meat'].add_command(partial(self.collapse_field, self.widgets['unprocessed_meat_entry']), '1-3')
        self.widgets['unprocessed_meat'].add_command(partial(self.collapse_field, self.widgets['unprocessed_meat_entry']), '4-7')

        self.widgets['processed_meat'] = radiobutton(["Never", "1-3", "4-7", "More often:"], self.frame)
        self.widgets['processed_meat'].var.set(0)

        self.widgets['processed_meat_entry'] = tk.Entry(self.frame, bg = 'light grey', font = header_font)

        self.widgets['processed_meat'].add_command(partial(self.expand_field,   self.widgets['processed_meat_entry']), 'More often:')
        self.widgets['processed_meat'].add_command(partial(self.collapse_field, self.widgets['processed_meat_entry']), 'Never')
        self.widgets['processed_meat'].add_command(partial(self.collapse_field, self.widgets['processed_meat_entry']), '1-3')
        self.widgets['processed_meat'].add_command(partial(self.collapse_field, self.widgets['processed_meat_entry']), '4-7')

        self.widgets['smoking_age_started'] = tk.Entry(self.subframes['smoking'], bg = 'light grey', font = header_font)
        self.widgets['smoking_age_stopped'] = tk.Entry(self.subframes['smoking'], bg = 'light grey', font = header_font)
        self.widgets['smoking_cig_per_day'] = tk.Entry(self.subframes['smoking'], bg = 'light grey', font = header_font)

        self.widgets['still_smoking'] = radiobutton(["Yes", "No, Age stopped:"], self.subframes['smoking'])
        self.widgets['still_smoking'].var.set(0)
        self.widgets['still_smoking'].add_command(partial(self.expand_field,   self.widgets['smoking_age_stopped']), 'No, Age stopped:')
        self.widgets['still_smoking'].add_command(partial(self.collapse_field, self.widgets['smoking_age_stopped']), 'Yes')

        self.widgets['alcohol_drinks_per_week'] = tk.Entry(self.subframes['alcohol'], bg = 'light grey', font = header_font)
        self.widgets['drinking_frequency']      = radiobutton(["Never", "Monthly or less", "2-4 times/month", "2-3 times/week", "4+ times/week"], self.subframes['alcohol'])
        self.widgets['drinks_on_drinking_days'] = radiobutton(["1-2", "3-4", "5-6", "7-9", "10+"], self.subframes['alcohol'])
        self.widgets['frequency_5_or_more']     = radiobutton(["Never", "Less than monthly", "Monthly", "Weekly", "Daily or almost daily"], self.subframes['alcohol'])
    def build(self):
        self.frame.grid(row = 0, column = 0, columnspan = 2)
        tk.Label(self.frame, text = "E. Diet and Lifestyle", font = title_font).grid(row = 0,column = 0, sticky = W, pady = 1, columnspan = 1)
        tk.Label(self.frame, text = "\tE1. Dietary intolerances               ", font = header_font).grid(row = 1,column = 0, sticky = W, pady = 1, columnspan = 1)
        tk.Label(self.frame, text = "\tE2. Specific diet                      ", font = header_font).grid(row = 2,column = 0, sticky = W, pady = 1, columnspan = 1)
        self.widgets['Dietary intolerances'].place(rows = [1,1], columns = [1, 2])
        self.widgets['Dietary intolerances_expanded'].grid(row = 1, column = 3, sticky = W, columnspan = 3)
        self.widgets['specific diet'].place(rows = [2,2], columns = [1, 2])
        self.widgets['specific diet_expanded'].grid(row = 2, column = 3, sticky = W, columnspan = 3)
        if self.widgets['specific diet'].get() == 1:
            self.widgets['specific diet_expanded'].grid_remove()
        if self.widgets['Dietary intolerances'].get() == 1:
            self.widgets['Dietary intolerances_expanded'].grid_remove()

        tk.Label(self.frame, text = "\tE3. Unprocessed red meat per week      ", font = header_font).grid(row = 3, column = 0, sticky = W, pady = 1, columnspan = 1)
        self.widgets['unprocessed_meat'].place(rows = [3,3,3,3], columns = [1,2,3,4])
        self.widgets['unprocessed_meat_entry'].grid(row = 3, column = 5)
        if self.widgets['unprocessed_meat'].get() != 3:
            self.widgets['unprocessed_meat_entry'].grid_remove()

        tk.Label(self.frame, text = "\tE4. Processed red meat per week        ", font = header_font).grid(row = 4, column = 0, sticky = W, pady = 1, columnspan = 1)
        self.widgets['processed_meat'].place(rows = [4,4,4,4], columns = [1,2,3,4])
        self.widgets['processed_meat_entry'].grid(row = 4, column = 5)
        if self.widgets['processed_meat'].get() != 3:
            self.widgets['processed_meat_entry'].grid_remove()

        tk.Label(self.frame, text = "\tE5. Vitamins or Supplements            ", font = header_font).grid(row = 5,column = 0, sticky = W, pady = 1, columnspan = 1)
        self.widgets['vitamins'].place(rows = [5,5], columns = [1, 2])
        self.widgets['vitamins_expanded'].grid(row = 5, column = 3, sticky = W, columnspan = 3)
        if self.widgets['vitamins'].get() == 1:
            self.widgets['vitamins_expanded'].grid_remove()


        tk.Label(self.frame, text = "\tE6. Was subject ever a regular smoker? ", font = header_font).grid(row = 6,column = 0, sticky = W, pady = 1, columnspan = 1)
        self.widgets['smoking'].place(rows = [6,6], columns = [1,2])
        self.subframes['smoking'].grid(row = 7, column = 0, columnspan = 6, sticky = EW)
        for i, label in enumerate([ "\t\tAge started", "\t\tStill regular smoker?", "\t\tCigarettes per day"]):
            tk.Label(self.subframes['smoking'], text = label, font = header_font).grid(row = i, column = 0, sticky = W)

        self.widgets['smoking_age_started'].grid(row = 0, column = 1, columnspan = 3)
        self.widgets['smoking_age_stopped'].grid(row = 1, column = 3)
        self.widgets['smoking_cig_per_day'].grid(row = 2, column = 1, columnspan = 3)
        self.widgets['still_smoking'].place(rows = [1,1], columns = [1,2])
        if self.widgets['still_smoking'].get() == 0:
            self.widgets['smoking_age_stopped'].grid_remove()
        if self.widgets['smoking'].get() == 1:
            self.subframes['smoking'].grid_remove()

        tk.Label(self.frame, text = "\tE7. Does subject drink alcohol?        ", font = header_font).grid(row = 8,column = 0, sticky = W, pady = 1, columnspan = 1)
        self.widgets['alcohol'].place(rows = [8,8], columns = [1,2])
        self.subframes['alcohol'].grid(row = 9, column = 0, columnspan = 6, sticky = EW)
        for i, label in enumerate(["\t\tDrinks per week: ","\t\tDrinking Frequency","\t\tStandard drinks on drinking days","\t\tFrequency of 5 or more drinks"]):
            tk.Label(self.subframes['alcohol'], text = label, font = header_font).grid(row = i, column = 0, sticky = W, columnspan = 1)

        self.widgets['alcohol_drinks_per_week' ].grid(row = 0, column = 1, columnspan = 4, sticky = W)
        self.widgets['drinking_frequency'     ].place(rows = [1,1,1,1,1], columns = [1,2,3,4,5])
        self.widgets['drinks_on_drinking_days'].place(rows = [2,2,2,2,2], columns = [1,2,3,4,5])
        self.widgets['frequency_5_or_more'    ].place(rows = [3,3,3,3,3], columns = [1,2,3,4,5])
        if self.widgets['alcohol'].get() == 1:
            self.subframes['alcohol'].grid_remove()
    def expand_field(self, field):
        field.grid()
        self.page_frame.update_idletasks()
        self.page_frame.configure(height = self.main_app.root.winfo_height() - self.main_app.navigation_frame.winfo_reqheight(), width = self.frame.winfo_reqwidth(), scrollregion=self.page_frame.bbox('all'))
        if self.frame.winfo_reqwidth() > self.main_app.root.winfo_width():
            self.main_app.root.configure(width = self.frame.winfo_reqwidth() + 20)
    def collapse_field(self, field):
        field.grid_remove()
        self.page_frame.update_idletasks()
        self.page_frame.configure(height = self.main_app.root.winfo_height() - self.main_app.navigation_frame.winfo_reqheight(), width = self.frame.winfo_reqwidth(), scrollregion=self.page_frame.bbox('all'))
    def write_summary(self, file = None, path = None, file_name = None):
        super().write_summary(file = file, path = path, file_name = file_name)
        try: # ~~~~~~ From page seventeen ~~~~~~
            self.file.write("\nE. Diet and Lifestyle\n")
            self.file.write("\tE1. Do you have any dietary intolerances? {} {}\n".format("Yes" if not self.widgets['Dietary intolerances'].get() else "No", '- Specify: {}'.format(self.widgets['Dietary intolerances_expanded'].get()) if not self.widgets['Dietary intolerances'].get() and self.widgets['Dietary intolerances_expanded'].get() != "" else ""))
            self.file.write("\tE2. Do you follow a specific diet? {} {}\n".format("Yes" if not self.widgets['specific diet'].get() else "No", '- Specify: {}'.format(self.widgets['specific diet_expanded'].get()) if not self.widgets['specific diet'].get() and self.widgets['specific diet_expanded'].get() != "" else ""))
            self.file.write("\tE3. On average how often per week do you eat unprocessed red meat? {}\n".format("Never" if self.widgets['unprocessed_meat'].get() == 0 else "1-3" if self.widgets['unprocessed_meat'].get() == 1 else "4-7" if self.widgets['unprocessed_meat'].get() == 2 else "More often: {}".format(self.widgets['unprocessed_meat_entry'].get())))
            self.file.write("\tE4. On average how often per week do you eat processed red meat? {}\n".format("Never" if self.widgets['processed_meat'].get() == 0 else "1-3" if self.widgets['processed_meat'].get() == 1 else "4-7" if self.widgets['processed_meat'].get() == 2 else "More often: {}".format(self.widgets['processed_meat_entry'].get())))
            self.file.write("\tE5. Do you take any vitamins or supplements? {} {}\n".format("Yes" if not self.widgets['vitamins'].get() else "No", '- Specify: {}'.format(self.widgets['vitamins_expanded'].get()) if not self.widgets['vitamins'].get() and self.widgets['vitamins_expanded'].get() != "" else ""))

            self.file.write("\tE6. Have you ever been a regular smoker? {}\n".format("Yes" if not self.widgets['smoking'].get() else "No"))
            if not self.widgets['smoking'].get():
                self.file.write("{}".format("\t\tHow old were you when you started? {}\n".format(self.widgets['smoking_age_started'].get()) if self.widgets['smoking_age_started'].get() != "" else ""))
                self.file.write("\t\tDo you still smoke regularly? {} {}\n".format("Yes" if not self.widgets['still_smoking'].get() else "No", "Age stopped: {}".format(self.widgets['smoking_age_stopped'].get()) if self.widgets['still_smoking'].get() else ""))
                self.file.write("{}".format("\t\tHow many cigarettes smoked per day? {}\n".format(self.widgets['smoking_cig_per_day'].get()) if self.widgets['smoking_cig_per_day'].get() != "" else ""))

            self.file.write("\tE7. Do you drink alcohol? {}\n".format("Yes" if not self.widgets['alcohol'].get() else "No"))
            if not self.widgets['alcohol'].get():
                self.file.write("{}".format("\t\tHow many standard drinks per week: {}\n".format(self.widgets['alcohol_drinks_per_week'].get()) if self.widgets['alcohol_drinks_per_week'].get() != "" else ""))
                self.file.write("\t\tHow often do you drink alcohol? {}\n".format("Never" if self.widgets['drinking_frequency'].get() == 0 else "Monthly or less" if self.widgets['drinking_frequency'].get() == 1 else "2-4 times/month" if self.widgets['drinking_frequency'].get() == 2 else "2-3 times/week" if self.widgets['drinking_frequency'].get() == 3 else "4+ times/week"))
                self.file.write("\t\tHow many standard drinks on a drinking day? {}\n".format("1-2" if self.widgets['drinks_on_drinking_days'].get() == 0 else "3-4" if self.widgets['drinks_on_drinking_days'].get() == 1 else "5-6" if self.widgets['drinks_on_drinking_days'].get() == 2 else "7-9" if self.widgets['drinks_on_drinking_days'].get() == 3 else "10+"))
                self.file.write("\t\tHow often do you have 5 or more drinks? {}\n".format("Never" if self.widgets['frequency_5_or_more'].get() == 0 else "Less than monthly" if self.widgets['frequency_5_or_more'].get() == 1 else "Monthly" if self.widgets['frequency_5_or_more'].get() == 2 else "Weekly" if self.widgets['frequency_5_or_more'].get() == 3 else "Daily or almost daily"))
        except:
            print("Error during writing of page seventeen")
        if path != None:
            self.file.close()
    def write_output(self, file, error_file, year_of_birth):
        self.write_entry("Dietary intolerances response", 'Yes' if not self.widgets['Dietary intolerances'].get() else 'No', file, error_file)
        self.write_entry("Dietary intolerances expanded response",  self.widgets['Dietary intolerances_expanded'].get() if not self.widgets['Dietary intolerances'].get() else '', file, error_file)
        self.write_entry("specific diet response", 'Yes' if not self.widgets['specific diet'].get() else 'No', file, error_file)
        self.write_entry("specific diet expanded response",  self.widgets['specific diet_expanded'].get() if not self.widgets['specific diet'].get() else '', file, error_file)
        self.write_entry("unprocessed meats frequency", 'Never' if self.widgets['unprocessed_meat'].get() == 0 else '1-3' if self.widgets['unprocessed_meat'] == 1 else '4-7' if self.widgets['unprocessed_meat'] == 2 else 'More often', file, error_file)
        self.write_entry("unprocessed meats frequency explanation",  self.widgets['unprocessed_meat_entry'].get() if self.widgets['unprocessed_meat'].get() == 3 else '', file, error_file)
        self.write_entry("processed meats frequency", 'Never' if self.widgets['processed_meat'].get() == 0 else '1-3' if self.widgets['processed_meat'] == 1 else '4-7' if self.widgets['processed_meat'] == 2 else 'More often', file, error_file)
        self.write_entry("processed meats frequency explanation",  self.widgets['processed_meat_entry'].get() if self.widgets['processed_meat'].get() == 3 else '', file, error_file)
        self.write_entry("vitamins response", 'Yes' if not self.widgets['vitamins'].get() else 'No', file, error_file)
        self.write_entry("vitamins expanded response",  self.widgets['vitamins_expanded'].get() if not self.widgets['vitamins'].get() else '', file, error_file)

        self.write_entry("smoking response", 'Yes' if not self.widgets['smoking'].get() else 'No', file, error_file)
        self.write_entry("smoking age",  self.widgets['smoking_age_started'].get() if not self.widgets['smoking'].get() else '', file, error_file)
        self.write_entry("still smoking response",  '{}'.format('Yes' if not self.widgets['still_smoking'].get() else 'No') if not self.widgets['smoking'].get() else '', file, error_file)
        self.write_entry("age stopped smoking",  '{}'.format(self.widgets['smoking_age_stopped'].get() if self.widgets['still_smoking'].get() else '') if not self.widgets['smoking'].get() else '', file, error_file)
        self.write_entry("cigarettes per day",  self.widgets['smoking_cig_per_day'].get() if not self.widgets['smoking'].get() else '', file, error_file)

        self.write_entry("alcohol response", 'Yes' if not self.widgets['alcohol'].get() else 'No', file, error_file)
        if not self.widgets['alcohol'].get():
            self.write_entry("drinks per week", self.widgets['alcohol_drinks_per_week'].get(), file, error_file)
            self.write_entry("drinking freqeuncy", 'Never' if self.widgets['drinking_frequency'].get() == 0 else 'Monthly or less' if self.widgets['drinking_frequency'].get() == 1 else '2-4 times/month' if self.widgets['drinking_frequency'].get() == 2 else '2-3 times/week' if self.widgets['drinking_frequency'].get() == 3 else '4+ times/week', file, error_file)
            self.write_entry("drinks on drinking days", '1-2' if self.widgets['drinks_on_drinking_days'].get() == 0 else '3-4' if self.widgets['drinks_on_drinking_days'].get() == 1 else '5-6' if self.widgets['drinks_on_drinking_days'].get() == 2 else '7-9' if self.widgets['drinks_on_drinking_days'].get() == 3 else '10+', file, error_file)
            self.write_entry("frequency of 5 or more drinks", 'Never' if self.widgets['frequency_5_or_more'].get() == 0 else "Less than monthly" if self.widgets['frequency_5_or_more'].get() == 1 else "Monthly" if self.widgets['frequency_5_or_more'].get() == 2 else "Weekly" if self.widgets['frequency_5_or_more'].get() == 3 else "Daily or almost daily", file, error_file)
        else:
            file.write("\t\t\t\t")
    def testing(self):
        for label in ['Dietary intolerances', 'specific diet', 'smoking', 'alcohol', 'vitamins']:
            self.widgets[label].var.set(0)
            if label not in ['smoking', 'alcohol']:
                self.widgets['{}_expanded'.format(label)].insert(0, '{}_expanded'.format(label))

        self.widgets['unprocessed_meat'].var.set(2)
        self.widgets['processed_meat'] = radiobutton(["Never", "1-3", "4-7", "More often:"], self.frame)
        self.widgets['processed_meat'].var.set(3)
        self.widgets['processed_meat_entry'].insert(0, 'lots of meat')

        self.widgets['smoking_age_started'].insert(0, 'age started smoking')
        self.widgets['smoking_age_stopped'].insert(0, 'age stopped smoking')
        self.widgets['smoking_cig_per_day'].insert(0, 'number of cigs per day')
        self.widgets['still_smoking'].var.set(1)

        self.widgets['alcohol_drinks_per_week'].insert(0, 'number of drinks per week')
        self.widgets['drinking_frequency'].var.set(2)
        self.widgets['drinks_on_drinking_days'].var.set(4)
        self.widgets['frequency_5_or_more'].var.set(3)
class page_eighteen(pages):                                                     # Additional Information
    def __init__(self, main_app, page, frame_page):
        super().__init__(main_app, page, frame_page)
        self.widgets['additional_information'] = text(self.frame, height = 20, bg = 'light grey', font = header_font)
    def build(self):
        self.frame.grid(row = 0, column = 0, columnspan = 2)
        tk.Label(self.frame, text = "F. Any Additional Information", font = title_font).grid(row = 0,column = 0, sticky = W, pady = 1, columnspan = 1)
        self.widgets['additional_information'].grid(row = 1, column = 0, sticky = W)
    def write_summary(self, file = None, path = None, file_name = None):
        super().write_summary(file = file, path = path, file_name = file_name)
        try: # ~~~~~~ From page eighteen ~~~~~~
            self.file.write("\nF. Additional Information\n")
            self.file.write("\t{}".format(self.widgets['additional_information'].get()))
        except:
            print("Error during writing of page eighteen")
        if path != None:
            self.file.close()
    def write_output(self, file, error_file, year_of_birth):
        self.write_entry("additional information", self.widgets['additional_information'].get(), file, error_file)
    def testing(self):
        self.widgets['additional_information'].insert(0, 'END - additional information')
class radiobutton():
    def __init__(self, conditions, frame):
        self.var = tk.IntVar()
        self.conditions = conditions
        self.values = {i:j for i, j in enumerate(conditions)}
        self.buttons = {}
        for value, condition in self.values.items():
            self.buttons[condition] = tk.Radiobutton(frame, text = condition, font = label_font, variable = self.var, value = value)

    def place(self, rows, columns):
        for condition, row, column in zip(self.conditions, rows, columns):
            self.buttons[condition].grid(row = row, column = column, sticky = W)

    def add_command(self, command, condition):
        self.buttons[condition].config(command = command)

    def get(self):
        return self.var.get()
class checkbutton():
    def __init__(self, condition, frame):
        self.var = tk.IntVar()
        self.condition = condition
        self.button = tk.Checkbutton(frame, text = condition, font = label_font, variable = self.var, onvalue = 1, offvalue = 0)

    def place(self, row, column, padx = (0,0)):
        self.button.grid(row = row, column = column, sticky = W, padx = padx)

    def add_command(self, command):
        self.button.config(command = command)

    def get(self):
        return self.var.get()
class text(tk.Text):
    def get(self):
        string = super().get("1.0", 'end-1c')
        string = re.sub('\n|\t', ' ', string)
        return string

    def insert(self, pos, string):
        super().insert("1.0", string)



if __name__ == '__main__':
    app = gui(testing = False)
    app.mainloop()

import tkinter as tk
from  tkinter import ttk
from tkinter import messagebox, filedialog, scrolledtext
import threading
import os
import csv
from storing_logs.add_logs_to_database import get_collection, set_logs_collection, set_alerts_collection
from handling_logs import check_log
import queue
from handling_logs.handling_logs import get_all_services, create_alerts
import datetime
from datetime import datetime
import time

class Gui(tk.Tk):  
    def __init__(self, *args, **kwargs) -> None:
        tk.Tk.__init__(self, *args, **kwargs)

        # Setting up the screen
        self.title('Suspicious behaviour monitor')
        width= self.winfo_screenwidth()
        height= self.winfo_screenheight()
        self.geometry("%dx%d" % (width, height))

        # Initialising variables
        self.select_all_flag = True
        self.blacklisted_app_list = []
        self.existing_entries = set()
        self.connect_to_collections()
        set_alerts_collection(create_alerts())


        # Create all tabs,  all frames and set up the all pages
        self.create_tabs()
        self.create_frames()
        self.create_outlay_logs()
        self.create_outlay_alerts()
        self.create_outlay_dashboard()
        self.create_outlay_config()
        self.create_outlay_doc()

        # Connecting to the database
        self.update_data()

        #Start tailing system logs
        self.tail_logs()

        
    def update_data(self):

        update = threading.Thread(target =self.add_from_db_to_logs, daemon=True)
        update.start()
        

    def tail_logs(self):

        self.event = threading.Event()
        threshold = self.intvar.get()/100
        self.q = queue.Queue()
        tail_logs = threading.Thread(target=check_log.log_tailer, args=(self.q, self.event,self.blacklisted_app_list, threshold,), daemon=True)
        show_tailed_logs = threading.Thread(target=self.fill_dashboard, args=(self.q, self.event), daemon=True)

        tail_logs.start()
        show_tailed_logs.start()
    
    def connect_to_collections(self):
        
        # Load in collections.
        self.logs_collection = get_collection("Logs")
        self.alerts_collection = get_collection("Alerts")

    def add_from_db_to_logs(self):
        
        while True:
            set_logs_collection()
            data = list(self.logs_collection.find({}))
            self.add_to_logs(data)

            # Every 10 minutes the logs table is updated from the database
            time.sleep(600)

    

    def create_outlay_logs(self):

        table_scroll_v = tk.Scrollbar(self.table_frame_logs)
        table_scroll_v.pack(side="right", fill="y")

        self.my_data = ttk.Treeview(self.table_frame_logs,yscrollcommand=table_scroll_v.set)
        self.my_data.pack(side="top", fill = "both", expand=True)

        table_scroll_v.config(command=self.my_data.yview)

        #Define columns

        self.my_data['columns'] = ('index', 'timestamp', 'hostname', 'appname', "pid", "message")

        #Format  column
        self.my_data.column("#0", width=0,  stretch="no")
        for col in self.my_data['columns']:
            if col == "message":
                self.my_data.column(col, anchor="w", width=400)
            elif col == "index" or col == "pid":
                self.my_data.column(col, anchor="center", width=50)
            else:
                self.my_data.column(col, anchor="center", width= 110)
        

        #Create Headings 
        self.my_data.heading("#0",text="",anchor="center")
        headings = ["Index", "Timestamp", "Hostname", "Service", "Process ID", "Message"]
        for idx, col in enumerate(self.my_data['columns']):
            self.my_data.heading(col, text=headings[idx], anchor="center", command=lambda col=col: self.sort_column(self.my_data, col))


        #labels
        for idx, col in enumerate(self.my_data['columns']):
            tk.Label(self.table_frame_logs_entries,text=headings[idx]).grid(row=1, column=idx)



        #Entry boxes

        self.index_entry_logs = tk.Entry(self.table_frame_logs_entries)
        self.index_entry_logs.grid(row=2,column=0)

        self.timestamp_entry_logs= tk.Entry(self.table_frame_logs_entries)
        self.timestamp_entry_logs.grid(row=2, column=1)

        self.hostname_entry_logs = tk.Entry(self.table_frame_logs_entries)
        self.hostname_entry_logs.grid(row=2,column=2)

        self.appname_entry_logs = tk.Entry(self.table_frame_logs_entries)
        self.appname_entry_logs.grid(row=2,column=3)

        self.pid_entry_logs= tk.Entry(self.table_frame_logs_entries)
        self.pid_entry_logs.grid(row= 2, column=4)

        self.message_entry_logs = tk.Entry(self.table_frame_logs_entries)
        self.message_entry_logs.grid(row=2,column=5)

        

        # Buttons
        self.entry_list = [self.index_entry_logs, self.timestamp_entry_logs, self.hostname_entry_logs, 
                      self.appname_entry_logs, self.pid_entry_logs, self.message_entry_logs]
        
        
        select_all_button = tk.Button(self.table_frame_logs_buttons,text="Select All", command=lambda: self.select_all(self.my_data))
        select_all_button.pack(side="left",pady=10, padx=10)

        export_button = tk.Button(self.table_frame_logs_buttons,text="Export as CSV", command=lambda: self.export(self.my_data))
        export_button.pack(side="left",pady=10, padx=10)

        view_message_button = tk.Button(self.table_frame_logs_buttons, text="View Message", command=lambda: self.view_message(self.my_data))
        view_message_button.pack(side="left", pady=10, padx=10)

        clear_all_button = tk.Button(self.table_frame_logs_entries,text="Clear Fields", command=lambda: self.clear_entry_fields(self.entry_list))
        clear_all_button.grid(row=3, column=3, pady=10, padx=10)
        

        search_button = tk.Button(self.table_frame_logs_entries, text="Search", command=lambda: self.add_to_logs(list(self.search(self.entry_list))))
        search_button.grid(row=3, column=2, pady=10, padx=10)

        data = list(self.logs_collection.find({}))
        self.add_to_logs(data)

    def add_to_logs(self, data):    
        # Delete previous data
        self.my_data.delete(*self.my_data.get_children())
        
        # Add data from main
        for idx, dct in enumerate(data):
            if not dct.get("pid"):
                dct["pid"] = None
                
            keyorder = ['_id', 'timestamp', 'hostname', 'appname', 'pid', 'message']
            new_dct = {k: dct[k] for k in keyorder if k in dct}
            
            to_insert = tuple(new_dct.values())
            self.my_data.insert(parent='', index="end", text='', values=to_insert)
        self.my_data.pack()


    def create_outlay_dashboard(self):

        table_scroll_v = tk.Scrollbar(self.table_frame_dash)
        table_scroll_v.pack(side="right", fill="y")

        self.my_data_dash = ttk.Treeview(self.table_frame_dash,yscrollcommand=table_scroll_v.set)
        self.my_data_dash.pack(fill="both", expand=True)

        table_scroll_v.config(command=self.my_data_dash.yview)

        #Define columns

        self.my_data_dash['columns'] = ('index', "alert", "probability",'timestamp', 'hostname', 'appname', "pid", "message")

        #Format  column
        self.my_data_dash.column("#0", width=0,  stretch="no")
        for col in self.my_data_dash['columns']:
            if col == "message":
                self.my_data_dash.column(col, anchor="w", width=400)
            elif col == "index" or col == "alert":
                self.my_data_dash.column(col, anchor="center", width=50)
            elif col == "probability" or col == "hostname" or col == "timestamp":
                self.my_data_dash.column(col, anchor="center", width=200)
            else:
                self.my_data_dash.column(col, anchor="center", width= 110)
        

        #Create Headings 
        self.my_data_dash.heading("#0",text="",anchor="center")
        headings = ["Index", "Alert", "Probability of occurrence","Timestamp", "Hostname", "Service", "Process ID", "Message"]
        for idx, col in enumerate(self.my_data_dash['columns']):
            self.my_data_dash.heading(col,text=headings[idx],anchor="center")    
        
        
        # Create buttons
        select_all_button = tk.Button(self.table_frame_dash_buttons,text="Select all", command=lambda: self.select_all(self.my_data_dash))
        select_all_button.pack(side="left", padx=10)

        view_message_button = tk.Button(self.table_frame_dash_buttons, text="View Message", command=lambda: self.view_message(self.my_data_dash))
        view_message_button.pack(side="left", padx=10)
        
        export_button = tk.Button(self.table_frame_dash_buttons, text="Export as CSV", command=lambda: self.export(self.my_data_dash))
        export_button.pack(side="left", padx=10)

        report_button = tk.Button(self.table_frame_dash_buttons,text="Report", command=lambda: self.report(self.my_data_dash))
        report_button.pack(side="left", padx=10)

        safe_button = tk.Button(self.table_frame_dash_buttons,text="Mark safe", command=lambda: self.mark_safe(self.my_data_dash))
        safe_button.pack(side="left", padx=10)

        dismiss_button = tk.Button(self.table_frame_dash_buttons,text="Dismiss", command=lambda: self.dismiss(self.my_data_dash))
        dismiss_button.pack(side="left", padx=10)
      
    def fill_dashboard(self, queue, event):
        index = 1 
        while True:
            if event.is_set():
                break
            log_dct = queue.get()
            log_dct["_id"] = str(index)
            if not log_dct.get("pid"):
                log_dct["pid"] = None
            
            keyorder = ['_id', "alert", "probability", 'timestamp', 'hostname', 'appname', "pid", "message"]
            new_dct = {k: log_dct[k] for k in keyorder if k in log_dct}
            to_insert = tuple(new_dct.values())
            
            if to_insert not in self.existing_entries:  # Check if the data is already inserted
                # If suspicious then add it to the alert tab also
                if new_dct.get("alert") == True:
                    self.my_data_alerts.insert(parent='', index='end', text='', values=to_insert)
                    self.my_data_alerts.pack()
                self.my_data_dash.insert(parent='', index='end', text='', values=to_insert)
                self.my_data_dash.pack()
                self.existing_entries.add(to_insert)
                index += 1

    def create_outlay_alerts(self):

        table_scroll_v = tk.Scrollbar(self.table_frame_alerts)
        table_scroll_v.pack(side="right", fill="y")

        self.my_data_alerts = ttk.Treeview(self.table_frame_alerts,yscrollcommand=table_scroll_v.set)
        self.my_data_alerts.pack(fill="both", expand=True)

        table_scroll_v.config(command=self.my_data_alerts.yview)

        #Define columns

        self.my_data_alerts['columns'] = ('index', "alert", "probability", 'timestamp', 'hostname', 'appname', "pid", "message")

        #Format  column
        self.my_data_alerts.column("#0", width=0,  stretch="no")
        for col in self.my_data_alerts['columns']:
            if col == "message":
                self.my_data_alerts.column(col, anchor="w", width=400)
            elif col == "index" or col == "alert":
                self.my_data_alerts.column(col, anchor="center", width=50)
            elif col == "probability" or col == "hostname" or col == "timestamp":
                self.my_data_alerts.column(col, anchor="center", width=200)
            else:
                self.my_data_alerts.column(col, anchor="center", width= 110)

        #Create Headings 
        self.my_data_alerts.heading("#0",text="",anchor="center")
        headings = ["Index", "Alert", "Probability of occurrence", "Timestamp", "Hostname", "Service", "Process ID", "Message"]
        for idx, col in enumerate(self.my_data_alerts['columns']):
            self.my_data_alerts.heading(col,text=headings[idx],anchor="center")    

        # Buttons
        select_all_button = tk.Button(self.table_frame_alerts_buttons,text="Select all", command=lambda: self.select_all(self.my_data_alerts))
        select_all_button.pack(side="left", padx=10)

        view_message_button = tk.Button(self.table_frame_alerts_buttons, text="View Message", command=lambda: self.view_message(self.my_data_alerts))
        view_message_button.pack(side="left", padx=10)

        save_button = tk.Button(self.table_frame_alerts_buttons,text="Export", command=lambda: self.export(self.my_data_alerts))
        save_button.pack(side="left", padx=10)

        safe_button = tk.Button(self.table_frame_alerts_buttons,text="Mark safe", command=lambda: self.mark_safe(self.my_data_alerts))
        safe_button.pack(side="left", padx=10)

        dismiss_button = tk.Button(self.table_frame_alerts_buttons,text="Dismiss", command=lambda: self.dismiss(self.my_data_alerts))
        dismiss_button.pack(side="left", padx=10)
    
    def create_outlay_config(self):
        # Scrollbar
        yscrollbar = tk.Scrollbar(self.table_frame_config)
        yscrollbar.pack(side="right", fill="y")
        
        # Label and selected items display
        label = tk.Label(self.table_frame_config,
                         text="Select the actions/services that you would like to report as suspicious:",
                         padx=10, pady=10)
        label.pack(side="left")
        
        self.strvar = tk.StringVar()
        selected_items_label = tk.Label(self.table_frame_config_buttons, textvariable=self.strvar)
        selected_items_label.pack(padx=10, pady=10)
        
        # Listbox
        service_listbox = tk.Listbox(self.table_frame_config, selectmode="multiple", yscrollcommand=yscrollbar.set)
        service_listbox.pack(expand=True, fill="both", padx=50)
        yscrollbar.config(command=service_listbox.yview)
        
        # Populate listbox with services
        services = get_all_services()
        for service in services:
            service_listbox.insert("end", service)
        
        # Confirm button
        confirm = tk.Button(self.table_frame_config_buttons, text="Confirm selection", command=lambda: self.get_selected_services(self.strvar, service_listbox))
        confirm.pack(side="top")

        label_prob = tk.Label(self.table_frame_config_probability,
                        text="Set probability threshold percentage by entering a number between 0 and 100: ",
                        padx=10, pady=10)
        label_prob.pack(side="left")

        self.intvar = tk.IntVar()
        self.intvar.set(10)
        prob_label = tk.Label(self.table_frame_config_probability, textvariable=self.intvar)
        prob_label.pack(side="left", padx=10)

        enty_prob = tk.Entry(self.table_frame_config_probability)
        enty_prob.pack(side="left", padx=10)

        button_prob = tk.Button(self.table_frame_config_probability, text="Confirm threshold", command=lambda: self.change_threshold(enty_prob, self.intvar))
        button_prob.pack(side="left", padx=10)
    

    def  create_outlay_doc(self):
        # text_box = tk.Text(self.table_frame_doc, height = 5, width = 52)
        # documentation = "kaka"
        # text_box.insert(tk.END, documentation)
        # text_box.pack()
        tk.Label(self.table_frame_doc,text = "Instructions on how to use the app").pack()
  
        # Creating scrolled text area
        # widget with Read only by
        # disabling the state
        text_area = tk.scrolledtext.ScrolledText(self.table_frame_doc)
        
        text_area.pack(fill="both", expand=True)
        text="""
        This is a scrolledtext widget to make tkinter text read only.
        This is only placeholder!!!!!!!!
        """
        # Inserting Text which is read only
        text_area.insert(tk.INSERT,text)

        # Making the text read only
        text_area.configure(state ='disabled')
    
    def change_threshold(self, entry, intvar):
        
        try:
            new_threshold = int(entry.get())
            if new_threshold < 0 or new_threshold > 100:
                messagebox.showerror("Invalid input", "Please enter an integer number between 0 and 100.")
                return
            intvar.set(new_threshold)
            # Set event to stop and restart the tailing of the logs
            self.event.set()
            self.tail_logs()

        except ValueError:
            messagebox.showerror("Invalid input", "Please enter an integer number between 0 and 100.")

    def get_selected_services(self, strvar, service_listbox):
        self.blacklisted_app_list = [service_listbox.get(i) for i in service_listbox.curselection()]
        strvar.set(", ".join(self.blacklisted_app_list))
        self.event.set()
        self.tail_logs()

    def create_tabs(self):
        tabControl = ttk.Notebook(self)
        self.dashboard_tab = ttk.Frame(tabControl)
        self.logs_tab = ttk.Frame(tabControl)
        self.alerts_tab = ttk.Frame(tabControl)
        self.config_tab = ttk.Frame(tabControl)
        self.documentation_tab = ttk.Frame(tabControl)
        
        tabControl.add(self.dashboard_tab, text = "Dashboard")
        tabControl.add(self.logs_tab, text ='Logs')
        tabControl.add(self.alerts_tab, text ='Alerts')
        tabControl.add(self.config_tab, text ='Configuration')
        tabControl.add(self.documentation_tab, text ='Documentation')

        tabControl.pack(expand = 1, fill ="both")

    def create_frames(self):
        #Logs tab Frames
        self.table_frame_logs = tk.Frame(self.logs_tab, highlightbackground="black", highlightthickness=1, borderwidth=1, relief="sunken")
        self.table_frame_logs.pack(fill="both", expand=True)
        self.table_frame_logs_buttons = tk.Frame(self.logs_tab)
        self.table_frame_logs_buttons.pack()
        self.table_frame_logs_entries = tk.Frame(self.logs_tab)
        self.table_frame_logs_entries.pack(pady=90)

        # Alerts tab frames
        self.table_frame_alerts = tk.Frame(self.alerts_tab, highlightbackground="black", highlightthickness=1, borderwidth=1, relief="sunken")
        self.table_frame_alerts.pack(fill="both", expand=True)
        self.table_frame_alerts_buttons = tk.Frame(self.alerts_tab)
        self.table_frame_alerts_buttons.pack(pady=50)

        # Dashboard tab frames
        self.table_frame_dash = tk.Frame(self.dashboard_tab, highlightbackground="black", highlightthickness=1, borderwidth=1, relief="sunken")
        self.table_frame_dash.pack(fill= "both", expand=True)
        self.table_frame_dash_buttons = tk.Frame(self.dashboard_tab)
        self.table_frame_dash_buttons.pack(pady=50)

        # Config tab frames
        self.table_frame_config = tk.Frame(self.config_tab, width=700, height=450, highlightbackground="black", highlightthickness=1, borderwidth=1, relief="sunken")
        self.table_frame_config.pack(fill="both", expand=True)
        self.table_frame_config_buttons = tk.Frame(self.config_tab, highlightbackground="black", highlightthickness=1, borderwidth=1, relief="sunken")
        self.table_frame_config_buttons.pack(fill= "x")
        self.table_frame_config_probability = tk.Frame(self.config_tab, highlightbackground="black", highlightthickness=1, borderwidth=1, relief="sunken")
        self.table_frame_config_probability.pack(fill="both", expand = True)

        # Doc tab frames
        self.table_frame_doc = tk.Frame(self.documentation_tab, highlightbackground="black", highlightthickness=1, borderwidth=1, relief="sunken")
        self.table_frame_doc.pack(fill="both", expand=True)
    
    def export(self, tree):
        curItems = tree.selection()
        data = [tree.item(i)["values"] for i in curItems]
        if len(data) < 1:
            messagebox.showerror("No data", "No data available to export")
            return
        try:
            fln = filedialog.asksaveasfilename(initialdir=os.getcwd(), title="Save as CSV", filetypes=(("CSV File", "*.csv"), ("All files", "*.*")))
            with open(fln, mode="w", newline='') as myfile:
                exp_writer = csv.writer(myfile)
                exp_writer.writerows(data)        
        # If selection is cancelled return    
        except TypeError:
            return
        messagebox.showinfo("Data Exported", "Your data has been exported to "+os.path.basename(fln)  +" successfully")

    def dismiss(self, tree):
        selected_items = tree.selection()
        if selected_items:
            if messagebox.askyesno("Dismiss action", "Are you sure you want to dismiss the selected action(s)?"):
                for i in selected_items:
                    tree.delete(i)
        else:
            messagebox.showerror("No data", "No rows were selected")

    def view_message(self, tree):
        selected_items = tree.selection()
        message_list = []
        if selected_items:
            for iid in selected_items:
                data = tree.item(iid, 'values')
                message_list.append(data[-1])
            messagebox.showinfo("View Messsage", message_list)
        else:
            messagebox.showerror("No data", "No rows were selected")
    
    def report(self, tree):
        selected_items = tree.selection()
        if selected_items:
            if messagebox.askyesno("Report action", "Are you sure you want to report the selected action(s)?"):
                for iid in selected_items:
                    data = tree.item(iid, 'values')
                    if data[1] == "True":
                        messagebox.showerror("Already reported", "The selected item(s) have been flagged as suspicious already")
                        return
                    else:
                        updated_data = list(data)  # Convert the tuple to a list
                        updated_data[1] = "True"  # Set the "alert" value to "True"

                        host, app = data[4], data[5]
                        # Update the identified field in the alerts_collection
                        self.alerts_collection.update_one(
                            {"hostname": host, 
                            "appname": app
                            },
                            {"$set": 
                            {"identified": True}
                            }
                        )

                        tree.delete(iid)  # Remove the existing item
                        tree.insert("", "end", iid=iid, values=tuple(updated_data))  # Insert the updated item
                        self.my_data_alerts.insert("", "end", iid=iid, values=tuple(updated_data))

                messagebox.showinfo("Reported", "The selected items have been reported")
        else:
            messagebox.showerror("No data", "No rows were selected")

    def mark_safe(self, tree):
        selected_items = tree.selection()
        if selected_items:
            if messagebox.askyesno("Mark action as safe", "Are you sure you want to mark the selected action(s) as safe?"):
                for iid in selected_items:
                    data = tree.item(iid, "values")
                    if data[1] == "False":
                        messagebox.showerror("Already safe", "The selected item(s) is already marked as safe")
                        return
                    # row[1] = False
                    else:
                        updated_data = list(data)
                        updated_data[1] = "False"
                        host, app = data[4], data[5]
                        self.alerts_collection.update_one({
                            "hostname": host,
                            "appname":app
                        },
                        {
                            "$set": {
                                "identified": "Safe"
                            }
                        })
                        tree.delete(iid)  # Remove the existing item
                        if tree == self.my_data_dash:
                            tree.insert("", "end", iid=iid, values=tuple(updated_data))  # Insert the updated item
                        if tree == self.my_data_alerts:
                            self.my_data_dash.delete(iid)  # Remove the existing item
                            self.my_data_dash.insert("", "end", iid=iid, values=tuple(updated_data))  # Insert the updated item
                        else:
                            self.my_data_alerts.delete(iid)  # Remove the existing item

        else:
            messagebox.showerror("No data", "No rows were selected")
     

    def select(self, tree):
        curItems = tree.selection()
        self.to_export = [tree.item(i)["values"] for i in curItems]

    def select_all(self, tree):
        if self.select_all_flag:
            for item in tree.get_children():
                tree.item(item, open=True)
                tree.selection_add(item)
            self.select_all_flag = False
        else:
            for item in tree.selection():
                tree.selection_remove(item)
            self.select_all_flag = True
    
    def search(self, entry_list):
        keys = ["_id","timestamp", "hostname", "appname","pid", "message"]
        query = {}
        for idx, entry in enumerate(entry_list):
            try:
                to_search = str(entry.get())
                if to_search:
                    if entry == self.timestamp_entry_logs:
                        datetime_object = datetime.strptime(to_search, "%Y-%m-%d %H:%M:%S")
                        query[keys[idx]] = datetime_object
                    else:
                        query[keys[idx]] = to_search
            except ValueError:
                messagebox.showerror("Input error",
                "The entry you have entered is not in the correct format.")
        return self.logs_collection.find(query)
    
    def clear_entry_fields(self, entry_list):
        for entry in entry_list:
            entry.delete(0, "end")
    
    def sort_table(self, column, asc=1):
    
        # return self.logs_collection.find({}).sort(column, asc)
        return (self.search(self.entry_list)).sort(column, asc)

    def sort_column(self, tree, col):
        headings = ["Index", "Timestamp", "Hostname", "Service", "Process ID", "Message"]

        current_sort_column = tree.heading(col, 'command')

        # Function to sort in ascending order
        def ascending_sort(col=col):
            tree.heading(col, text=f"{headings[tree['columns'].index(col)]} ▲", anchor="center", command=lambda: descending_sort(col))
            self.add_to_logs(self.sort_table(col, 1))

        # Function to sort in descending order
        def descending_sort(col=col):
            tree.heading(col, text=f"{headings[tree['columns'].index(col)]} ▼", anchor="center", command=lambda: ascending_sort(col))
            self.add_to_logs(self.sort_table(col, -1))

        if callable(current_sort_column):
            if current_sort_column == ascending_sort:
                descending_sort()
            else:
                ascending_sort()
        else:
            ascending_sort()

    def select_record(self, my_data, entry_list):
    #clear entry boxes
        for entry in entry_list:
            entry.delete(0, "end")

        #grab record
        selected = my_data.focus()
        #grab record values
        values = my_data.item(selected, 'values')
        #output to entry boxes
        for idx, entry in enumerate(entry_list):
            entry.insert(0, values[idx])
        self.select(tree=my_data)            


if __name__ == "__main__":
  
    app = Gui()
    app.mainloop()
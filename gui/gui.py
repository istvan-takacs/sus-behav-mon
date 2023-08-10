import tkinter as tk
from  tkinter import ttk
from tkinter import messagebox, filedialog, Scrollbar
import threading
import sys
import os
import csv
sys.path.insert(0, '/home/istvan/Desktop/sus-behav-mon/storing_logs')
sys.path.insert(0, '/home/istvan/Desktop/sus-behav-mon/handling_logs')
import check_log
import queue
import handling_logs
import mongo_connect
import pymongo
import datetime
from datetime import datetime
import time
import add_logs_to_database

class Gui(tk.Tk):
    def __init__(self, *args, **kwargs) -> None:
        tk.Tk.__init__(self, *args, **kwargs)

        self.title('Suspicious Behaviour Monitor')
        width= self.winfo_screenwidth()
        height= self.winfo_screenheight()
        self.geometry("%dx%d" % (width, height))
        self.connect_to_collections()
        self.create_tabs()
        self.create_frames()
        self.create_outlay_logs()
        self.create_outlay_alerts()
        self.create_outlay_dashboard()
        self.create_outlay_config()
        self.tail_logs()

        
      

        # NEED TO SET UP COMM with DB
        # ALERTS
        # handling_logs.add_alerts_to_db(self.alert_table_data) ##update alerts
        # handling_logs.get_alerts_from_db() ## to get alerts table

        # LOGS
        # add_logs_to_database.set_logs_collection() ## update logs collection
        # add_logs_to_database.get_logs_collection() ## get logs collection
    def tail_logs(self):

        self.q = queue.Queue()
        tail_logs = threading.Thread(target=check_log.log_tailer, args=(self.q,), daemon=True)
        show_tailed_logs = threading.Thread(target=self.fill_dashboard, args=(self.q,), daemon=True)

        tail_logs.start()
        show_tailed_logs.start()
    
    def connect_to_collections(self):

        self.client = mongo_connect.get_client()

        # Create a connection to the database.
        self.db = self.client[mongo_connect.get_database_name()]

        # Load in collections.
        self.logs_collection = self.db["Logs"]
        self.alerts_collection = self.db["Alerts"]

    

    def create_outlay_logs(self):

        table_scroll_v = tk.Scrollbar(self.table_frame_logs)
        table_scroll_v.pack(side="right", fill="y")

        table_scroll_h = tk.Scrollbar(self.table_frame_logs,orient='horizontal')
        table_scroll_h.pack(side= "bottom",fill="x")



        self.my_data = ttk.Treeview(self.table_frame_logs,yscrollcommand=table_scroll_v.set, xscrollcommand=table_scroll_h.set)
        self.my_data.pack(fill = "both", expand=True)

    

        table_scroll_v.config(command=self.my_data.yview)
        table_scroll_h.config(command=self.my_data.xview)


        #Define columns

        self.my_data['columns'] = ('index', 'timestamp', 'hostname', 'appname', "pid", "message")

        #Format  column
        self.my_data.column("#0", width=0,  stretch="no")
        for col in self.my_data['columns']:
            if col == "message":
                self.my_data.column(col, anchor="center", width=800)
            elif col == "index" or col =="pid" or col=="appname":
                self.my_data.column(col, anchor="center", width=100)
            else:
                self.my_data.column(col, anchor="center", width= 300)
        

        #Create Headings 
        self.my_data.heading("#0",text="",anchor="center")
        headings = ["Index", "Timestamp", "Hostname", "Service", "Process ID", "Message"]
        for idx, col in enumerate(self.my_data['columns']):
            self.my_data.heading(col, text=headings[idx], anchor="center", command=lambda col=col: self.sort_column(self.my_data, col))


        #labels
        for idx, col in enumerate(self.my_data['columns']):
            tk.Label(self.table_frame_logs_entries,text=headings[idx]).grid(row=0, column=idx)



        #Entry boxes

        self.index_entry_logs = tk.Entry(self.table_frame_logs_entries)
        self.index_entry_logs.grid(row=1,column=0)

        self.timestamp_entry_logs= tk.Entry(self.table_frame_logs_entries)
        self.timestamp_entry_logs.grid(row=1, column=1)

        self.hostname_entry_logs = tk.Entry(self.table_frame_logs_entries)
        self.hostname_entry_logs.grid(row=1,column=2)

        self.appname_entry_logs = tk.Entry(self.table_frame_logs_entries)
        self.appname_entry_logs.grid(row=1,column=3)

        self.pid_entry_logs= tk.Entry(self.table_frame_logs_entries)
        self.pid_entry_logs.grid(row= 1, column=4)

        self.message_entry_logs = tk.Entry(self.table_frame_logs_entries)
        self.message_entry_logs.grid(row=1,column=5)

        

        # Buttons
        entry_list = [self.index_entry_logs, self.timestamp_entry_logs, self.hostname_entry_logs, 
                      self.appname_entry_logs, self.pid_entry_logs, self.message_entry_logs]
        
        
        select_all_button = tk.Button(self.table_frame_logs_buttons,text="Select All", command=lambda: self.select_all(self.my_data))
        select_all_button.pack(side="left")
        
        export_button = tk.Button(self.table_frame_logs_buttons,text="Export as CSV", command=lambda: self.export(self.my_data))
        export_button.pack(side="left")

        search_button = tk.Button(self.table_frame_logs_buttons, text="Search", command=lambda: self.add_to_logs(self.search(entry_list)))
        search_button.pack(side="left")

        data = list(self.logs_collection.find({}))
        self.add_to_logs(data)

    def add_to_logs(self, data):    
        
        # delete previous data
        self.my_data.delete(*self.my_data.get_children())
        #add data from main
        for idx, dct in enumerate(data):

            if not dct.get("pid"):
                dct["pid"] = None

            keyorder = ['_id', 'timestamp', 'hostname', 'appname', 'pid', 'message']
            new_dct = {k: dct[k] for k in keyorder if k in dct}
            # print(new_dct)
            to_insert = tuple(new_dct.values())
            self.my_data.insert(parent='',index="end",iid=idx,text='',values= to_insert)
        self.my_data.pack()


    def create_outlay_dashboard(self):

        table_scroll_v = tk.Scrollbar(self.table_frame_dash)
        table_scroll_v.pack(side="right", fill="y")

        table_scroll_h = tk.Scrollbar(self.table_frame_dash,orient='horizontal')
        table_scroll_h.pack(side= "bottom",fill="x")



        self.my_data_dash = ttk.Treeview(self.table_frame_dash,yscrollcommand=table_scroll_v.set, xscrollcommand=table_scroll_h.set)
        self.my_data_dash.pack()

        table_scroll_v.config(command=self.my_data_dash.yview)
        table_scroll_h.config(command=self.my_data_dash.xview)


        #Define columns

        self.my_data_dash['columns'] = ('index', "alert", "probability",'timestamp', 'hostname', 'appname', "pid", "message")

        #Format  column
        self.my_data_dash.column("#0", width=0,  stretch="no")
        for col in self.my_data_dash['columns']:
            if col == "message":
                self.my_data_dash.column(col, anchor="center", width=800)
            elif col == "index" or col =="pid" or col=="appname" or col == "alert":
                self.my_data_dash.column(col, anchor="center", width=100)
            else:
                self.my_data_dash.column(col, anchor="center", width= 200)
        

        #Create Headings 
        self.my_data_dash.heading("#0",text="",anchor="center")
        headings = ["Index", "Alert", "Probability of occurrence","Timestamp", "Hostname", "Service", "Process ID", "Message"]
        for idx, col in enumerate(self.my_data_dash['columns']):
            self.my_data_dash.heading(col,text=headings[idx],anchor="center")    
        
        
        
        f = tk.Frame(self.dashboard_tab)
        f.pack(pady=20)

        #labels
        for idx, col in enumerate(self.my_data_dash['columns']):
            tk.Label(f,text=headings[idx]).grid(row=0, column=idx)



        #Entry boxex
        self.timestamp_entry_dash= tk.Entry(f)
        self.timestamp_entry_dash.grid(row= 1, column=0)

        self.alert_entry_dash= tk.Entry(f)
        self.alert_entry_dash.grid(row= 1, column=1)

        self.hostname_entry_dash = tk.Entry(f)
        self.hostname_entry_dash.grid(row=1,column=2)

        self.appname_entry_dash = tk.Entry(f)
        self.appname_entry_dash.grid(row=1,column=3)

        self.pid_entry_dash= tk.Entry(f)
        self.pid_entry_dash.grid(row= 1, column=4)

        self.message_entry_dash = tk.Entry(f)
        self.message_entry_dash.grid(row=1,column=5)

        self.index_entry_dash = tk.Entry(f)
        self.index_entry_dash.grid(row=1,column=6)

        # Buttons
        entry_list = [self.timestamp_entry_dash, self.alert_entry_dash, self.hostname_entry_dash, 
                      self.appname_entry_dash, self.pid_entry_dash, self.message_entry_dash, self.index_entry_dash]
        
        
        select_all_button = tk.Button(self.dashboard_tab,text="Select all", command=lambda: self.select_all(self.my_data_dash))
        select_all_button.pack(side="left")
        
        export_button = tk.Button(self.dashboard_tab, text="Export as CSV", command=lambda: self.export(self.my_data_dash))
        export_button.pack(side="left")

        report_button = tk.Button(self.dashboard_tab,text="Report", command=lambda: self.report(self.my_data_dash))
        report_button.pack(side="left")

        safe_button = tk.Button(self.dashboard_tab,text="Mark safe", command=lambda: self.mark_safe(self.my_data_dash))
        safe_button.pack(side="left")

        dismiss_button = tk.Button(self.dashboard_tab,text="Dismiss", command=lambda: self.dismiss(self.my_data_dash))
        dismiss_button.pack(side="left")
      
    def fill_dashboard(self, queue):
        index = 1 
        while True:
            log_dct = queue.get()
            log_dct["_id"] = str(index)
            if not log_dct.get("pid"):
                log_dct["pid"] = None
            

            keyorder = ['_id', "alert", "probability", 'timestamp', 'hostname', 'appname', "pid", "message"]
            new_dct = {k: log_dct[k] for k in keyorder if k in log_dct}
            to_insert = tuple(new_dct.values())
            # If suspicious then add it to the alert tab also
            if new_dct.get("alert") == True:
                self.my_data_alerts.insert(parent='',index='end', iid=to_insert[0],text='',values= to_insert)
                self.my_data_alerts.pack()

            
            self.my_data_dash.insert(parent='',index='end',iid=to_insert[0], text='',values= to_insert)
            self.my_data_dash.pack()
            index += 1

    def create_outlay_alerts(self):

        table_scroll_v = tk.Scrollbar(self.table_frame_alerts)
        table_scroll_v.pack(side="right", fill="y")

        table_scroll_h = tk.Scrollbar(self.table_frame_alerts,orient='horizontal')
        table_scroll_h.pack(side= "bottom",fill="x")



        self.my_data_alerts = ttk.Treeview(self.table_frame_alerts,yscrollcommand=table_scroll_v.set, xscrollcommand=table_scroll_h.set)
        self.my_data_alerts.pack(fill="both", expand=True)

        table_scroll_v.config(command=self.my_data_alerts.yview)
        table_scroll_h.config(command=self.my_data_alerts.xview)


        #Define columns

        self.my_data_alerts['columns'] = ('index', "alert", "probability", 'timestamp', 'hostname', 'appname', "pid", "message")

        #Format  column
        self.my_data_alerts.column("#0", width=0,  stretch="no")
        for col in self.my_data_alerts['columns']:
            if col == "message":
                self.my_data_alerts.column(col, anchor="center", width=800)
            elif col == "index" or col =="pid" or col=="appname" or col == "alert":
                self.my_data_alerts.column(col, anchor="center", width=100)
            else:
                self.my_data_alerts.column(col, anchor="center", width= 200)
        

        #Create Headings 
        self.my_data_alerts.heading("#0",text="",anchor="center")
        headings = ["Index", "Alert", "Probability of occurrence", "Timestamp", "Hostname", "Service", "Process ID", "Message"]
        for idx, col in enumerate(self.my_data_alerts['columns']):
            self.my_data_alerts.heading(col,text=headings[idx],anchor="center")    
        

        # Buttons
        select_all_button = tk.Button(self.table_frame_alerts_buttons,text="Select all", command=lambda: self.select_all(self.my_data_alerts))
        select_all_button.pack(side="left")

        save_button = tk.Button(self.table_frame_alerts_buttons,text="Export", command=lambda: self.export(self.my_data_alerts))
        save_button.pack(side="left")

        safe_button = tk.Button(self.table_frame_alerts_buttons,text="Mark safe", command=lambda: self.mark_safe(self.my_data_alerts))
        safe_button.pack(side="left")

        dismiss_button = tk.Button(self.table_frame_alerts_buttons,text="Dismiss", command=lambda: self.dismiss(self.my_data_alerts))
        dismiss_button.pack(side="left")
    
    def create_outlay_config(self):
        # for scrolling vertically
        yscrollbar = tk.Scrollbar(self.table_frame_config)
        yscrollbar.pack(side = "right", fill = "y")
        
        label = tk.Label(self.table_frame_config,
                    text = "Select the languages below :  ",
                    padx = 10, pady = 10)
        label.pack(side="left")
        list = tk.Listbox(self.table_frame_config, selectmode = "multiple", yscrollcommand = yscrollbar.set)
        
        # Widget expands horizontally and 
        # vertically by assigning both to
        # fill option
        list.pack(padx = 10, pady = 10,side="left", expand = "yes", fill = "both")
        
        x =["C", "C++", "C#", "Java", "Python",
            "R", "Go", "Ruby", "JavaScript", "Swift",
            "SQL", "Perl", "XML"]
        
        for item in range(len(x)):
            
            list.insert("end", x[item])
            list.itemconfig(item)
        
        # Attach listbox to vertical scrollbar
        yscrollbar.config(command = list.yview)

        selected_text_list = [list.get(i) for i in list.curselection()]
        l = tk.Label(self.table_frame_config, text=selected_text_list).pack()

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
        self.table_frame_logs = tk.Frame(self.logs_tab)
        self.table_frame_logs.pack(fill="both", expand=True)
        self.table_frame_logs_entries = tk.Frame(self.logs_tab)
        self.table_frame_logs_entries.pack(pady=90)
        self.table_frame_logs_buttons = tk.Frame(self.logs_tab)
        self.table_frame_logs_buttons.pack(pady=80)

        # Alerts tab frames
        self.table_frame_alerts = tk.Frame(self.alerts_tab)
        self.table_frame_alerts.pack(fill="both", expand=True)
        self.table_frame_alerts_buttons = tk.Frame(self.alerts_tab)
        self.table_frame_alerts_buttons.pack(pady=150)

        # Dashboard tab frames
        self.table_frame_dash = tk.Frame(self.dashboard_tab)
        self.table_frame_dash.pack()

        # Config tab frames
        self.table_frame_config = tk.Frame(self.config_tab)
        self.table_frame_config.pack()

        # Doc tab frames
        self.table_frame_doc = tk.Frame(self.documentation_tab)
        self.table_frame_doc.pack()
    
    def export(self, tree):
        curItems = tree.selection()
        data = [tree.item(i)["values"] for i in curItems]
        if len(data) < 1:
            messagebox.showerror("No data", "No data available to export")
        fln = filedialog.asksaveasfilename(initialdir=os.getcwd(), title="Save as CSV", filetypes=(("CSV File", "*.csv"), ("All files", "*.*")))
        with open(fln, mode="w", newline='') as myfile:
            exp_writer = csv.writer(myfile)
            exp_writer.writerows(data)
        messagebox.showinfo("Data Exported", "Your data has been exported to "+os.path.basename(fln)  +" successfully")

    def dismiss(self, tree):
        selected_items = tree.selection()
        if selected_items:
            for i in selected_items:
                tree.delete(i)
        else:
            messagebox.showerror("No data", "No rows were selected")
    
    def report(self, tree):
        selected_items = tree.selection()
        if selected_items:
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
        # data = [tree.item(i)["values"] for i in selected_items]
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
        for item in tree.get_children():
            tree.item(item, open=True)
            tree.selection_add(item)
    
    def search(self, entry_list):
        keys = ["_id","timestamp", "hostname", "appname","pid", "message"]
        query = {}
        for idx, entry in enumerate(entry_list):
            to_search = str(entry.get())
            if to_search:
                if entry == self.timestamp_entry_logs:
                    datetime_object = datetime.strptime(to_search, "%Y-%m-%d %H:%M:%S")
                    query[keys[idx]] = datetime_object
                else:
                    query[keys[idx]] = to_search
        return list(self.logs_collection.find(query))
    
    
    def sort_table(self, column, asc=1):
    
        return self.logs_collection.find({}).sort(column, asc)

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

    # TODO rewrite this to save record 
    def update_record(self, my_data, entry_list):
        selected=my_data.focus()
        #save new data 
        all_entries = tuple([entry.get() for entry in entry_list])
        my_data.item(selected,text="",values=all_entries)
        
    #clear entry boxes
        for entry in entry_list:
            entry.delete(0, "end")


if __name__ == "__main__":
  
    app = Gui()
    app.mainloop()
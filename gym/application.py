import collections
import calendar
import datetime
from tkinter import *
from tkinter.ttk import *
from . import database



# TODO create widget InputTable to enhance input_rows of _create_new_session
# function. Constructor should take parent widget and starting column, row as
# arguments.
class InputsTable:

    
    def __init__(self, master, col0, row0):
        self._master = master
        self._col0 = col0
        self._row0 = row0
        self._columns = []
        self._rows = []


    def add_column(self, heading, input_class):
        # TODO
        return


    def remove_column(self, **kwargs):
        # TODO if heading or index is in kwargs, remove accordingly
        return


    def add_row(self, widgets_list):
        assert len(widgets_list) == len(self._columns)
        for i, (w, grid_ops) in enumerate(widgets_list):
            # TODO if w is not instance of input_class raise error else place
            # it in master with grid_ops
            pass


    def remove_row(self):
        # TODO remove last added row
        if self._rows:
            last = self._rows[-1]
            for w in last:
                w.destroy()


class ConfirmationWindow(Toplevel):


    def __init__(self, master, title, text, on_confirm_command, on_reject_command=None):
        super().__init__(master)
        self.title(title)
        self._text = text
        self._on_confirm_command = on_confirm_command
        self._on_reject_command = self.destroy
        if on_reject_command:
            self._on_reject_command = on_reject_command
        
        self._create_widgets()
        
        self.update()
        self.minsize(self.winfo_width(), self.winfo_height())
        self.maxsize(self.winfo_width(), self.winfo_height())


    @property
    def on_confirm_command(self):
        return self._on_confirm_command


    @property
    def on_reject_command(self):
        return self._on_reject_command


    @property
    def text(self):
        return self._text


    def _create_widgets(self):
        Label(self, text=self._text).grid(column=1, row=0, padx=5, pady=5)
        Button(self, text="OK",
               command=self._on_confirm_command).grid(column=0, row=1, padx=5,
                                                     pady=5)
        Button(self, text="Cancel",
               command=self._on_reject_command).grid(column=2, row=1, padx=5,
                                                     pady=5)
       

class Calendar:


    _years = list(range(1900, datetime.datetime.now().year + 1))
    _months = list(range(1, 13))
    _date_format = "%Y-%m-%d %H:%M:%S"


    def __init__(self, master, col0, row0, **kwargs):
        self._master = master
        self._col0 = col0
        self._row0 = row0
        self._kwargs = kwargs

        for i, row in enumerate(range(row0, row0+3)):
            if i == 0:
                Label(self._master, text="Year:", anchor=W, justify=LEFT).grid(
                    column=col0, row=row, padx=5, pady=5)
                self._yearcb = Combobox(self._master, state="readonly", values=self._years)
                self._yearcb.grid(column=col0+1, row=row)
            elif i == 1:
                Label(self._master, text="Month:", anchor=W, justify=LEFT).grid(
                    column=col0, row=row, padx=5, pady=5)
                self._monthcb = Combobox(self._master, state="readonly",
                                        values=self._months)
                self._monthcb.grid(column=col0+1, row=row)
            elif i == 2:
                Label(self._master, text="Day:", anchor=W, justify=LEFT).grid(
                    column=col0, row=row, padx=5, pady=5)
                self._daycb = Combobox(self._master, state="readonly")
                self._daycb.grid(column=col0+1, row=row)

        self._yearcb.bind("<<ComboboxSelected>>", self._on_year_selected)
        self._monthcb.bind("<<ComboboxSelected>>", self._on_month_selected)

        self._set_default_date()


    def _set_default_date(self):
        default_date = self._kwargs.get("default_date", None)
        if not default_date:
            now = datetime.datetime.now()
            self._set_days(now.year, now.month)
            self._yearcb.set(now.year)
            self._monthcb.set(now.month)
            self._daycb.set(now.day)
        else:
            try:
                date = datetime.datetime.strptime(default_date, self._date_format)
                self._yearcb.set(date.year)
                self._monthcb.set(date.month)
                self._daycb.set(date.day)
                self._set_days(date.year, date.month)
            except ValueError:
                # timestamp not provided, try collection (year, month, day)
                self._yearcb.set(default_date[0])
                self._monthcb.set(default_date[1])
                self._daycb.set(default_date[2])
                self._set_days(default_date[0], default_date[1])


    def _get_selected_value(self, widget):
        val = widget.get()
        try:
            return int(val)
        except ValueError:
            try:
                return float(val)
            except ValueError:
                return val


    def _set_days(self, year, month):
        _, days = calendar.monthrange(year, month)
        self._daycb.configure(values=list(range(1, days+1)))


    def _on_year_selected(self, event):
        year = self._get_selected_value(self._yearcb)
        month = self._get_selected_value(self._monthcb)
        if year and month and year in self._years and month in self._months:
            self._set_days(year, month)


    def _on_month_selected(self, event):
        year = self._get_selected_value(self._yearcb)
        month = self._get_selected_value(self._monthcb)
        if year and month and year in self._years and month in self._months:
            self._set_days(year, month)


    def _is_date_selected(self):
        return (self._get_selected_value(self._yearcb) and
                self._get_selected_value(self._monthcb) and
                self._get_selected_value(self._daycb))


    def get_selected_date(self):
        if self._is_date_selected():
            return datetime.datetime(
                self._get_selected_value(self._yearcb),
                self._get_selected_value(self._monthcb),
                self._get_selected_value(self._daycb)
            )
        return None



class Application(Tk):


    def __init__(self, master=None):

        super().__init__(master)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        ## frame containing table with sessions
        self.table_frame = Frame(self, padding=(5, 5))
        self.table_frame.grid(column=0, row=0, sticky=(N, E, S, W))
        self.table_frame.columnconfigure(0, weight=1)
        self.table_frame.rowconfigure(0, weight=1)

        ## frame containing buttons
        self.widget_frame = Frame(self, padding=(5, 5))
        self.widget_frame.grid(column=1, row=0, sticky=(N, E, S, W))
        #self.widget_frame.columnconfigure(0, weight=1)
        self.widget_frame.rowconfigure(98, weight=1)

        ## create table
        self.table = Treeview(self.table_frame, selectmode="browse")
        self.table.grid(column=0, row=0, sticky=(N, S, E, W))
        headers = list(map(str.upper, database.get_session_headers()))
        self.table['columns'] = headers[1:]
        for i in range(len(headers)):
            colid = "#{}".format(i)
            text = "{}".format(headers[i])
            self.table.heading(colid, text=text, anchor="w")
            self.table.column(colid, anchor="w")
        
        # populate table
        self.__populate_table()
        
        ## create buttons

        # details button
        Button(self.widget_frame, text="Details",
               command=self.__display_session_details).grid(
               column=0, row=0, padx=5, pady=5, sticky=(N, W, S, E))

        # update button
        Button(self.widget_frame, text="Update",
               command=self.__update_session).grid(
               column=0, row=1, padx=5, pady=5, sticky=(N, W, S, E))

        # delete button
        Button(self.widget_frame, text="Delete",
               command=self.__delete_session).grid(
               column=0, row=2, padx=5, pady=5, sticky=(N, W, S, E))

        # Quit button
        b = Button(self.widget_frame, text="Quit", command=self.destroy)
        b.grid(column=99, row=99, padx=5, pady=5, sticky=(N, W, S, E))

        # new button
        b = Button(self.widget_frame, text="New", command=self.__create_new)
        b.grid(column=0, row=99, padx=5, pady=5, sticky=(N, W, S, E))

        ## set min size
        self.update()
        self.minsize(self.winfo_width(), self.winfo_height())


    def __populate_table(self):
        self.table.delete(*self.table.get_children())
        sessions = database.get_session()
        for record in sessions:
            self.table.insert('', 'end', text="{}".format(record[0]), values=record[1:])


    def __get_selected_session(self):
        return self.table.item(self.table.focus())


    def __display_session_details(self):
        session = self.__get_selected_session()
        if session["text"]:
            session_details = database.get_session_details(
                session_id=session["text"])

            # create session details window
            details_win = Toplevel(self)
            details_win.title("Details")
            details_win.columnconfigure(0, weight=1)
            details_win.rowconfigure(1, weight=1)
            Button(details_win, text="Cancel",
                   command=details_win.destroy).grid(column=1, row=2, padx=5,
                                                     pady=5)
            session_frame = Frame(details_win)
            session_frame.grid(column=0, row=0, sticky=(S, W, N, E))
            Label(session_frame, text="Session ID:").grid(column=0, row=0,
                                                          padx=5, pady=5)
            e = Entry(session_frame)
            e.insert(0, session["text"])
            e.configure(state="readonly", justify=CENTER)
            e.grid(column=1, row=0, padx=5, pady=5)
            Label(session_frame, text="Date:").grid(column=2, row=0,
                                                          padx=5, pady=5)
            e = Entry(session_frame)
            e.insert(0, session["values"][0])
            e.configure(state="readonly", justify=CENTER)
            e.grid(column=3, row=0, padx=5, pady=5)

            # create exercise details window
            details_frame = Frame(details_win)
            details_frame.grid(column=0, row=1, sticky=(S, W, N, E))
            details_frame.columnconfigure(0, weight=1)
            details_frame.rowconfigure(0, weight=1)
            table = Treeview(details_frame)
            table.grid(column=0, row=0, sticky=(S, W, N, E))
            headers = ("#", "EXERCISE", "WEIGHT, KG", "TOTAL REPETITIONS",
                       "SETS", "INTENSITY")
            table.configure(columns=headers[1:])
            for i in range(len(headers)):
                col = "#{}".format(i)
                table.heading(col, text=headers[i])
            for i, details in enumerate(session_details):
                eid = details[2]
                ename = "UNNAMED"
                if eid:
                    ename = database.get_exercise(_id=eid)[0][1].upper()
                values = (ename,) + details[3:]
                table.insert('', 'end', text=i+1, values=values)

            details_win.update()
            details_win.minsize(details_win.winfo_width(),
                                details_win.winfo_height())


    def __update_session(self):
        session = self.__get_selected_session()
        if session["text"]:
            def edit_date():
                def _edit_date():
                    # get new values from calendar and update database
                    new_date = c.get_selected_date()
                    if new_date:
                        date_entry.configure(state="normal")
                        date_entry.delete(0, 'end')
                        date_entry.insert(0, new_date)
                        date_entry.configure(state="readonly")
                    date_form.destroy()

                date_form = Toplevel(form)
                date_form.title("Update date")
                Button(date_form, text="OK", command=_edit_date).grid(column=0, row=3,
                                                            padx=5, pady=5)
                Button(date_form, text="Cancel", command=date_form.destroy).grid(column=2, row=3,
                                                            padx=5, pady=5)
                c = Calendar(date_form, 0, 0, default_date=date_entry.get())

            # TODO open up form for edditing session
            form = Toplevel(self)
            form.title("Edit session")
            form.columnconfigure(0, weight=1)
            form.rowconfigure(1, weight=1)

            # session details
            sd_frame = Frame(form)
            sd_frame.grid(column=0, row=0)
            Label(sd_frame, text="Session ID:").grid(column=0, row=0, padx=5,
                                                     pady=5)
            e = Entry(sd_frame)
            e.insert(0, session["text"])
            e.configure(state="readonly")
            e.grid(column=1, row=0, padx=5, pady=5)

            Label(sd_frame, text="Date:").grid(column=0, row=1, padx=5,
                                                     pady=5)
            date_entry = Entry(sd_frame)
            date_entry.insert(0, session["values"][0])
            date_entry.configure(state="readonly")
            date_entry.grid(column=1, row=1, padx=5, pady=5)
            Button(sd_frame, text="Edit", command=edit_date).grid(column=2,
                                                                  row=1,
                                                                  padx=5,
                                                                  pady=5)



            # exercise details
            ed_frame = Frame(form)
            ed_frame.grid(column=0, row=1)



            form.update()
            form.minsize(form.winfo_width(), form.winfo_height())
            form.maxsize(form.winfo_width(), form.winfo_height())


    def __delete_session(self):
        session = self.__get_selected_session()
        if session["text"]:
            def do_on_yes():
                database.delete_session(session["text"])
                self.__populate_table()
                c.destroy()

            c = ConfirmationWindow(
                self,
                "Delete session",
                "Are you sure you want to delete selected session?",
                do_on_yes
            )


    def __create_new(self):
        form = Toplevel(self)
        form.title("New")
        form.columnconfigure(0, weight=1)
        form.rowconfigure(0, weight=1)

        # new session button
        b = Button(form, text="New session",
                   command=lambda: self.__create_new_session(form))
        b.grid(column=0, row=1, padx=5, pady=5, sticky=(N, W, S, E))

        # new exercise button
        b = Button(form, text="New exercise",
                   command=lambda: self.__create_new_exercise(form))
        b.grid(column=0, row=2, padx=5, pady=5, sticky=(N, W, S, E))

        # cancel button
        b = Button(form, text="Cancel", command=form.destroy)
        b.grid(column=0, row=99, padx=5, pady=(10, 15), sticky=(N, W, S, E))

        # set min and max windows size
        form.update()
        form.minsize(self.winfo_width(), form.winfo_height())
        form.maxsize(self.winfo_width(), form.winfo_height())


    def __create_new_session(self, root):
        def create_session():
            session_details = []
            for inp in input_rows.rows:
                if inp[0].get() and inp[0].get() != '':
                    details = {}
                    acronym = inp[0].get().split(",")[-1].strip()
                    eid = list(filter(
                        lambda x: x[2] == acronym, exercises
                    ))[-1][0]
                    details["exercise_id"] = eid
                    details["weight_kg"] = float(inp[1].get())
                    details["reps_total"] = int(inp[2].get())
                    details["sets"] = int(inp[3].get())
                    details["intensity"] = int(inp[4].get())
                    session_details.append(details)

            # return if no input provided
            if not session_details or not cal.get_selected_date():
                return

            # insert session in database
            date = cal.get_selected_date()
            database.insert_session(timestamp=date)
            session_id = database.get_last_rowid()
            for sd in session_details:
                sd["session_id"] = int(session_id)
                database.insert_session_details(**sd)

            form.destroy()
            self.__populate_table()

        class input_rows:
            row0 = 4
            rows = []

            @classmethod
            def add_input_rows(cls, count=5):
                _maxrows = len(exercises)
                _min, _max = cls.row0, cls.row0 + count
                for row_id in range(_min, _max):
                    if len(cls.rows) == _maxrows:
                        break
                    row = tuple()
                    # add exercise dropdown
                    # updated
                    cb = Combobox(form, state="readonly")
                    cb.bind("<<ComboboxSelected>>", cls.populate_dropdowns)
                    cb.grid(column=0, row=row_id, padx=5, pady=5)
                    row += (cb,)
                    # add weight entry
                    e = Entry(form)
                    e.grid(column=1, row=row_id, padx=5, pady=5)
                    row += (e,)
                    # add total repetitions entry
                    e = Entry(form)
                    e.grid(column=2, row=row_id, padx=5, pady=5)
                    row += (e,)
                    # add sets entry
                    e = Entry(form)
                    e.grid(column=3, row=row_id, padx=5, pady=5)
                    row += (e,)
                    # add intensity entry
                    e = Spinbox(form, values=list(range(1, 11)), wrap=True,
                                state="readonly")
                    e.grid(column=4, row=row_id, padx=5, pady=5)
                    row += (e,)
                    cls.rows.append(row)
                    cls.row0 += 1
                form.update_idletasks()
                form.minsize(form.winfo_reqwidth(), form.winfo_reqheight())
                form.maxsize(form.winfo_reqwidth(), form.winfo_reqheight())

                cls.populate_dropdowns()

            @classmethod
            def populate_dropdowns(cls, *args):
                acronyms = list(map(
                    lambda x: x[0].get().split(",")[-1].strip(), cls.rows
                ))
                selected = set(filter(
                    lambda x: x[2] in acronyms,
                    exercises
                ))

                non_selected = [('', '', '')] + list(exercises.difference(
                    selected))

                for r in cls.rows:
                    dd = r[0]
                    dd.configure(values=list(map(
                        lambda x: x[1] + ", " + x[2] if x[1] else '', non_selected
                    )))

        root.withdraw()
        form = Toplevel(root)
        form.title("New session")
        form.columnconfigure(0, weight=1)
        form.rowconfigure(0, weight=1)

        # session date selection
        cal = Calendar(form, 0, 0)

        # cancel button
        b = Button(form, text="Cancel", command=form.destroy)
        b.grid(column=4, row=99, padx=5, pady=5, sticky=(N, W, S, E))

        # more inputs button
        b = Button(form, text="Add more exercises", command=lambda: input_rows.add_input_rows(1))
        b.grid(column=4, row=98, padx=5, pady=5, sticky=(N, W, S, E))

        # add button
        b = Button(form, text="Create", command=create_session)
        b.grid(column=0, row=99, padx=5, pady=5, sticky=(N, W, S, E))

        # create 5 dropdowns with available exercises
        # on select, update dropdown list to remove selected item
        Label(form, text="Execise", anchor=W, justify=LEFT).grid(
            column=0, row=3, padx=5, pady=5)
        Label(form, text="Weight, KG", anchor=W, justify=LEFT).grid(
            column=1, row=3, padx=5, pady=5)
        Label(form, text="Total repetition", anchor=W, justify=LEFT).grid(
            column=2, row=3, padx=5, pady=5)
        Label(form, text="Sets", anchor=W, justify=LEFT).grid(
            column=3, row=3, padx=5, pady=5)
        Label(form, text="Intensity", anchor=W, justify=LEFT).grid(
            column=4, row=3, padx=5, pady=5)

        exercises = set(database.get_exercise())
        input_rows.add_input_rows()

        # set min and max windows size
        form.update()
        form.minsize(form.winfo_width(), form.winfo_height())
        form.maxsize(form.winfo_width(), form.winfo_height())


    def __create_new_exercise(self, root):

        def create_exercise():
            exercise = {
                "name": inputs[0].get(),
                "acronym": inputs[1].get(),
                "description": inputs[2].get("1.0", END)
            }
            database.insert_exercise(**exercise)
            form.destroy()

        def delete_exercise():
            def _delete():
                for i, e in enumerate(exercises):
                    if e and e[2] == acronym:
                        database.delete_exercise(e[0])
                        del exercises[i]
                        exercisecb.configure(values=__get_exercisecb_values())
                        break
                exercisecb.set("")
                c.destroy()

            selected = exercisecb.get()
            acronym = selected.split(",")[-1].strip()
            if acronym:
                c = ConfirmationWindow(
                    self,
                    "Delete exercise",
                    "Are you sure you want to delete selected exercise?",
                    _delete
                )
                
        def __get_exercisecb_values():
            return [""] + [e[1] + ", " + e[2] if e else "" for e in exercises]

        root.withdraw()
        form = Toplevel(root)
        form.title("New exercise")
        form.columnconfigure(3, weight=1)
        form.rowconfigure(0, weight=1)

        # list of existing exercises and delete button
        Label(form, text="Exercises:").grid(column=0, row=0, padx=5, pady=5)
        exercises = database.get_exercise()
        exercisecb = Combobox(form, values=__get_exercisecb_values(), state="readonly")
        exercisecb.grid(column=1, row=0, padx=5, pady=5)
        Button(form, text="Delete", command=delete_exercise).grid(column=2,
                                                                  row=0,
                                                                  padx=5,
                                                                  pady=5)

        # inputs
        Label(form, text="Name").grid(column=0, row=1, padx=5, pady=5)
        Label(form, text="Acronym").grid(column=0, row=2, padx=5, pady=5)
        Label(form, text="Description").grid(column=0, row=3, padx=5, pady=5)
        inputs = (
            Entry(form),
            Entry(form),
            Text(form)
        )
        for i, e in enumerate(inputs):
            e.grid(column=1, row=i+1, padx=5, pady=5, sticky=(S, E, W, N),
                   columnspan=3)

        # cancel button
        b = Button(form, text="Cancel", command=form.destroy)
        b.grid(column=4, row=99, padx=5, pady=5, sticky=(N, W, S, E))

        # add button
        b = Button(form, text="Create", command=create_exercise)
        b.grid(column=0, row=99, padx=5, pady=5, sticky=(N, W, S, E))

        # set min and max windows size
        form.update()
        form.minsize(form.winfo_width(), form.winfo_height())
        form.maxsize(form.winfo_width(), form.winfo_height())



def main():
    database.init_db()
    app = Application()
    app.title("Gym")
    app.mainloop()
    database.close_db()


if __name__ == '__main__':
    main()

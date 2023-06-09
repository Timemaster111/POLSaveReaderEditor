"""Display class and functions for a GUI"""
import datetime
import os
import tkinter as tk
import winfiletime
from tkinter import filedialog as fd
from typing import List, Union, Optional
import shutil

from reader import Reader
from util.save import Save
from writer import Writer
from playsound import playsound


class Display:
    """
    Display class for handling GUI and associated methods
    """

    def __init__(self):
        self._window = tk.Tk()
        self._reader = Reader()
        self._writer = Writer()
        self._main = None
        self._mainsave = Save()
        self._compsave = Save()
        self.mode = "EDIT"
        self.mainvals = []
        self.compvals = []
        self._buttons = {
            "LEFT": [],
            "RIGHT": []
        }
        self._backupButton = None
        self.__timestamp: List[bool, Optional[tk.Button]] = [False, None]
        self.__version: List[bool, Optional[tk.Button]] = [False, None]
        self.__elapsed: List[bool, Optional[tk.Button]] = [False, None]
        self.__deaths: List[bool, Optional[tk.Button]] = [True, None]
        self.__slot: List[bool, Optional[tk.Button]] = [False, None]
        self.__chapter: List[bool, Optional[tk.Button]] = [True, None]
        self.__scene: List[bool, Optional[tk.Button]] = [True, None]
        self.__position: List[bool, Optional[tk.Button]] = [False, None]
        self.__shrines: List[bool, Optional[tk.Button]] = [False, None]
        self._logging: List[bool, Optional[tk.Button], int] = [True, None, 0]
        self.__lastFile = ""

    def run(self):
        """
        Run the GUI
        """
        self.__setupEditorGui()
        self._window.mainloop()

    def __setupMainGui(self):
        win = self._window
        if self._main:
            self._main.destroy()
            self._main = tk.Frame(win)
        frame = self._main = tk.Frame(win)
        frame.config(bd=1, relief=tk.GROOVE)
        frame.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(frame)
        left.config(bd=1, relief=tk.RIDGE, padx=2, pady=3)
        left.columnconfigure(0, weight=1)
        left.pack(fill=tk.BOTH, side=tk.LEFT)
        left_cont = tk.Frame(left)
        left_cont.pack(fill=tk.X, side=tk.TOP)

        self._editButton = tk.Button(left_cont, text="Edit", command=self.__setupEditorGui)
        self._editButton.pack(fill=tk.X, expand=True)
        self._compareButton = tk.Button(left_cont, text="Compare", command=self.__setupCompareGui)
        self._compareButton.pack(fill=tk.X, expand=True)
        self._monitorButton = tk.Button(left_cont, text="Monitor", command=self.__setupConstantCompareGui)
        self._monitorButton.pack(fill=tk.X, expand=True)

    def __setupToolbarGui(self, cont, save, side):
        but1 = tk.Button(cont, text="1", command=lambda: self.__buttonPress(lambda: self._reader.readFile(
            f'{os.getenv("APPDATA")}\\..\\LocalLow\\Wishfully\\Planet of Lana\\slot_0.sav', saveOverride=save),
                                                                            side, 0)
                         )
        but1.pack(fill=tk.X, expand=True, side=tk.LEFT)
        but2 = tk.Button(cont, text="2", command=lambda: self.__buttonPress(lambda: self._reader.readFile(
            f'{os.getenv("APPDATA")}\\..\\LocalLow\\Wishfully\\Planet of Lana\\slot_1.sav', saveOverride=save),
                                                                            side, 1)
                         )
        but2.pack(fill=tk.X, expand=True, side=tk.LEFT)
        but3 = tk.Button(cont, text="3", command=lambda: self.__buttonPress(lambda: self._reader.readFile(
            f'{os.getenv("APPDATA")}\\..\\LocalLow\\Wishfully\\Planet of Lana\\slot_2.sav', saveOverride=save),
                                                                            side, 2)
                         )
        but3.pack(fill=tk.X, expand=True, side=tk.LEFT)
        but4 = tk.Button(cont, text="Custom", command=lambda: self.__buttonPress(lambda: self.__openCustom(save),
                                                                                 side, 3))
        but4.pack(fill=tk.X, expand=True, side=tk.LEFT)
        self._buttons[side] = [but1, but2, but3, but4]

    def __buttonPress(self, action, side, button=4):
        action()
        if self.mode == "EDIT":
            self.__changeVals(self.mainvals, self._mainsave)
        if self.mode == "COMPARE":
            if side == "LEFT":
                self.__changeVals(self.mainvals, self._mainsave)
            else:
                self.__changeVals(self.compvals, self._compsave)
            if self._mainsave.version is not None and self._compsave.version is not None:
                self.__checkCompare()
        if self.mode == "MONITOR":
            self.__changeVals(self.mainvals, self._mainsave)
            self._window.after(1, self.__constantCompare)

        if button < len(self._buttons[side]):
            for but in self._buttons[side]:
                but["relief"] = tk.RAISED
            self._buttons[side][button]["relief"] = tk.SUNKEN

    def __constantCompare(self):
        if self.mode != "MONITOR":
            return
        newSave = Save()
        currFile = self._reader.lastFile[:]
        self._reader.readFile(self._reader.lastFile, newSave)
        changes = self._reader.compare(newSave, self._mainsave)
        if len(changes) or self.__lastFile == "":
            if self._logging[0]:
                if not self._logging[2]:
                    self._logging[2] = int(datetime.datetime.now().timestamp())
                if self._reader.lastFile:
                    os.makedirs(f'{os.getenv("APPDATA")}\\..\\LocalLow\\Wishfully\\Planet of Lana\\'
                                f'{datetime.datetime.fromtimestamp(self._logging[2]).strftime("%Y%m%d - %H%M%S")}'
                                , exist_ok=True)
                    shutil.copy(self._reader.lastFile,
                                f'{os.getenv("APPDATA")}\\..\\LocalLow\\Wishfully\\Planet of Lana\\'
                                f'{datetime.datetime.fromtimestamp(self._logging[2]).strftime("%Y%m%d - %H%M%S")}'
                                f'\\{datetime.datetime.now().strftime("%Y%m%d - %H%M%S")}.sav')

        if currFile != self.__lastFile:
            self.__lastFile = currFile
            print("skipped")
            self._window.after(10000, self.__constantCompare)
            return
        self.__lastFile = currFile
        ding = False
        if "timestamp" in changes:
            self.mainvals[0]["fg"] = "red"
            if self.__timestamp[0]:
                ding = True
        else:
            self.mainvals[0]["fg"] = "black"
        if "version" in changes:
            self.mainvals[1]["fg"] = "red"
            if self.__version[0]:
                ding = True
        else:
            self.mainvals[1]["fg"] = "black"
        if "elapsed" in changes:
            self.mainvals[2]["fg"] = "red"
            if self.__elapsed[0]:
                ding = True
        else:
            self.mainvals[2]["fg"] = "black"
        if "deathcounter" in changes:
            self.mainvals[3]["fg"] = "red"
            if self.__deaths[0]:
                ding = True
        else:
            self.mainvals[3]["fg"] = "black"
        if "slot" in changes:
            self.mainvals[4]["fg"] = "red"
            if self.__slot[0]:
                ding = True
        else:
            self.mainvals[4]["fg"] = "black"
        if "chapterId" in changes:
            self.mainvals[5]["fg"] = "red"
            if self.__chapter[0]:
                ding = True
        else:
            self.mainvals[5]["fg"] = "black"
        if "sceneId" in changes:
            self.mainvals[6]["fg"] = "red"
            if self.__scene[0]:
                ding = True
        else:
            self.mainvals[6]["fg"] = "black"
        if "position" in changes:
            if changes["position"][0][0] != changes["position"][1][0]:
                self.mainvals[7][0]["fg"] = "red"
                if self.__position[0]:
                    ding = True
            else:
                self.mainvals[7][0]["fg"] = "black"
            if changes["position"][0][1] != changes["position"][1][1]:
                self.mainvals[7][1]["fg"] = "red"
                if self.__position[0]:
                    ding = True
            else:
                self.mainvals[7][1]["fg"] = "black"
            if changes["position"][0][2] != changes["position"][1][2]:
                self.mainvals[7][2]["fg"] = "red"
                if self.__position[0]:
                    ding = True
            else:
                self.mainvals[7][2]["fg"] = "black"
        self.__changeVals(self.mainvals, newSave)
        self._mainsave = newSave
        if ding:
            playsound("snd_fragment_retrievewav-14728.mp3")
        self._window.after(10000, self.__constantCompare)

    def __checkCompare(self):
        for i in range(8):
            if type(self.mainvals[i]) != list:
                if self.mainvals[i]["text"] != self.compvals[i]["text"]:
                    self.mainvals[i]["fg"] = "red"
                    self.compvals[i]["fg"] = "red"
                else:
                    self.mainvals[i]["fg"] = "black"
                    self.compvals[i]["fg"] = "black"
            else:
                for j in range(3):
                    if self.mainvals[i][j]["text"] != self.compvals[i][j]["text"]:
                        self.mainvals[i][j]["fg"] = "red"
                        self.compvals[i][j]["fg"] = "red"
                    else:
                        self.mainvals[i][j]["fg"] = "black"
                        self.compvals[i][j]["fg"] = "black"

    def __changeVals(self, vals: List[Union[tk.Entry, tk.Label, List[tk.Entry]]], save):
        vals[0]["text"] = winfiletime.to_datetime(save.timestamp).strftime("%Y/%m/%d - %H:%M:%S")
        vals[1]["text"] = save.version
        vals[2]["text"] = datetime.datetime.fromtimestamp(save.elapsed).strftime("%Hh %Mm %Ss")
        vals[3]["text"] = str(save.deathcounter)
        if type(vals[4]) == tk.Entry:
            vals[4].delete(0, "end")
            vals[4].insert(0, str(save.slot + 1))
            vals[5].delete(0, "end")
            vals[5].insert(0, str(save.chapterId))
            vals[6].delete(0, "end")
            vals[6].insert(0, str(save.sceneId))
            vals[7][0].delete(0, "end")
            vals[7][0].insert(0, str(save.position[0]))
            vals[7][1].delete(0, "end")
            vals[7][1].insert(0, str(save.position[1]))
            vals[7][2].delete(0, "end")
            vals[7][2].insert(0, str(save.position[2]))
        else:
            vals[4]["text"] = str(save.slot + 1)
            vals[5]["text"] = str(save.chapterId)
            vals[6]["text"] = str(save.sceneId)
            vals[7][0]["text"] = str(save.position[0])
            vals[7][1]["text"] = str(save.position[1])
            vals[7][2]["text"] = str(save.position[2])

    def __openCustom(self, save):
        file = fd.askopenfilename(initialdir=f'{os.getenv("APPDATA")}\\..\\LocalLow\\Wishfully\\Planet of Lana\\',
                                  defaultextension="sav", filetypes=(("Save Files", "*.sav"), ("All Files", "*.*")))
        if file:
            self._reader.readFile(file, saveOverride=save)

    def __saveAs(self):
        file = fd.asksaveasfilename(initialdir=f'{os.getenv("APPDATA")}\\..\\LocalLow\\Wishfully\\Planet of Lana\\',
                                    defaultextension="sav", filetypes=(("Save Files", "*.sav"), ("All Files", "*.*")))
        if not file:
            return
        shutil.copy("./base.sav", file)
        self.__save(file)

    def __save(self, file):
        self._mainsave.chapterId = int(self.mainvals[5].get())
        self._mainsave.sceneId = int(self.mainvals[6].get())
        self._mainsave.position = [int(self.mainvals[7][0].get()),
                                   int(self.mainvals[7][1].get()),
                                   int(self.mainvals[7][2].get())]
        self._mainsave.slot = int(self.mainvals[4].get()) - 1
        self._writer.writeFile(file, saveOverride=self._mainsave)
        self.__buttonPress(lambda: self._reader.readFile(file, saveOverride=self._mainsave), "LEFT")

    def __setupEditorGui(self):
        self.mode = "EDIT"
        self.__setupMainGui()
        self._window.title("Planet of Lana Save Editor - Editing")
        self._editButton["relief"] = tk.SUNKEN
        right = tk.Frame(self._main)
        right.config(bd=1, relief=tk.SUNKEN)
        right.columnconfigure(1, weight=1)
        right.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)

        tools = tk.Frame(right)
        tools.config(bd=1, relief=tk.SUNKEN, padx=2, pady=3)
        tools.rowconfigure(0, weight=1)
        tools.pack(fill=tk.BOTH, side=tk.TOP)
        tools_cont = tk.Frame(tools)
        tools_cont.pack(fill=tk.X, side=tk.LEFT)

        self.__setupToolbarGui(tools, self._mainsave, "LEFT")
        tk.Button(tools, text="Save",
                  command=lambda: self.__save(self._reader.lastFile)) \
            .pack(fill=tk.X, expand=True, side=tk.LEFT)
        tk.Button(tools, text="Save As", command=self.__saveAs).pack(fill=tk.X, expand=True, side=tk.LEFT)
        self._backupButton = tk.Button(tools, text="Backup", command=self.__backup)
        self._backupButton.pack(fill=tk.X, expand=True, side=tk.LEFT)

        self.mainvals = self.__setupValsEntry(right)

    def __backup(self):
        if self._reader.lastFile:
            os.makedirs(f'{os.getenv("APPDATA")}\\..\\LocalLow\\Wishfully\\Planet of Lana\\'
                        f'backups\\'
                        , exist_ok=True)
            shutil.copy(self._reader.lastFile,
                        f'{os.getenv("APPDATA")}\\..\\LocalLow\\Wishfully\\Planet of Lana\\backups\\'
                        f'{datetime.datetime.now().strftime("%Y%m%d - %H%M%S")}.sav')
            self._backupButton["fg"] = "green"

    def __setupValsEntry(self, frame):
        column1 = tk.Frame(frame)
        column1.pack(fill=tk.BOTH, side=tk.LEFT)
        column2 = tk.Frame(frame)
        column2.pack(fill=tk.BOTH, side=tk.LEFT)
        row1 = tk.Frame(column1)
        row1.pack(fill=tk.BOTH, side=tk.TOP)
        tk.Label(row1, text="Timestamp: ").pack(side=tk.LEFT)
        row1 = tk.Frame(column2)
        row1.pack(fill=tk.BOTH, side=tk.TOP)
        timestampEntry = tk.Label(row1, text=str(winfiletime.to_datetime(self._mainsave.timestamp)
                                                 .strftime("%Y/%m/%d - %H:%M:%S")
                                                 if self._mainsave.timestamp is not None else None))
        timestampEntry.pack(side=tk.LEFT)
        row2 = tk.Frame(column1)
        row2.pack(fill=tk.BOTH, side=tk.TOP)
        tk.Label(row2, text="Deaths: ").pack(side=tk.LEFT)
        row2 = tk.Frame(column2)
        row2.pack(fill=tk.BOTH, side=tk.TOP)
        deathcounterEntry = tk.Label(row2, text=str(self._mainsave.deathcounter))
        deathcounterEntry.pack(side=tk.LEFT)
        row3 = tk.Frame(column1)
        row3.pack(fill=tk.BOTH, side=tk.TOP)
        tk.Label(row3, text="Chapter: ").pack(side=tk.LEFT)
        row3 = tk.Frame(column2)
        row3.pack(fill=tk.BOTH, side=tk.TOP)
        chapterEntry = tk.Entry(row3)
        chapterEntry.insert(0, str(self._mainsave.chapterId))
        chapterEntry.pack(side=tk.LEFT)
        column3 = tk.Frame(frame)
        column3.pack(fill=tk.BOTH, side=tk.LEFT)
        tk.Label(column3, text="\t").pack(side=tk.LEFT)

        column1 = tk.Frame(frame)
        column1.pack(fill=tk.BOTH, side=tk.LEFT)
        column2 = tk.Frame(frame)
        column2.pack(fill=tk.BOTH, side=tk.LEFT)
        row1 = tk.Frame(column1)
        row1.pack(fill=tk.BOTH, side=tk.TOP)
        tk.Label(row1, text="Version: ").pack(side=tk.LEFT)
        row1 = tk.Frame(column2)
        row1.pack(fill=tk.BOTH, side=tk.TOP)
        versionEntry = tk.Label(row1, text=self._mainsave.version)
        versionEntry.pack(side=tk.LEFT)
        row2 = tk.Frame(column1)
        row2.pack(fill=tk.BOTH, side=tk.TOP)
        tk.Label(row2, text="Shrines: ").pack(side=tk.LEFT)
        row2 = tk.Frame(column2)
        row2.pack(fill=tk.BOTH, side=tk.TOP)
        shrineEntry = tk.Label(row2, text="WIP")
        shrineEntry.pack(side=tk.LEFT)
        row3 = tk.Frame(column1)
        row3.pack(fill=tk.BOTH, side=tk.TOP)
        tk.Label(row3, text="Scene: ").pack(side=tk.LEFT)
        row3 = tk.Frame(column2)
        row3.pack(fill=tk.BOTH, side=tk.TOP)
        sceneEntry = tk.Entry(row3)
        sceneEntry.insert(0, str(self._mainsave.sceneId))
        sceneEntry.pack(side=tk.LEFT)
        column3 = tk.Frame(frame)
        column3.pack(fill=tk.BOTH, side=tk.LEFT)
        tk.Label(column3, text="\t").pack(side=tk.LEFT)

        column1 = tk.Frame(frame)
        column1.pack(fill=tk.BOTH, side=tk.LEFT)
        column2 = tk.Frame(frame)
        column2.pack(fill=tk.BOTH, side=tk.LEFT)
        row1 = tk.Frame(column1)
        row1.pack(fill=tk.BOTH, side=tk.TOP)
        tk.Label(row1, text="Elapsed: ").pack(side=tk.LEFT)
        row1 = tk.Frame(column2)
        row1.pack(fill=tk.BOTH, side=tk.TOP)
        elapsedEntry = tk.Label(row1, text=str(datetime.datetime.fromtimestamp(self._mainsave.elapsed)
                                               .strftime("%Hh %Mm %Ss")
                                               if self._mainsave.elapsed is not None else None))
        elapsedEntry.pack(side=tk.LEFT)
        row2 = tk.Frame(column1)
        row2.pack(fill=tk.BOTH, side=tk.TOP)
        tk.Label(row2, text="Slot: ").pack(side=tk.LEFT)
        row2 = tk.Frame(column2)
        row2.pack(fill=tk.BOTH, side=tk.TOP)
        slotEntry = tk.Entry(row2)
        slotEntry.insert(0, str(self._mainsave.slot + 1 if self._mainsave.slot is not None else None))
        slotEntry.pack(side=tk.LEFT)
        row3 = tk.Frame(column1)
        row3.pack(fill=tk.BOTH, side=tk.TOP)
        tk.Label(row3, text="Position: ").pack(side=tk.LEFT)
        row3 = tk.Frame(column2)
        row3.pack(fill=tk.BOTH, side=tk.TOP)
        positionEntry = [tk.Entry(row3), tk.Entry(row3), tk.Entry(row3)]
        for i in range(3):
            positionEntry[i].insert(0, str(self._mainsave.position[i]))
            positionEntry[i].pack(side=tk.LEFT)

        return [
            timestampEntry, versionEntry, elapsedEntry, deathcounterEntry, slotEntry, chapterEntry, sceneEntry,
            positionEntry
        ]

    def __setupValsLabel(self, frame, save):
        column1 = tk.Frame(frame)
        column1.pack(fill=tk.BOTH, side=tk.LEFT)
        column2 = tk.Frame(frame)
        column2.pack(fill=tk.BOTH, side=tk.LEFT)
        row1 = tk.Frame(column1)
        row1.pack(fill=tk.BOTH, side=tk.TOP)
        tk.Label(row1, text="Timestamp: ").pack(side=tk.LEFT)
        row1 = tk.Frame(column2)
        row1.pack(fill=tk.BOTH, side=tk.TOP)
        timestampEntry = tk.Label(row1, text=str(winfiletime.to_datetime(save.timestamp)
                                                 .strftime("%Y/%m/%d - %H:%M:%S")
                                                 if save.timestamp is not None else None))
        timestampEntry.pack(side=tk.LEFT)
        row2 = tk.Frame(column1)
        row2.pack(fill=tk.BOTH, side=tk.TOP)
        tk.Label(row2, text="Deaths: ").pack(side=tk.LEFT)
        row2 = tk.Frame(column2)
        row2.pack(fill=tk.BOTH, side=tk.TOP)
        deathcounterEntry = tk.Label(row2, text=str(save.deathcounter))
        deathcounterEntry.pack(side=tk.LEFT)
        row3 = tk.Frame(column1)
        row3.pack(fill=tk.BOTH, side=tk.TOP)
        tk.Label(row3, text="Chapter: ").pack(side=tk.LEFT)
        row3 = tk.Frame(column2)
        row3.pack(fill=tk.BOTH, side=tk.TOP)
        chapterEntry = tk.Label(row3, text=str(save.chapterId))
        chapterEntry.pack(side=tk.LEFT)
        column3 = tk.Frame(frame)
        column3.pack(fill=tk.BOTH, side=tk.LEFT)
        tk.Label(column3, text="\t").pack(side=tk.LEFT)

        column1 = tk.Frame(frame)
        column1.pack(fill=tk.BOTH, side=tk.LEFT)
        column2 = tk.Frame(frame)
        column2.pack(fill=tk.BOTH, side=tk.LEFT)
        row1 = tk.Frame(column1)
        row1.pack(fill=tk.BOTH, side=tk.TOP)
        tk.Label(row1, text="Version: ").pack(side=tk.LEFT)
        row1 = tk.Frame(column2)
        row1.pack(fill=tk.BOTH, side=tk.TOP)
        versionEntry = tk.Label(row1, text=save.version)
        versionEntry.pack(side=tk.LEFT)
        row2 = tk.Frame(column1)
        row2.pack(fill=tk.BOTH, side=tk.TOP)
        tk.Label(row2, text="Shrines: ").pack(side=tk.LEFT)
        row2 = tk.Frame(column2)
        row2.pack(fill=tk.BOTH, side=tk.TOP)
        shrineEntry = tk.Label(row2, text="WIP")
        shrineEntry.pack(side=tk.LEFT)
        row3 = tk.Frame(column1)
        row3.pack(fill=tk.BOTH, side=tk.TOP)
        tk.Label(row3, text="Scene: ").pack(side=tk.LEFT)
        row3 = tk.Frame(column2)
        row3.pack(fill=tk.BOTH, side=tk.TOP)
        sceneEntry = tk.Label(row3, text=str(save.sceneId))
        sceneEntry.pack(side=tk.LEFT)
        column3 = tk.Frame(frame)
        column3.pack(fill=tk.BOTH, side=tk.LEFT)
        tk.Label(column3, text="\t").pack(side=tk.LEFT)

        column1 = tk.Frame(frame)
        column1.pack(fill=tk.BOTH, side=tk.LEFT)
        column2 = tk.Frame(frame)
        column2.pack(fill=tk.BOTH, side=tk.LEFT)
        row1 = tk.Frame(column1)
        row1.pack(fill=tk.BOTH, side=tk.TOP)
        tk.Label(row1, text="Elapsed: ").pack(side=tk.LEFT)
        row1 = tk.Frame(column2)
        row1.pack(fill=tk.BOTH, side=tk.TOP)
        elapsedEntry = tk.Label(row1, text=str(datetime.datetime.fromtimestamp(save.elapsed)
                                               .strftime("%Hh %Mm %Ss")
                                               if save.elapsed is not None else None))
        elapsedEntry.pack(side=tk.LEFT)
        row2 = tk.Frame(column1)
        row2.pack(fill=tk.BOTH, side=tk.TOP)
        tk.Label(row2, text="Slot: ").pack(side=tk.LEFT)
        row2 = tk.Frame(column2)
        row2.pack(fill=tk.BOTH, side=tk.TOP)
        slotEntry = tk.Label(row2, text=str(save.slot + 1 if save.slot is not None else None))
        slotEntry.pack(side=tk.LEFT)
        row3 = tk.Frame(column1)
        row3.pack(fill=tk.BOTH, side=tk.TOP)
        tk.Label(row3, text="Position: ").pack(side=tk.LEFT)
        row3 = tk.Frame(column2)
        row3.pack(fill=tk.BOTH, side=tk.TOP)
        positionEntry = [tk.Label(row3, text=str(save.position[i])) for i in range(3)]
        for i in range(3):
            positionEntry[i].pack(side=tk.LEFT)

        return [
            timestampEntry, versionEntry, elapsedEntry, deathcounterEntry, slotEntry, chapterEntry, sceneEntry,
            positionEntry
        ]

    def __reverse(self, thing):
        thing[0] = not thing[0]
        if thing[0]:
            thing[1]["fg"] = "green"
            if len(thing) == 3:
                if not self._logging[2]:
                    self._logging[2] = int(datetime.datetime.now().timestamp())
                if self._reader.lastFile:
                    os.makedirs(f'{os.getenv("APPDATA")}\\..\\LocalLow\\Wishfully\\Planet of Lana\\'
                                f'{datetime.datetime.fromtimestamp(self._logging[2]).strftime("%Y%m%d - %H%M%S")}'
                                , exist_ok=True)
                    shutil.copy(self._reader.lastFile,
                                f'{os.getenv("APPDATA")}\\..\\LocalLow\\Wishfully\\Planet of Lana\\'
                                f'{datetime.datetime.fromtimestamp(self._logging[2]).strftime("%Y%m%d - %H%M%S")}'
                                f'\\{datetime.datetime.now().strftime("%Y%m%d - %H%M%S")}.sav')
        else:
            thing[1]["fg"] = "red"
            if len(thing) == 3:
                thing[2] = 0

    def __setupValsInverse(self, frame):
        column1 = tk.Frame(frame)
        column1.pack(fill=tk.BOTH, side=tk.LEFT)
        column2 = tk.Frame(frame)
        column2.pack(fill=tk.BOTH, side=tk.LEFT)
        row1 = tk.Frame(column1)
        row1.pack(fill=tk.BOTH, side=tk.TOP)
        timestamp = tk.Button(row1, text="Timestamp: ", command=lambda: self.__reverse(self.__timestamp),
                              relief=tk.GROOVE, borderwidth=0, pady=0, fg="red")
        timestamp.pack(side=tk.LEFT)
        row1 = tk.Frame(column2)
        row1.pack(fill=tk.BOTH, side=tk.TOP)
        timestampEntry = tk.Label(row1, text=str(winfiletime.to_datetime(self._mainsave.timestamp)
                                                 .strftime("%Y/%m/%d - %H:%M:%S")
                                                 if self._mainsave.timestamp is not None else None))
        timestampEntry.pack(side=tk.LEFT)
        row2 = tk.Frame(column1)
        row2.pack(fill=tk.BOTH, side=tk.TOP)
        deaths = tk.Button(row2, text="Deaths: ", command=lambda: self.__reverse(self.__deaths), relief=tk.GROOVE,
                           borderwidth=0, pady=0, fg="green")
        deaths.pack(side=tk.LEFT)
        row2 = tk.Frame(column2)
        row2.pack(fill=tk.BOTH, side=tk.TOP)
        deathcounterEntry = tk.Label(row2, text=str(self._mainsave.deathcounter))
        deathcounterEntry.pack(side=tk.LEFT)
        row3 = tk.Frame(column1)
        row3.pack(fill=tk.BOTH, side=tk.TOP)
        chapter = tk.Button(row3, text="Chapter: ", command=lambda: self.__reverse(self.__chapter), relief=tk.GROOVE,
                            borderwidth=0, pady=0, fg="green")
        chapter.pack(side=tk.LEFT)
        row3 = tk.Frame(column2)
        row3.pack(fill=tk.BOTH, side=tk.TOP)
        chapterEntry = tk.Entry(row3)
        chapterEntry.insert(0, str(self._mainsave.chapterId))
        chapterEntry.pack(side=tk.LEFT)
        column3 = tk.Frame(frame)
        column3.pack(fill=tk.BOTH, side=tk.LEFT)
        tk.Label(column3, text="\t").pack(side=tk.LEFT)

        column1 = tk.Frame(frame)
        column1.pack(fill=tk.BOTH, side=tk.LEFT)
        column2 = tk.Frame(frame)
        column2.pack(fill=tk.BOTH, side=tk.LEFT)
        row1 = tk.Frame(column1)
        row1.pack(fill=tk.BOTH, side=tk.TOP)
        version = tk.Button(row1, text="Version: ", command=lambda: self.__reverse(self.__version), relief=tk.GROOVE,
                            borderwidth=0, pady=0, fg="red")
        version.pack(side=tk.LEFT)
        row1 = tk.Frame(column2)
        row1.pack(fill=tk.BOTH, side=tk.TOP)
        versionEntry = tk.Label(row1, text=self._mainsave.version)
        versionEntry.pack(side=tk.LEFT)
        row2 = tk.Frame(column1)
        row2.pack(fill=tk.BOTH, side=tk.TOP)
        shrines = tk.Button(row2, text="Shrines: ", command=lambda: self.__reverse(self.__shrines), relief=tk.GROOVE,
                            borderwidth=0, pady=0, fg="red")
        shrines.pack(side=tk.LEFT)
        row2 = tk.Frame(column2)
        row2.pack(fill=tk.BOTH, side=tk.TOP)
        shrineEntry = tk.Label(row2, text="WIP")
        shrineEntry.pack(side=tk.LEFT)
        row3 = tk.Frame(column1)
        row3.pack(fill=tk.BOTH, side=tk.TOP)
        scene = tk.Button(row3, text="Scene: ", command=lambda: self.__reverse(self.__scene), relief=tk.GROOVE,
                          borderwidth=0, pady=0, fg="green")
        scene.pack(side=tk.LEFT)
        row3 = tk.Frame(column2)
        row3.pack(fill=tk.BOTH, side=tk.TOP)
        sceneEntry = tk.Entry(row3)
        sceneEntry.insert(0, str(self._mainsave.sceneId))
        sceneEntry.pack(side=tk.LEFT)
        column3 = tk.Frame(frame)
        column3.pack(fill=tk.BOTH, side=tk.LEFT)
        tk.Label(column3, text="\t").pack(side=tk.LEFT)

        column1 = tk.Frame(frame)
        column1.pack(fill=tk.BOTH, side=tk.LEFT)
        column2 = tk.Frame(frame)
        column2.pack(fill=tk.BOTH, side=tk.LEFT)
        row1 = tk.Frame(column1)
        row1.pack(fill=tk.BOTH, side=tk.TOP)
        elapsed = tk.Button(row1, text="Elapsed: ", command=lambda: self.__reverse(self.__elapsed), relief=tk.GROOVE,
                            borderwidth=0, pady=0, fg="red")
        elapsed.pack(side=tk.LEFT)
        row1 = tk.Frame(column2)
        row1.pack(fill=tk.BOTH, side=tk.TOP)
        elapsedEntry = tk.Label(row1, text=str(datetime.datetime.fromtimestamp(self._mainsave.elapsed)
                                               .strftime("%Hh %Mm %Ss")
                                               if self._mainsave.elapsed is not None else None))
        elapsedEntry.pack(side=tk.LEFT)
        row2 = tk.Frame(column1)
        row2.pack(fill=tk.BOTH, side=tk.TOP)
        slot = tk.Button(row2, text="Slot: ", command=lambda: self.__reverse(self.__slot), relief=tk.GROOVE,
                            borderwidth=0, pady=0, fg="red")
        slot.pack(side=tk.LEFT)
        row2 = tk.Frame(column2)
        row2.pack(fill=tk.BOTH, side=tk.TOP)
        slotEntry = tk.Entry(row2)
        slotEntry.insert(0, str(self._mainsave.slot + 1 if self._mainsave.slot is not None else None))
        slotEntry.pack(side=tk.LEFT)
        row3 = tk.Frame(column1)
        row3.pack(fill=tk.BOTH, side=tk.TOP)
        position = tk.Button(row3, text="Position: ", command=lambda: self.__reverse(self.__position), relief=tk.GROOVE,
                             borderwidth=0, pady=0, fg="red")
        position.pack(side=tk.LEFT)
        row3 = tk.Frame(column2)
        row3.pack(fill=tk.BOTH, side=tk.TOP)
        positionEntry = [tk.Entry(row3), tk.Entry(row3), tk.Entry(row3)]
        for i in range(3):
            positionEntry[i].insert(0, str(self._mainsave.position[i]))
            positionEntry[i].pack(side=tk.LEFT)

        return [[
                    timestampEntry, versionEntry, elapsedEntry, deathcounterEntry, slotEntry, chapterEntry, sceneEntry,
                    positionEntry
                ], [timestamp, version, elapsed, deaths, slot, chapter, scene, position, shrines]]

    def __setupCompareGui(self):
        self.mode = "COMPARE"
        self.__setupMainGui()
        self._window.title("Planet of Lana Save Editor - Comparing")
        self._compareButton["relief"] = tk.SUNKEN
        main = tk.Frame(self._main)
        main.config(bd=1, relief=tk.SUNKEN)
        main.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)

        left = tk.Frame(main)
        left.config(bd=1, relief=tk.FLAT)
        left.columnconfigure(1, weight=1)
        left.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        mid = tk.Frame(main)
        mid.config(bd=1, relief=tk.FLAT)
        mid.pack(fill=tk.BOTH, side=tk.LEFT)
        tk.Label(mid, text="\t").pack()

        right = tk.Frame(main)
        right.config(bd=1, relief=tk.FLAT)
        right.columnconfigure(1, weight=1)
        right.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)

        lefttools = tk.Frame(left)
        lefttools.config(bd=1, relief=tk.SUNKEN, padx=2, pady=3)
        lefttools.rowconfigure(0, weight=1)
        lefttools.pack(fill=tk.BOTH, side=tk.TOP)
        lefttools_cont = tk.Frame(lefttools)
        lefttools_cont.pack(fill=tk.X, side=tk.LEFT)

        righttools = tk.Frame(right)
        righttools.config(bd=1, relief=tk.SUNKEN, padx=2, pady=3)
        righttools.rowconfigure(0, weight=1)
        righttools.pack(fill=tk.BOTH, side=tk.TOP)
        righttools_cont = tk.Frame(righttools)
        righttools_cont.pack(fill=tk.X, side=tk.RIGHT)

        self.__setupToolbarGui(lefttools, self._mainsave, "LEFT")

        self.__setupToolbarGui(righttools, self._compsave, "RIGHT")

        self.mainvals = self.__setupValsLabel(left, self._mainsave)
        self.compvals = self.__setupValsLabel(right, self._compsave)

        self.__checkCompare()

    def __setupConstantCompareGui(self):
        self.mode = "MONITOR"
        self.__setupMainGui()
        self._window.title("Planet of Lana Save Editor - Monitoring")
        self._monitorButton["relief"] = tk.SUNKEN
        right = tk.Frame(self._main)
        right.config(bd=1, relief=tk.SUNKEN)
        right.columnconfigure(1, weight=1)
        right.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)

        tools = tk.Frame(right)
        tools.config(bd=1, relief=tk.SUNKEN, padx=2, pady=3)
        tools.rowconfigure(0, weight=1)
        tools.pack(fill=tk.BOTH, side=tk.TOP)
        tools_cont = tk.Frame(tools)
        tools_cont.pack(fill=tk.X, side=tk.LEFT)

        self.__setupToolbarGui(tools, self._mainsave, "LEFT")

        logButton = tk.Button(tools, text="Log", command=lambda: self.__reverse(self._logging),
                              fg="green" if self._logging[0] else "red")
        logButton.pack(fill=tk.X, expand=True, side=tk.LEFT)
        self._logging[1] = logButton

        self.mainvals, compButtons = self.__setupValsInverse(right)
        vals = [
            self.__timestamp, self.__version, self.__elapsed, self.__deaths, self.__slot,
            self.__chapter, self.__scene, self.__position, self.__shrines
        ]
        for i in range(len(vals)):
            vals[i][1] = compButtons[i]


if __name__ == '__main__':
    display = Display()
    display.run()

# TODO - add types and comments and like useful stuff
# TODO - reformat into different classes

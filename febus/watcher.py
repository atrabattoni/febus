import datetime
import pathlib

from . import parser


class Watcher():

    def __init__(self):
        self.currentfile = None
        self.directory = pathlib.Path(".")
        self.files = list(self.directory.glob("*.h5"))
        self.info = {}
        self.lines = []
        self.newfile = None

    def parse(self, line):
        if parser.parse_new_loop(line):
            if None in self.info.values():
                error = True
            else:
                error = False
            self.dump_info(error=error)
            self.dump_lines(error=error)
            self.log_info()

        gpstime, pulseid = parser.parse_gpstime_pulseid(line)
        if (gpstime is not None) and (pulseid is not None):
            self.info["gpstime"] = gpstime
            self.info["pulseid"] = pulseid

        walltime = parser.parse_walltime(line)
        if walltime is not None:
            self.info["walltime"] = walltime

        trigid = parser.parse_trigid(line)
        if trigid is not None:
            self.info["trigid"] = trigid

        utcdatetime, blockid = parser.parse_utcdatetime_blockid(line)
        if (utcdatetime is not None) and (blockid is not None):
            self.info["utcdatetime"] = utcdatetime
            self.info["blockid"] = blockid

        writetime = parser.parse_writetime(line)
        if writetime is not None:
            self.info["writetime"] = writetime
            self.watch_files()
            self.info["currentfile"] = self.currentfile

        coprocessingtime = parser.parse_coprocessingtime(line)
        if coprocessingtime is not None:
            self.info["coprocessingtime"] = coprocessingtime

        self.lines.append(line)

    def dump_info(self, error=False):
        fname = "info"
        if error:
            now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            fname += f"_error_{now}"
        with open(fname, "w") as file:
            for key, item in self.info.items():
                file.write(f"{key}: {item}\n")
                self.info[key] = None

    def dump_lines(self, error=False):
        fname = "stream"
        if error:
            now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            fname += f"_error_{now}"
        with open(fname, "w") as file:
            file.writelines(self.lines)
        self.lines = []

    def watch_files(self):
        files = list(self.directory.glob("*.h5"))
        newfiles = [file for file in files if file not in self.files]
        self.files.extend(newfiles)
        if len(newfiles) == 1:
            self.newfile, = newfiles
            self.currentfile = self.newfile
        else:
            self.newfile = None

    def log_info(self):
        fname = str(self.currentfile).replace("h5", "log")
        sep = ","
        with open(fname, "a") as file:
            lines = []
            if self.newfile is not None:
                lines.append(sep.join(self.info.keys()) + "\n")
            values = [str(value) for value in self.info.values()]
            lines.append(sep.join(values) + "\n")
            file.writelines(lines)

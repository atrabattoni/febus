import cmd
import importlib.util
import pathlib

from .cli import FebusDevice
from .watcher import Watcher


class FebusShell(cmd.Cmd):
    intro = "Welcome to the febus shell. Type help or ? to list commands.\n"
    prompt = "(febus) "

    def __init__(self, *args, **kwargs):
        self.device = FebusDevice()
        super().__init__(*args, **kwargs)

    def do_server(self, arg):
        ""
        if "start" in arg:
            if "gps" in arg:
                self.device.start_server(gps=True)
            else:
                self.device.start_server(gps=False)
        if "stop" in arg:
            self.device.terminate_server()

    def do_acquisition(self, arg):
        ""
        if "start" in arg:
            kwargs = {}
            kwargs["fiber_length"] = int(input("Fiber length [m]: "))
            kwargs["frequency_resolution"] = float(
                input("Frequency resolution [Hz]: "))
            kwargs["spatial_resolution"] = int(input("Pulse width [m]: "))
            kwargs["ampli_power"] = int(input("Ampli power [dBm]: "))
            kwargs["cutoff_frequency"] = float(input("Ampli power [dBm]: "))
            kwargs["gauge_length"] = 1
            kwargs["sampling_resolution"] = int(
                input("Sampling resolution [cm]: "))
            kwargs["pipeline_fname"] = int(input("Pipeline path: "))
            self.device.start_acquisition(**kwargs)
        if "stop" in arg:
            self.device.stop_acquisition()

    def do_writings(self, arg):
        ""
        if "start" in arg:
            self.device.enable_writings()
        if "stop" in arg:
            self.device.disable_writings()

    def do_watcher(self, arg):
        ""
        if "start" in arg:
            path = input("Data_processor_path :")
            if path:
                path = pathlib.Path(path)
                spec = importlib.util.spec_from_file_location(path.name, path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                data_processor = module.data_processor
            else:
                data_processor = None
            self.watcher = Watcher(self.device, data_processor=data_processor)
            self.watcher.start_monitoring()
        if "stop" in arg:
            self.watcher.terminate_monitoring()


if __name__ == '__main__':
    FebusShell().cmdloop()
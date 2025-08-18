import os
import shutil
from openfast_toolbox.io import FASTInputFile
from rosco.toolbox.utilities import read_DISCON, write_DISCON


def ROSCOControllerInterface(fstffile, updateperiod=1.0, port=5555, backup_discon=True):
    """
    This function modifies FAST.Farm input files to enable wind farm control
    using the ROSCO controller using the ROSCOs ZeroMQ interface.
    """
    fstfpath = os.path.dirname(fstffile)

    # Read the fstf file
    fstfdata = FASTInputFile(fstffile)
    numturbines = fstfdata["NumTurbines"]

    # Read files for each turbine
    for turbine in range(numturbines):
        # Read the fst file
        fstfile = fstfdata["WindTurbines"][turbine][3].replace(
            "'", "").replace('"', "")
        fstpath = os.path.dirname(fstfile)
        fstdata = FASTInputFile(os.path.join(fstfpath, fstfile))

        # Read servodyn file
        servofile = fstdata["ServoFile"].replace("'", "").replace('"', "")
        servopath = os.path.dirname(servofile)
        servodata = FASTInputFile(os.path.join(fstfpath, fstpath, servofile))

        # Read DISCON Input file
        DISCONfile = servodata["DLL_InFile"].replace("'", "").replace('"', "")
        # DISCONpath = os.path.dirname(DISCONfile)
        DISCONData = read_DISCON(os.path.join(
            fstfpath, fstpath, servopath, DISCONfile))

        # Modify DISCON file to add ZMQ interface information
        DISCONData["ZMQ_Mode"] = 1
        DISCONData["ZMQ_ID"] = turbine
        DISCONData["ZMQ_UpdatePeriod"] = updateperiod
        DISCONData["ZMQ_CommAddress"] = f"tcp://localhost:{port}"

        class DummyTurbineClass:
            def __init__(self, TurbineName):
                self.TurbineName = TurbineName

        turbine = DummyTurbineClass("FAST.Farm")
        if backup_discon:
            shutil.copy(
                os.path.join(fstfpath, fstpath, servopath, DISCONfile),
                os.path.join(fstfpath, fstpath, servopath,
                             DISCONfile + ".bak"),
            )

        write_DISCON(
            turbine,
            controller={},
            param_file=os.path.join(fstfpath, fstpath, servopath, DISCONfile),
            rosco_vt=DISCONData,
        )


if __name__ == "__main__":
    fstffile = "/home/abhineet/Work/FFInterface/tools/AG_ROSCO/Examples/examples_out/17c_FASTFarm.fstf"
    ROSCOControllerInterface(fstffile)

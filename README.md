# EndoFI, a fine-grained and controllable fault injection method for endogenous database fault.

EndoFI has the following advantages:
* EndoFI can accurately control the blast radius of faults because it is able to only inject faults into a specific SQL statement from specific a user connection without affecting other users or even other SQL statements of the same user.
* EndoFI can simulate internal faults of the system more realistically because it can cause a specific process faulty.
* EndoFI is extensible because it injects custom logic into a process by calling a shared library file in the process, which makes it easy to extend to support new faults.
* EndoFI's fault injection methodology is white-box because it enables runtime fault injection at the source code level.

## Usage
1. Set the configuration
2. Modify the `FILE_PATH` in `main.py`
3. run `run.sh`

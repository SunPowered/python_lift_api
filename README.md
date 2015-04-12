# SunPowered's Codelift Challenge
A python API to the Lift simulator for the Box Lift competition at Pycon 2015. 

A simple working model of the elevators has been implemented.  There 
was unfortunately not enough time to perfect the algorithm, a little
more work would have been useful.

A config object is used, so if you are forking this, be sure to 
include your own object such as

    class Config:
        username = "Meeps"
        email = "meeps@email.com"
        registration_id = 12345

The simulation is run via the `main.py` file.  There are several
arguments available as shown in the help msg:

    usage: main.py [-h] [-d] [-v] [-s] plan

    Codelift Challenge - SunPowered

    positional arguments:
      plan           The plan to use for the simulation

    optional arguments:
      -h, --help     show this help message and exit
      -d, --debug    Enables debug mode, stops after each step
      -v, --verbose  Enables API verbosity, logging API requests and responses
      -s, --sandbox  Enable sandbox mode. Auto enabled with debug option

Training in sandbox mode, for example, is run with:

    python main.py -s -v Training1


#Provenance Command and Control

Provenance is a Command and Control server used to distribute commands
across different Redteam beacons in order to create a centralized monitoring platform.

#### Why?
Provenance is personal project used in conjunction with the following beacons in order
to teach myself more about redteaming, malware, evasion and persistence tactics on Windows
and Linux operating systems. Also, I love development :)

| Beacon        | Protocol      | Windows           | Linux     |
| ------------- |:-------------:| ----------------- | --------- |
| resolution    | DNS           | in development    | up next   |
|  ?            | ICMP          | future project    | future project |
|  ?            | HTTP          | future project    | future project |

#### Installation
Provenance supports python3 on both Windows and Linux. More specifically,
it is being developed primarily on 3.7.7

##### Linux
```bash
virutalenv -p python3 c2-env
source c2-env/bin/activate
# Verify it's using the virtiualenv using "which pip3"
pip3 install -r requirements.txt
python3 Provenance.py -h
```

##### Windows
```
python3 -m get-pip.py
pip3 install virtualenv
virtualenv -p python3 c2-env
pip3 install -r requirements.txt
./c2-env/Scripts/python.exe ./Provenance.py -h
```

## Design and Architecture
During development I tried to adhere as best as I could remember to good,
software-engineering design patterns in order to make the code more readable and 
extendable. As such, below will contain as much specification as possible. 

#### Directory Structure
| Directory     | Description                                                           |
| ------------- | --------------------------------------------------------------------- |
| `backend`     | Server code and `handlers` for different beacons                      |
| `controllers` | Clases that provide an abstraction layer between the model and the UI |
| `frontend`    | Code need to run WebGUI or command line UI                            |
| `backups`     | Default directory where server backups are stored upon creation       |
| `logs`        | Default directory where server logs are stored                        |

#### Server Architecture
![Server Architecture](docs/server-architecture.png)

The server architecture attempts to follow Model-View-Controller Design pattern and as such
implements the `ModelController` class which exposes limited functionality to any UI that interacts with it. 
The `ModelController` is instantiated with a concrete class that inherits from the `ModelInterface`
class, which defines standard methods for retrieving information from the server. At this moment,
`ProvenanceServer` or a `ThreadedProvenanceServer` are the define the functionality of serving C2 commands.

Regardless of the type of server, internally they store information about the beaconing machines via
multiple `ProvenanceClient` instances. Each instance will independently track the commands that need to be sent to
it, last beaconing time, etc. However, this class doesn't define the implementation for actually responding
to requests from beacons.

In order to process each request coming into the server, each `ProvenanceClient` instance must have a valid 
`protocolhandler`, which will properly define the server's response when handling a request from a beacon via
the `handle_request()` method that all concrete subclasses must implement. 

#### UI Architecture
The User Interface for Provenance is broken into two implementations: CLI and GUI, which can be specified at launch
of the program. However, as of right now `v0.5` only the CLI is being worked on due to the parallel process of
building out beacon and server functionality.

##### Command Line Interface
The command line interface is built on top of a python library [asciimatics](https://github.com/peterbrittain/asciimatics),
a cross-platform [ncurses](https://en.wikipedia.org/wiki/Ncurses) API that provides predefined "building blocks" for
creating CLI programs. 

![MainMenu](docs/mainmenu.PNG)

The main menu allows users to view critical information about the machines being managed by Progenance such as
the type of beacon being used, the OS, Hostname, IP address, the last time it beaconed out, and the next command
that is being sent. In order to add a command, users can click the "Add CMD" button that will allow them to specify
various parameters to decide what machines to add commands to.

![AddCommandMenu](docs/addcommand.PNG)

To view more detailed information about the machine, a user can click on the machine on the main menu, bringing
up the advanced details screen.

![ViewMachineMenu](docs/viewmachine.PNG)

# LightSim2Grid
Provide a fast backend for grid2op using c++ KLU and Eigen librairies. Its primary goal is to serve as a fast
backend for the grid2op platform, used primarily as a testbed platform for sequential decision making in
the world of power system.

See the [Disclaimer](DISCLAIMER.md) to have a more detailed view on what is and what is not this package. For example
this package should not be used for detailed power system computations or simulations.

## Installation (from source)
**At time of writing, this procedure only work on Gnu-Linux / Mac OS, unless you manage to compile SparseSuite from
source**

You need to:
- clone this repository
- get the code of Eigen and SparseSuite (mandatory for compilation)
- compile a piece of SparseSuite
- install the package

First, you can download it with git with:
```commandline
git clone https://github.com/BDonnot/lightsim2grid.git
cd lightsim2grid
# it is recommended to do a python virtual environment
python -m virtualenv venv  # optional
source venv/bin/activate  # optional
```

**NB** On windows you can rely on the "WSL" 
[Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10) to emulate the behavior
of a linux-like machine running from windows. This possibility will make it possible for you to have lightsim2grid
on this system, provided that you installed WSL (now WSL verion 2) and all the necessary packages there.

### 1. Compilation of SuiteSparse
We only detail the procedure on a system using "make" (so most likely GNU-Linux and MacOS). If you manage to
do this step on Windows, you can continue (and let us know!). If you don't feel confortable with this, we
provided a docker version. See the next section for more information.


```commandline
# retrieve the code of SparseSuite and Eigen
git submodule init
git submodule update

# compile static libraries of SparseSuite
make
```

### 2. Installation of the python package
Provided that you manage to create the file above (either you are on GNU-Linus / MacOS and could run the commands above)
or you are an expert in software development in Windows (in that case let us know !), you simply need to install
the lightsim2grid package this way:

```commandline
# install the dependency
pip install -U pybind11
# compile and install the python package
pip install -U .
```

And you are done :-)

## Installation (using docker)
In this section we cover the use of docker with grid2op.

### 1. Install docker
First, you need to install docker. You can consult the 
[docker on windows](https://hub.docker.com/editions/community/docker-ce-desktop-windows) if you use a windows like
operating system, if you are using MacOs you can consult 
[docker on Mac](https://hub.docker.com/editions/community/docker-ce-desktop-mac/). The installation of docker on linux
depends on your linux distribution, we will not list them all here here.

### 2. Get the lightsim2grid image

Once done, you can simply "install" the lightsim2grid image with:
```commandline
docker pull bdonnot/lightsim2grid:latest
```

This step should be done only once (unless you delete the image) it will download approximately 4 or 5GB from the
internet. The lightsim2grid image contains lightsim and grid2op python packages (as well as their
dependencies), equivalent of what would be installed if you typed:
```commandline
pip install -U grid2op[optional] pybind11
# and do steps detailed in section "Installation (from source)"
# that we will not repeat
```

### 3. Run a code on this container
You can skip this section if you know how to use docker. We will present here "the simplest way" to use. This is NOT
a tutorial on docker, and you can find better use of this technology on 
[the docker website](https://www.docker.com/get-started).

For this tutorial, we suppose you have a script named `my_script.py` located in the directory (complete path) 
`DIR_PATH` (*e.g.* on windows you can have `DIR_PATH` looking like "c:\User\MyName\L2RPNCompeitionCode" or 
on Linux `DIR_PATH` will look like "/home/MyName/L2RPNCompeitionCode", this path is your choice, you can name it
the way you like)


#### 3.1) Start a docker container
You first need to start a docker container and tell docker that the container can access your local files with the 
following command:

```commandline
docker run -t -d -p 8888:8888 --name lightsim_container -v DIR_PATH:/L2RPNCompeitionCode -w /L2RPNCompeitionCode bdonnot/lightsim2grid
```
More information on this command 
[in the official docker documentation](https://docs.docker.com/engine/reference/commandline/run/)

After this call you can check everything went smoothly with by invoking:
```commandline
docker ps
```
And the results should look like:
```
CONTAINER ID        IMAGE                   COMMAND             CREATED             STATUS              PORTS               NAMES
89750964ca55        bdonnot/lightsim2grid   "python3"           5 seconds ago       Up 4 seconds        80/tcp              lightsim_container
```

**NB** I insist, `DIR_PATH` should be replaced by the path on which you are working, see again the introduction of this
section for more information, in the example above this can look like:
```commandline
docker run -t -d -p 8888:8888 --name lightsim_container -v /home/MyName/L2RPNCompeitionCode:/L2RPNCompeitionCode -w /L2RPNCompeitionCode bdonnot/lightsim2grid
```

#### 3.2) Execute your code on this container
Once everything is set-up you can execute anything you want on this container. Note that doing so, the execution
of the code will be totally independant of your system. Only the things located in `DIR_PATH` will be visible 
by your script, only the python package installed in the container will be usable, only the python interpreter
of the containter (python 3.6 at time of writing) will be usable etc.

```commandline
docker exec lightsim_container python my_script.py
```

Of course, the "my_script.py" should save its output somewhere on the hard drive.

If you rather want to execute a python REPL (read-eval-print loop), corresponding to the "interactive python 
interpreter", you can run this command:
```commandline
docker exec -it lightsim_container python
```

We also added the possibility to run jupyter notebook from this container. To do so, you can run the command:
```commandline
docker exec -it lightsim_container jupyter notebook --port=8888 --no-browser --ip='*' --allow-root
```

More information is provided in the official documentation of 
[docker exec](https://docs.docker.com/engine/reference/commandline/exec/).

#### 3.3) Disclaimer
Usually, docker run as root on your machine, be careful, you can do irreversible things with it. "A great power 
comes with a great responsibility".

Also, we recall that we presented a really short introduction to docker and its possibility. We have not implied
that this was enough, nor explain (on purpose, to make this short) any of the commands. 
We strongly encourage you to have a look for yourself. 

We want to recall the paragraph `7. Limitation of Liability` under which lightsim2grid, and this "tutorial" 
is distributed:

*Under no circumstances and under no legal 
theory, whether tort (including negligence), 
contract, or otherwise, shall any Contributor, or 
anyone who distributes Covered Software as 
permitted above, be liable to You for any direct, 
indirect, special, incidental, or consequential 
damages of any character including, without 
limitation, damages for lost profits, loss of 
goodwill, work stoppage, __**computer failure or**__
__**malfunction**__, or any and all other commercial 
damages or losses, even if such party shall have 
been informed of the possibility of such damages.*

### 4) Clean-up
Once you are done with your experiments, you can stop the docker container:
```commandline
docker container stop lightsim_container
```
This will free all the CPU / GPU resources that this container will use. If you want to start it again, for another 
experiment for example, just use the command:
```commandline
docker container start lightsim_container
```
This will allow you to run another batch of `dcoker exec` (see `3.2) Execute your code on this container`) 
without having to re run the container.


If you want to go a step further, you can also delete the container with the command:
```commandline
docker container rm lightsim_container
```
This will remove the container, and all your code executed there, the history of commands etc. If you want to use
lightsim2grid with docker again you will have to go through section `3. Run a code on this container` all over
again.

And if you also want to remove the image, you can do:
```commandline
docker rmi bdonnot/lightsim2grid 
```
**NB** this last command will completely erase the lightsim2grid image from your machine. This means that 
if you want to use it again, you will have to download it again (see section `2. Get the lightsim2grid image`)

Finally, you can see the official documentation in case you need to uninstall docker completely from your system.

## LightSim2Grid usage
Once installed (don't forget, if you used the optional virtual env
above you need to load it with `source venv/bin/activate`) you can
use it as any python package.

### 1. As a grid2op backend (preferred method)
This functionality requires you to have grid2op installed, with at least version 0.7.0. You can install it with
```commandline
pip install grid2op>=0.7.0
```

Then you can use a LightSimBackend instead of the default PandapowerBackend this way:

```python3
import grid2op
from lightsim2grid import LightSimBackend
backend = LightSimBackend()
env = grid2op.make(backend=backend)
# do regular computation as you would with grid2op
```
And you are good to go.

### 2. replacement of pandapower "newtonpf" method (advanced method)
Suppose you somehow get:
- `Ybus` the admittance matrix of your powersystem given by pandapower
- `V0` the (complex) voltage vector at each bus given by pandapower
- `Sbus` the (complex) power absorb at each bus as given by pandapower
- `ppci` a ppc internal pandapower test case
- `pv` list of PV buses
- `pq` list of PQ buses
- `options` list of pandapower "options"

You can define replace the `newtonpf` function of `pandapower.pandapower.newtonpf` function with the following
piece of code:
```python
from lighsim2grid.newtonpf import newtonpf
V, converged, iterations, J = newtonpf(Ybus, V, Sbus, pv, pq, ppci, options)
```

This function uses the KLU algorithm and a c++ implementation of a Newton solver for speed.

## Miscelanous
And some official tests, to make sure the solver returns the same results as pandapower
are performed in "lightsim2grid/tests"
```bash
cd lightsim2grid/tests
python -m unittest discover
```

This tests ensure that the results given by this simulator are consistent with the one given by pandapower when
using the Newton-Raphson algorithm, with a single slack bus, without enforcing q limits on the generators etc.

**NB** to run these tests you need to install grid2op from source otherwise all the test of the LightSim2gridBackend 
will fail. In order to do so you can do:
```
git clone https://github.com/rte-france/Grid2Op.git
cd Grid2Op
pip3 install -U -e .
cd ..
```


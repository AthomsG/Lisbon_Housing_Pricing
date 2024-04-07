# How to use this repository

create a python virtual environment with:

```bash
python3.11 -m venv [environment name]
```

activate the virtual environment with:

```bash
source [environment name]/bin/activate
```

you can add the virtual environemnt as a jupyter kernel as follows:

```bash
pip install --user ipykernel

ipython kernel install --user --name=[environment name]
```

which should print the following:

```bash
Installed kernelspec [environment name] in /home/user/(...)
```

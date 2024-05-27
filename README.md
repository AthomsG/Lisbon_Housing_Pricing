![Alt text](graphics/logo.png)

# 🏡 Lisbon House Pricing Model 🏡

Welcome to the Lisbon Housing Pricing Model project. Below you'll find our current roadmap, outlining the key tasks that will drive this project towards its first major milestone. If you're looking to contribute, this list is your go-to resource for understanding what's needed and how you can help.

## Todo 🚀

- [X] **Develop a Proof of Concept (PoC):** Lay the foundation of our project with a robust PoC.
- [X] **Pull Market Data from INE:** Efficiently gather and organize relevant market data from [INE Database](https://www.ine.pt/xportal/xmain?xpid=INE&xpgid=ine_base_dados).
- [X] **Optimize the Data Scraping Process:** Streamline our approach to gathering data efficiently.
- [ ] **Improve Regression Model:** Develop a better model (less error and more robust) than the current Random Forest solution.
- [ ] **Develop an API for Our Model:** Follow the tutorial [here](https://dorian599.medium.com/ml-deploy-machine-learning-models-using-fastapi-6ab6aef7e777) to create a scalable API.
- [ ] **Create a Prototype App:** Utilize Gradio or a similar solution to bring our model to life with a user-friendly interface.


## How to use this repository

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

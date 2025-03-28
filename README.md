# 🌎 Brazilian Seismographic Network: Data quality 🌎

This repository contains reproducible material for the study *"15 years of the Brazilian Seismographic Network: Data quality and Current Status"* by **Diogo Luiz de Oliveira Coelho,Gilberto da Silva Leite Neto,Sergio Luiz Fontes**, submitted to *...*.

The provided scripts and notebooks demonstrate the generation and inversion of surface wave dispersion data, enabling the retrieval of the S-wave velocity profile as a function of depth using Evolutionary Algorithms.

## 📦 Required Libraries 📦

The following libraries are used in this project:

- [NumPy](https://numpy.org/): Fundamental package for numerical computing in Python.
- [Pandas](https://pandas.pydata.org/): Data analysis and manipulation tool.
- [PyArrow](https://arrow.apache.org/docs/index.html): Arrow manages data in arrays (pyarrow.Array).
- [SciPy](https://scipy.org/): A library for scientific and technical computing, offering algorithms for optimization, integration, interpolation, and more.
- [Matplotlib](https://matplotlib.org/): Visualization library for creating static, animated, and interactive plots.
- [tqdm](https://github.com/tqdm/tqdm): Library for displaying progress bars in loops and scripts.
- [kneed](https://kneed.readthedocs.io/en/latest/#): Library to identify the knee/elbow point of a line fit to the data.


## 📀 Installation 📀

To use the provided notebooks, install the required dependencies using pip:

```bash
pip install numpy pandas pyarrow matplotlib tqdm kneed
```

## 🏗️ Project structure 🏗️
This repository is organized as follows:

* 🗃️ **CODES**: These scripts collectively enable the generation, simulation, inversion, and visualization of surface wave dispersion data. 🚀
    * 🗒️ **...py**: Computes **surface wave dispersion curves** based on velocity profiles, essential for inversion analysis.
    * 🗒️ **...py**: Implements an **evolutionary algorithm** for inverting dispersion curves and estimating S-wave velocity profiles.  
    * 🗒️ **...py**: Defines **geological models** and manages layer properties used in the inversion process. 

* 🗃️ **NOTEBOOKS**: set of jupyter notebooks reproducing the experiments in the paper (see below for more details);

## 📑 Notebooks 📑
The following notebooks are provided:

- 📔 ``...ipynb``: notebook used to 
- 📔 ``...ipynb``: notebook performing the 
- 📔 ``...ipynb``: notebook to perform

## 🖱️ Usage 🖱️

1. Clone this repository:
   ```bash
   git clone <repository_url>
   cd RSBR_15_years
   ```
2. Open the Jupyter Notebook environment:
   ```bash
   jupyter-lab
   ```
3. Run the following notebooks to reproduce the results:
   - `...ipynb`: ...
   - `...ipynb`: ...
   - `...ipynb`: ...

## 📝 License 📝 

This project is licensed under the MIT License. See the `LICENSE` file for details.

## 📚 References 📚  

The implementation of the algorithms and methods in this repository is based on the following key references:  

- Gallagher, K., & Sambridge, M. (1994). **Genetic algorithms: a powerful tool for large-scale nonlinear optimization problems**. *Computers & Geosciences*, 20(7–8), 1229–1236.  
- Fortin, F. A., Rainville, F. M., Gardner, M., Parizeau, M., & Gagné, C. (2012). **DEAP: Evolutionary Algorithms Made Easy**. *Journal of Machine Learning Research*, 13, 2171-2175.  
- Haskell, N. A. (1953). **The dispersion of surface waves on multi-layered media**. *Bulletin of the Seismological Society of America*, 43, 17-34.  
- Xia, J., Miller, R. D., & Park, C. B. (1999). **Estimation of near-surface shear-wave velocity by inversion of Rayleigh waves**. *Geophysics*, 64(3), 691-700.  
- Yamanaka, H., & Ishida, H. (1996). **Application of genetic algorithms to an inversion of surface-wave dispersion data**. *Bulletin of the Seismological Society of America*, 86, 436–444.


## 🔖 Disclaimer 🔖  

All experiments were conducted on two different setups running **Debian GNU/Linux 12 (Bookworm)**:  

- 💻 **AMD Ryzen 7 5700U** with **10 GB RAM**  
- 💻 **Intel® Core™ Ultra 9** with **64 GB RAM**  

📣 **Multiprocessing is implemented.**  

---
For further details, refer to the paper associated with this repository.
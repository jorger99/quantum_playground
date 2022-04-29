import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
from scipy import constants, special

#hbar = sp.constants.hbar
hbar = 1

""" 

This portion exists to isolate the quantsim object creation from numpy calculations. this script will accept any form of quantsim, and will run a simulation based on the predefined object properties of the quantsim.

This is where experimental parameters are important, the user will define for what values of x and t should the simulation run over, what the dx and dt values will be, and overall control everything that is related to the simulation of the system.


- simulation parameters
    - [sq well] how many modes to show, if any
    - [sq well] potential well, depth
    - [tunneling particle] potential barrier height, thickness
    - [free particle] use wavepacket or not
"""


''' begin simulation methods '''

def InfSqWell(quantsim):
    """
    This method will take a quantsim object set to Infinite Square Well and calculate the wavefunction with probability densities.
    
    Parameters
    ----------
        quantsim - QuantSim object
            should be generated by QuantSimObj.py, then fed into this script
    
    Returns
    -------
        wfn_solns - list of numpy arrays
            list of multiple numpy arrays. Each numpy array is a solution for the wavefunction amplitude of the schrodinger equation within a InfSqWell. The numpy arrays are ordered by their mode, n, with index 0 being the first mode (n=1) for the InfSqWell.
        prob_densities - list of numpy arrays
            the squares of each wavefunction amplitude, this gives a normalized probability density.
    
    """
    L = quantsim.sim_params['length']
    m = quantsim.sim_params['mass']
    dx = quantsim.sim_params['dx']
    num_of_wfns = quantsim.sim_params['num_modes']
    wfn_solns, prob_densities, energy_levels = [], [], []
    
    # save x_vals to object, choose num to include end point
    # want 0 to 10, 0.1 steps; note that num = 10.1/0.1 = 101 data points, [0, 10.1)
    x_vals = np.linspace(0, L, num=(L+dx) / dx)  
    
    # make arrays of constants for each unique wfn
    n_array = np.arange(1, num_of_wfns+1)  # 1 to n+1 to include end point :)

    for n in n_array:
        kn = np.pi * n / L
        wfn_ampl = np.sqrt(L/2) * np.sin(kn * x_vals)
        wfn_solns.append(wfn_ampl)
        prob_densities.append(np.power(wfn_ampl, 2))
        energy_levels.append((n*np.pi*hbar)**2/(2*m*L**2))

    # save useful arrays in sim_param dict
    quantsim.sim_params['x_vals'] = x_vals
    quantsim.sim_params['E_array'] = energy_levels
    
    return wfn_solns, prob_densities

def FinSqWell(quantsim):
    
    return

def ParabSqWell(quantsim):
    
    def hermite(x, n):
        xi = np.sqrt(m*w/hbar)*x
        herm_coeffs = np.zeros(n+1)
        herm_coeffs[n] = 1
        return np.polynomial.hermite.hermval(xi, herm_coeffs)
    
    L = quantsim.sim_params['length']
    m = quantsim.sim_params['mass']
    k = quantsim.sim_params['force_constant_k']
    dx = quantsim.sim_params['dx']
    num_of_wfns = quantsim.sim_params['num_modes']
    
    wfn_solns, prob_densities = [], []

    x_vals = np.arange(-L, L, dx) 
    
    # make arrays of constants for each unique wfn
    n_array = np.arange(0, num_of_wfns+1)  # 0 to n+1 to include end point :)

    # calculate constants
    w = np.sqrt(k/m)  # ang freq
    E_array = (n_array + 0.5) * hbar * w
    
    
    for n in n_array:
        # calculate energy for each n
        En = E_array[n]

        # split the wavefunction into several pieces
        alpha = 1/np.sqrt(2**n * np.math.factorial(n)) * (m*w/(np.pi*hbar))**0.25
        
        exp_decay = np.exp(-(x_vals**2/2) * (m*w/hbar))
        
        # calculate final wavefunction
        #wfn_ampl = alpha * (zeta/np.pi**0.25) * exp_decay * hermite(x_vals,n)
        wfn_ampl = alpha * exp_decay * hermite(x_vals, n)
        
        # save to soln list
        wfn_solns.append(wfn_ampl)
        prob_densities.append(np.power(wfn_ampl, 2))

    # save useful arrays in sim_param dict
    quantsim.sim_params['x_vals'] = x_vals
    quantsim.sim_params['E_array'] = E_array/w
    quantsim.sim_params['ang_freq'] = w
    
    return wfn_solns, prob_densities

def simulate(quantsim):
    
    """
    This method will perform numpy calculations to simulate the correct equations for each physical system. Equations and wavefunctions are hardcoded in their own method. Final solutions to the wavefunctions and probability densities are saved in each quantsim object.
    
    Parameters
    ----------
        quantsim - QuantSim object
            should be generated by QuantSimObj.py, then fed into this script
        
    Returns
    -------
    
    """
    choice = quantsim.sys
    
    if choice in ["1", "Infinite Square Well", "ISW"]:
        soln, prob_dens = InfSqWell(quantsim)
        quantsim.soln = soln
        quantsim.prob_dens = prob_dens
        pass

    elif choice in ["2", "Finite Square Well", "FSW"]:
        quantsim.soln = FinSqWell(quantsim)
        pass

    elif choice in ["3", "Quantum Harmonic Oscillator", "QHO"]:
        soln, prob_dens = ParabSqWell(quantsim)
        quantsim.soln = soln
        quantsim.prob_dens = prob_dens
    
    else:
        print("\nSystem not found. Please reinitialize object.\n")
    
    return


def plot_func(quantsim):
    choice = quantsim.sys
    fig, ax = plt.subplots()
    ax.axis('off')
    
    x_vals = quantsim.sim_params['x_vals']
    wfn_list = quantsim.soln
    energy_levels = quantsim.sim_params['E_array']
    
    if choice in ["1", "Infinite Square Well", "ISW"]:
        for n, wfn in enumerate(wfn_list):
            ax.plot(x_vals, wfn, label=n)
        
        plt.vlines([0, quantsim.sim_params['length']], min(quantsim.soln[1]), max(quantsim.soln[1]))
        plt.hlines(min(quantsim.soln[1]), 0, quantsim.sim_params['length'])
        pass
    
    elif choice in ["2", "Finite Square Well", "FSW"]:
        pass
    
    elif choice in ["3", "Quantum Harmonic Oscillator", "QHO"]:
        for n, wfn in enumerate(wfn_list):
            ax.plot(x_vals, wfn, label="{:.1f} $\hbar \omega$".format(energy_levels[n]))
        
        L = quantsim.sim_params['length']
        plt.vlines([-L, L], -max(quantsim.soln[0]), max(quantsim.soln[0]))
        plt.hlines(-max(quantsim.soln[0]), -L, L)
        ax.set_xlim([-12, 12])
        ax.set_ylim([-1, 1])
    
    else:
        print("\nSystem not found. Please reinitialize object.\n")
        
    ax.legend()
    return
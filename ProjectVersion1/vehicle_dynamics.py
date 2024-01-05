#
# Optimal Control of a vehicle
# Discrete-time nonlinear dynamics of a vehicle
# Bertamè Sebastiano
# Bologna, 04/01/2024
#

import numpy as np

# Constants for the dynamics
ns = 6  # number of states
ni = 2  # number of inputs
dt = 1e-3  # discretization stepsize - Forward Euler

# Vehicle parameters
mm = 1480  # Kg
Iz = 1950  # Kg*m^2
aa = 1.421  # m           
bb = 1.029  # m
mi = 1  # nodim
gg = 9.81  # m/s^2


########################################################################
###################### TASK 0: DISCRETIZATION #########################
########################################################################

#######################################
# Car Dynamics
#######################################

def dynamics(xx, uu):
    """
    Nonlinear dynamics of a vehicle

    Args:
        xx (numpy.ndarray): State at time t, R^6.
        uu (numpy.ndarray): Input at time t, R^2.

    Returns:
        numpy.ndarray: Next state xx_{t+1}.
        numpy.ndarray: Gradient of f wrt xx, at xx,uu.
        numpy.ndarray: Gradient of f wrt uu, at xx,uu.
    """

    # Add a dimension for improving the compatibility of the code
    #xx = xx[:, None]
    #uu = uu[:, None]     
    
    # Preallocate the next state vector
    xxp = np.zeros((ns, 1))
    
    # Compute slip angles for front and rear (Beta_f, Beta_r)
    Beta = [
        uu[0] - (xx[3]*np.sin(xx[4]) + aa*xx[5]) / (xx[3]*np.cos(xx[4])), 
        - (xx[3]*np.sin(xx[4]) - bb*xx[5]) / (xx[3]*np.cos(xx[4]))
    ]
    
    # Compute vertical forces at front and rear (F_zf, F_zr)
    Fz = [mm*gg*bb/(aa+bb), mm*gg*aa/(aa+bb)]
    
    # Compute lateral forces at front and rear (F_yf, F_yr)
    Fy = [mi*Fz[0]*Beta[0], mi*Fz[1]*Beta[1]]

    # Discrete-time nonlinear dynamics calculations for next state
    xxp[0] = xx[0] + dt * (xx[3] * np.cos(xx[4]) * np.cos(xx[2]) - xx[3] * np.sin(xx[4]) * np.sin(xx[2]))                                 
    xxp[1] = xx[1] + dt * (xx[3] * np.cos(xx[4]) * np.sin(xx[2]) + xx[3] * np.sin(xx[4]) * np.cos(xx[2]))                                 
    xxp[2] = xx[2] + dt * xx[5]                                                                                                           
    xxp[3] = xx[3] + dt * ((Fy[1] * np.sin(xx[4]) + uu[1] * np.cos(xx[4] - uu[0]) + Fy[0] * np.sin(xx[4] - uu[0]))/mm)                     
    xxp[4] = xx[4] + dt * ((Fy[1] * np.cos(xx[4]) + Fy[0] * np.cos(xx[4] - uu[0]) - uu[1] * np.sin(xx[4] - uu[0]))/(mm * xx[3]) - xx[5])   
    xxp[5] = xx[5] + dt * (((uu[1] * np.sin(uu[0]) + Fy[0] * np.cos(uu[0])) * aa - Fy[1] * bb)/Iz)                                          

    # Gradient computation (for future use in optimization)
    # Gradient wrt xx and uu (df/dx and df/du)
    fx = np.zeros((ns, ns))
    fu = np.zeros((ni, ns))
    
    # Pre-compute repeated terms for efficiency
    cos_xx4 = np.cos(xx[4])
    sin_xx4 = np.sin(xx[4])
    cos_xx4_minus_uu0 = np.cos(xx[4] - uu[0])
    sin_xx4_minus_uu0 = np.sin(xx[4] - uu[0])
    m_xx3_sq = mm * (xx[3]**2)

    # Derivative of dynamics w.r.t. state (fx)
    fx = np.array([
        [1, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0],
        [dt*(-xx[3] * cos_xx4 * np.sin(xx[2]) - xx[3] * sin_xx4 * np.cos(xx[2])), 
         dt*(xx[3] * cos_xx4 * np.cos(xx[2]) - xx[3] * sin_xx4 * np.sin(xx[2])), 1, 0, 0, 0],
        [dt*(np.cos(xx[4]) * np.cos(xx[2]) - np.sin(xx[4]) * np.sin(xx[2])), 
         dt*(np.cos(xx[4]) * np.sin(xx[2]) + np.sin(xx[4]) * np.cos(xx[2])), 0, 1, 
         dt*((Fy[1] * np.cos(xx[4]) + Fy[0] * np.cos(xx[4] - uu[0]) - uu[1] * np.sin(xx[4] - uu[0]))*(-1/m_xx3_sq)), 0],
        [dt*(-xx[3] * sin_xx4 * np.cos(xx[2]) - xx[3] * cos_xx4 * np.sin(xx[2])), 
         dt*(-xx[3] * sin_xx4 * np.sin(xx[2]) + xx[3] * cos_xx4 * np.cos(xx[2])), 0, 
         dt*((Fy[1] * np.cos(xx[4]) - uu[1] * np.sin(xx[4] - uu[0]) + Fy[0] * np.cos(xx[4] - uu[0]))/mm), 
         1 + dt*((-Fy[1] * np.sin(xx[4]) - Fy[0] * np.sin(xx[4] - uu[0]) - uu[1] * np.cos(xx[4] - uu[0]))/(mm * xx[3])), 0],
        [0, 0, dt, 0, -dt, 1]
    ])
    
    # Removing singleton dimensions for the next state
    xxp = xxp.squeeze()
    fx.squeeze()
    fu.squeeze() 
       
    return xxp, fx, fu

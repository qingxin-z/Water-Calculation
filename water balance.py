import numpy as np
from scipy import constants

humidity_ratio_air =  18.01528 / 28.8160
humidity_ratio_h2 = 18.01528 / 2.01588

air_density_stp = 1.292
water_vapour_density_stp = 0.80375 # g/L
hydrogen_density_stp = 0.0888
F = constants.physical_constants['Faraday constant'][0]

def vapour_pressure(temp):
    """This calculates the water vapour pressure according to Antoine Equation"""
    # Ref: https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185&Mask=4&Type=ANTOINE&Plot=on Stull, 1947
    A = 4.6543
    B = 1435.264
    C = -64.848
    T = constants.zero_Celsius + temp
    logP = A - (B / (T + C)) # Antoine Equation
    Pbar = 10**logP
    P = Pbar * 1e2
    return P

def water_to_gas_ratio_air(pressure, dewpoint_temp):
    abs_pressure = constants.atm / 1000 + pressure
    water_sat_p = vapour_pressure(dewpoint_temp)
    gas_p = abs_pressure - water_sat_p
    mass_ratio = humidity_ratio_air * water_sat_p / gas_p
    return mass_ratio

def water_to_gas_ratio_hydrogen(pressure, dewpoint_temp):
    abs_pressure = constants.atm / 1000 + pressure
    water_sat_p = vapour_pressure(dewpoint_temp)
    gas_p = abs_pressure - water_sat_p
    mass_ratio = humidity_ratio_h2 * water_sat_p / gas_p
    return mass_ratio

def mass_flow_calc(flow_rate_nlpm, density):
    # Alicat defines NTP is 0 degC and 1 atm
    mass_flow = flow_rate_nlpm * density
    return mass_flow

def water_generation_rate(current):
    water_mol_min =  60 * current / (2 * F)
    react_mass_flow = 18.01528 * water_mol_min
    return react_mass_flow

def water_drag(current, nd):
    proton_mol_min = 60 * current / F
    drag_mass_flow = 18.01528 * nd * proton_mol_min
    return drag_mass_flow

def water_back_diff(anode_mass_flow, cathode_mass_flow, D_w, thickness):
    water_gradient = cathode_mass_flow - anode_mass_flow
    diffusion_flux = -D_w * water_gradient / thickness
    return diffusion_flux

def reacted_gas_flow_rate(current, n):
    # n = 4 for o2, 2 for h2
    gas_mol_min = 60 * current / (n * F)
    gas_stp = gas_mol_min * constants.R * constants.zero_Celsius / (constants.atm / 1000)
    return gas_stp


# Let's consider this scenario:
h2_flow_rate = 0.5
air_flow_rate = 2 #NLPM
ca_dewpoint = 68 # degC
an_dewpoint = 68
cell_temp = 70
inlet_bp = 100 #kPa
outlet_bp = 60 #kPa
op_current = 15 #A
nd = 1


inlet_water_mass_flow_ca = water_to_gas_ratio_air(inlet_bp, ca_dewpoint) * mass_flow_calc(air_flow_rate, air_density_stp) #g/min
water_generated = water_generation_rate(op_current)
drag_flow = water_drag(op_current, nd)
back_diff_flux = 8e-6 * 18.01528 * 60 * 50# g/min

inlet_water_mass_flow_an = water_to_gas_ratio_hydrogen(inlet_bp, an_dewpoint) * mass_flow_calc(h2_flow_rate, hydrogen_density_stp)

outlet_air_flow_rate = air_flow_rate - reacted_gas_flow_rate(op_current, 4)
outlet_h2_flow_rate = h2_flow_rate - reacted_gas_flow_rate(op_current, 2) 

outlet_water_vapour_flow_allowed_an = water_to_gas_ratio_hydrogen(outlet_bp, cell_temp) * mass_flow_calc(outlet_h2_flow_rate, hydrogen_density_stp)

outlet_water_vapour_flow_allowed_ca = water_to_gas_ratio_air(outlet_bp, cell_temp) * mass_flow_calc(outlet_air_flow_rate, air_density_stp) #assuming air concentration not changed

outlet_water_mass_flow = inlet_water_mass_flow_ca + water_generated# + drag_flow - back_diff_flux

total_water_in = inlet_water_mass_flow_an + inlet_water_mass_flow_ca
total_water_out = total_water_in + water_generated
total_water_vapour_out_allowed = outlet_water_vapour_flow_allowed_an + outlet_water_vapour_flow_allowed_ca

print(inlet_water_mass_flow_an, outlet_water_vapour_flow_allowed_an)
print(outlet_water_vapour_flow_allowed_ca)

print(outlet_water_mass_flow)
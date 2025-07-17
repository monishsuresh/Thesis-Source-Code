from joblib import load
import pandas as pd

# Basic GPR controller
basic_gpr_scaler = load('models/basic_gpr_scaler.pkl')
basic_gpr_model = load('models/basic_gpr.joblib')
def basic_gpr(target_v, vo, vs):
    vo_c = target_v - vo
    data = {'vo': [vo], 'vs': [vs], 'vo_c':[vo_c]}
    df = pd.DataFrame(data=data) 
    scaled_df = basic_gpr_scaler.transform(df)
    duty_cycle_ = basic_gpr_model.predict(scaled_df)
    duty_cycle=max(min(duty_cycle_[0], 100), 0)
    return duty_cycle

# Maximum-initial controller
max_initial_gpr_scaler = load('models/basic_gpr_scaler.pkl')
max_initial_gpr_model = load('models/basic_gpr.joblib')
def max_initial_gpr(target_v, vo, vs):
    vo_c = target_v - vo
    data = {'vo': [vo], 'vs': [vs], 'vo_c':[vo_c]}
    df = pd.DataFrame(data=data) 
    scaled_df = max_initial_gpr_scaler.transform(df)
    duty_cycle_ = max_initial_gpr_model.predict(scaled_df)
    duty_cycle=max(min(duty_cycle_[0], 100), 0)
    return duty_cycle


# GPR+PI controller
integral_active = False
t_old = 0
vo_old = 0
integral = 0
Ki = 0
def gpr_pi(target_v, vo, vs, t):
    global integral_active, t_old, vo_old, integral, Ki
    
    # calculate rate of change of load voltage
    t_new = t
    vo_new = vo
    dt = t_new - t_old
    dvdt = (vo_new - vo_old) / dt
    t_old = t_new
    vo_old = vo_new
    
    # GPR prediction
    vo_c = target_v - vo
    data = {'vo': [vo], 'vs': [vs], 'vo_c':[vo_c]}
    df = pd.DataFrame(data=data) 
    scaled_df = max_initial_gpr_scaler.transform(df)
    temp = max_initial_gpr_model.predict(scaled_df)
    gpr_pred=max(min(temp[0], 100), 0)
    
    # PI control
    if abs(dvdt) <5:
        Ki = 250
    elif abs(dvdt) > 80: 
        Ki = 0
        integral = 0
    prop = 3 * vo_c
    integral = integral + (Ki * vo_c * dt)
    
    # Final duty cycle
    duty_cycle = gpr_pred + prop + integral
    
    return duty_cycle

import controllers_module, ad2_module
import time
import matplotlib.pyplot as plt

dwf, hdwf = ad2_module.ad2_setup()


# data
time_plot = []
vo_plot = []
vs_plot = []
vo_c_plot = []
dc_plot = []

target_voltage = 5.137
digital_control = True

total_time = 0
start_time = time.perf_counter()
while total_time < 1:
    total_time = time.perf_counter() - start_time
    vo, vs = ad2_module.read_buffer(dwf, hdwf)
    
    if digital_control:
        dc = controllers_module.gpr_pi(target_voltage, vo, vs, total_time)
        ad2_module.pwm(dwf, hdwf, dc)
        
    if total_time > 1 and total_time < 2 and not power_on:
        ad2_module.toggle_power(dwf, hdwf, True)
        power_on = True
    elif total_time > 2 and power_on:
        ad2_module.toggle_power(dwf, hdwf, False)
        power_on = False
    
    time_plot.append(total_time)
    vo_plot.append(vo)
    vs_plot.append(vs)
    dc_plot.append(dc)
    
    if total_time > 3:  # 10
            break
        
ad2_module.ad2_close(dwf, hdwf)

plt.plot(time_plot, vo_plot, label='Load Voltage')
plt.plot(time_plot, [target_voltage] * len(time_plot), '--', label='Targte Voltage')
plt.fill_between(time_plot, target_voltage * 0.99, target_voltage * 1.01, color='green', alpha=0.3, label='±1% Error Band')
plt.ylabel('Voltage (V)')
plt.xlabel('Time (s)')
plt.title('Load Voltage')
plt.legend()
plt.grid()
plt.show()
# This starts two timers
import pandas as pd
 
import time
start = time.time()
start_2 = time.time()

# This ingests just the period and demand data, for the 13 periods
df = pd.read_excel('filepath/chapter_2_instruction.xlsx', sheet_name='2.4_figure_2.15_new_exercise', header=33, index_col=None, nrows=13, usecols=[0,1])

# This sets the period 1 base level and growth rate for Holt's model 
holts_base = (df['Demand'][0]+df['Demand'][1])/2
holts_growth = holts_base - df['Demand'][0]

# This function creates a list which contains the results of Holt's model
def holtsModel(period, alpha, beta):
    global holts_persisted_list
    holts_persisted_list = [['Period','Holt\'s base','Holt\'s growth','Holt\'s forecast'],[1,holts_base,holts_growth,holts_base+holts_growth]]
    for i in range(1, period+1):
        if i == 1:
            holts_persisted_list[i][3]
        else:
            current_demand = df['Demand'][i-1]
            last_base = holts_persisted_list[i-1][1]
            last_forecast = holts_persisted_list[i-1][3]
            new_base = alpha*current_demand+((1-alpha)*last_forecast)
            new_growth = beta*(new_base-last_base)+(1-beta)*holts_persisted_list[i-1][2]
            holts_persisted_list.append([i,new_base,new_growth,new_base+new_growth])
    return holts_persisted_list

mse_max = len(df['Period'])

def holtsMSE(x):
    global holts_persisted_list
    sse_val = 0
    sse_count = 0
    holtsModel(mse_max, x[0], x[1])
    for i in range(1,mse_max):
        global holts_persisted_list
        holts_forecast = holts_persisted_list[i][3]
        current_demand = df['Demand'][i]
        sse_val = (holts_forecast-current_demand)**2 + sse_val
        sse_count += 1
    mse_val = sse_val/sse_count
    return mse_val

# # I used the actual optimized alpha and beta to test the functions were written correctly
# test_alpha = 0.397039357774243
# test_beta = 0.723873580393962

test_alpha = 0.1
test_beta = 0.2
initial_guess = [test_alpha, test_beta]
# print("holtsMSE: \n",holtsMSE(initial_guess))

# This is the actual optimization
from scipy.optimize import minimize
result = minimize(holtsMSE, initial_guess, bounds=((0,1),(0,1)))
print ("\n",result.x)

#This ends the first timer
end = time.time()
print("\n Seconds:\n",end - start)

import statsmodels.api as sm 
X = sm.add_constant(df['Period'])
results = sm.OLS(df['Demand'], X).fit()
df['sm.OLS regression forecast'] = pd.DataFrame(results.predict(X))
print(df)

holts_df = pd.DataFrame(holts_persisted_list[1:], columns=holts_persisted_list[0])
holts_df['Holt\'s forecast'] = holts_df['Holt\'s forecast'].shift(1)
print(holts_df)

full_df = pd.merge(df, holts_df, how='outer', on=['Period'])
print(full_df)

# #This ends the second timer
# end_2 = time.time()
# print("\n Seconds:\n",end_2 - start_2)
import streamlit as st
import pandas as pd
import numpy as np
import heapq
from help_func import calc_e_series, find_parallel_resistor_pairs, find_parallel_resisitor


def main():
    st.title("Resistor Value Calculator")
    # input for the target resistor
    target_resist = st.number_input("Target resistance (Ohm)", value=10.00, step=0.01, format='%.2f')
    # input for tolerance in percent
    tol_per = st.number_input("Tolerance (%):", value=1.0, step=0.1)
    tol = tol_per * 10**(-2) * target_resist
    # slection of E series
    e_series = st.multiselect("E-series:", [3, 6, 12, 24, 48], default=12)
    # decades for the E series
    decades = st.slider('Choose how many decades to include', 2, 4, 1)
    # input to show top X results
    top = st.number_input("Show top:", min_value=1, value=10, step=1)
    # calculate the resistor values of the defined E series
    R_list = calc_e_series(e_series, decades)
    tab1, tab2, tab3, tab4 = st.tabs(["Low Cost", "Optimal Power Distribution", "Temperature", "Given Value"])
    # low cost resistors
    with tab1:
        st.subheader("Low Cost")
        st.write(f"Only E12 standard resistors with a deviation of +/- 1% are considered")
        if st.button("Calculate", key=3):
            # List of 1% low cost resistors (EIA E12)
            eiae12_list = [10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82]
            low_R_list = []
            for item in eiae12_list:
                for i in range(1, decades+1):
                    R_decade = item*i
                    R_1_per = R_decade + 1/100*R_decade
                    low_R_list.append(R_1_per)
                    R_1_per = R_decade - 1/100*R_decade
                    low_R_list.append(R_1_per)
            # remove all duplicates
            low_R_list = [*set(low_R_list)]
            # remove 0
            low_R_list = [i for i in low_R_list if i != 0]
                
            low_R_pairs, _ = find_parallel_resistor_pairs(target_resist, tol, low_R_list, low_R_list)
            st.write(f"For your search there are {len(low_R_pairs)} possible pairs.")
            st.write("This is within a tolerance of: +/-", tol_per, "%")
            # Calculate the difference between each element and the value
            diff = [(abs(x[2] - target_resist), x) for x in low_R_pairs]
            # Find the top smallest differences
            closest = heapq.nsmallest(top, diff)
            # Return only the values
            data = [x for _, x in closest]
            column_names = ['R1', 'R2', 'Total Resistance']
            df = pd.DataFrame(data, columns=column_names)
            st.table(df)
        
    # low power pair
    with tab2:
        st.subheader("Optimal Power Distribution")
        # set current to 1 A
        i = 1
        p_list = []
        R_triples, _ = find_parallel_resistor_pairs(target_resist, tol, R_list, R_list)
        if st.button("Calculate", key=2):
            st.write(f"For your search there are {len(R_triples)} possible pairs.")
            st.write("This is within a tolerance of: +/-", tol_per, "%")
            for pair in R_triples:
                # calculate the total power
                power_total = pair[2]*i**2
                # Stromteiler law
                i1 = i * (pair[2]/pair[0])
                i2 = i * (pair[2]/pair[1])
                # calculate the share of each resistor of the total power
                p_share1 = i1**2*pair[0]/power_total*100
                p_share2 = i2**2*pair[1]/power_total*100
                p_list.append([pair[0], p_share1, pair[1], p_share2])
                
            column_names = ['R1', 'P share 1[%]', 'R2', 'P share 2[%]']
            df = pd.DataFrame(p_list, columns=column_names)

            # Calculate the Euclidean distance between each row for columns 'A' and 'B'
            distances = np.sqrt((df['P share 1[%]'] - df['P share 2[%]'])**2)
            df['distance'] = distances
            # Sort the DataFrame by the distances
            df.sort_values(by='distance', inplace=True, ascending=True)
            df = df.drop(columns=['distance'])
            # Select the first top rows with the smallest distances
            df = df.iloc[:top, :]
            df = df.round(2)
            df = df.reset_index(drop=True)
            st.table(df)
        
    with tab3:
        st.subheader("Temperature change")
        col1, col2 = st.columns(2)
        with col2:
            # Select the unit of the temperature
            temp_unit = st.selectbox('Unit', ('°C', 'K'))
        with col1:
            # define delta T
            delta_T = st.number_input(f"Δ Temperature({temp_unit}):", value=10.0, step=0.1)
        if temp_unit == 'K':
            temp_c = round(delta_T - 273.15, 2)
            st.write(f"This equals {temp_c} °C.")
        else:
            temp_K = round(delta_T - 273.15, 2)
            st.write(f"This equals {temp_K} K.")
        # input for the temperature coefficient
        K1 = st.number_input("Temperature coefficient for R1 (ppm):", value=100.0, step=0.1) / (10**6) 
        K2 = st.number_input("Temperature coefficient for R2 (ppm):", value=100.0, step=0.1) / (10**6) 
  
        if st.button("Calculate", key=1):
            # apply temperature change formula for resistors
            R_list1 = [res*(1 + K1 * delta_T) for res in R_list]
            R_list2 = [res*(1 + K2 * delta_T) for res in R_list]
            R_triples, _ = find_parallel_resistor_pairs(target_resist, tol, R_list1, R_list2)
            column_names = ['R1', 'R2', 'R total']
            df = pd.DataFrame(R_triples, columns=column_names)
            df = df.round(2)
            df['diff'] = abs(df['R total'] - target_resist)
            df = df.sort_values('diff', ascending=True)
            df = df.drop(columns=['diff'])
            df = df.iloc[:top, :]
            df = df.round(2)
            df = df.reset_index(drop=True)         
            st.table(df)
    with tab4:
        st.subheader("Given Resistance value")
        # input for the given resistor
        val_resist = st.number_input("Given resistance (Ohm)", min_value=target_resist+0.1, value=20.00, step=0.01, format='%.2f')
        if st.button("Calculate", key=4):
            R_triples, _ = find_parallel_resisitor(target_resist, tol, R_list, val_resist)
            st.write(f"For your search there are {len(R_triples)} possible pairs.")
            st.write("This is within a tolerance of: +/-", tol_per, "%")
            column_names = ['R1', 'R2', 'R total']
            df = pd.DataFrame(R_triples, columns=column_names)
            df = df.round(2)
            df['diff'] = abs(df['R total'] - target_resist)
            df = df.sort_values('diff', ascending=True)
            df = df.drop(columns=['diff'])
            df = df.iloc[:top, :]
            df = df.round(2)
            df = df.reset_index(drop=True)         
            st.table(df) 
    with st.sidebar:     
        if st.button("Help"):
            import webbrowser
            link = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            webbrowser.open(link)
            st.balloons()

            
if __name__ == '__main__':
    main()

"""Helper functions."""


def calc_e_series(e_series, decades):
    """Calculate the E series resistor values.
    
    Args:
        e_series: values of E series.
        decades: decades to calculate.
    
    Returns:
        R_list: list of standard resistor values.
    """
    R_list = []
    for m in e_series:
        for n in range(m):
            for i in range(decades+1):
                R_list.append(round(round((10**(1/m))**n, 1)*10**i, 1))
    # remove all duplicates
    R_list = [*set(R_list)]
    # remove 0
    R_list = [i for i in R_list if i != 0]
    return R_list


def remove_duplicates(res_list):
    my_dict = {}
    new_list = []

    for sublist in res_list:
        key = tuple(sorted(sublist[:2]))
        if key not in my_dict:
            my_dict[key] = sublist
            new_list.append(sublist)
    return new_list


def find_parallel_resistor_pairs(target_resistance, tolerance, R_listx, R_listy):
    """Find the resistor pairs for a given resistance, tolerance and resistor list.
    
    Args:
        target_resistance: Target resisitance in Ohm to achieve.
        tolerance: deviation to target resistance in Ohm.
        R_listx: list of resistors for the first resistor.
        R_listy: list of resistors for the second resistor.
    Returns:
        R_triple: List of pairs with resistor values that achieve given tolerance.
        best_resist: clostest resistance to target resistance.
        best_resist_pair: pair that results in closest restitance to target resistance.
    """
    # list to store resistance pairs that fulfill conditions
    R_triple = []
    best_resist = 100000000000000
    best_resist_pair = [0, 0]
    for R_x in R_listx:
        for R_y in R_listy:
            # Parallel resistors formula
            total_resist = (R_x * R_y)/(R_x + R_y)
            if abs(total_resist - target_resistance) <= tolerance:
                R_triple.append([R_x, R_y, total_resist])
            if abs(total_resist - target_resistance) < abs(best_resist - target_resistance):
                best_resist_pair = [R_x, R_y, round(total_resist, 2)]
    R_triple = remove_duplicates(R_triple)
    return R_triple, best_resist_pair


def find_parallel_resisitor(target_resistance, tolerance, R_list, R_x):
    R_triple = []
    best_resist = 100000000000000
    best_resist_pair = [0, 0]
    for R_y in R_list:
        # Parallel resistors formula
        total_resist = (R_x * R_y)/(R_x + R_y)
        if abs(total_resist - target_resistance) <= tolerance:
            R_triple.append([R_x, R_y, total_resist])
        if abs(total_resist - target_resistance) < abs(best_resist - target_resistance):
            best_resist_pair = [R_x, R_y, round(total_resist, 2)]
    R_triple = remove_duplicates(R_triple)
    return R_triple, best_resist_pair


def one_perc_deviation(triples):
    data = []
    for R in triples:
        R1_dev = R[0] + 1/100 * R[0]
        R2_dev = R[1] + 1/100 * R[1]
        R_total = (R1_dev * R2_dev)/(R1_dev + R2_dev)
        R_diff = abs(R[2] - R_total)
        R_diff_per = R_diff/R_total * 100
        data.append([R[0], R[1], R[2], round(R_diff_per, 1), round(R_diff, 2)])
    return data
        
def temp_change(triples, K1, K2, delta_T):
    data = []
    for R in triples:
        R1_dev = R[0]*(1 + K1 * delta_T) 
        R2_dev = R[1]*(1 + K2 * delta_T) 
        R_total = (R1_dev * R2_dev)/(R1_dev + R2_dev)
        R_diff = abs(R[2] - R_total)
        R_diff_per = R_diff/R_total * 100
        data.append([R[0], R[1], R[2], round(R_diff_per, 1), round(R_diff, 2)])
    return data
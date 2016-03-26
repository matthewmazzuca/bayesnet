from BayesianNetwork import *
import itertools

##Implement all of the following functions

## Do not modify any of the objects passed in as parameters!
## Create a new Factor object to return when performing factor operations



'''
multiply_factors(factors)

Parameters :
              factors : a list of factors to multiply
Return:
              a new factor that is the product of the factors in "factors"
'''
def multiply_factors(factors):
    factor_list = list(factors)
    while(len(factor_list) > 1):
        common_variables = find_common_variables(factor_list)
        if len(common_variables) is 0: #There may be a constant factor
            constant_factor = None
            for factor in factor_list:
                if len(factor.get_scope()) is 0:
                    constant_factor = factor
                    break
            if constant_factor is not None: #There is a constant factor
                other_factor = None
                if constant_factor is not factor_list[0]:
                    other_factor = factor_list[0]
                else:
                    other_factor = factor_list[1]
                combos = get_all_value_combinations(other_factor.get_scope())
                new_factor_table = []
                for combo in combos:
                    entry = list(combo)
                    value = constant_factor.get_value([]) * other_factor.get_value(combo)
                    entry.append(value)
                    new_factor_table.append(entry)
                new_factor = Factor("Product of {} and {}".format(constant_factor, other_factor), other_factor.get_scope())
                new_factor.add_values(new_factor_table)
                factor_list.remove(constant_factor)
                factor_list.remove(other_factor)
                factor_list.append(new_factor)
                continue #Check for more constant factors
        #There is no constant factor
        mapping = [] #Contains maps to the indices of common variables in each factor
        combos = [] #Contains arrays of variable value combos for each factor
        product_scope = [] #Product factor's scope
        uncommon_variables = [] #List of uncommon variables, we will use this to guarantee order in the new entries
        for factor in factor_list:
            factor_map = []
            for var in common_variables:
                factor_map.append(factor.get_scope().index(var))
            mapping.append(factor_map)
            combos.append(get_all_value_combinations(factor.get_scope()))
            product_scope = list(set(product_scope).union(factor.get_scope()))
            uncommon_temp = list(set(factor.get_scope()).difference(common_variables))
            uncommon_variables = list(set(uncommon_variables).union(uncommon_temp))
        product_combos = get_all_value_combinations(product_scope)
        #Generate new factor table
        new_factor_table = []
        for product_combo in product_combos:
            #Compute matches
            matches = []
            for factor_index in range(len(factor_list)):
                filter_array = [[],[]]
                for var_index in range(len(product_scope)):
                    if product_scope[var_index] in factor_list[factor_index].get_scope():
                        filter_array[0].append(product_scope[var_index])
                        filter_array[1].append(product_combo[var_index])
                factor_matches = get_all_value_combinations(factor_list[factor_index].get_scope(), filter_array)
                matches.append(factor_matches)
            #Compute products
            cart = list(itertools.product(*matches))
            for index in range(len(cart)):
                product_value = factor_list[0].get_value(cart[index][0])
                for index2 in range(len(cart[index])):
                    if not product_value: #If it is 0, we can stop
                            break
                    if index2 is 0:
                        continue #Do nothing, we initialized at this value
                    else:
                        product_value *= factor_list[index2].get_value(cart[index][index2])
                #Add new entry to factor table
                entry = list(product_combo)
                entry.append(product_value)
                new_factor_table.append(entry)
        #Create new factor object and return it
        new_factor = Factor("Product of {}".format(factor_list), product_scope)
        new_factor.add_values(new_factor_table)
        factor_list = [new_factor]
    return factor_list[0]

def find_common_variables(factors):
    #Given a list of factors, return an array of common_variables assuming there is at least one
    return_list = None
    for factor in factors:
        if return_list is None:
            return_list = factor.get_scope()
        else:
            return_list = list(set(return_list).intersection(factor.get_scope()))
        if len(return_list) is 0:
            break
    return return_list
            
def get_all_value_combinations(variables, filter_array=None):
    '''
    Given an ordered list of variables, returns a list of lists containing
    every combination of possible values within the variable domains, in
    the order of the given list.
    
    Filter is a list of two lists. The first list is a list of variables
    and the second is a list of values to filter for. The index of the
    variables must match the values.
    '''
    if filter_array is None:
        filter_array = [[None]]
    return_list = [[]]
    for var in variables:
        if var in filter_array[0]:
            for item in return_list:
                item.append(filter_array[1][filter_array[0].index(var)])
        else:
            new_list = []
            for value in var.domain():
                for item in return_list:
                    new_item = list(item)
                    new_item.append(value)
                    new_list.append(new_item)
            return_list = new_list
    return return_list
'''
restrict_factor(factor, variable, value):

Parameters :
              factor : the factor to restrict
              variable : the variable to restrict "factor" on
              value : the value to restrict to
Return:
              A new factor that is the restriction of "factor" by
              "variable"="value"
      
              If "factor" has only one variable its restriction yields a 
              constant factor
'''
def restrict_factor(factor, variable, value):
    new_factor_table = []
    var_index = factor.get_scope().index(variable)
    combos = get_all_value_combinations(factor.get_scope())
    for combo in combos:
        if combo[var_index] is value:
            entry = list(combo)
            entry.pop(var_index)
            entry.append(factor.get_value(combo))
            new_factor_table.append(entry)
    new_scope = factor.get_scope()
    new_scope.pop(var_index)
    restricted_factor = Factor("Restriction:{};{};{}".format(factor,variable,value),new_scope)
    restricted_factor.add_values(new_factor_table)
    return restricted_factor

    
'''    
sum_out_variable(factor, variable)

Parameters :
              factor : the factor to sum out "variable" on
              variable : the variable to sum out
Return:
              A new factor that is "factor" summed out over "variable"
'''
def sum_out_variable(factor, variable):
    var_index = factor.get_scope().index(variable)
    popped_scope = factor.get_scope()
    popped_scope.pop(var_index)
    popped_combos = get_all_value_combinations(popped_scope)
    new_factor_table = []
    for combo in popped_combos:
        combo_sum = 0
        for value in variable.domain():
            query = list(combo)
            query.insert(var_index, value)
            combo_sum += factor.get_value(query)
        entry = list(combo)
        entry.append(combo_sum)
        new_factor_table.append(entry)
    sum_out_factor = Factor("Sum Out:{},{}".format(factor, variable),popped_scope)
    sum_out_factor.add_values(new_factor_table)
    return sum_out_factor

'''
VariableElimination(net, queryVar, evidenceVars)

 Parameters :
              net: a BayesianNetwork object
              queryVar: a Variable object
                        (the variable whose distribution we want to compute)
              evidenceVars: a list of Variable objects.
                            Each of these variables should have evidence set
                            to a particular value from its domain using
                            the set_evidence function. 

 Return:
         A distribution over the values of QueryVar
 Format:  A list of numbers, one for each value in QueryVar's Domain
         -The distribution should be normalized.
         -The i'th number is the probability that QueryVar is equal to its
          i'th value given the setting of the evidence
 Example:

 QueryVar = A with Dom[A] = ['a', 'b', 'c'], EvidenceVars = [B, C]
 prior function calls: B.set_evidence(1) and C.set_evidence('c')

 VE returns:  a list of three numbers. E.g. [0.5, 0.24, 0.26]

 These numbers would mean that Pr(A='a'|B=1, C='c') = 0.5
                               Pr(A='a'|B=1, C='c') = 0.24
                               Pr(A='a'|B=1, C='c') = 0.26
'''       
def VariableElimination(net, queryVar, evidenceVars):
    #Restrict all factors based on evidence
    cur_factors = net.factors()
    for var in evidenceVars:
        restricted_factors = list(cur_factors)
        for factor in cur_factors:
            if var in factor.get_scope():
                new_factor = restrict_factor(factor, var, var.get_evidence())
                restricted_factors.remove(factor)
                restricted_factors.append(new_factor)
        cur_factors = restricted_factors
    #Conduct VE using min fill ordering
    elimination_order = min_fill_ordering(cur_factors, queryVar)
    for elim_var in elimination_order:
        elim_factor_list = [] #A list of factors containing elim_var
        for factor in cur_factors:
            if elim_var in factor.get_scope():
                elim_factor_list.append(factor)
        compressed_factors = sum_out_variable(multiply_factors(elim_factor_list), elim_var)
        #print("ELIMINATION OF:{}, SCOPE:{}".format(elim_var, compressed_factors.get_scope()))
        #print("COMPRESSED FACTORS CHECK")
        #my_print_table(compressed_factors)
        cur_factors = list(set(cur_factors).difference(elim_factor_list))
        cur_factors.append(compressed_factors)
    #Compute product and normalize
    final_factor = multiply_factors(cur_factors)
    #print("BEFORE NORMALIZATION CHECK")
    #my_print_table(final_factor)
    #Normalize
    combo_list = get_all_value_combinations(final_factor.get_scope())
    probability_sum = 0
    for combo in combo_list:
        probability_sum += final_factor.get_value(combo)
    distribution = []
    for combo in combo_list:
        if not probability_sum: #If the sum is 0
            distribution.append(0)
        else:
            distribution.append(final_factor.get_value(combo)/probability_sum)
    #print("SOLUTION")
    #my_print_table(final_factor)
    return distribution

def my_print_table(factor): #My own print table method
    combos = get_all_value_combinations(factor.get_scope())
    print("Table of: {}".format(factor))
    print("-----------")
    for combo in combos:
        print("{} |{}".format(combo, factor.get_value(combo)))
    print("-----------")

if __name__ == "__main__":
    '''
    var1 = Variable("V1", ["on","off"])
    var2 = Variable("V2", ["George","Martha"])
    var3 = Variable("V3", [1,2])
    fac1 = Factor("F1", [var1,var2])
    fac1.add_values([["on","George",0.1],
                     ["on","Martha",0.2],
                     ["off","George",0.4],
                     ["off","Martha",0.99]])
    my_print_table(fac1)
    fac2 = Factor("F2", [var2,var3])
    fac2.add_values([["George",1,0.16],
                     ["George",2,0.32],
                     ["Martha",1,0.64],
                     ["Martha",2,0.128]])
    my_print_table(fac2)

    restriction = restrict_factor(fac1,var1,"on")
    my_print_table(restriction)
    restriction = restrict_factor(fac1,var1,"off")
    my_print_table(restriction)
    
    fac3 = Factor("F3", [var1])
    fac3.add_values([["on",0.2],
                     ["off",0.5]])
    constant = restrict_factor(fac3,var1,"on")
    my_print_table(constant)
    test_net = BayesianNetwork("TestNet", [var1,var2,var3], [fac1,fac2,fac3])
    var2.set_evidence("Martha")
    var3.set_evidence(2)
    print("TA-DA:{}".format(VariableElimination(test_net, var1, [var2,var3])))'''
    
    #Class example: (slide 116)
    var_a = Variable("a", [0, 1])
    var_b = Variable("b", [0, 1])
    var_c = Variable("c", [0, 1])
    
    factor_1 = Factor("F1", [var_a])
    factor_1.add_values([[0, 0.1],
                         [1, 0.9]])
    factor_2 = Factor("F2", [var_a, var_b])
    factor_2.add_values([[0, 0, 0.6],
                         [0, 1, 0.4],
                         [1, 0, 0.1],
                         [1, 1, 0.9]])
    factor_3 = Factor("F3", [var_b, var_c])
    factor_3.add_values([[0, 0, 0.8],
                         [0, 1, 0.2],
                         [1, 0, 0.3],
                         [1, 1, 0.7]])
    my_print_table(sum_out_variable(multiply_factors([factor_1,factor_2]), var_a))
    class_example = BayesianNetwork("ClassNet", [var_a,var_b,var_c], [factor_1,factor_2,factor_3])
    print("Class Example:{}".format(VariableElimination(class_example, var_c, [])))
    



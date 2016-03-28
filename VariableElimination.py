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
    flist = list(factors)

    while(len(flist) > 1):
        freq_used = find_freq_used(flist)
        # Check for any constant factors

        if len(freq_used) == 0:
            flist = check_const_factors(freq_used, flist)


        # There is no constant factors
        product_combos, product_scope = no_const_factor(freq_used, flist)

        #Generate a new factor table from factors
        
        product_scope, flist, product_combos, newie_table = get_connect(product_combos, flist, product_scope)
        
        #Return new Factor table
        newie = Factor("Product of {}".format(flist), product_scope)
        newie.add_values(newie_table)
        flist = [newie]
    return flist[0]

def get_connect(product_combos, flist, product_scope):
    newie_table = []
    for product_combo in product_combos:
        #Compute connect
        connect = []
        for factor_index in range(len(flist)):
            filters = [[],[]]
            for ind in range(len(product_scope)):
                if product_scope[ind] in flist[factor_index].get_scope():
                    filters[0].append(product_scope[ind])
                    filters[1].append(product_combo[ind])
            factor_connect = get_all_value_combinations(flist[factor_index].get_scope(), filters)
            connect.append(factor_connect)
        #Compute products
        cart = list(itertools.product(*connect))
        for index in range(len(cart)):
            product_value = flist[0].get_value(cart[index][0])
            for index2 in range(len(cart[index])):
                if not product_value: #If it is 0, we can stop
                        break
                if index2 == 0:
                    continue #Do nothing, we initialized at this value
                else:
                    product_value *= flist[index2].get_value(cart[index][index2])
            #Add new entry to factor table
            entry = list(product_combo)
            entry.append(product_value)
            newie_table.append(entry)
    return product_scope, flist, product_combos, newie_table

def no_const_factor(freq_used, flist):
    mapping = [] #Contains maps to the indices of common variables in each factor
    combos = [] #Contains arrays of variable value combos for each factor
    product_scope = [] #Product factor's scope
    unfreq_used = [] #List of uncommon variables, we will use this to guarantee order in the new entries
    for factor in flist:
        factor_map = []
        for item in freq_used:
            factor_map.append(factor.get_scope().index(item))
        mapping.append(factor_map)
        combos.append(get_all_value_combinations(factor.get_scope()))
        product_scope = list(set(product_scope).union(factor.get_scope()))
        uncommon_temp = list(set(factor.get_scope()).difference(freq_used))
        unfreq_used = list(set(unfreq_used).union(uncommon_temp))
    product_combos = get_all_value_combinations(product_scope)

    return product_combos, product_scope

def check_const_factors(freq_used, flist):
    constant_factor = None
    for factor in flist:
        if len(factor.get_scope()) == 0:
            constant_factor = factor
            break
    if constant_factor != None: #There is a constant factor
        other_factor = None
        if constant_factor != flist[0]:
            other_factor = flist[0]
        else:
            other_factor = flist[1]
        combos = get_all_value_combinations(other_factor.get_scope())
        newie_table = []
        for combo in combos:
            entry = list(combo)
            value = constant_factor.get_value([]) * other_factor.get_value(combo)
            entry.append(value)
            newie_table.append(entry)
        newie = Factor("Product of {} and {}".format(constant_factor, other_factor), other_factor.get_scope())
        newie.add_values(newie_table)
        flist.remove(constant_factor)
        flist.remove(other_factor)
        flist.append(newie)

    return flist

def find_freq_used(factors):
    #Given a list of factors, return an array of freq_used assuming there is at least one
    return_list = None
    for factor in factors:
        if return_list == None:
            return_list = factor.get_scope()
        else:
            return_list = list(set(return_list).intersection(factor.get_scope()))
        if len(return_list) == 0:
            break
    return return_list
            
def get_all_value_combinations(variables, filters=None):
    '''
    Given an ordered list of variables, returns a list of lists containing
    every combination of possible values within the variable domains, in
    the order of the given list.
    
    Filter is a list of two lists. The first list is a list of variables
    and the second is a list of values to filter for. The index of the
    variables must match the values.
    '''
    if filters == None:
        filters = [[None]]
    return_list = [[]]
    for it in variables:
        if it in filters[0]:
            for item in return_list:
                item.append(filters[1][filters[0].index(it)])
        else:
            new_list = []
            for value in it.domain():
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
    newie_table = []
    ind = factor.get_scope().index(variable)
    combos = get_all_value_combinations(factor.get_scope())
    for combo in combos:
        if combo[ind] == value:
            entry = list(combo)
            entry.pop(ind)
            entry.append(factor.get_value(combo))
            newie_table.append(entry)
    new_scope = factor.get_scope()
    new_scope.pop(ind)
    restricted_factor = Factor("Restriction:{};{};{}".format(factor,variable,value),new_scope)
    restricted_factor.add_values(newie_table)
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
    ind = factor.get_scope().index(variable)
    popped_scope = factor.get_scope()
    popped_scope.pop(ind)
    popped_combos = get_all_value_combinations(popped_scope)
    newie_table = []
    for combo in popped_combos:
        combo_sum = 0
        for value in variable.domain():
            query = list(combo)
            query.insert(ind, value)
            combo_sum += factor.get_value(query)
        entry = list(combo)
        entry.append(combo_sum)
        newie_table.append(entry)
    sum_out_factor = Factor("Sum Out:{},{}".format(factor, variable),popped_scope)
    sum_out_factor.add_values(newie_table)
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
    
    currents = evid_vars(evidenceVars, net.factors())

    #Conduct VE using min fill ordering
    currents = min_order_fill_fact(currents, queryVar)
    
    #Compute product and normalize
    finals = multiply_factors(currents)
    #print("BEFORE NORMALIZATION CHECK")
    #my_print_table(finals)
    #Normalize
    combo_list = get_all_value_combinations(finals.get_scope())
    fin_sum = 0
    
    #print("SOLUTION")
    #my_print_table(finals)
    return get_distr(finals, combo_list, fin_sum)

def get_distr(finals, combo_list, fin_sum):
    for combo in combo_list:
        fin_sum += finals.get_value(combo)
    distribution = []
    for combo in combo_list:
        if not fin_sum: #If the sum is 0
            distribution.append(0)
        else:
            distribution.append(finals.get_value(combo)/fin_sum)

    return distribution

def evid_vars(evidenceVars, currents):
    for evid in evidenceVars:
        restricts = list(currents)
        for factor in currents:
            if evid in factor.get_scope():
                newie = restrict_factor(factor, evid, evid.get_evidence())
                restricts.remove(factor)
                restricts.append(newie)
        currents = restricts
    return currents

def min_order_fill_fact(currents, queryVar):
    elimination_order = min_fill_ordering(currents, queryVar)
    for elim_var in elimination_order:
        elim_flist = [] #A list of factors containing elim_var
        for factor in currents:
            if elim_var in factor.get_scope():
                elim_flist.append(factor)
        compressed_factors = sum_out_variable(multiply_factors(elim_flist), elim_var)
        #print("ELIMINATION OF:{}, SCOPE:{}".format(elim_var, compressed_factors.get_scope()))
        #print("COMPRESSED FACTORS CHECK")
        #my_print_table(compressed_factors)
        currents = list(set(currents).difference(elim_flist))
        currents.append(compressed_factors)
    return currents





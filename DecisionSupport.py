#Implement the function DecisionSupport
'''
For this question you may use the code from part 1

Note however that part 2 will be marked independent of part 1

The solution for VariableElimination.py will be used for testing part2 instead
of the copy you submit. 
'''

from MedicalBayesianNetwork import * 
from VariableElimination import * 

'''
Parameters:
             medicalNet - A MedicalBayesianNetwork object                        

             patient    - A Patient object
                          The patient to calculate treatment-outcome
                          probabilites for
Return:
         -A factor object

         This factor should be a probability table relating all possible
         Treatments to all possible outcomes
'''
def DecisionSupport(medicalNet, patient):
    medicalNet.set_evidence_by_patient(patient)
    eliminate = list(set(set(set(medicalNet.net.variables()) \
                .difference(medicalNet.getTreatmentVars()) \
                .difference(medicalNet.getOutcomeVars()))) \
                .difference(patient.evidenceVariables()))

    curr = medicalNet.net.factors() #A running list of all factors of interest
    #Restrict factors based on evidence

    curr = restrict_factors(curr, patient)
    
    #Eliminate variables not in the final factor
    curr = elim_vars_fin_factors(eliminate, curr)

    final = multiply_factors(curr)
    #Normalize with respect to each treatment option
    mixing = get_all_value_combinations(medicalNet.getTreatmentVars())
    
    return norm_for_treatments(medicalNet, final)

def norm_for_treatments(medicalNet, final):
    mixing = get_all_value_combinations(medicalNet.getTreatmentVars())
    for mix in mixing:
        num_treat = 0
        connect = get_all_value_combinations(final.get_scope(), \
                [medicalNet.getTreatmentVars(),mix])

        for m in connect:
            num_treat += final.get_value(m)
        #Overwrite entries with normalized value
        for m in connect:
            if num_treat != 0:
                final.add_value_at_assignment(final.get_value(m)/num_treat, m)
    return final


def restrict_factors(curr, patient):
    for item in patient.evidenceVariables():
        restrict = list(curr)
        for factor in curr:
            if item in factor.get_scope():
                new_factor = restrict_factor(factor, item, item.get_evidence())
                restrict.remove(factor)
                restrict.append(new_factor)
        curr = restrict

    return curr

def elim_vars_fin_factors(eliminate, curr):
    for item in eliminate:
        #Get all factors with var
        all_factors = []
        iter_list = list(curr)
        for factor in iter_list:
            if item in factor.get_scope():
                all_factors.append(factor)
                curr.remove(factor)
        new_factor = sum_out_variable(multiply_factors(all_factors), item)
        curr.append(new_factor)
    return curr


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
    for thg in variables:
        if thg in filter_array[0]:
            for item in return_list:
                item.append(filter_array[1][filter_array[0].index(thg)])
        else:
            new_list = []
            for value in thg.domain():
                for item in return_list:
                    new_item = list(item)
                    new_item.append(value)
                    new_list.append(new_item)
            return_list = new_list
    return return_list
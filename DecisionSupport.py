from MedicalBayesianNetwork import * 
from VariableElimination import * 

def norm_for_treatments(medicalNet, final):

    mixing = all_pairs(medicalNet.getTreatmentVars())
    for mix in mixing:
        num_treat = 0
        connect = all_pairs(final.get_scope(), \
                [medicalNet.getTreatmentVars(),mix])

        for m in connect:
            num_treat = num_treat + final.get_value(m)
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
                add_fact = restrict_factor(factor, item, item.get_evidence())
                restrict.remove(factor)
                restrict.append(add_fact)
        curr = restrict

    return curr

def elim_vars_fin_factors(eliminate, curr):
    '''
    Eliminates the appropriate factors
    '''

    for item in eliminate:
        all_factors = []
        iteration = list(curr)

        for factor in iteration:
            if item in factor.get_scope():
                all_factors.append(factor)
                curr.remove(factor)

        add_fact = sum_out_variable(multiply_factors(all_factors), item)
        curr.append(add_fact)
        
    return curr


def all_pairs(variables, conditions=None):
    '''
    Return list of possible combinations
    '''
    if conditions is None:
        conditions = [[None]]
    pairs = [[]]
    for thg in variables:
        if thg in conditions[0]:
            for item in pairs:
                item.append(conditions[1][conditions[0].index(thg)])
        else:
            newie = []
            for value in thg.domain():
                for item in pairs:
                    nitem = list(item)
                    nitem.append(value)
                    newie.append(nitem)
            pairs = newie

    return pairs

def DecisionSupport(medicalNet, patient):
    medicalNet.set_evidence_by_patient(patient)
    eliminate = list(set(set(set(medicalNet.net.variables()) \
                .difference(medicalNet.getTreatmentVars()) \
                .difference(medicalNet.getOutcomeVars()))) \
                .difference(patient.evidenceVariables()))

    # get the full list of necessary factors
    curr = medicalNet.net.factors() 

    #restrict the factors based on provided evidence

    curr = restrict_factors(curr, patient)
    
    #eliminate the appropriate variable. i.e. the ones not in the final factors
    curr = elim_vars_fin_factors(eliminate, curr)

    # standard multiply the factors together

    final = multiply_factors(curr)

    #Normalize according to each appropriate treatment option

    mixing = all_pairs(medicalNet.getTreatmentVars())
    
    return norm_for_treatments(medicalNet, final)


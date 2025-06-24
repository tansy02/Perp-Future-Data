import pandas as pd

def factorial(no_of_results):
    n = 1
    for i in range(no_of_results):
        n = n*(i+1)

    return(n)

factorial(8)

#permutations for unique elements ONLY
def permutations(N,r):
    a = factorial(N)
    b = factorial(N-r)
    return (a/b)

def combination (N,r):
    return permutations(N,r)/factorial(r)

def prob_permu(N,r):
    a = permutations(N,r)
    b = factorial(N)
    return (a/b)

#Binomial Probability Distribution
def probability(no_succession, no_trials, prob_success):
    a = factorial(no_trials)/(factorial(no_succession)*factorial(no_trials- no_succession))
    b = prob_success**(no_succession)
    c = (1 - prob_success)**(no_trials-no_succession)
    ans = a*b*c
    return ans
print("permutation", permutations(8,4))
print("combination", combination(8,4))
print("combination", combination(4,1))
print(probability(4,10,1/6))
print(prob_permu(26,5))

#Correlation Formula

def correlation(x,y):
    mean_x = sum(x)/len(x)
    mean_y = sum(y)/len(y)

    #numerator portion of formula
    
    numerator = []
    for i in range (len(x)-1):
        a = x[i] - mean_x
        b = y[i] - mean_y
        c = a*b 
        numerator.append(c)
    numerator = sum(numerator)

    #denominator portion of formula
    denominator = []
    sum_1 = []
    sum_2 = []
    for i in range (len(x)-1):
        a = x[i] - mean_x
        b = y[i] - mean_y
        a = a*a
        b = b*b
        sum_1.append(a) #even indexes
        sum_2.append(b) #odd indexes

    sum_1 = sum(sum_1)
    sum_2 = sum(sum_2)
    denominator = ((sum_1*sum_2) **(1/2)) #square root whole thing

    ans = numerator/denominator
    return ans

list1 = [54,2,5]
list2 = [2,22,4]
print(correlation(list1, list2))





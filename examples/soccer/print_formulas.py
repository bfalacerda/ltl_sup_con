import sys



n_robots=int(sys.argv[1])

formulas_list=[None for i in range(0, 2*n_robots+1)]

formula1='[] (('
for i in range(0,n_robots):
    formula1+= 'moving2ball' + str(i) + ' || hasball' + str(i) + ' || '
    
formula1=formula1[:-4] + ') -> X (!('

for i in range(0,n_robots):
    formula1+='move2ball' + str(i) + ' || '
    
formula1=formula1[:-4] + ')))'

formulas_list[0]=formula1

for i in range(0,n_robots):
    formula2='[] ((';
    for j in range(0,n_robots):
        if i != j:
            formula2+='startpassing' + str(j) + str(i) + ' || '
    formula2=formula2[:-4] + ')->(X (('
    formula2+='!move2ball' + str(i) + ' && !getball' + str(i) + ' && !move2goal' + str(i) + ' && !kickball' + str(i)
    for k in range(0,n_robots):
        if i != k:
            formula2+= ' && !startpassing' + str(i) + str(k) + ' && !pass' + str(i) + str(k)
    formula2+= ') W startreceiving' + str(i) + ')))'
    formulas_list[i+1]=formula2;

for i in range(0,n_robots):
    formula3='[](('
    for j in range(0,n_robots):
        if j != i:
            formula3+='!startpassing' + str(j) + str(i) + ' && '
    formula3=formula3[:-4] + ') -> (X !startreceiving' + str(i) + '))'
    formulas_list[n_robots+i+1]=formula3

for formula in formulas_list:
    print(formula)
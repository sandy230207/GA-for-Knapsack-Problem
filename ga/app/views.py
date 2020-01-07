from django.shortcuts import render, redirect
from django.http import HttpResponse
from app.knapsackproblem import knapsack



def index(request):
    try:
        # set the default value
        NGEN = 50
        MU = 50
        LAMBDA = 100
        CXPB = 0.7
        MUTPB = 0.2
        
        # retrieve input
        if request.method == 'POST':
            NGEN = int(request.POST['NGEN'])
            MU = int(request.POST['MU'])
            LAMBDA = int(request.POST['LAMBDA'])
            CXPB = float(request.POST['CXPB'])
            MUTPB = float(request.POST['MUTPB'])
            
        # call function and retrieve return value from knapsack.main
        ks=knapsack.main(NGEN,MU,LAMBDA,CXPB,MUTPB)

        r1=ks[0]
        r2=ks[1]
        r3=ks[2]
    
        return render(request, "index.html", locals())
    
    except Exception as e:
        message = str(e)
        return render(request, "index.html", locals())
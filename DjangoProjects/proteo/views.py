from django.shortcuts import render


# Create your views here.
def home(request):
    return render(request, "proteo/home.html", locals())

def Onedimension(request):
    return render(request,'proteo/1D.html',locals())


def Twodimension(request):
    return render(request,'proteo/2D.html',locals())

def Pred3Ddimension(request):
    return render(request,'proteo/Pred_3D.html',locals())

def Threedimension(request):
    return render(request,'proteo/3D.html',locals())

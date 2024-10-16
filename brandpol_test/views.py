from django.shortcuts import redirect


def main(request):
     return redirect('tests:all_tests')
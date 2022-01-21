:: Uncomment to show errors
::if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )

MODE 57

python2 "main.py"
@echo off

cd C:\Users\thigi\CPUShedulingSim\
goto :RunSimulator

:RunSimulator
bokeh serve --show main.py



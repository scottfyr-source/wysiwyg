@echo off
start "Laptop A (Tavia)" cmd /k "python main.py --name LaptopA --port 5555"
start "Laptop B (Scott)" cmd /k "python main.py --name LaptopB --port 5556"
start "Laptop C (Tyler)" cmd /k "python main.py --name LaptopD --port 5557"
start "Laptop D (Charlie)" cmd /k "python main.py --name LaptopD --port 5558"
start "Laptop E (MULTIUSER)" cmd /k "python main.py --name LaptopE --port 5559"

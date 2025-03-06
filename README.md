# Industrial Automated Systems Lab  

This repository contains lab materials for the **Industrial Automated Systems** course. The labs focus on **PLC programming, HMI design, temperature control, and PID implementation** using Siemens and Omron PLCs.  

## 📌 Overview  

Students will be divided into **groups of 2 or 3** and assigned to work on either:  
- **Siemens System**: **5 setups available** (Siemens S7-1200 PLC + KTP700 HMI)  
- **Omron System**: **2 setups available** (Omron NJ301-1100 PLC + NA5 HMI)  

Each group will follow structured lab exercises to learn:  
✔️ Basic PLC programming using **Siemens TIA Portal** and **Omron Sysmac Studio**.  
✔️ **Modbus communication** between a **Raspberry Pi 4** and the PLC.  
✔️ **Temperature measurement** using **MAX31855 with a PT100 RTD**.  
✔️ **PWM control** for a heater coil via a **MOSFET and optotransistor**.  
✔️ **PID control implementation** in the PLC for precise temperature regulation.  
✔️ **HMI development** for real-time user interaction.  

At the end of the lab, students will **successfully implement a PID controller in their PLC** and understand its application in an industrial process.  

## 📂 Repository Structure  
Industrial_Automation_Labs/ │── README.md # Overview of the project and lab structure │── Lab_Sheets/ # Markdown files for each lab │── PLC_Code/ # Siemens & Omron PLC programs │── RaspberryPi_Code/ # Python scripts for MAX31855 and PyModbus │── Docs/ # Additional setup guides and troubleshooting


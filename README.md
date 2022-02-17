# Automated Quotation System (AQS)
This repository contains the source code for Automated Quotation System to automate the groundwork tasks involved for each customer’s request for quotation (RFQ) and provide a standardised way to track RFQs.

### Contributors
| Name  | Github |
| ------------- |:-------------:|
| Calvin Ang Chong Yap   | calvinacy     |
| Darren Ho Shu Hao    | darrenho1994   |
|   Desmond Chin Jun Hao   | desmondchin97  |
|   Ng Jing Wen   | ngjw1599     |
|   Mohamed Izzat Khair  | izzkhairable   |

### The AQS consist of the following:
1. **Bot Programs**
    * Parts Extraction Bot
    * Parts Sourcing Bot
    * Quotation Generation Bot
    * Win-Loss Tracker Bot
1. **Web Application**
    * Supervisor Portal
    * Salesperson Portal
    * Public/Guest Portal

## System Requirement
* Windows OS
* Microsoft SQL Server 2008 Installed
* SQL Server Management Studio Installed

> If not installed, visit the following link: https://www.microsoft.com/en-sg/download/details.aspx?id=30438

## Running the Automated Quotation System

**Pre-requisite Steps**

1. Installing Application/System Dependecies
```
pip install -r requirements.txt
```

2. Import Sample Database into Microsoft SQL Server 2008


### For Parts Sourcing Bot
Change directory via the following command
```
cd aqs_bot\parts_sourcing
```

Run the main_controller.py file
```
python main_controller.py
```

> You should see the quotation_component, quotation and item_master table updated

# Automated Quotation System (AQS)
This repository contains the source code for Automated Quotation System to automate the groundwork tasks involved for each customer’s request for quotation (RFQ) and provide a standardised way to track RFQs.

### Screenshots
> To be added...

### Client
TSH Synergy Pte Ltd

<img width="200" alt="image" src="https://user-images.githubusercontent.com/60332263/154437668-095eccf6-b9cf-4da7-9296-a2d50f4af127.png">

### Project By
<img width="190" alt="image" src="https://user-images.githubusercontent.com/60332263/154437956-5e90398a-6c33-4812-a03a-fd9b64cbdf89.png">

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

## Known Issues
There are no known issues

## System Requirement
* Windows OS
* Microsoft SQL Server 2008 Installed
* SQL Server Management Studio Installed

> If not installed, visit the following link: https://www.microsoft.com/en-sg/download/details.aspx?id=30438

## Running the Automated Quotation System

**Pre-requisite Steps**

1. Installing Application/System Dependencies
```
pip install -r requirements.txt
```

2. Import Sample Database into Microsoft SQL Server 2008

   1. Open SQL Server Management Studio 

      <img width="235" alt="image" src="https://user-images.githubusercontent.com/60332263/154434841-d8037df6-e180-4510-9644-478c4b8f236d.png">

   1. Connect to database & select folder icon

      <img src="https://user-images.githubusercontent.com/60332263/154434376-983874cc-2910-4032-bf5a-058d0b025bbc.png" alt="drawing" width="200"/>
      
   1. Select the aqs.sql file found in the repo
 
      <img width="530" alt="image" src="https://user-images.githubusercontent.com/60332263/154435405-6e8a4680-0a30-4263-a91d-f571eef1c30c.png">

   1. Execute the queries in the file by clicking "Execute" button
      
      <img width="200" alt="image" src="https://user-images.githubusercontent.com/60332263/154436249-87be1913-b329-4ba5-88c3-e0fc81367b1e.png">

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

### For Part Extraction Bot
> To be added...
### For Quotation Generation Bot
> To be added...
### For Win-Loss Tracker Bot
> To be added...
### For Web Application
> To be added...

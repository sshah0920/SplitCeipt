# SplitCeipt

## How to run? 
To run you will need ethereum installed and you also need to pip the following: <br />
1. web3 <br />
2. py-solc-x <br />

Then in a separate tab/window you can run the following in our project folder to start our provider (Password is _ ‘nweier’ _):


_ $ geth --nodiscover --networkid 42 --datadir bkc_data --unlock
0x28A56aBcC035Ebef4922C386F127EdCC7800Ec4D --mine --http --http.api
geth,eth,net,web3,personal,miner --http.addr 127.0.0.1 --allow-insecure-unlock _


## Backend web3 Client 
Open up a python prompt and you can run the client functions directly. test() runs through each of the functions and prints updates, but you may also manually run them as shown below

Python 3.6.9 (default, Oct 8 2020, 12:12:24)
[GCC 8.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from Web3Client import *
>>> test()
0x10b33fd33Acdeb4dc9Eae8C6117f73F634179214
Group 0x6AEE50D8120737DAb462479e9d09FB176e9d05D6
Receipt 1 0xE599Bd116629BD4F5C7A9Dac8B19D2f8034Ce8b8
Receipt 2 0xE599Bd116629BD4F5C7A9Dac8B19D2f8034Ce8b8
Receipt 3 0xE599Bd116629BD4F5C7A9Dac8B19D2f8034Ce8b8
>>> w3_client = Web3Client()
>>> w3_client.connect('http://127.0.0.1:8545')
True
>>> w3_client.login('nweier','2668')
0x10b33fd33Acdeb4dc9Eae8C6117f73F634179214
True
>>> grp = w3_client.createGroup()>>> receipt =
w3_client.initReceipt(grp,[[w3_client.addr],[w3_client.addr],w3_client.addr,[100]
])
>>> grp
'0x0FA12afb0bB5F69F9b36125B7074b94d6eE7B818'
>>> receipt
'0x350884c49E04Be741849527e80be3C4C4Dc49EDf'
>>> 

## Frontend(python3 main.py)
login with (username:‘nweier’,pwd:’2668’), or create your own account(but this will by default have 0 funds to do anything)

Then you will be brought to a receipt management page. <br />
For Buyers and Payers you can enter a set of addresses separated by commas Arbitrator is a single address and prices is a set of integers comma separated. Then hit “+” to submit it

In the command prompt you should see a [*] log message with the receipt details where @ indicates the address of the receipt.

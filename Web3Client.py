from solcx import *
from web3 import Web3,eth,geth,HTTPProvider
from threading import Thread
from time import sleep

class Web3Client:
  def __init__(self):
    # Client parameters
    self.w3     = None
    self.addr   = 0
    self.pwd    = ""
    self.groups = [] # List of group addresses for our listeners
    self.receipts = {}
    # Contract paremeters
    self.rabi = """
[
	{
		"constant": false,
		"inputs": [],
		"name": "revokeDispute",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [],
		"name": "disputeReceipt",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [],
		"name": "confirmReceipt",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [],
		"name": "MakeDeposit",
		"outputs": [],
		"payable": true,
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [],
		"name": "Timelock",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [],
		"name": "Revoke",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [],
		"name": "Destroy",
		"outputs": [],
		"payable": true,
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "decide",
				"type": "int256"
			}
		],
		"name": "Arbitrate",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"name": "_buyers",
				"type": "address[]"
			},
			{
				"name": "_payers",
				"type": "address[]"
			},
			{
				"name": "_arb",
				"type": "address"
			},
			{
				"name": "_maker",
				"type": "address"
			},
			{
				"name": "_prices",
				"type": "uint8[]"
			}
		],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "constructor"
	}
]
    """

    self.abi = """
[
	{
		"constant": false,
		"inputs": [
			{
				"name": "_buyers",
				"type": "address[]"
			},
			{
				"name": "_payers",
				"type": "address[]"
			},
			{
				"name": "_arb",
				"type": "address"
			},
			{
				"name": "_prices",
				"type": "uint8[]"
			}
		],
		"name": "addReciept",
		"outputs": [
			{
				"name": "",
				"type": "address"
			}
		],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "con",
				"type": "address"
			},
			{
				"name": "_buyers",
				"type": "address[]"
			}
		],
		"name": "changeBuyers",
		"outputs": [
			{
				"name": "",
				"type": "address"
			}
		],
		"payable": true,
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "con",
				"type": "address"
			},
			{
				"name": "_prices",
				"type": "uint8[]"
			}
		],
		"name": "changePrices",
		"outputs": [
			{
				"name": "",
				"type": "address"
			}
		],
		"payable": true,
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "con",
				"type": "address"
			},
			{
				"name": "_arb",
				"type": "address"
			}
		],
		"name": "changeArbitrator",
		"outputs": [
			{
				"name": "",
				"type": "address"
			}
		],
		"payable": true,
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "con",
				"type": "address"
			}
		],
		"name": "destroyReceipt",
		"outputs": [],
		"payable": true,
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "con",
				"type": "address"
			},
			{
				"name": "_payers",
				"type": "address[]"
			}
		],
		"name": "changePayers",
		"outputs": [
			{
				"name": "",
				"type": "address"
			}
		],
		"payable": true,
		"stateMutability": "payable",
		"type": "function"
	}
]
    """
    self.sol = """
pragma solidity ^ 0.4.22;
contract Tokens {
  address owner;
  mapping(address => uint256) balance;
  function deposit(address _owner, uint256 amount) public{
    owner = _owner;
    balance[owner] += amount;
  }

  function transfer(address sender, address recipient, uint256 amount) public returns(uint256){
    // Transfer function returns amount transferred
    if(balance[sender] < amount || balance[recipient]+amount < balance[recipient]){ return 0; }
    balance[sender] = balance[sender] - amount;
    balance[recipient] = balance[recipient] + amount;
    return amount;
  }

  function redeem(address account) public returns(uint256){
    uint amount = balance[account];
    balance[account] = 0;
    return amount;
  }
}

contract ReceiptEscrow {
  // Who initialized receipt
  address maker;

  // The Receipt this escrow contract concerns
  struct Receipt
  {
    address[] buyers;
    address[] payers;
    uint8[]   prices;
    bool      active;
  }
  Receipt receipt;

  // A mapping indicating which addresses have confirmed the reciept
  mapping (address => bool) receiptConfirmed;
  // The sum owed per address
  mapping (address => uint256) sums;

  Tokens tok;

  address arb;  // Arbitrator addr
  address dsp;  // Disputer addr
  uint dispute; // Dispute flag
  uint confirm; // Number of peeps who have confirmed
  uint blckNum; // Blocknumber for timelock


  constructor(address[] _buyers, address[] _payers, address _arb, address _maker, uint8[] _prices) public{
    require(_buyers.length == _payers.length && _payers.length == _prices.length);
    arb     = _arb;
    dispute = 0;
    confirm = 0;
    blckNum  = 0;
    receipt = Receipt( _buyers, _payers, _prices, true);
    tok     = new Tokens();
    maker   = _maker;
    
    for(uint i=  0; i < _buyers.length; i++)
    {
        sums[_buyers[i]]+=_prices[i];
    }
    
  }

  function Revoke() public{
    require(receipt.active && msg.sender == maker);
    receipt.active = false;
    Destroy();
  }

  function MakeDeposit() public payable{
    require(sums[msg.sender]<msg.value && receipt.active);
   // Make sure address is associated with contract
    bool flag = false;
    for(uint i = 0; i < receipt.buyers.length; i++){ if(msg.sender==receipt.buyers[i]){ flag=true; } }
    if(flag){ tok.deposit(msg.sender,msg.value); }
  }
  
  function ConfirmReceipt() public{
    require(receipt.active);
    bool flag = tok.transfer(msg.sender,msg.sender,sums[msg.sender]) == sums[msg.sender];
    require(flag);
    receiptConfirmed[msg.sender] = true;
    confirm += 1;
    if(confirm == receipt.payers.length)
    {
      for(uint i=  0; i < receipt.buyers.length; i++)
      {
        receipt.payers[i].transfer(tok.transfer(receipt.buyers[i],receipt.payers[i],receipt.prices[i]));
      }
    }
  }

  function disputeReceipt() public{
    bool flag = tok.transfer(msg.sender,msg.sender,sums[msg.sender]) == sums[msg.sender];
    require(flag);
    flag = false;
    // Only involved address can dispute
    for(uint i = 0; i < receipt.payers.length; i++){ if(msg.sender==receipt.payers[i]){ flag=true; } }
    for(uint j = 0; j < receipt.buyers.length; j++){ if(msg.sender==receipt.buyers[j]){ flag=true; } }
    if(flag){
      dispute = 1;
      blckNum  = block.number;
    }
  }

  function revokeDispute() public{
    require(msg.sender == dsp && receipt.active);
    dispute = 0;
    blckNum = 0;
    receiptConfirmed[msg.sender] = true;
  }

  function Arbitrate(int decide) public{
    require(dispute == 1 && msg.sender == arb && receipt.active);
    if(decide < 0){ // Vote against disputer and force their hand
      dispute = 0;
      blckNum  = 0;
      receiptConfirmed[dsp] = true;
    }else{ // Otherwise mark receipt inactive
      receipt.active = false;
      Destroy();
    }
  }

  function Timelock() public{
    require(receipt.active);
    if(blckNum + 48 < block.number){ receipt.active = false; Destroy();}
  }
  
  function Destroy() public payable{
    require(!receipt.active);
    // Send money back to all the buyers
    for(uint i = 0; i < receipt.buyers.length; i++){ receipt.buyers[i].transfer(tok.redeem(receipt.buyers[i]));  }
    selfdestruct(msg.sender);
  }
}

contract GroupContract{
  struct Receipt
  {
    address[] buyers;
    address[] payers;
    uint8[]   prices;
    address      arb;
    address    maker;
  }

  mapping(address => Receipt) receipts;

  function addReciept(address[] _buyers, address[] _payers, address _arb, uint8[] _prices) public returns(address){
    ReceiptEscrow escrow = new ReceiptEscrow(_buyers,_payers, _arb, msg.sender, _prices);
    receipts[address(escrow)] = Receipt(_buyers,_payers,_prices,_arb, msg.sender);
    return address(escrow);
  }

  function destroyReceipt(address con) public payable{
    delete(receipts[con]);
  }

  function changePrices(address con, uint8[] _prices) public payable returns(address){
    Receipt memory receipt = receipts[con];
    require(msg.sender==receipt.maker);
    receipt.prices = _prices;
    ReceiptEscrow escrow = new ReceiptEscrow(receipt.buyers,receipt.payers,receipt.arb, receipt.maker, receipt.prices);
    receipts[address(escrow)] = receipt;
    destroyReceipt(con);
    return address(escrow);
  }

  function changePayers(address con, address[] _payers) public payable returns(address){
    Receipt memory receipt = receipts[con];
    require(msg.sender==receipt.maker);
    receipt.payers = _payers;
    ReceiptEscrow escrow = new ReceiptEscrow(receipt.buyers,receipt.payers,receipt.arb, receipt.maker, receipt.prices);
    receipts[address(escrow)] = receipt;
    destroyReceipt(con);
    return address(escrow);
  }
  
  function changeBuyers(address con, address[] _buyers) public payable returns(address){
    Receipt memory receipt = receipts[con];
    require(msg.sender==receipt.maker);
    receipt.buyers = _buyers;
    ReceiptEscrow escrow = new ReceiptEscrow(receipt.buyers,receipt.payers,receipt.arb, receipt.maker, receipt.prices);
    receipts[address(escrow)] = receipt;
    destroyReceipt(con);
    return address(escrow);
  }
  
  function changeArbitrator(address con, address _arb) public payable returns(address){
    Receipt memory receipt = receipts[con];
    require(msg.sender==receipt.maker);
    receipt.arb = _arb;
    ReceiptEscrow escrow = new ReceiptEscrow(receipt.buyers,receipt.payers,receipt.arb, receipt.maker, receipt.prices);
    receipts[address(escrow)] = receipt;
    destroyReceipt(con);
    return address(escrow);
  }
}
    """

    self.code = ''

  def listener(self,address,labi, interval):
    """
    Listner that listens for updates based off contract address
    """
    # We want the latest blocks
    handle  = self.w3.eth.contract(abi=abi,address=receipt)
    Filter = self.w3.eth.filter({'fromBlock':'latest', 'address':address})
    while True:
      for event in Filter.get_new_entries():
        # Fetch transaction
        data = self.w3.eth.getTransactionReceipt(event['transactionHash'])
        data = handle.decode_function_input(data.input)
        print(data)
        
      
  def start_Listener(self,address,labi):
    worker = Thread(target=self.listener, args=(address,labi, 5), daemon=True)

  def connect(self,provider):
    """
    Try to connect to the provider
    """
    self.w3 = Web3(Web3.HTTPProvider(provider))
    self.w3.geth.miner.start(1)
    return self.w3.isConnected()

  def login(self,usr,pss):
    """
    Authenticate user via their account on our HTTP Provider
    Locally we store a username to address map
    """
    try: # No username/username file will cause program to crash here
      with open("UserMap","r") as f:
        data = {c.split(':')[0]:c.split(':')[1] for c in f.read().split('\n') if len(c)}
        self.addr = data[usr]
      self.pwd = pss
      print(self.addr)
      return self.w3.geth.personal.unlock_account(self.addr,self.pwd)
    except:
      return False
  
  def signup(self,usr,pss):
    """
    Create an account with our HTTP Provider
    """
    self.addr = self.w3.geth.personal.new_account(pss)
    with open("UserMap","a") as f:
      f.write(str(usr)+':'+str(self.addr))
    self.pwd = pss
    return self.w3.geth.personal.unlock_account(self.addr,self.pwd)

  def createGroup(self):
    """
    This creates a group contract
    People you share the group address with can create/manage receipts via this contract
    Function returns the address of the group contract
    """
    install_solc("0.4.22")
    self.code = compile_source(self.sol)['<stdin>:GroupContract']['bin']

    contract = self.w3.eth.contract(abi=self.abi,bytecode=self.code)
    self.w3.geth.personal.unlock_account(self.addr,self.pwd)

    # Call GroupContract constructor, from the returned contract stuff we only want the address
    # *Most other functions for reciepts return contract addresses themselves
    tx_hash  = contract.constructor().transact({'from':self.addr,'gas':7000000})
    con_addr = self.w3.eth.waitForTransactionReceipt(tx_hash)['contractAddress']
    self.start_Listener(con_addr,self.abi)
    return con_addr

  def initReceipt(self,group,receipt):
    """
    Creates a receipt within a given group(by address)
    Each receipt is represented by it's own Escrow contract
    """
    self.w3.geth.personal.unlock_account(self.addr,self.pwd)
    handle  = self.w3.eth.contract(abi=self.abi,address=group)

    # Here receipt is expected to be a list of args in the form [ buyer_list, payer_list, arbitrator, prices]
    # Everywhere else receipt is espected to be an address of a receipt
    res = handle.functions.addReciept(*receipt).call({'from': self.addr})
    self.receipts[res] = receipt
    return res

  def revokeReceipt(self,receipt):
    """
    Destroy/Revoke reciept that I made
    """

    self.w3.geth.personal.unlock_account(self.addr,self.pwd)
    handle  = self.w3.eth.contract(abi=self.rabi,address=receipt)
    self.receipts.pop(receipt)
    tx_hash = handle.functions.Revoke().transact({'from':self.addr,'gas':7000000})
    return self.w3.eth.waitForTransactionReceipt(tx_hash)

  def modify(self,group,receipt,mod):
    """
    Function to modify/destroy a receipt (by address)
    """
    # Valid Modifications in the form (letter_mod,value)
    #  Destroy It     - ('D',)
    #  Change Buyers  - ('B',buyers)
    #  Change Payers  - ('P',payers)
    #  Change Arbitr  - ('A',arbitor)
    #  Change Prices  - ('$',prices)
    self.w3.geth.personal.unlock_account(self.addr,self.pwd)
    handle  = self.w3.eth.contract(abi=self.abi,address=group)
    old = [i for i in self.receipts.pop(receipt)]
    tx = 0 
    if mod[0]=='D':
      rct = self.w3.eth.contract(abi=self.rabi,address=receipt)
      tx = handle.functions.destroyReceipt(receipt).call({'from': self.addr})
      tx = rct.functions.Revoke().call({'from': self.addr})
    if mod[0]=='B': 
      old[0] = mod[1]
      tx = handle.functions.addReciept(*old).call({'from': self.addr})
    if mod[0]=='P':
      old[1] = mod[1]
      tx = handle.functions.addReciept(*old).call({'from': self.addr})
    if mod[0]=='A': 
      old[2] = mod[1]
      tx = handle.functions.addReciept(*old).call({'from': self.addr})
    if mod[0]=='$':
      old[-1] = mod[1]
      tx = handle.functions.addReciept(*old).call({'from': self.addr})
    
    if mod[0]!='D': self.receipts[tx] = old

    return tx

  def arbitrate(self,receipt,decide):
    """
     Arbitrate on a receipt
    """
    self.w3.geth.personal.unlock_account(self.addr,self.pwd)
    handle = self.w3.eth.contract(abi=self.rabi,address=receipt)
    tx_hash = handle.functions.Arbitrate(decide).transact({'from':self.addr,'gas':7000000})

    return self.w3.eth.waitForTransactionReceipt(tx_hash)

  def deposit(self,receipt,amount):
    """
    Make a deposit towards a receipt (by address)
    """
    self.w3.geth.personal.unlock_account(self.addr,self.pwd)
    handle = self.w3.eth.contract(abi=self.rabi,address=receipt)
    tx_hash = handle.functions.MakeDeposit().transact({'from':self.addr,'gas':7000000,'value':amount})
    return self.w3.eth.waitForTransactionReceipt(tx_hash)

  def confirm(self,receipt):
    """
    Confirm a receipt (by address)
    """
    self.w3.geth.personal.unlock_account(self.addr,self.pwd)
    handle = self.w3.eth.contract(abi=self.rabi,address=receipt)
    tx_hash = handle.functions.confirmReceipt().transact({'from':self.addr,'gas':7000000})
    return self.w3.eth.waitForTransactionReceipt(tx_hash)

  def dispute(self,receipt,val):
    """
    Dispute(or revoke a dipute on) a receipt (by address)
    """
    self.w3.geth.personal.unlock_account(self.addr,self.pwd)
    handle  = self.w3.eth.contract(abi=self.rabi,address=receipt)
    tx_hash = 0
    if val == 1: tx_hash = handle.functions.disputeReceipt().transact({'from':self.addr,'gas':7000000})
    else: tx_hash = handle.functions.revokeDispute().transact({'from':self.addr,'gas':7000000})

    return self.w3.eth.waitForTransactionReceipt(tx_hash)

def test():
  """
  Function for easy demo of backen web3 client
  """
  w3_client = Web3Client()
  w3_client.connect('http://127.0.0.1:8545')
  w3_client.login('nweier','2668')

  # Group Creation
  grp = w3_client.createGroup()
  print("Group",grp)

  # Create Receipt
  receipt = w3_client.initReceipt(grp,[[w3_client.addr],[w3_client.addr],w3_client.addr,[100]])
  print("Receipt 1",receipt)
  # Make a deposit towards a receipt and confirm it
  w3_client.deposit(receipt,100)
  w3_client.confirm(receipt)
  
  # Dispute stuff
  receipt = w3_client.initReceipt(grp,[[w3_client.addr],[w3_client.addr],w3_client.addr,[100]])
  print("Receipt 2",receipt)
  w3_client.deposit(receipt,100)
  w3_client.dispute(receipt,1) # Sets dispute
  w3_client.dispute(receipt,0) # Revoke Disput
  w3_client.dispute(receipt,1)
  w3_client.arbitrate(receipt,1) # Arbitrate to discard receipt, can use -1 to force disputer's hand
  

  # Modifiying existing receipt only succeds if you are the maker
  receipt = w3_client.modify(grp,receipt,('B',[w3_client.addr]))  # Change payers
  receipt = w3_client.modify(grp,receipt,('P',[w3_client.addr]))  # Change buyers
  receipt = w3_client.modify(grp,receipt,('$',[50])) # Change prices
  print("Receipt 3",receipt)
  w3_client.modify(grp,receipt,('D',))      # Destroy receipt


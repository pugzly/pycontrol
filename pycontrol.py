import requests, json
from web3 import Web3

# address of smart contract we want to control:
contract_address = "0x_DEPLOY_CONTRACT_AND_PASTE_ADDRESS_HERE_"

# contract owner (genesis wallet) address, and secret key:
genesis_address     = "0x__GENESIS_WALLET_ADDRESS_FOR_REFERENCE__"
genesis_private_key = "00______EXPORT_GENESIS_WALLET_PRIVATE_KEY_FROM_METAMASK_______00"


# contract function name for current tax rate:
tax_rate_function_name   = "burnTaxPercent"
# contract function name for setting new tax rate:
set_tax_function_name    = "setBurnTax"
# contract function name for getting contract owner:
get_owner_function_name  = "owner"


if __name__ == "__main__":
  bsc = "https://bsc-dataseed.binance.org/"
  web3 = Web3(Web3.HTTPProvider(bsc))
  print("PyControl BSC Web3 connection status: ", web3.isConnected())
  
  url_eth = "https://api.bscscan.com/api"
  contract_checked = web3.toChecksumAddress(contract_address)
  API_ENDPOINT = url_eth+"?module=contract&action=getabi&address="+str(contract_checked)
  r = requests.get(url = API_ENDPOINT)
  response = r.json()
  abi=json.loads(response["result"])
  contract = web3.eth.contract(address=contract_checked, abi=abi)

  # show all available contract functions
  print("--------------------------------------")
  print("Contract address: ", contract_checked)
  print("Available contract functions:")
  for func in contract.all_functions():
    print(func)
  print("--------------------------------------")
  
  # get current tax rate (example contract is token with burn tax)
  get_rate = contract.get_function_by_name(tax_rate_function_name)
  burnTax = get_rate().call() 
  print("Current burn tax: "+str(burnTax)+"%")

  # check if private key is valid
  get_contract_owner = contract.get_function_by_name(get_owner_function_name)
  contract_owner = get_contract_owner().call()
  key_account = web3.eth.account.privateKeyToAccount(genesis_private_key)
  if key_account.address != contract_owner:
    print("Private Key is NOT valid!")
    print("Contract owner address: ", contract_owner)
    print("Private key address:    ", key_account.address)
  else:
    print("Private Key is valid.")
    newTax = int(input("Enter new tax rate percent:\n"))
    if newTax < 0: newTax = 0
    if newTax > 100: newTax = 100
    
    # set new tax rate with signed transaction
    nonce = web3.eth.get_transaction_count(key_account.address)
    set_new_tax = contract.get_function_by_name(set_tax_function_name)
    transaction = set_new_tax(newTax).buildTransaction({
              'gas': 70000,
              'gasPrice': web3.toWei('5', 'gwei'),
              'from': key_account.address,
              'nonce': nonce
              })
    signed_txn = web3.eth.account.signTransaction(transaction, private_key=genesis_private_key)
    #tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print("Executed. Signed transaction hash: ", tx_hash.hex())



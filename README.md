# cryptomon_CLI
A python3 tool to quickly monitor coinmarketcap and your crypto portfolio into a terminal.

# Usage
You need to have python 3.6 or higher on your computer and run the script.  
This script use pre-installed python3 libraries only.
  
cryptomon_CLI.py [-h] [-n NUMBER] [-f [FILE]]
Please specify the full path when your run this script.  
E.g : python3 /Users/username/cryptomon_CLI.py -f /Users/username/portfolio

optional arguments:  
  -h, --help            show this help message and exit  
  -n NUMBER, --number NUMBER  
                        Number of currencies to display in the main board  
  -f [FILE], --file [FILE]  
                        Your portfolio file, formatted like the portfolio file example.  
                        It has to be the full name of the coin not his symbol.  
                        The name can be in lower case and if it contains a space, replace the space by a dash (-).  

  -c COINAME, --coiname COINAME  
                        Name of the specific coin you want to display.  
                        e.g : zcash , bitcoin-cash  
# View
![alt text](https://github.com/TheAsouka/cryptomon_CLI/blob/master/render.png)

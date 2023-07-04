#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# @uthor : TheAsouka


import re, sys, os, json, argparse, time
from urllib.request import urlopen
from random import randint

def Argument_Parser():
    """Parse argument supplied by the user"""

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-n","--number",help="Number of currencies to display in the main board",type=int,nargs=1)
    arg_parser.add_argument("-f","--file",help="Your portfolio file, formatted like this : {\"EUR Invested\":XXX,\"CoinName\":XXX, ..., \"Bitcoin\":18}",type=argparse.FileType('r'),nargs='?')
    arg_parser.add_argument("-c","--coiname",help="Name of the specific coin you want to display. e.g : zcash , bitcoin-cash")    
    args = arg_parser.parse_args()

    return args

def Get_JSON(s_API_url):
    """Retrieve market values from CMC.com API,
    and store them in a list of dictionaries"""

    try :
        b_source = urlopen(s_API_url).read()
    except :
        print ("Error : Can't connect to the API, please check your internet connection.")
        sys.exit(0)

    l_JSON_data = json.loads(b_source)
    return l_JSON_data

def Get_Desired_Values(i_rank, l_data):
    """Retrieve desired values of a coin in list returned by GetJSON()"""

    l_coin_values = []
    l_key = [
            "rank",
            "name",
            "symbol",
            "price_btc",
            "price_usd",
            "price_eur",
            "market_cap_usd",
            "percent_change_1h",
            "percent_change_24h",
            "percent_change_7d"]

    for key in l_key:
        l_coin_values.append(l_data[i_rank][key])
    return l_coin_values

def Make_a_Frame(s_to_frame, i_max_lenght):
    """Create a frame for a string and place it in the middle
        to get a clean display of values"""

    i_positioner = int((i_max_lenght - len(s_to_frame)) / 2)

    #prevent misalignments when strings are sized differently
    if (len("|" + "_" * i_positioner + s_to_frame + "_" * i_positioner + "|") % 2) != 0:
        return "|" + " " * i_positioner + s_to_frame + " " * (i_positioner - 1) + "|"

    return "|" + " " * i_positioner + s_to_frame + " " * i_positioner + "|"

def Colorize(s_to_colorize):
    """Add some color to changing values"""

    re_minus = re.compile("\-")
    if re.search(re_minus, s_to_colorize):
        return "\033[1;31m" + s_to_colorize + "\033[0;m" #RED
    else:
        return "\033[1;32m" + s_to_colorize + "\033[0;m" #GREEN

def Display_Time():
    print ("Source : www.coinmarketcap.com")
    s_currentime = time.strftime("%d/%m/%Y %H:%M:%S")
    print (s_currentime)

    return s_currentime

def Display_Header(l_max_length):
    """Display first line of the board which explains columns"""

    l_categories = [
                    "Rank",
                    "Name",
                    "Symbol",
                    "BTC Price",
                    "USD Price",
                    "EUR Price",
                    "Marketcap M$",
                    "\0" * 6 + "1h"  + "\0" * 6, #"\0" (NULL) * 6
                    "\0" * 6 + "24h" + "\0" * 6, #to respect colorized strings length
                    "\0" * 6 + "7d"  + "\0" * 6] #and avoid misalignments

    print ("=" * (sum(l_max_length)-26))

    i = 0
    for cat in l_categories:
        print (Make_a_Frame(cat,l_max_length[i]),end='')
        i += 1

    print ("\r")
    print ("="*(sum(l_max_length)-26))
    """Display a long line to separate headers and boards,
       -26 because colorized elements strings are longer
       (~15 chars) than what is displayed (~3 chars), and
       fit the perfect size"""

def Display_Main_Board(s_coin_number,l_market_values,l_max_length):
    """Display properly the main board (top marketcap)"""
    i = 0
    j = 0

    while i != int(s_coin_number):

        for element in Get_Desired_Values(i, l_market_values):

            element = Element_Modifier(element, j)
            print (Make_a_Frame(element, l_max_length[j]), end='') #Display values in a row
            j += 1

        print ("\r") #New line when all values for a coin are displayed

        i += 1
        j = 0

    print ("=" * (sum(l_max_length) - 26))

def Display_Header_Portfolio(l_max_length):
    """Display first line of the portfolio board which explains columns"""

    print ("=" * (sum(l_max_length)-26))
    print ("\n"+Make_a_Frame("Your portfolio",16)) #Fixed length
    l_categories = [
                    "Name",
                    "Symbol",
                    "Quantity",
                    "% Holdings",
                    "BTC Value",
                    "USD Value",
                    "EUR Value"]

    print ("=" * (len(l_categories)*16))

    i = 0
    for cat in l_categories:
        print (Make_a_Frame(cat,15),end='')
        i += 1

    print ("\r")
    print ("=" * (len(l_categories)*16)) # Utiliser qu'une fonction pour display les headers.

def Display_Portfolio_Board(l_l_proper_values_coins):

    for l_coin in l_l_proper_values_coins:
        for element in l_coin:
            print (Make_a_Frame(element,15),end='')
        print ("\r")
    print ("=" * 112)

def Element_Modifier(s_element,i_list_index):
    """"Apply changes to some element of the board"""

    if i_list_index == 3: #BTC Price
        if len(s_element) != 10:
            s_element = s_element + "0" * (10 - len(s_element))

    if i_list_index == 4: #USD Price
        s_element = str(round(float(s_element), 3))

    if i_list_index == 5: #EUR Price
        s_element = str(round(float(s_element), 3))

    if i_list_index == 6: #Marketcap
        s_element = str(round(float(s_element) / 10**6, 3))

    if i_list_index == 7 or i_list_index == 8 or i_list_index == 9: #Changes
        s_element = Colorize(s_element)

    #ifififififififififif
    return s_element

def Get_Portfolio_Values(o_portfolio_file,i_coin_number,l_market_values,l_max_length):
    """Get coins and their values in portfolio file"""
    
    re_exclude = re.compile("\#")
    #You can exclude a currency in your portfolio by adding a # before the name
    #(e.g : "#Ripple":100)
    
    i = 0
    i_rank = 0
    l_l_values_coins_portfolio = []

    try :
        d_portfolio_values = json.load(o_portfolio_file)
    except :
        print ("Your portfolio file is not formatted correctly.")
        print ("May be a comma at the end, try to remove it")
        print ("The portfolio file has to be formatted like this : ")
        print ("{\"EUR Invested\":XXX,\"CoinName\":XXX, ..., \"Bitcoin\":18}")
        sys.exit(0)

    for s_currency, f_quantity in d_portfolio_values.items():
        
        if re.match(re_exclude,s_currency):
            continue
            
        f_quantity = float(f_quantity) #Some values are integers

        while i != i_coin_number:

            if s_currency == str(Get_Desired_Values(i,l_market_values)[1]):
                #If the coin is already displayed
                b_isnew = False
                i_rank = i
                break

            else :
                b_isnew = True

            i += 1
        i = 0

        if s_currency == "EUR Invested":
            f_fiat_investment = f_quantity
            pass

        elif b_isnew == True:
            n = 0
            # Coins that aren't displayed yet
            # Need to call the API to retrieve their values
            l_new_coin_values = Get_Desired_Values(0, Get_JSON("https://api.coinmarketcap.com/v1/ticker/" + s_currency + "?convert=EUR"))

            # Display in main board coins in portfolio that aren't displayed yet
            for s_values in l_new_coin_values:
                s_values = Element_Modifier(s_values,n)
                print (Make_a_Frame(s_values,l_max_length[n]), end='')
                n += 1
            print ("\r")

            l_new_coin_values.append(f_quantity) # Add quantity of a coin in list

            # Add list of values of a coin into a general list
            l_l_values_coins_portfolio.append(l_new_coin_values)

        elif b_isnew == False:
            # Coins that are already displayed
            l_displayed_coins = Get_Desired_Values(i_rank, l_market_values)
            l_displayed_coins.append(f_quantity)
            l_l_values_coins_portfolio.append(l_displayed_coins)

    o_portfolio_file.close()

    for l_coin_values in l_l_values_coins_portfolio:

        l_coin_values.pop(0) # Remove undesired values got from Get_Desired_Values()
        l_coin_values.pop(5)
        l_coin_values.pop(5)
        l_coin_values.pop(5)
        l_coin_values.pop(5)

        l_coin_values.insert(2,l_coin_values[5]) # Copy f_quantity to another index
        l_coin_values.pop() # Remove duplicate f_quantity


    # list of lists
    return l_l_values_coins_portfolio, f_fiat_investment

def Process_Portfolio_Values(l_l_values_coins_portfolio):
    """Process portfolio values to get total values, % holdings ..."""

    # Variables to return
    l_l_proper_values_coins = []
    f_total_BTC_value = 0.0
    f_total_USD_value = 0.0
    f_total_EUR_value = 0.0

    for l_coin_values in l_l_values_coins_portfolio:

        s_BTC_value = round(l_coin_values[2] * float(l_coin_values[3]), 8)
        i_len_s_BTC_value = len(str(s_BTC_value))

        if i_len_s_BTC_value != 10 :
            # To have satoshi value (8 decimals)
            s_BTC_value = str(s_BTC_value) + "0" * (10 - i_len_s_BTC_value)

        f_USD_value = l_coin_values[2] * float(l_coin_values[4])
        f_USD_value = round(f_USD_value,2)

        f_EUR_value = l_coin_values[2] * float(l_coin_values[5])
        f_EUR_value = round(f_EUR_value,2)

        # Calculate portfolio total value
        f_total_BTC_value = f_total_BTC_value + float(s_BTC_value)
        f_total_USD_value = f_total_USD_value + f_USD_value
        f_total_EUR_value = f_total_EUR_value + f_EUR_value

        # Put right values at right places
        l_coin_values[2] = str(l_coin_values[2])
        l_coin_values[4] = str(s_BTC_value)
        l_coin_values[5] = str(f_USD_value)
        l_coin_values.append(str(f_EUR_value))

    for l_coin_values in l_l_values_coins_portfolio:

        # Calculate in % representation of a coin in total portfolio value
        s_coin_holding = round((float(l_coin_values[5]) / f_total_USD_value) * 100 , 2)
        l_coin_values[3] = str(s_coin_holding)

        l_l_proper_values_coins.append(l_coin_values)

    return l_l_proper_values_coins, f_total_BTC_value, f_total_USD_value, f_total_EUR_value

def Random_Sentence():
    """Pick a random sentence to display in portfolio summary"""
    """Feel free to add some, max 20 chars long"""

    l_words = [
                    "Are you broke ?",
                    "Are you rich ?",
                    "1-800-273-8255",
                    "01 45 39 40 00",
                    "Let's go to Palawan",
                    "Don't cry",
                    "HODL",
                    "Time to sell.",
                    "Buy more",
                    "Shitcoins only",
                    "It's a scam.",
                    "Learn the tech",
                    "Read whitepapers",
                    "We <3 Blockchain",
                    "Amazing script !",
                    "Send me some.",
                    "Satoshi Nakamoto",
                    "Vitalik Buterin",
                    "Hal Finney",
                    "Nick Szabo",
                    "Andreas Antonopoulos"]

    i_rand = randint(0,len(l_words) - 1)

    return l_words[i_rand]

def Portfolio_Summary(t_proper_portfolio_values,f_fiat_investment):
    """Display the summary of your portfolio, to quickly know if you are rich or poor."""

    print ("\r")
    print ("=" * 44)
    print (Make_a_Frame("Portfolio Summary",21) + Make_a_Frame(Random_Sentence(),21))
    print ("=" * 44)

    l_portfolio_summary = []
    d_portfolio_summary = {}
    l_summary_categories = [
                            "Investment",
                            "BTC Value",
                            "USD Value",
                            "EUR Value",
                            "EUR Profit",
                            "%%% Profit"]

    l_portfolio_summary.append(f_fiat_investment)
    l_portfolio_summary.append(round(t_proper_portfolio_values[1],8)) # f_total_BTC_value
    l_portfolio_summary.append(round(t_proper_portfolio_values[2],2)) # f_total_USD_value
    l_portfolio_summary.append(round(t_proper_portfolio_values[3],2)) # f_total_EUR_value

    f_profit = round(l_portfolio_summary[3] - l_portfolio_summary[0],2)
    l_portfolio_summary.append(f_profit)

    f_percentage_profit = round((l_portfolio_summary[3] * 100) / l_portfolio_summary[0] - 100, 2)
    l_portfolio_summary.append(f_percentage_profit)

    i = 0
    for categories in l_summary_categories:
        print (Make_a_Frame(categories,21) + Make_a_Frame(str(l_portfolio_summary[i]),21) ,end='')
        d_portfolio_summary.update({categories:l_portfolio_summary[i]}) # Create a dictionary with these values, to log them.
        print ("\r")
        i += 1

    print ("=" * 44)

    return d_portfolio_summary

def Write_Logs(d_portfolio_summary,s_currentime):
    """Write logs to a txt file of your portfolio summary"""

    #Create a log file in the same directory as the script
    file_log = open(str(os.path.dirname(sys.argv[0])) + "/portfolog.txt", "a+")
    file_log.write(s_currentime + " : " + str(d_portfolio_summary) + "\n")
    file_log.close()

def main(args):
   
    ### Display specific coin ###
    l_max_length = [7, 21, 11, 13, 13, 13, 15, 21, 21, 21] #Max length for each desired values
    s_currentime = Display_Time()
    Display_Header(l_max_length)

    if args.coiname :
        s_coiname = (str(args.coiname)).lower()
        l_specific_values = Get_JSON("https://api.coinmarketcap.com/v1/ticker/"+s_coiname+"/?convert=EUR")
        Display_Main_Board(1,l_specific_values,l_max_length)
        
    ### Main board ###
    if args.number and args.number[0] > 0 :
        s_coin_number = str(args.number[0])
    else :
        s_coin_number = "15"

    l_market_values = Get_JSON("https://api.coinmarketcap.com/v1/ticker/?convert=EUR&limit=" + s_coin_number)
    Display_Main_Board(s_coin_number,l_market_values,l_max_length)

    
    ### Portfolio board ###
    if args.file :

        l_l_portfolio_values = Get_Portfolio_Values(args.file, int(s_coin_number), l_market_values, l_max_length)
        Display_Header_Portfolio(l_max_length)

        t_proper_portfolio_values = Process_Portfolio_Values(l_l_portfolio_values[0])
        Display_Portfolio_Board(t_proper_portfolio_values[0])

        d_portfolio_summary = Portfolio_Summary(t_proper_portfolio_values,l_l_portfolio_values[1])
        Write_Logs(d_portfolio_summary,s_currentime)

    return 0

if __name__ == "__main__":
   main(Argument_Parser())

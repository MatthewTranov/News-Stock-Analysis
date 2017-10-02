import datetime
import os
import re

import math
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import matplotlib.pyplot as plt

# get list of stock tickers and names
def get_stock_list(excel_file_path):

    # all sheets get loaded into dataframe
    df_all_sheets = pd.ExcelFile(excel_file_path)
    # Loads a single sheet into a DataFrame by name
    excel_df = df_all_sheets.parse('companylist')
    # gets number of rows ([1] would be number of columns)
    rows = excel_df.shape[0]
    # convert into array
    excel_df = excel_df.values

    # create lists for dynamic storage of names and tickers
    ticker_list = []
    name_list = []
    for x in range(0, rows):
        ticker_list.append(excel_df[x][0])
        name_list.append(excel_df[x][1])

    return ticker_list, name_list


# get last hour of news
def last_hour_news(search):
    URL = 'https://www.google.ca/search?safe=off&biw=927&bih=760&tbs=qdr%3Ah&tbm=nws&q={}&oq={}&gs_l=psy-ab'

    # replaces spaces in URL with +
    search_in_url = search.replace(" ", "+")

    # tells server who is doing the search
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }

    # get html code from the google search
    try:
        response = requests.get(URL.format(search_in_url, search_in_url), headers=headers)
    except:
        return []

    # create a BeautifulSoup object to use beautifulsoup methods
    soup = BeautifulSoup(response.text, "html.parser")

    # print(soup.prettify())

    # create list for dynamic storage of titles
    title_list = []
    descriptions_list = []

    # check if there are any results (empty strings are false)
    there_are_no_results = soup.findAll("div", {"class": "mnr-c"})

    if there_are_no_results:
        print('there are no results')
        return [], []
    else:

        titles = soup.findAll("a", class_="l _PMs")
        titles_soup = BeautifulSoup(str(titles), "html.parser")

        for line in titles_soup.find_all('a'):
            title_list.append(line.text)

        descriptions = soup.findAll("div", {"class": "st"})
        descriptions_soup = BeautifulSoup(str(descriptions), "html.parser")

        for line in descriptions_soup.find_all('div'):
            descriptions_list.append(line.text)

        return title_list, descriptions_list


# get current price
def current_price(ticker):
    URL = 'https://finance.yahoo.com/quote/{}?p={}'

    # tells server who is doing the search
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }


    # get html code from the google search
    try:
        response = requests.get(URL.format(ticker,ticker), headers=headers)
    except:
        return 'not found'
    # create a BeautifulSoup object to use beautifulsoup methods
    soup = BeautifulSoup(response.text, "html.parser")


    price = soup.find("span", {"class": "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"}) # current stock price tag
    if price is None:
        return 'not found'
    else:
        try:
            return float(price.text)
        except:
            return 'not found'


# get last hour of news and current price for all stocks
def get_news_and_price_every_hour_of_trading_day(name_list,ticker_list):
    now = datetime.now()
    endtime = now.replace(hour=16, minute=30, second=0)
    next_search_hour = 10
    while (datetime.now() < endtime):
        if next_search_hour == datetime.now().hour:
            date = datetime.now()
            file_path_prices = 'C:/Users/Matthew/Documents/Excel/price files/{}.{}.{} {}.{}.txt'.format(date.day, date.month, date.year, date.hour, date.minute)
            file_path_prices_backup = 'C:/Users/Matthew/Documents/Excel/price files backup/{}.{}.{} {}.{}.txt'.format(date.day, date.month, date.year, date.hour, date.minute)

            write_last_hour_news_and_price_for_all_stocks(file_path_prices, file_path_prices_backup, name_list, ticker_list)
            next_search_hour += 1
        else:
            time.sleep(60)


# writes last hour news and price of all stocks in list and writes them in a text file
def write_last_hour_news_and_price_for_all_stocks(file_path, file_path_backup, name_list,ticker_list):
    textfile = open(file_path, 'w', encoding='utf-8')
    textfile_backup = open(file_path_backup, 'w', encoding='utf-8')
    for x in range(0, len(name_list)):
        stock_name = name_list[x].lower()
        stock_name_list = cleanup_name_into_list(stock_name)

        time.sleep(2)
        title_list, description_list = last_hour_news(stock_name)

        price_bid_ask = current_price_bid_and_ask(ticker_list[x])
        price_bid_ask_backup = current_price_bid_and_ask_backup(ticker_list[x])

        price = price_bid_ask[0]
        bid = price_bid_ask[1]
        ask = price_bid_ask[2]

        backup_price = price_bid_ask_backup[0]
        backup_bid = price_bid_ask_backup[1]
        backup_ask = price_bid_ask_backup[2]

        if (backup_price != 'not found'):
            print("stock # " + str(x) + ': ' + stock_name)
            print(str(backup_price))
            print(backup_bid)
            print(backup_ask)
            print(ticker_list[x])

            textfile_backup.write(str(backup_price))
            textfile_backup.write(os.linesep)
            textfile_backup.write(backup_bid)
            textfile_backup.write(os.linesep)
            textfile_backup.write(backup_ask)
            textfile_backup.write(os.linesep)
            textfile_backup.write(ticker_list[x])
            textfile_backup.write(os.linesep)

            for y in range(0, len(title_list)):
                # removes non letters from google title
                current_title = re.sub("[^\w]", "", title_list[y].lower())

                # checks if a word from the stock name is found in the title
                if any(word in current_title for word in stock_name_list):

                    textfile_backup.write(title_list[y])
                    textfile_backup.write(os.linesep)

                    textfile_backup.write('    ' + description_list[y])
                    textfile_backup.write(os.linesep)

            print()

        else:
            print('huh')

        if (price != 'not found'):
            print("stock # " + str(x) + ': ' + stock_name)
            print(str(price))
            print(bid)
            print(ask)
            print(ticker_list[x])

            textfile.write(str(price))
            textfile.write(os.linesep)
            textfile.write(bid)
            textfile.write(os.linesep)
            textfile.write(ask)
            textfile.write(os.linesep)
            textfile.write(ticker_list[x])
            textfile.write(os.linesep)

            for y in range(0, len(title_list)):
                # removes non letters from google title
                current_title = re.sub("[^\w]", "", title_list[y].lower())

                # checks if a word from the stock name is found in the title
                if any(word in current_title for word in stock_name_list):
                    print(title_list[y])

                    textfile.write(title_list[y])
                    textfile.write(os.linesep)

                    print('    ' + description_list[y])

                    textfile.write('    ' + description_list[y])
                    textfile.write(os.linesep)

                    print()
        else:
            print('huh')




    textfile.close()
    textfile_backup.close()




# converts company names into a list of words
def cleanup_name_into_list(string):
    noPunctuation_list = re.sub("[^\w]", " ", string.lower()).split()
    filter_words = ['inc', 'ltd', 'plc', 'limited', 'corp', 'corporation', 'lp', 'llc']
    return list(set(noPunctuation_list) - set(filter_words))


# writes file with percent change from price found in all files to next hour price
def compare_price_and_write_new_file_for_all_files(directory_read):
    file_list,date_list = get_all_txt_files_in_order(directory_read)
    final_bid_list,final_ask_list = [],[]

    for x in range (0,len(file_list)-1):
        file_path_changes_backup = 'C:/Users/Matthew/Documents/Excel/% change files backup/{}.{}.{} {}.{}.txt'.format(date_list[x].day, date_list[x].month, date_list[x].year, date_list[x].hour, date_list[x].minute)
        file_path_changes = 'C:/Users/Matthew/Documents/Excel/% change files/{}.{}.{} {}.{}.txt'.format(date_list[x].day, date_list[x].month, date_list[x].year, date_list[x].hour, date_list[x].minute)
        if (date_list[x].day == date_list[x+1].day): # makes sure the changes occur on the same day
            #compare_2_text_files_and_write_percent_change_file(file_list[x],file_list[x+1], file_path_changes)
            #compare_2_text_files_and_write_percent_change_file_of_next_hour(file_list[x], file_list[x + 1], file_path_changes)
            bid_list, ask_list = compare_2_text_files_and_write_percent_change_file_with_bid_and_ask_of_next_hour_backup(file_list[x], file_list[x + 1], file_path_changes_backup)

            #bid_list, ask_list = compare_2_text_files_and_write_percent_change_file_with_bid_and_ask_of_next_hour(file_list[x], file_list[x + 1], file_path_changes)
            final_bid_list += bid_list
            final_ask_list += ask_list
    return final_bid_list, final_ask_list


# writes file with percent change from price found in 2 files to next hour price
def compare_2_text_files_and_write_percent_change_file(file_1,file_2, write_file):
    old_price_list = []
    line_list1 = []
    line_list2 = []
    final_line_list = []
    ticker_list1 = []


    # reads files into 2 lists

    readFile1 = open(file_1, 'r', encoding='utf-8')
    lines1 = readFile1.readlines()

    readFile2 = open(file_2, 'r', encoding='utf-8')
    lines2 = readFile2.readlines()

    for x in range(0, len(lines1)):
        if x % 2 == 0:
            line_list1.append((lines1[x].strip(os.linesep)))
    for x in range(0, len(lines2)):
        if x % 2 == 0:
            line_list2.append((lines2[x].strip(os.linesep)))


    # gets prices and tickers and put them into lists

    for y in range (0, len(line_list1)):
        try:
            old_price_list.append(float(line_list1[y]))
            ticker_list1.append(line_list1[y+1])
        except ValueError:
            pass

    # finds stocks change in price

    found_ticker = False

    for y in range(0, len(line_list2)):
        try:
            now_price = float(line_list2[y])
            current_ticker = (line_list2[y + 1])

            if current_ticker in ticker_list1:
                current_index = ticker_list1.index(current_ticker)
                past_price = old_price_list[current_index]
                final_line_list.append(round((now_price - past_price) / past_price * 100, 2))
                found_ticker = True
            else:
                found_ticker = False

        except:
            if found_ticker and line_list2[y] != current_ticker:
                final_line_list.append(line_list2[y])

    textfile = open(write_file, 'w', encoding='utf-8')
    for x in range(0, len(final_line_list)):
        textfile.write(str(final_line_list[x]))
        textfile.write(os.linesep)
    textfile.close()


def compare_2_text_files_and_write_percent_change_file_of_next_hour(file_1,file_2, write_file):
    new_price_list = []
    line_list1 = []
    line_list2 = []
    final_line_list = []
    ticker_list1 = []


    # reads files into 2 lists

    readFile1 = open(file_1, 'r', encoding='utf-8')
    lines1 = readFile1.readlines()

    readFile2 = open(file_2, 'r', encoding='utf-8')
    lines2 = readFile2.readlines()

    for x in range(0, len(lines1)):
        if x % 2 == 0:
            line_list1.append((lines1[x].strip(os.linesep)))
    for x in range(0, len(lines2)):
        if x % 2 == 0:
            line_list2.append((lines2[x].strip(os.linesep)))


    # gets prices and tickers and put them into lists

    for y in range (0, len(line_list2)):
        try:
            new_price_list.append(float(line_list2[y]))
            ticker_list1.append(line_list2[y+1])
        except ValueError:
            pass

    # finds stocks change in price

    found_ticker = False

    for y in range(0, len(line_list1)):
        try:
            old_price = float(line_list1[y])
            current_ticker = (line_list1[y + 1])

            if current_ticker in ticker_list1:
                current_index = ticker_list1.index(current_ticker)
                new_price = new_price_list[current_index]
                final_line_list.append(round((new_price - old_price) / old_price * 100, 2))
                found_ticker = True
            else:
                found_ticker = False

        except:
            if found_ticker and line_list1[y] != current_ticker:
                final_line_list.append(line_list1[y])

    textfile = open(write_file, 'w', encoding='utf-8')
    for x in range(0, len(final_line_list)):
        textfile.write(str(final_line_list[x]))
        textfile.write(os.linesep)
    textfile.close()


def compare_2_text_files_and_write_percent_change_file_with_bid_and_ask_of_next_hour_backup(file_1,file_2, write_file):
    new_price_list = []
    bid_list = []
    ask_list = []
    line_list1 = []
    line_list2 = []
    final_line_list = []
    ticker_list1 = []
    final_bid_list = []
    final_ask_list = []

    # reads files into 2 lists

    readFile1 = open(file_1, 'r', encoding='utf-8')
    lines1 = readFile1.readlines()

    readFile2 = open(file_2, 'r', encoding='utf-8')
    lines2 = readFile2.readlines()

    for x in range(0, len(lines1)):
        if x % 2 == 0:
            line_list1.append((lines1[x].strip(os.linesep)))
    for x in range(0, len(lines2)):
        if x % 2 == 0:
            line_list2.append((lines2[x].strip(os.linesep)))

    # gets prices and tickers and put them into lists

    for y in range(0, len(line_list2)):
        try:

            bid = float(line_list2[y + 1])
            ask = float(line_list2[y + 2])

            if bid < ask:
                new_price_list.append(float(line_list2[y]))
                bid_list.append(float(line_list2[y + 1].split()[0]))
                ask_list.append(float(line_list2[y + 2].split()[0]))
                ticker_list1.append(line_list2[y + 3])
        except:
            pass

    # finds stocks change in price

    found_ticker = False

    for y in range(0, len(line_list1)):
        try:
            past_price = float(line_list1[y])
            last_price_line = y
            bid = (float(line_list1[y + 1]))
            ask = (float(line_list1[y + 2]))
            current_ticker = (line_list1[y + 3])

            if current_ticker in ticker_list1 and bid < ask:
                current_index = ticker_list1.index(current_ticker)
                bid_price = bid_list[current_index]

                if (abs(round((bid_price - ask) / ask * 100, 3)) > 5):
                    final_line_list.append(round((new_price_list[current_index] - past_price) / past_price * 100, 2))
                    if abs(round((new_price_list[current_index] - past_price) / past_price * 100, 2)) > 30:
                        print(current_ticker)
                        print(past_price)
                        print(new_price_list[current_index])
                else:
                    final_line_list.append(round((bid_price - ask) / ask * 100, 2))

                final_bid_list.append(bid_price)
                final_ask_list.append(ask)
                found_ticker = True
            else:
                found_ticker = False

        except:
            if found_ticker and y - last_price_line > 2:
                final_line_list.append(line_list1[y])

    textfile = open(write_file, 'w', encoding='utf-8')
    for x in range(0, len(final_line_list)):
        textfile.write(str(final_line_list[x]))
        textfile.write(os.linesep)
    textfile.close()

    return final_bid_list, final_ask_list



def get_biggest_changes(file_path_list,bid_list,ask_list):

    change_list = []
    file_name_list = []
    ticker_list = []

    for i in range(0, len(file_path_list)):
        line_list = []
        readFile = open(file_path_list[i], 'r', encoding='utf-8')
        lines = readFile.readlines()

        for j1 in range(0, len(lines)):
            if j1 % 2 == 0:
                line_list.append((lines[j1].strip(os.linesep)))

        for j2 in range(0, len(line_list)):
            try:
                change_list.append(float(line_list[j2]))
                ticker_list.append(line_list[j2 + 1])
                if abs(float(line_list[j2])) > 10:
                    print(file_path_list[i])
                    print(line_list[j2])
                    print(line_list[j2 + 1])


            except ValueError:
                pass

    #change_list,bid_list,ask_list,ticker_list = zip(*sorted(zip(change_list, bid_list, ask_list, ticker_list), reverse=True, key=lambda x: x[0]))
    change_list, ticker_list = zip(*sorted(zip(change_list, ticker_list), reverse=True, key=lambda x: x[0]))


    for i in range(0, len(change_list)):
        print(change_list[i])
        print(ticker_list[i])



# sorts files by date
def get_all_txt_files_in_order(directory):
            file_list = []
            time_stamp_list = []
            dates = []
            for file in os.listdir(directory):
                if file.endswith(".txt"):
                    # get the first number in the list which is the day
                    date_list = re.sub("[^\w]", " ", file.lower()).split()
                    file_date = datetime(int(date_list[2]), int(date_list[1]), int(date_list[0]), int(date_list[3]),
                                         int(date_list[4]))
                    dates.append(file_date)
                    time_stamp_list.append((int(time.mktime(file_date.timetuple()))))

                    file_list.append(os.path.join(directory, file))

            time_stamp_list, file_list, dates = zip(
                *sorted(zip(time_stamp_list, file_list, dates), reverse=False, key=lambda x: x[0]))

            return file_list, dates


# get # of word occurrences and the average stock change when they occur for all files
def get_words_and_changes_from_list(file_path_list):
    word_list = []
    word_occurrences = []
    total_change = []
    average_change = []
    current_change = 0
    stock_name_word_list =[]

    #for i in range (0,len(name_list)):
    #    current_stock_name_list = cleanup_name_into_list(name_list[i])
    #    for j in range (0,len(current_stock_name_list)):
    #        if not current_stock_name_list[j] in stock_name_word_list:
    #            stock_name_word_list.append(current_stock_name_list[j])
#
    #for i in range (0, len(ticker_list)):
    #    stock_name_word_list.append(ticker_list[i].lower())





    for i in range (len(file_path_list)):
        line_list = []
        readFile = open(file_path_list[i], 'r', encoding='utf-8')
        lines = readFile.readlines()
        for j1 in range(len(lines)):
            if j1 % 2 == 0:
                line_list.append((lines[j1].strip(os.linesep)))

        for j in range(len(line_list)):
            try:
                current_change = float(line_list[j])
            except ValueError:
                current_words = re.sub("[^\w]", " ", line_list[j].lower()).split()
                for x in range(len(current_words)):
                    try:
                        current_index = word_list.index(current_words[x])
                        word_occurrences[current_index] += 1
                        total_change[current_index] += current_change
                    except:
                        word_list.append(current_words[x])
                        word_occurrences.append(1)
                        total_change.append(current_change)

    for x in range(0, len(word_list)):
        average_change.append(total_change[x] / word_occurrences[x])

    word_list, word_occurrences, average_change = zip(
        *sorted(zip(word_list, word_occurrences, average_change), reverse=True, key=lambda x: x[2]))

    for x in range(0, len(word_list)):
        if (word_occurrences[x] > 30 and not word_list[x] in stock_name_word_list):
            print('word: {}'.format(word_list[x]))
            print('occurances: {}'.format(word_occurrences[x]))
            print('average: {}'.format(round(average_change[x], 2)))
            print('')



    while True:
        find = input('Search for stories with word: ')
        if find == 'exit':
            break
        for i in range(0, len(file_path_list)):
            with open(file_path_list[i], 'r', encoding='utf-8') as inF:
                for line in inF:
                    try:
                        current_change = float(line)
                    except:
                        noPunctuation_list = re.sub("[^\w]", " ", line.lower()).split()
                        if find in noPunctuation_list:
                            print (file_path_list[i])
                            print (current_change)
                            print (line)


def price_graph_day (file_path_list, date_list):
    while True:
        ticker = input('ticker: ')
        day_chosen = int(input('day: '))
        price_list = []
        hour_list = []
        for i in range(0,len(date_list)):
            if date_list[i].day == day_chosen:
                with open(file_path_list[i], 'r', encoding='utf-8') as inF:
                    for line in inF:
                        try:
                            price = float(line)
                        except ValueError:
                            if (line.strip(os.linesep)).lower() == ticker.lower():
                                price_list.append(price)
                                hour_list.append(date_list[i].hour)
        plt.plot(hour_list, price_list)
        plt.ylabel('price')
        plt.xlabel('hour')
        plt.show()


def price_graph_all (file_path_list, date_list):
    while True:
        ticker = input('ticker: ')
        day_chosen = int(input('day: '))
        price_list = []
        hour_list = []

        for i in range(0,len(date_list)):
            if date_list[i].day == day_chosen:
                with open(file_path_list[i], 'r', encoding='utf-8') as inF:
                    for line in inF:
                        try:
                            price = float(line)
                        except ValueError:
                            if (line.strip(os.linesep)).lower() == ticker.lower():
                                price_list.append(price)
                                hour_list.append(date_list[i].hour)

        plt.plot(hour_list, price_list)
        plt.ylabel('price')
        plt.xlabel('hour')
        plt.show()



def change_with_no_words_vs_words (file_path_list):
    total_changes_with_words = 0
    count_changes_with_words = 0
    total_changes_with_no_words = 0
    count_changes_with_no_words = 0

    found_word = False
    line_list = []


    for i in range(0, len(file_path_list)):
        readFile = open(file_path_list[i], 'r', encoding='utf-8')
        lines = readFile.readlines()

        for x in range(0, len(lines)):
            if x % 2 == 0:
                line_list.append((lines[x].strip(os.linesep)))

        for j in range(0, len(line_list)):
            try:
                current_change = float(line_list[j])
                if found_word:
                    total_changes_with_words += current_change
                    count_changes_with_words += 1
                else:
                    total_changes_with_no_words += current_change
                    count_changes_with_no_words += 1
                found_word = False
                print
            except ValueError:
                found_word = True


    print('average no words: {}'.format(round(total_changes_with_no_words/count_changes_with_no_words, 2)))
    print('number no words: {}'.format(count_changes_with_no_words))
    print('average words: {}'.format(round(total_changes_with_words/count_changes_with_words, 2)))
    print('number words: {}'.format(count_changes_with_words))


# gets all text files in a file
def get_all_txt_files(directory):
    file_list = []
    for file in os.listdir(directory):
        if file.endswith(".txt"):
            file_list.append(os.path.join(directory, file))

    return file_list


# returns current stock price, ask, and ,bid from yahoo
def current_price_bid_and_ask(ticker):

    price_bid_ask = ['not found', 'not found', 'not found']

    URL = 'https://finance.yahoo.com/quote/{}?p={}'

    # tells server who is doing the search
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    }

    # get html code from the google search
    try:
        response = requests.get(URL.format(ticker,ticker), headers=headers)
    except:
        return price_bid_ask
    # create a BeautifulSoup object to use beautifulsoup methods
    soup = BeautifulSoup(response.text, "html.parser")


    price = soup.find("span", {"class": "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"})  # current stock price tag
    if price is None:
        pass
    else:
        try:
            price_bid_ask[0] = float(price.text)
        except:
            pass

    span_class = soup.find_all("span", {"class": "Trsdu(0.3s)"})  # current stock price tag
    for i in range(len(span_class)):
        if 'x' in span_class[i].text:
            if price_bid_ask[1] == 'not found':
                price_bid_ask[1] = span_class[i].text
            else:
                price_bid_ask[2] = span_class[i].text

    return price_bid_ask


def current_price_bid_and_ask_backup(ticker):
    price_bid_ask = ['not found', 'not found', 'not found']

    try:
        URL = 'https://web.tmxmoney.com/quote.php?qm_symbol={}:US'

        # tells server who is doing the search
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }


        response = requests.get(URL.format(ticker), headers=headers)
        # create a BeautifulSoup object to use beautifulsoup methods
        soup = BeautifulSoup(response.text, "html.parser")

        price = soup.find("div", {"class": "quote-price priceLarge"})  # current stock price tag

        price_bid_ask[0] = price.text.split()[1]

        span_class = soup.find_all("td", {"class": ""})  # current stock price tag
        for i in range(len(span_class)):

            if 'Bid:' in span_class[i].text and 'High:' in span_class[i].text:
                span_list = (span_class[i].text.split())
                for j in range(len(span_list)):
                    if span_list[j] == 'Bid:':
                        price_bid_ask[1] = span_list[j + 1]
                        break
            elif 'Ask:' in span_class[i].text and 'Low:' in span_class[i].text:
                span_list = (span_class[i].text.split())
                for j in range(len(span_list)):
                    if span_list[j] == 'Ask:':
                        price_bid_ask[2] = span_list[j+1]
                        break
        return price_bid_ask
    except:
        return price_bid_ask


def compare_2_text_files_and_write_percent_change_file_with_bid_and_ask (file_1, file_2, write_file):
    old_price_list = []
    line_list1 = []
    line_list2 = []
    final_line_list = []
    ask_list = []
    bid_list = []
    ticker_list1 = []


    # reads files into 2 lists

    readFile1 = open(file_1, 'r', encoding='utf-8')
    lines1 = readFile1.readlines()

    readFile2 = open(file_2, 'r', encoding='utf-8')
    lines2 = readFile2.readlines()

    for x in range(0, len(lines1)):
        if x % 2 == 0:
            line_list1.append((lines1[x].strip(os.linesep)))
    for x in range(0, len(lines2)):
        if x % 2 == 0:
            line_list2.append((lines2[x].strip(os.linesep)))


    # gets prices and tickers and put them into lists

    for y in range (0, len(line_list1)):
        try:
            old_price_list.append(float(line_list1[y]))
            bid_list.append(float(line_list1[y+1].split()[0]))
            ask_list.append(float(line_list1[y+2].split()[0]))
            ticker_list1.append(line_list1[y+3])
        except:
            pass

    # finds stocks change in price

    found_ticker = False

    for y in range(0, len(line_list2)):
        try:
            now_price = float(line_list2[y])
            last_price_line = y
            bid = (float(line_list2[y + 1].split()[0]))
            ask = (float(line_list2[y + 2].split()[0]))
            current_ticker = (line_list2[y + 3])

            if current_ticker in ticker_list1:
                current_index = ticker_list1.index(current_ticker)
                ask_price = ask_list[current_index]
                final_line_list.append(round((bid - ask_price) / ask_price * 100, 2))
                found_ticker = True
            else:
                found_ticker = False

        except:
            if found_ticker and y - last_price_line > 2:
                final_line_list.append(line_list2[y])

    textfile = open(write_file, 'w', encoding='utf-8')
    for x in range(0, len(final_line_list)):
        textfile.write(str(final_line_list[x]))
        textfile.write(os.linesep)
    textfile.close()


def compare_2_text_files_and_write_percent_change_file_with_bid_and_ask_of_next_hour (file_1, file_2, write_file):
    new_price_list = []
    bid_list = []
    ask_list = []
    line_list1 = []
    line_list2 = []
    final_line_list = []
    ticker_list1 = []
    final_bid_list = []
    final_ask_list = []

    # reads files into 2 lists

    readFile1 = open(file_1, 'r', encoding='utf-8')
    lines1 = readFile1.readlines()

    readFile2 = open(file_2, 'r', encoding='utf-8')
    lines2 = readFile2.readlines()

    for x in range(0, len(lines1)):
        if x % 2 == 0:
            line_list1.append((lines1[x].strip(os.linesep)))
    for x in range(0, len(lines2)):
        if x % 2 == 0:
            line_list2.append((lines2[x].strip(os.linesep)))

    # gets prices and tickers and put them into lists

    for y in range(0, len(line_list2)):
        try:

            bid = float(line_list2[y + 1].split()[0])
            ask = float(line_list2[y + 2].split()[0])

            if bid < ask:
                new_price_list.append(float(line_list2[y]))
                bid_list.append(float(line_list2[y+1].split()[0]))
                ask_list.append(float(line_list2[y+2].split()[0]))
                ticker_list1.append(line_list2[y+3])
        except:
            pass

    # finds stocks change in price

    found_ticker = False

    for y in range(0, len(line_list1)):
        try:
            past_price = float(line_list1[y])
            last_price_line = y
            bid = (float(line_list1[y + 1].split()[0]))
            ask = (float(line_list1[y + 2].split()[0]))
            current_ticker = (line_list1[y + 3])

            if current_ticker in ticker_list1 and bid < ask:
                current_index = ticker_list1.index(current_ticker)
                bid_price = bid_list[current_index]

                if(abs(round((bid_price - ask) / ask * 100, 3))>5):
                    final_line_list.append(round((new_price_list[current_index] - past_price) / past_price * 100, 2))
                    if abs(round((new_price_list[current_index] - past_price) / past_price * 100, 2))>30:
                        print(current_ticker)
                        print(past_price)
                        print(new_price_list[current_index])
                else:
                    final_line_list.append(round((bid_price - ask) / ask * 100, 2))

                final_bid_list.append(bid_price)
                final_ask_list.append(ask)
                found_ticker = True
            else:
                found_ticker = False

        except:
            if found_ticker and y - last_price_line > 2:
                final_line_list.append(line_list1[y])

    textfile = open(write_file, 'w', encoding='utf-8')
    for x in range(0, len(final_line_list)):
        textfile.write(str(final_line_list[x]))
        textfile.write(os.linesep)
    textfile.close()

    return final_bid_list,final_ask_list


def main_method():

    excel_file_with_stocks_path = 'C:/Users/Matthew/Documents/Excel/clean-NYSE.xlsx'
    change_file_folder_path = 'C:/Users/Matthew/Documents/Excel/% change files'
    price_file_path = 'C:/Users/Matthew/Documents/Excel/price files'
    price_file_path_backup = 'C:/Users/Matthew/Documents/Excel/price files backup'
    change_file_folder_path_backup = 'C:/Users/Matthew/Documents/Excel/% change files backup'

    ticker_list, name_list = get_stock_list(excel_file_with_stocks_path)
    change_file_list = get_all_txt_files(change_file_folder_path_backup)
    file_list, date_list = get_all_txt_files_in_order(price_file_path)

    #get_news_and_price_every_hour_of_trading_day(name_list,ticker_list)

    bid_list,ask_list = compare_price_and_write_new_file_for_all_files('C:/Users/Matthew/Documents/Excel/price files backup')

    #get_words_and_changes_from_list(change_file_list)

    #change_with_no_words_vs_words(change_file_list)
    get_biggest_changes(change_file_list,bid_list,ask_list)
    #price_graph_day(file_list, date_list)


    # market data distribution platforms (ie Bloomberg, Reuters & Exegy)



main_method()



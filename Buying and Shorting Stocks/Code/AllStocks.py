import robin_stocks.robinhood as rh
import pandas_market_calendars as mcal
import json
import csv
from datetime import datetime, timedelta
import operator
from random import randint
import sys
import math
from scipy import stats
import smtplib
import schedule
import time

#   https://www.barchart.com/etfs-funds/quotes/AMLP/price-history/historical

#   INSTANTIATIONS
stonks = []
one_stonk = []
operations = []
progression = []
correlation_log = []
percent_correct = [0, 0]
number_range = [0, 0]
stocks = []
maximumCompanies = 0

#   Parameters for dates
TOTAL_CHANGE = 50
DECIMAL_VALUE = []
FILE_OUTPUT = "AllStocks/(" + str(datetime.today().date()) + ")DecimalSequences.csv"
FILE_TEST = "AllStocks/(" + str(datetime.today().date()) + ")Analysis.csv"
VOLUME = "Temp"
VOLUME_COLUMN = 155
PRICE_COLUMN = 1
GROUPINGS = 5
LIQUIDITY = round(260.67 * 1000)

#   Scheduler Conditions
give_stocks = False
nyse = mcal.get_calendar('NYSE')


def login_robinhood():
    # Robinhood Account Login
    # --------------------------
    content = open('config.json').read()
    config = json.loads(content)
    rh.login(config['robinhood_username'], config['robinhood_password'])
    # --------------------------


def format_stocks_for_analysis():
    with open("AllStocks.csv") as g:
        companies = g.readlines()

    companies = [x.strip() for x in companies]

    last_trading_days = rh.stocks.get_stock_historicals("SPY", interval='day', span='year', bounds='regular')

    number_list = [' ']
    test_day = 1
    while not len(nyse.valid_days(start_date=datetime.today().date() - timedelta(test_day),
                                  end_date=datetime.today().date() - timedelta(test_day))):
        test_day += 1

    valid_trading_day = nyse.valid_days(start_date=datetime.today().date() - timedelta(test_day),
                                        end_date=datetime.today().date() - timedelta(test_day))[0].date()

    if str(last_trading_days[-1]['begins_at'].split('T')[0]) == str(valid_trading_day):
        for i in last_trading_days[-(TOTAL_CHANGE + 20):]:
            number_list.append(i["begins_at"].split("T")[0])
    else:
        for i in last_trading_days[-(TOTAL_CHANGE + 19):]:
            number_list.append(i["begins_at"].split("T")[0])
        number_list.append(valid_trading_day)

    with open("AllStocks/(" + str(datetime.today().date()) + ")Analysis.csv", 'w', 1,
              newline='') as f:
        writer = csv.writer(f)
        writer.writerow(number_list)
        count = 0
        repeat = " "
        for i in companies:
            if 100 * round(count / len(companies), 2) % 10 == 0:
                if repeat != str(100 * round(count / len(companies), 2)):
                    print("Formatting " + str(100 * round(count / len(companies), 2)) + "% Complete")
                    repeat = str(100 * round(count / len(companies), 2))
            count += 1
            percent_difference = [i]
            price = 0
            all_stocks = rh.stocks.get_stock_historicals(str(i), interval='day', span='year', bounds='regular')

            try:
                test_date = str(all_stocks[-1]['begins_at'].split('T')[0])
            except:
                continue

            test_day = 1
            while not len(nyse.valid_days(start_date=datetime.today().date() - timedelta(test_day),
                                          end_date=datetime.today().date() - timedelta(test_day))):
                test_day += 1

            valid_trading_day = nyse.valid_days(start_date=datetime.today().date() - timedelta(test_day),
                                                end_date=datetime.today().date() - timedelta(test_day))[0].date()

            if test_date == str(valid_trading_day):
                for j in all_stocks[-(TOTAL_CHANGE + 21):]:
                    if j is not None:
                        if j != all_stocks[-1]:
                            # Stocks must change in value and have volume of 20000 (money must be .1% or less)
                            if j["low_price"] == j["high_price"] or float(j['volume']) * float(
                                    j['close_price']) < LIQUIDITY:
                                break
                            if price == 0:
                                price = j['close_price']
                            else:
                                try:
                                    percent_difference.append(
                                        100 * ((float(j['close_price']) - float(price)) / (abs(float(price)))))
                                    price = j['close_price']
                                except ZeroDivisionError:
                                    break
                        else:
                            try:
                                percent_difference.append(100 * ((float(rh.get_latest_price(str(i))[0]) -
                                                                  float(all_stocks[-2]['close_price'])) /
                                                                 (abs(float(all_stocks[-2]['close_price'])))))
                                writer.writerow(percent_difference)
                            except:
                                break
                    else:
                        break
            else:
                for j in all_stocks[-(TOTAL_CHANGE + 20):]:
                    if j is not None:
                        if j != all_stocks[-1]:
                            # Stocks must change in value and have volume of 20000 (money must be .1% or less)
                            if j["low_price"] == j["high_price"] or float(j['volume']) * float(
                                    j['close_price']) < 20000:
                                break
                            if price == 0:
                                price = j['close_price']
                            else:
                                try:
                                    percent_difference.append(
                                        100 * ((float(j['close_price']) - float(price)) / (abs(float(price)))))
                                    price = j['close_price']
                                except ZeroDivisionError:
                                    break
                        else:
                            try:
                                percent_difference.append(
                                    100 * ((float(j['close_price']) - float(price)) / (abs(float(price)))))
                                percent_difference.append(100 * ((float(rh.get_latest_price(str(i))[0]) -
                                                                  float(all_stocks[-1]['close_price'])) /
                                                                 (abs(float(all_stocks[-1]['close_price'])))))
                                writer.writerow(percent_difference)
                            except:
                                break
                    else:
                        break

    print("Formatting Complete")


def weekly_options():
    global FILE_TEST
    global FILE_OUTPUT
    global number_range
    global maximumCompanies
    global GROUPINGS

    #   Need this here since the values are changing
    FILE_OUTPUT = "AllStocks/(" + str(datetime.today().date()) + ")DecimalSequences.csv"
    FILE_TEST = "AllStocks/(" + str(datetime.today().date()) + ")Analysis.csv"
    number_range[0] = 7
    number_range[1] = -7
    maximumCompanies = randint(5, 10)
    GROUPINGS = randint(6, 10)


def template(money):
    for addition in range(0, TOTAL_CHANGE):
        stonks.clear()
        one_stonk.clear()
        with open(FILE_TEST, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)

            x = 0

            for line in csv_reader:
                if x >= 1:
                    try:
                        tup1 = ([float(line[1 + addition]), float(line[2 + addition]), float(line[3 + addition]),
                                 float(line[4 + addition]), float(line[5 + addition]),
                                 float(line[6 + addition]), float(line[7 + addition]), float(line[8 + addition]),
                                 float(line[9 + addition]), float(line[10 + addition]),
                                 float(line[11 + addition]), float(line[12 + addition]), float(line[13 + addition]),
                                 float(line[14 + addition]), float(line[15 + addition]),
                                 float(line[16 + addition]), float(line[17 + addition]), float(line[18 + addition]),
                                 float(line[19 + addition]), float(line[20 + addition])])

                        one_stonk.append(tup1)
                        one_stonk.append(float(line[21 + addition]))
                        one_stonk.append(line[0])
                        one_stonk.append(float(line[PRICE_COLUMN]))
                        stonks.append(one_stonk.copy())
                    except:
                        pass

                    one_stonk.clear()
                x += 1
        counter = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
        for i in range(len(stonks)):
            if operations[0](stonks[i][0][19], DECIMAL_VALUE[0]):  # and stonks[i][3] > 500000:  # volume limit
                counter[0].append(stonks[i])
                if operations[1](stonks[i][0][18], DECIMAL_VALUE[1]):
                    counter[1].append(stonks[i])
                    if operations[2](stonks[i][0][17], DECIMAL_VALUE[2]):
                        counter[2].append(stonks[i])
                        if operations[3](stonks[i][0][16], DECIMAL_VALUE[3]):
                            counter[3].append(stonks[i])
                            if operations[4](stonks[i][0][15], DECIMAL_VALUE[4]):
                                counter[4].append(stonks[i])
                                if operations[5](stonks[i][0][14], DECIMAL_VALUE[5]):
                                    counter[5].append(stonks[i])
                                    if operations[6](stonks[i][0][13], DECIMAL_VALUE[6]):
                                        counter[6].append(stonks[i])
                                        if operations[7](stonks[i][0][12], DECIMAL_VALUE[7]):
                                            counter[7].append(stonks[i])
                                            if operations[8](stonks[i][0][11], DECIMAL_VALUE[8]):
                                                counter[8].append(stonks[i])
                                                if operations[9](stonks[i][0][10], DECIMAL_VALUE[9]):
                                                    counter[9].append(stonks[i])
                                                    if operations[10](stonks[i][0][9], DECIMAL_VALUE[10]):
                                                        counter[10].append(stonks[i])
                                                        if operations[11](stonks[i][0][8], DECIMAL_VALUE[11]):
                                                            counter[11].append(stonks[i])
                                                            if operations[12](stonks[i][0][7], DECIMAL_VALUE[12]):
                                                                counter[12].append(stonks[i])
                                                                if operations[13](stonks[i][0][6], DECIMAL_VALUE[13]):
                                                                    counter[13].append(stonks[i])
                                                                    if operations[14](stonks[i][0][5],
                                                                                      DECIMAL_VALUE[14]):
                                                                        counter[14].append(stonks[i])
                                                                        if operations[15](stonks[i][0][4],
                                                                                          DECIMAL_VALUE[15]):
                                                                            counter[15].append(stonks[i])
                                                                            if operations[16](stonks[i][0][3],
                                                                                              DECIMAL_VALUE[16]):
                                                                                counter[16].append(stonks[i])
                                                                                if operations[17](stonks[i][0][2],
                                                                                                  DECIMAL_VALUE[17]):
                                                                                    counter[17].append(stonks[i])
                                                                                    if operations[18](stonks[i][0][1],
                                                                                                      DECIMAL_VALUE[
                                                                                                          18]):
                                                                                        counter[18].append(stonks[i])
                                                                                        if operations[19](
                                                                                                stonks[i][0][0],
                                                                                                DECIMAL_VALUE[19]):
                                                                                            counter[19].append(
                                                                                                stonks[i])

        save = []
        for i in range(len(counter)):
            if len(counter[i]) <= maximumCompanies:
                save = counter[i]
                break

        companies = []
        value = 0
        for i in range(len(save)):
            value += save[i][1]
            companies.append([save[i][2], save[i][3]])
        if len(save) > 0:
            value = value / len(save)

        # print(value)
        # print(companies)
        global stocks
        stocks = companies
        # print(companies)
        # print("Strength: " + str(strength))
        money = money + money * value / 100
        # print(money)
        progression.append(money)
        if value != 0:
            correlation_log.append(math.log(money))
        if money * value / 100 > 0:
            percent_correct[0] += 1
        elif money * value / 100 < 0:
            percent_correct[1] += 1
    return money


def generate_sequences_decimal():
    try:
        count = 0
        weekly_options()
        global give_stocks
        with open(FILE_OUTPUT, "a", 1, newline="") as f:
            writer = csv.writer(f)
            while True:
                for j in range(20):
                    if randint(0, 1) == 1:
                        DECIMAL_VALUE.append(randint(number_range[1], 0))
                        operations.append(operator.lt)
                    else:
                        DECIMAL_VALUE.append(randint(0, number_range[0]))
                        operations.append(operator.gt)

                cash = 300
                change = []
                for k in range(20):
                    if operations[k] == operator.lt:
                        change.append(0)
                    else:
                        change.append(1)
                progression.insert(0, change)
                progression.insert(0, DECIMAL_VALUE)
                progression.insert(0, maximumCompanies)
                progression.insert(0, template(cash))
                if progression[0] > 300:
                    progression.insert(1, percent_correct[0] / (percent_correct[0] + percent_correct[1]))
                elif progression[0] < 300:
                    progression.insert(1, percent_correct[1] / (percent_correct[0] + percent_correct[1]))
                progression.insert(1, weighted_correlation(correlation_log))
                progression.insert(6, GROUPINGS)
                writer.writerow(progression)
                count += 1
                print(str(count) + " " + str(progression[0]))
                operations.clear()
                progression.clear()
                correlation_log.clear()
                percent_correct[0] = 0
                percent_correct[1] = 0
                DECIMAL_VALUE.clear()
                scheduler2.run_pending()
                if give_stocks:
                    break
                # Required for randomization for # of companies and groupings
                weekly_options()
            give_stocks = False
            f.close()
    except KeyboardInterrupt:
        sys.exit()


def weighted_correlation(test):
    test = list(reversed(test))

    correlation_list = [[], []]
    figure = []
    counter = 0
    five_list = []

    for i in range(GROUPINGS):
        five_list.append(i)

    for i in test:
        if counter < GROUPINGS - 1:
            counter += 1
            figure.append(math.log(i))
        else:
            figure.append(math.log(i))
            correlation_list[0].append(stats.linregress(list(reversed(figure)), five_list).rvalue ** 2)
            correlation_list[1].append(stats.linregress(list(reversed(figure)), five_list).slope)
            figure.clear()
            figure.append(math.log(i))
            counter = 1

    calculation = 0
    correlation_list[0] = list(reversed(correlation_list[0]))
    correlation_list[1] = list(reversed(correlation_list[1]))

    if (all(val > 0 for val in correlation_list[1]) or all(val < 0 for val in correlation_list[1])) and len(
            correlation_list[0]) > 1:
        for i in range(len(correlation_list[0])):
            calculation += (i + 1) * correlation_list[0][i]
        calculation /= (len(correlation_list[0]) * (len(correlation_list[0]) + 1) / 2)
    else:
        calculation = 0
    return calculation


def escape_loop():
    global give_stocks
    give_stocks = True
    scheduler2.clear()


def send_email(subject, msg, msg2):
    content = open('config.json').read()
    config = json.loads(content)
    smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo()
    smtpserver.login(str(config['gmail_username']), str(config['gmail_password']))
    try:
        instruction = "Buy " + str(msg[1]) + " stocks with an R-squared value of " + str(round(msg[2], 5)) + "." \
                                                                                                             "\nThe balance rose to $" + str(
            round(msg[0], 2)) + " over " + str(msg[6]) + " days starting from $300 giving a " + \
                      str(round(((msg[0] - 300) / 300) * 100, 2)) + "% increase." + \
                      "\nThe decimal sequence was " + str(msg[3]) + ".\nThe binary sequence was " + str(msg[4]) + "." + \
                      "\nThe maximum number of companies you could buy stocks from was " + str(msg[5]) + "." + \
                      "\nThe groupings was " + str(msg[7]) + "." + \
                      "\n\nShort " + str(msg2[1]) + " stocks with an R-squared value of " + str(
            round(msg2[2], 5)) + "." \
                                 "\nThe balance dropped to $" + str(
            round(msg2[0], 2)) + " over " + str(msg2[6]) + " days starting from $300 giving a " + \
                      str(round(((300 - msg2[0]) / 300) * 100, 2)) + "% decrease." + \
                      "\nThe decimal sequence was " + str(msg2[3]) + ".\nThe binary sequence was " + str(
            msg2[4]) + "." + \
                      "\nThe maximum number of companies you could buy stocks from was " + str(msg2[5]) + "." + \
                      "\nThe groupings was " + str(msg2[7]) + "." + \
                      "\n\nStocks had a minimum daily dollar volume of " + str(LIQUIDITY) + " over the past year."

    except Exception as e:
        instruction = e
    message = 'Subject: {}\n\n{}'.format(subject, instruction)
    smtpserver.sendmail(config['gmail_username'], config['gmail_username'], message)
    smtpserver.quit()
    print("Success: Email Sent!")


def add_current_price():
    with open(FILE_TEST, newline='') as csvfile:
        companies = list(csv.reader(csvfile))
        csvfile.close()

    with open(FILE_TEST, "w", 1, newline="") as f:
        writer = csv.writer(f)
        temp = True
        count = 0
        repeat = " "
        for i in companies:
            if 100 * round(count / len(companies), 2) % 10 == 0:
                if repeat != str(100 * round(count / len(companies), 2)):
                    print("Formatting " + str(100 * round(count / len(companies), 2)) + "% Complete")
                    repeat = str(100 * round(count / len(companies), 2))
            count += 1
            if temp:
                i.append(str(datetime.today().date()))
                temp = False
                writer.writerow(i)
                continue
            try:
                stock = rh.stocks.get_stock_historicals(str(i[0]), interval='day', span='week', bounds='regular')
                i.append(100 * ((float(rh.get_latest_price(str(i[0]))[0]) - float(stock[-1]["close_price"])) / (
                    abs(float(stock[-1]["close_price"])))))
            except:
                i.append(0)
            writer.writerow(i)
        f.close()
    print("Current Price Added Complete")


def find_sequence_and_filter_stocks(value):
    with open(FILE_OUTPUT, newline='') as csvfile:
        sequences = list(csv.reader(csvfile))
        csvfile.close()

    if value(400, 300):
        check = sorted(sequences, reverse=True, key=lambda x: float(x[1]))
    else:
        check = sorted(sequences, reverse=True, key=lambda x: float(x[1]))

    with open(FILE_TEST, newline='') as csvfile:
        companies = list(csv.reader(csvfile))
        companies.pop(0)
        csvfile.close()

    for i in check:
        if value(float(i[0]), 300):
            counter = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
            for j in companies:
                decimal_sequence = list(i[4].split(", "))
                decimal_sequence = [s.strip("]") for s in decimal_sequence]
                decimal_sequence = [s.strip("[") for s in decimal_sequence]
                decimal_sequence = [float(s) for s in decimal_sequence]

                binary_sequence = list(i[5].split(", "))
                binary_sequence = [s.strip("]") for s in binary_sequence]
                binary_sequence = [s.strip("[") for s in binary_sequence]
                binary_sequence = [float(s) for s in binary_sequence]

                for k in range(20):
                    if binary_sequence[k] == 0 and float(j[-1 - k]) < decimal_sequence[k]:
                        counter[k].append(j[0])
                    elif binary_sequence[k] == 1 and float(j[-1 - k]) > decimal_sequence[k]:
                        counter[k].append(j[0])
                    else:
                        break

            for j in range(len(counter)):
                if len(counter[j]) <= int(i[3]) and len(counter[j]) != 0:
                    options = [float(i[0]), counter[j], float(i[1]), i[4], i[5], i[3], TOTAL_CHANGE, i[6]]
                    return options


def main():
    login_robinhood()
    format_stocks_for_analysis()
    scheduler2.every().day.at("15:30").do(escape_loop)
    generate_sequences_decimal()
    login_robinhood()
    add_current_price()
    send_email("AllStocks", find_sequence_and_filter_stocks(operator.gt),
               find_sequence_and_filter_stocks(operator.lt))


scheduler1 = schedule.Scheduler()
scheduler2 = schedule.Scheduler()

scheduler1.every().day.at("00:30").do(main)

while True:
    try:
        if len(nyse.valid_days(start_date=datetime.today().date(), end_date=datetime.today().date())):
            scheduler1.run_pending()
            print("OPEN")
            time.sleep(60)
        else:
            print("CLOSED")
            scheduler1.clear()
            scheduler2.clear()
            time.sleep(60)
            scheduler1.every().day.at("00:30").do(main)
    except KeyboardInterrupt:
        sys.exit()

from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from tkinter import *
import subprocess
import webbrowser
import requests
import urllib3
import string
import time
import csv
import re
import os
## disable warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


###### Change URL to the earnings call transcript from seekingalpha.com #####################      do not change + ("?part=single")
def gui_data():
    
    url = e1.get()
    url = url + ("?part=single")

    keyword1 = 'revenue'
    keyword2 = 'expense'
    keyword3 = 'margin'
    keyword4 = 'EPS'

    #############################################################################################


    ## request the first page
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    ## uncomment line below if request output = "None"
    #webbrowser.open_new(url)
    response = requests.get(url, verify=False, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    data = str(soup.find_all('p'))
    clean = re.sub("<.*?>", "\n", data)
    clean = clean.replace(",", "").replace("[", "").replace("]", "")
    clean = clean.replace("‚Äô", "\'")
    final = clean.lower().strip()
    final = final.replace("&amp;", "&")

    ## add the title
    header = str(soup.find("p", {"class": "p p1"}))
    header = re.sub("<.*?>", "", header)
    header = header.replace("Call ", "Call\n").replace(") ", ")\n").strip()
    header = header.replace("&amp;", "&")
    print(header + "\n")

    ## eps and revenue data snapshot
    ticker = str(re.findall('primary_ticker\":\[\"(.*?)\"', response.text))
    ticker = ticker.replace('[', '').replace(']', '').replace('\'', '').upper()
    quarter = re.findall('\) Q(.*?) ', response.text)
    quarter =("Q" + quarter[0] + ": ")
    date = re.findall('meta content=\"20(.*?) ', response.text)
    date = (date[0])
    parts = date.split('-')
    mys = parts[1] + '-' + parts[2] + '-' + parts[0]
    q_date = (quarter + mys)
    final_date = (q_date + "(.*?)h4")
    ## do not change the URL below
    url2 = "https://seekingalpha.com/symbol/{0}/earnings".format(ticker)
    ## uncomment line below if request output = "None"
    #webbrowser.open_new_tab(url2)
    response2 = requests.get(url2, verify=False, headers=headers)
    eps_rev = str(re.findall(final_date, response2.text))
    eps_rev = re.sub("<.*?>", "", eps_rev)
    eps_rev = eps_rev.replace("</", "").replace("[", "").replace("]", "").replace("\'", "")
    eps_rev = eps_rev.split("Q")
    eps_rev = (eps_rev[0]).replace("\'", "")
    eps_rev = re.sub("Revenue", "\nRevenue", eps_rev)
    print(eps_rev + "\n")

    ## all strings containing keyword1 data
    revenuedata = [s+'. ' for s in clean.split('. ') if keyword1 in s]
    revenuedata = ''.join(revenuedata)
    Revenue_data = str(revenuedata).strip().replace('. ', '.\n')

    ## all strings containing keyword2 data
    expensedata = [s+'. ' for s in clean.split('. ') if keyword2 in s]
    expensedata = ''.join(expensedata)
    Expense_data = str(expensedata).strip().replace('. ', '.\n')

    ## all strings containing keyword3 data
    margindata = [s+'. ' for s in clean.split('. ') if keyword3 in s]
    margindata = ''.join(margindata)
    Margin_data = str(margindata).strip().replace('. ', '.\n')

    ## all strings containing keyword4 data
    epsdata = [s+'. ' for s in clean.split('. ') if keyword4 in s]
    epsdata = ''.join(epsdata)
    epsdata = str(epsdata).strip().replace('. ', '.\n\n')
    EPS_data = epsdata
        
    ## read the positive and negative lexicon
    with open('positive.txt', 'r') as myFile:
        posWords = myFile.read().split('\n')

    with open('negative.txt', 'r') as myFile:
        negWords = myFile.read().split('\n')

    ## create a loop that will read through each item 
    for item in final:
        ## reset the counter to 0, otherwise, your numbers would reflect the prior iteration of the loop
        posCounter = 0
        negCounter = 0

        ## remove punctuation    
        for eachPunctuation in list(string.punctuation):
            datalist = final.replace(eachPunctuation, " ")
            
        ## split the item up into a list of words to look at each word and increment the appropriate counter
        words = final.split(" ")
        for eachWord in words:
            if eachWord in posWords:
                posCounter = posCounter + 1
            elif eachWord in negWords:
                negCounter = negCounter + 1
        break

    overall_Score = (posCounter - negCounter)

    ## look at the stats for the post-processed item
    print("Positive Words: " + str(posCounter))
    print("Negative Words: " + str(negCounter))
    print("Total Words Parsed: " + str(len(words)))
    print("Overall Score: " + str(overall_Score) + "\n")

    if overall_Score == 0:
        print("Neutral earnings call.\n")
        pass
    else:
        if overall_Score > 0:
            print("Good earnings call!\n")
            pass
        else:
            if overall_Score < 0:
                print("Bad earnings call.\n")
                pass

    ## attempt to calculate PT using forward P/E and forward EPS (do not change URL)
    url3 = "https://seekingalpha.com/symbol/{0}".format(ticker)
    response3 = requests.get(url3, verify=False, headers=headers)
    implied_price = re.sub("<.*?>", "", response3.text)
    implied_price = implied_price.replace("</", "").replace("[", "").replace("]", "").replace("\'", "")
    implied_EPS = str([y+'EPS (FWD):' for y in implied_price.split('PE ') if 'EPS (FWD):' in y])
    implied_EPS = implied_EPS.partition('EPS (FWD):')
    implied_EPS = (implied_EPS[2])
    implied_EPS = float(implied_EPS.replace("EPS (FWD):']", ""))

    implied_PE = re.sub("<.*?>", "", response3.text)
    implied_PE = implied_PE.replace("</", "").replace("[", "").replace("]", "").replace("\'", "")
    implied_PE = str([x+'PE (FWD):' for x in implied_PE.split('Div ') if 'PE (FWD):' in x])
    implied_PE = implied_PE.partition('PE (FWD):')
    implied_PE = (implied_PE[2])
    implied_PE = float(implied_PE.replace("PE (FWD):']", ""))

    current_price = re.sub("<.*?>", "", response3.text)
    current_price = current_price.replace("</", "").replace("[", "").replace("]", "").replace("\'", "")
    current_price = str([z+'"last":' for z in current_price.split(',') if '"last":' in z])
    current_price = current_price.partition('\"last\":')
    current_price = (current_price[2])
    current_price = float(current_price.partition('\"last\"')[0])
    current_price = float("%.2f" % current_price)

    PT = (implied_PE*implied_EPS)
    PT = float("%.2f" % PT)
    PT_percent = float((PT-current_price)/(current_price))
    PT_percent = (PT_percent*float(100))
    PT_percent_1 = ("%.2f" % PT_percent) + ("%")
    print('Current Price: ${}'.format(current_price))
    print('Implied Price: ${} \n'.format(PT))

    if PT_percent > 0.00:
        print('{} Projected Upside'.format(PT_percent_1))
    else:
        print('{} Projected Downside'.format(PT_percent_1))
    print("(Forward P/E: {} x Forward EPS: {})\n".format(implied_PE,implied_EPS))

    ## close opened browser tabs       
    #os.system("killall -9 'Google Chrome'")

    q_date = re.sub(": ", "_", q_date)

    with open('%s_%s_earnings_highlights.txt'%(ticker,q_date), "w") as txtfile:
        txtfile.write("\n%s\n" % header)
        txtfile.write("\n%s\n\n\n\n\n" % eps_rev)
        txtfile.write("%s Data:\n\n\n%s" % (keyword1.capitalize(), Revenue_data))
        txtfile.write("\n\n\n\n")
        txtfile.write("%s Data:\n\n%s" % (keyword2.capitalize(), Expense_data))
        txtfile.write("\n\n\n\n")
        txtfile.write("%s Data:\n\n%s" % (keyword3.capitalize(), Margin_data))
        txtfile.write("\n\n\n\n")
        txtfile.write("%s Data:\n\n%s" % (keyword4, EPS_data))
    print("\"%s_%s_earnings_highlights.txt\" file written"%(ticker,q_date))

    ## create Wordcloud
    wordcloud = WordCloud(background_color="white").generate(final)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.title('Word Frequency Cloud' + '\n' )
    plt.axis("off")
    plt.show()

master = Tk()
master.title("Earnings Call Transcript Parser")
master.geometry("400x100+50+50")
Label(master, text="URL: ").grid(row=4, column=5)
e1 = Entry(master)
e1.grid(row=4, column=7)
Button(master, text='Search', command = gui_data).grid(row=5, column=7, sticky=W, pady=4)
mainloop()

#!/usr/bin/env python
#
# LaunchBar Action Script
#
import sys
import json
import requests
import re
import datetime
import calendar
import os
import subprocess as sp
import cfscrape
from collections import OrderedDict

boslife_url = "https://justreadtheinstructions.net"
boslife_username = ""
boslift_password = ""

encoding = 'utf-8'

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
headers = OrderedDict(
    (
        ("Host", None),
        ("Connection", "keep-alive"),
        ("Upgrade-Insecure-Requests", "1"),
        ("User-Agent", user_agent),
        (
            "Accept",
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        ),
        ("Accept-Encoding", "gzip, deflate"),
        ("Accept-Language", "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"),
        
    )
)

my_env = os.environ.copy()
my_env["PATH"] = "/usr/local/bin:" + my_env["PATH"]

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12)
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)

def perform_bash_command(command): 
    sp.check_output(command, env=my_env)

# save cookie for following requests
session = requests.Session()
session.headers = headers
scraper = cfscrape.create_scraper(sess=session)

# get csrf token from clientarea.php
csrf_token_request = scraper.get(boslife_url + "/clientarea.php")
# print(csrf_token_request.content)
csrf_token = re.search(r"(?<=csrfToken = ').*(?=')",
                       csrf_token_request.content.decode(encoding))
# print(csrf_token)

# do login
do_login_data = {
    'token': csrf_token,
    'username': boslife_username,
    'password': boslift_password
}
do_login_request = scraper.post(
    boslife_url + "/dologin.php", data=do_login_data)
# print(do_login_request.content)

# get product I subscribed from clientarea.php
get_product_params = {
    'action': 'products'
}
# get_product_request = session.get(
#     boslife_url + "/clientarea.php", params=get_product_params)
get_product_request = scraper.get(boslife_url + "/clientarea.php", params=get_product_params)
# print(get_product_request.content)
get_product_content = get_product_request.content.decode(encoding)
# print(get_product_content)
get_product_content = re.sub(
    r'status-active[\s."></:;=?\-\w]*productdetails&amp;id=', "djew90423iofjewio09248FJIJFI", get_product_content)
# print(get_product_content)
product_id = re.search(
    r'(?<=djew90423iofjewio09248FJIJFI)\d*(?=")', get_product_content)
if product_id is not None:
    product_id = product_id.group(0)
else:
    ddos_protector = re.search(r'Cloudflare', get_product_content)
    __message = "Unknown error ocurred when trying to get product_id."
    perform_bash_command(["terminal-notifier",
              "-title", "BosLife",
              "-message", __message,
              "-appIcon", "https://boslife.info/images/icon.png",
              "-sound", "default",
              "-open", "https://boslife.info/index.html",
              "-ignoreDnD"])
    exit()

# get product details
get_product_details_request = scraper.get(boslife_url + "/clientarea.php", params={
    'action': "productdetails",
    'id': product_id
})
product_details_content = get_product_details_request.content.decode(encoding)
# print(product_details_content)

last_reset = re.search(
    r'(?<=Last Reset : ).*?(?=<\/li>)', product_details_content)
remaining = re.search(
    r'(?<=Remaining: )[0-9-]*(?= MB)', product_details_content)
next_reset_date = None
if last_reset.group(0) == "No Data":
    next_reset_date = "No Data"
else:
    last_reset = last_reset.group(0)
    # print(last_reset)
    next_reset_date = add_months(datetime.date(
        *(int(s) for s in last_reset.split('-'))), 1).strftime("%Y-%m-%d")
    # print(next_reset_date)

if remaining is not None:
    _remaining = float(remaining.group(0))
    if remaining >= 1000:
        remaining = ("%.2f" % (_remaining / 1000)) + "GB"
    else:
        remaining = ("%.2f" % _remaining) + "MB"
# print(next_reset_date, remaining)

# my_command = "terminal-notifier -title 'BosLife' -message 'Remaining Traffic: %s; Next Reset Date: %s' -appIcon https://boslife.info/images/icon.png  -sound default" % (remaining, next_reset_date)
perform_bash_command(["terminal-notifier",
              "-title", "BosLife",
              "-message", "RT: %s; NRD: %s.\nClick here to check out!" % (
                  remaining, next_reset_date),
              "-appIcon", "https://boslife.info/images/icon.png",
              "-sound", "default",
              "-open", "https://boslife.info/index.html",
              "-ignoreDnD"])


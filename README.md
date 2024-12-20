# 🏠 Accommodation Auto-enquiry Bot

## Backstory

When I moved to Dublin, Ireland for my studies I was faced with a severe accommodation crisis. Housing in Dublin is oversaturated by a large and sudden influx of people. It is very difficult to secure a reasonably priced and situated apartment, especially when moving from abroad.

I found myself sending tens of inquiries for accommodation every single day and only hearing back from a few of them. That is why I built this script - to automate the repetitive search for accommodation, yielding a successful result only after a couple of days of use.

## The Script

At its core, the notebook uses Selenium for programmatic control of the browser - it scrapes all valid accommodation from listings from [daft](https://daft.ie) and then proceeds to answer them with predetermined contact information and message.

After each successful inquiry, the respective link is saved into a CSV file to prevent double-quiring listings. In case of a failed inquiry links are also logged into a separate CSV file with failed listings to be tried later.

I chose a notebook file instead of regular Python to make the troubleshooting easier. This way I was able to separate the web-control functions in their own containers and use them independently of each other.

## Note on Usability

This project is not designed for general use and is not 100% stable. It is designed for a narrow usecase on [daft](https://daft.ie) and would require some control elements to be used by others.



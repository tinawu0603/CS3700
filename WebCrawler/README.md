# CS3700: Web Crawler

## Project Team Members
+ Franklin Fasano
+ Jack Michaud
+ Tina Wu

## Project Overview
This web crawler gathers data from a fake social networking website called Fakebook that the course staff has set up for us. The requirement for this web crawler is to recursively traverse through Fakebook and find 5 *secret flags* for every member on the team.

## Project Results

### The process
+ Log in to Fakebook
+ Go to the Fakebook homepage
+ Add URLs to a queue
+ Go to URLs and dissect the page source
+ Find more URLs in the page source, add any flags found to a flags array, and add the current url to a blacklist to avoid cycles
+ Rinse and repeat until all 5 flags are found.
There are a couple components of this project we needed to program. One is requesting a page, and the other is parsing a webpage to look for flags and links.

### Parsing
For parsing a webpage, all we needed to do was use the BeautifulSoup library. We can find tags by their attributes so finding the flags, csrf token, and anchor tags were all trivial with that library.

### Requesting
We needed to request/send data from/to the web server through both GET and POST requests. GETting a webpage needed to include the Hostname and Cookie headers and POSTing required those plus a content length header. We needed to make sure that the cookie included the CSRF token found on the login page and the session token for both types of requests.

### Receiving
Receving data from the web server was a little less trivial. We needed to handle both chunked and unchunked data. Unchunked data was easy because after an initial request for the header information we got a content length in the header, so all we needed to do from that point on was request the rest of the length. For chunked data, we needed to request the length of the data given just before the actual data, and then check for more data at the end of that data. In this case, it seemed like the web server served chunked data only in one chunk every time (at the end of the first chunk it would always say 0, indicating no more chunks).

## Points of Trouble
We encountered some error 500s that stops our scraping, but the issue had to do with how there's no content length in error 500s so the scraper was stopped dead in its tracks trying to request content that wasn't there.

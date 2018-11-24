from scrapy import cmdline
import delete
cmdline.execute("scrapy crawl youku".split())
#cmdline.execute("scrapy crawl youku -o t2.json".split())

#'str' object doesn't support item deletion
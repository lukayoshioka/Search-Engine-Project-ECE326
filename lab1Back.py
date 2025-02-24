from crawler import crawler
# import sqlite3 as lite
if __name__ == "__main__":
    # initialize and run crawler
    crawler = crawler(None, 'urls.txt')
    crawler.crawl(depth=1)
    # test out both functions and print the results
    inverted_index = crawler.get_inverted_index()
    print(inverted_index)
    resolved_inverted_index = crawler.get_resolved_inverted_index()
    print(resolved_inverted_index)

    # # testing each database
    crawler.mycursor.execute("SELECT * FROM LEXICON;")
    row = crawler.mycursor.fetchone()
    while row is not None:
        print(row)
        print(crawler.get_word_from_word_id(row[1]))
        row = crawler.mycursor.fetchone()

    crawler.mycursor.execute("SELECT * FROM INVERTED;")
    row = crawler.mycursor.fetchone()
    while row is not None:
        print(row)
        row = crawler.mycursor.fetchone()

    crawler.mycursor.execute("SELECT * FROM WORDS;")
    row = crawler.mycursor.fetchone()
    while row is not None:
        print(row)
        row = crawler.mycursor.fetchone()

    crawler.mycursor.execute("SELECT * FROM DOCUMENTS;")
    row = crawler.mycursor.fetchone()
    while row is not None:
        print(row)
        row = crawler.mycursor.fetchone()

    crawler.mycursor.execute("SELECT * FROM PAGERANKS;")
    row = crawler.mycursor.fetchone()
    while row is not None:
        print("("+crawler.get_url_from_id(row[0]) + ", "+str(row[1])+")")
        row = crawler.mycursor.fetchone()
   
    crawler.mydb.close()
import csv
with open('./questions.csv', 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
		#print( "insert into lottery_question(question, option1, option2, option3, answer) values ('', '', '', '','')" )
        print "insert into lottery_question(question, option1, option2, option3, answer) values ('%s', '%s', '%s', '%s','%s');" % (unicode(row[1],'gbk'),unicode(row[2],'gbk'),unicode(row[3],'gbk'),unicode(row[4],'gbk'),unicode(row[5],'gbk'))
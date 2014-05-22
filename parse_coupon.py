import csv
with open('./coupons.csv', 'rb') as csvfile:
	spamreader = csv.reader(csvfile, delimiter='	', quotechar='|')
	for row in spamreader:
		sql = ("insert into lottery_coupon (name,code,status,has_send) values ('"+ unicode(row[0],'gbk') + "','"+ unicode(row[1],'gbk') +"',0,0);").encode('gbk')
		print sql
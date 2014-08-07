#coding:UTF-8

#从VisitorOK表中获取数据
import _mssql 

from pymongo import MongoClient

server = '127.0.0.1'
user = 'sa'
password = '123456'

mongodb_server = '127.0.0.1'

def get_connection():
	conn = _mssql.connect(server=server, user=user, password=password, database='hdbusiness', charset="utf8")
	return conn;

def remove_digit_keys(row):
	for key in row.keys():
		if isinstance(key, int):
			row.pop(key)
	return row
	
def print_order(order):
	for (key, value) in order.items():
		if type(value) == type(unicode('','UTF-8')):
			try:
				print "{0}: {1} = {2}".format(type(value).__name__, key, value.encode('GBK'))
			except:
				print "EROR!!!!  {0}: {1}".format(type(value).__name__, key)
		else:
			print "{0}: {1} = {2}".format(type(value).__name__, key, value)
	
def deal_value_if_necessary(row):
	if row is None:
		return
	for (key, value) in row.items():
		if type(value) <> type(unicode('','UTF-8')):
			row[key] = str(value)
	return row

def get_one_row_from_order(sql, parameter):
	data = {}
	conn = get_connection()
	row = conn.execute_row(sql, parameter)
	if row is not None:
		data = remove_digit_keys(row)
	deal_value_if_necessary(row)
	conn.close()
	#print data
	return data

def get_rows_from_orders(sql, parameter):
	data = []
	conn = get_connection()
	conn.execute_query(sql, parameter)
	for row in conn:
		remove_digit_keys(row)
		deal_value_if_necessary(row)
		data.append(row)
	conn.close()
	return data
	
def get_visitorok_other(sellid):
	sql = "select top 1 * from tbdVisitorOkOther where sellid = %s"
	return get_one_row_from_order(sql, sellid)
	
def get_order_productions(sellid):
	sql = "select *, (select b.MyName from tbdProduction b where b.CurID = a.CurID) as DName from tbdVisitorOkPro a where SellID = %s";	
	return get_rows_from_orders(sql, sellid)

def get_order_hotel(sellid):
	data = {}
	sql = "select * from tbdVisitorOkHotel where SellID = %s"
	hotelinfo = get_one_row_from_order(sql, sellid)
	if hotelinfo is not None:
		data = hotelinfo
		sql = "select * from tbdVisitorOkHotelDetail where SellID = %s"
		data['hoteldetails'] = get_rows_from_orders(sql, sellid)
	return data
	
def get_order_visitoruser(sellid):
	sql = "select * from tbdVisitorOkUserInfo where SellID = %s"
	return get_one_row_from_order(sql, sellid)
	
def get_order_orderuser(sellid):
	sql = "select * from tbdVisitorInfo where UserID in (select a.UserID from tbdVisitorOk a where SellID = %s)"
	orderuser = get_one_row_from_order(sql, sellid)
	sql = "select * from tbdVisitorAgent where DTravelNo = %s"
	orderuser['agent'] = get_one_row_from_order(sql, orderuser['DTravelNo'])
	return orderuser

def get_order_payinfo(sellid):
	sql = "select * from tbdVisitorOkPay where SellID = %s"
	return get_one_row_from_order(sql, sellid)
	
def get_order_individualagents(sellid):
	sql = "select * from tbdVisitorOkIndividualAgent where SellID = %s"
	return get_rows_from_orders(sql, sellid)
	

def insert_order_to_mongodb(order):
	client = MongoClient(mongodb_server, 27017)
	db = client.order_system
	db.orders.insert(order)

def main():
	sql = "select * from tbdVisitorOK order by DDate desc"
	conn = get_connection()
	conn.execute_query(sql)
	for row in conn:
		#过滤掉数字的key
		#print row
		row = remove_digit_keys(row)
		deal_value_if_necessary(row)
		#print row
		sellid = row['SellID']
		#print_order(row)
		row['otherinfo'] = get_visitorok_other(row['SellID'])
		row['productions'] = get_order_productions(sellid)
		row['hotelinfo'] = get_order_hotel(sellid)
		row['visitoruserinfo'] = get_order_visitoruser(sellid)
		row['payinfo'] = get_order_payinfo(sellid)
		row['individualagents'] = get_order_individualagents(sellid)
		row['orderuser'] = get_order_orderuser(sellid)
		#print row
		insert_order_to_mongodb(row)
		
main()
	
	









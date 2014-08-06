import codecs

def parse_log(file_name):
	f = codecs.open(file_name, 'r', 'GBK')
	text = ''
	for line in f:
		text += line
	#print text
	
parse_log('log.txt')
	
	 

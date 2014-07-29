use strict;
use warnings;

#use MongoDB;
#use MongoDB:OID;
use DBI;
use Encode; 

my $dsn = "DBI:mysql:lottery";
my $username = "root";
my $password = '123456';
 
# connect to MySQL database
my %attr = ( PrintError=>0,  # turn off error reporting via warn()
             RaiseError=>1 );   # turn on error reporting via die()           
 
my $dbh  = DBI->connect($dsn,$username,$password, \%attr);
my $sql = "set names utf8";
my $stmt2 = $dbh->prepare($sql);
$stmt2->execute();
$sql = "insert into logsystem_ordersystemlogrecord (time, thread, level, 
clazz, content) values (?,?,?,?,?)";
my $stmt = $dbh->prepare($sql);

parse_log('c:/log.txt');

sub parse_log {
	my $file_name = shift;
	open FILE, '<', $file_name;
	
	my $text = '';
	while (<FILE>) {
		$text .= $_;
	}
	
	#my $conn = MongoDB::Connection->new;
	#my $db = $conn->order_system_log;
	#my $logs = $db->logs;
	
	while ($text =~ /
					 ([0-9]{4}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]{3})\s
					 \[([0-9]{1,3})\]\s
					 ([A-Z]{1,10})\s
					 (\w+(?:\.\w+){0,})\s
					 \[\(\w{1,}\)\]\s
					 -\s
					 (.*)
					/mx) {
		#print "$1 $2 $3 $4 $5\n";
	    #$logs->insert({"time" => $1,
		#	"thread" => $2,
		#	"level" => $3,
		#	"class" => $4,
		#	"content" => $5);
		$text = $';
		insert_record_mysql(encode("utf-8", decode("gb2312", $1)), 
							encode("utf-8", decode("gb2312", $2)), 
							encode("utf-8", decode("gb2312", $3)), 
							encode("utf-8", decode("gb2312", $4)), 
							encode("utf-8", decode("gb2312", $5)));
	}
}

$dbh->disconnect();

sub insert_record_mysql {
	$stmt->execute(@_);
}

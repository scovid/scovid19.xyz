package Util;

# Convert Date(Time) string to DateTime object
# Supports ISO-8601 and various bastardisations
sub iso2dt {
	my ($iso) = @_;

	return DateTime->now() unless $iso;

	if ($iso =~ /(\d{4})-?(\d{2})-?(\d{2})(\s|T)(\d{2}):?(\d{2}):?(\d{2})/) {
		return DateTime->new(
			year   => $1,
			month  => $2,
			day    => $3,
			hour   => $5,
			minute => $6,
			second => $7,
		);
	} elsif ($iso =~ /(\d{4})-?(\d{2})-?(\d{2})T?/) {
		return DateTime->new(year => $1, month => $2, day => $3);
	}
}

# Takes YYYYMMDD and returns YYYY-MM-DD
sub fix_date {
	my ($date) = @_;

	if ($date =~ /(\d{4})(\d{2})(\d{2})/) {
		return join('-', $1, $2, $3);
	}

	return $date;
}

1;

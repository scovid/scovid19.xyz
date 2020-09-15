package Util;

# Convert Date(Time) string to DateTime object
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

1;

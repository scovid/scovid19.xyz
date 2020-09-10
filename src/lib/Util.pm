package Util;

# Convert YYYYMMDD into a DateTime object
# TODO: Add full ISO-8601 support
sub iso2dt {
	my ($date) = @_;

	if ($date =~ /(\d{4})(\d{2})(\d{2})/) {
		return DateTime->new(year => $1, month => $2, day => $3);
	}

	return DateTime->now();
}

1;

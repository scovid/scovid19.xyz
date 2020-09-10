package SCOVID;

use strict;
use warnings;
use 5.32.0;
use Carp qw{carp};
use OpenData;
use Util;

sub new {
	my ($class) = @_;

	my $self = {
		OpenData => OpenData->new,
	};

	return bless $self, $class;
}

# Accessor for OpenData
sub odata { return $_[0]->{OpenData} }

# Get the mapping of council IDs to council names
sub councils {
	my ($self) = @_;

	# Mapping of council ID to name
	my $councils = $self->odata->fetch('councils')->{records};
	my %council_map = ();
	$council_map{$_->{CA}} = $_->{CAName} foreach @$councils;

	return \%council_map;
}

# Get the last updated time of the OpenData stats
# Based on the latest date in the "Daily and Cumulative Cases" data set
sub last_updated {
	my ($self) = @_;

	my $cases_by_day = $self->odata->fetch('daily', limit => 1, sort => 'Date DESC');
	my @records = $cases_by_day->{records}->@*;

	return Util::iso2dt($records[-1]->{Date});
}

1;

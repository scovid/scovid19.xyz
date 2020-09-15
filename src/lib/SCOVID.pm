# Wrapper around the NHS OpenData API

package SCOVID;

use strict;
use warnings;
use 5.32.0;

use Carp qw{carp};
use DateTime;

use OpenData;
use Cache;
use Util;

sub new {
	my ($class) = @_;

	my $self = {
		OpenData => OpenData->new,
		Cache    => Cache->new,
	};

	# Getters
	*SCOVID::odata = sub { return $_[0]->{OpenData} };
	*SCOVID::cache = sub { return $_[0]->{Cache} };

	return bless $self, $class;
}

# Get the mapping of council IDs to council names
sub councils {
	my ($self) = @_;

	# Mapping of council ID to name
	my $councils = $self->odata->fetch('councils')->{records};
	my %council_map = ();
	$council_map{$_->{CA}} = $_->{CAName} foreach @$councils;

	return \%council_map;
}

sub trend {
	my ($self, $params) = @_;

	# NOTE: Fetching 31 so we can count the daily deaths
	# We ignore the 31st day
	my $trend = $self->odata->fetch('daily', sort => 'Date DESC', limit => 31);

	my @dates  = ();
	my @cases  = ();
	my @deaths = ();

	my @records = reverse $trend->{records}->@*;
	my $first_day = shift @records;

	my $deaths_yesterday = $first_day->{Deaths};
	foreach my $day (@records) {
		push @dates, Util::iso2dt($day->{Date})->ymd;
		push @cases, $day->{DailyCases};
		push @deaths, $day->{Deaths} - $deaths_yesterday;

		$deaths_yesterday = $day->{Deaths};
	}

	return {
		labels => \@dates,
		datasets => [{
			backgroundColor => 'darkorange',
			label           => 'Positive',
			data            => \@cases,
		# },{
			# backgroundColor => 'lightgreen',
			# label           => 'Negative',
			# data            => \@cases,
		# },{

		# TODO: death stats work but want to make it disabled by default
			# backgroundColor => 'darkgrey',
			# label           => 'Deaths',
			# data            => \@deaths,
		}],
	}
}

# Get the last updated time of the OpenData stats
# Based on the latest date in the "Daily and Cumulative Cases" data set
sub last_updated {
	my ($self) = @_;

	if (my $cached = $self->cache->get('last_updated')) {
		return Util::iso2dt($cached);
	}

	my $cases_by_day = $self->odata->fetch('daily', limit => 1, sort => 'Date DESC');
	my @records = $cases_by_day->{records}->@*;

	$self->cache->set('last_updated', 7200, $records[-1]->{Date});
	return Util::iso2dt($records[-1]->{Date});
}

1;

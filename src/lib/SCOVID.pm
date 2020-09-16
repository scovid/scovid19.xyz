# Wrapper around the NHS OpenData API

package SCOVID;

use strict;
use warnings;
use 5.32.0;

use Carp qw{carp};
use DateTime;
use Data::Dumper;

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

	my ($limit, $offset) = (30, 0);
	if ($params->{start} && $params->{end}) {
		my $start        = Util::iso2dt($params->{start});
		my $end          = Util::iso2dt($params->{end});
		my $last_updated = Util::iso2dt($self->last_updated);

		$limit = $end->delta_days($start)->in_units('days') + 1; # Add one to make the bounds inclusive
		$offset = $last_updated->delta_days($end)->in_units('days');
	}

	my $trend = $self->odata->fetch('daily', sort => 'Date DESC', limit => $limit, offset => $offset);

	my @dates  = ();
	my @cases  = ();

	my @records = reverse $trend->{records}->@*;

	foreach my $day (@records) {
		push @dates, Util::fix_date($day->{Date});
		push @cases, $day->{DailyCases};
	}

	return {
		labels => \@dates,
		datasets => [{
			backgroundColor => 'darkorange',
			label           => 'Positive',
			data            => \@cases,
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

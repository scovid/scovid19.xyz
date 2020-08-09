#!/usr/bin/env perl

BEGIN {
	use Mojolicious::Lite;
	unshift @INC, app->home . "/lib";
};

use strict;
use warnings;
use v5.32.0;

use OpenData;
use Cache;
use DateTime;
use List::MoreUtils qw{uniq};

my $cache = Cache->new(app->mode);
my $TOTAL_COUNCILS = 32;

# Main page
get '/' => sub {
	my ($ctx) = @_;

	$ctx->render(
		template => 'index',
		summary  => get_summary(),
		date_fmt => '%d %b %Y',
	);
};

# API
get '/api/trend' => sub {
	my ($ctx) = @_;

	$ctx->render(
		json => $cache->wrap('trend', 7, \&get_trend),
	);
};

get '/api/breakdown' => sub {
	my ($ctx) = @_;

	$ctx->render(
		json => $cache->wrap('breakdown', 7200, \&get_breakdown),
	);
};

get '/api/locations/total' => sub {
	my ($ctx) = @_;

	$ctx->render(
		json => $cache->wrap('locations_total', 7200, \&get_locations_total),
	);
};

get '/api/locations/new' => sub {
	my ($ctx) = @_;

	$ctx->render(
		json => $cache->wrap('locations_new', 7200, \&get_locations_new),
	);
};

app->config(hypnotoad => { listen => ['http://[::]:8080'] });
app->start;

# == #

sub get_summary {
	my $odata = OpenData->new;
	my $cases_by_day = $odata->fetch('daily', limit => 1000, sort => 'Date ASC');

	my %summary = ();
	my @records = $cases_by_day->{records}->@*;

	$summary{last_updated}    = _dt($records[-1]->{Date});
	$summary{cases}->{total}  = $records[-1]->{CumulativeCases};
	$summary{cases}->{today}  = $records[-1]->{DailyCases};
	$summary{deaths}->{total} = $records[-1]->{Deaths};
	$summary{deaths}->{today} = $records[-1]->{Deaths} - $records[-2]->{Deaths};

	my ($max_deaths, $max_cases, $prev_day);
	foreach my $day (@records) {
		my $new_deaths = $prev_day ? $day->{Deaths} - $prev_day->{Deaths} : $day->{Deaths};

		if (not $max_deaths or $new_deaths > $max_deaths->{number}) {
			$max_deaths->{number} = $new_deaths;
			$max_deaths->{date}   = _dt($day->{Date});
		}

		if (not $max_cases or $day->{DailyCases} > $max_cases->{number}) {
			# On Apr 19th the stats started to include UK test centres
			# So this day isn't really an accurate representation
			if ($day->{Date} ne '20200420') {
				$max_cases->{number} = $day->{DailyCases};
				$max_cases->{date}   = _dt($day->{Date});
			}
		}

		$prev_day = $day;
	}

	$summary{cases}->{most}  = $max_cases;
	$summary{deaths}->{most} = $max_deaths;

	return \%summary;
}

sub get_trend {
	my $odata = OpenData->new;
	my $trend = $odata->fetch('daily', sort => 'Date DESC', limit => 30);

	my @dates = ();
	my @cases = ();

	foreach my $day (reverse $trend->{records}->@*) {
		push @dates, _dt($day->{Date})->ymd;
		push @cases, $day->{DailyCases};
	}

	return {
		labels => \@dates,
		datasets => [{
			backgroundColor => 'darkorange',
			label           => 'Positive',
			data            => \@cases,
		# },{
		# 	backgroundColor => 'lightgreen',
		# 	label           => 'Negative',
		# 	data            => \@cases,
		# },{
		# 	backgroundColor => 'darkgrey',
		# 	label           => 'Deaths',
		# 	data            => \@cases,
		}],
	}
}

sub get_breakdown {
	my ($positive, $negative, $deaths);

	# There doesn't seem to be a good endpoint for getting total negatives
	# So use total_by_deprivation and total it manually
	my $odata = OpenData->new;
	my $total_by_deprivation = $odata->fetch('total_by_deprivation');
	foreach my $record ($total_by_deprivation->{records}->@*) {
		$positive += $record->{TotalPositive};
		$negative += $record->{TotalNegative};
		$deaths   += $record->{TotalDeaths};
	}

	return {
		labels => [qw{Positive Negative Deaths}],
		datasets => [{
			backgroundColor => ['darkorange', 'lightgreen', 'darkgrey'],
			borderColor     => ['darkorange', 'lightgreen', 'darkgrey'],
			label           => 'Breakdown',
			data            => [$positive, $negative, $deaths],
		}],
	};
}

sub get_locations_total {
	my $odata = OpenData->new;

	my $council_map   = _council_map();
	my $total_by_area = $odata->fetch('total_by_area');

	my @sets = ();
	foreach my $location ($total_by_area->{records}->@*) {
		push @sets, {
			x => $council_map->{$location->{CA}},
			y => $location->{'TotalCases'},
		};
	}

	@sets = sort { $a->{x} cmp $b->{x} } @sets;

	return {
		labels => [ sort { $a cmp $b } uniq values %$council_map ],
		datasets => [{
			backgroundColor => [ map { _color($_->{x}) } @sets ],
			label           => 'Cases by area',
			data            => \@sets,
		}],
	};
}

sub get_locations_new {
	my ($type) = @_;

	my $odata = OpenData->new;

	my %totals        = ();
	my $council_map   = _council_map();
	my $daily_by_area = $odata->fetch('daily_by_area', limit => $TOTAL_COUNCILS * 7, sort => 'Date DESC');

	my @sets = ();
	foreach my $record ($daily_by_area->{records}->@*) {
		$totals{$record->{CA}} += $record->{DailyPositive};
	}

	foreach my $ca (keys %totals) {
		push @sets, {
			x => $council_map->{$ca},
			y => $totals{$ca},
		};
	}

	@sets = sort { $a->{x} cmp $b->{x} } @sets;

	return {
		labels => [ sort { $a cmp $b } uniq values %$council_map ],
		datasets => [{
			backgroundColor => [ map { _color($_->{x}) } @sets ],
			label           => 'Cases by area',
			data            => \@sets,
		}],
	};
}

sub _council_map {
	my $odata = OpenData->new;

	# Mapping of council ID to name
	my $councils = $odata->fetch('councils')->{records};
	my %council_map = ();
	$council_map{$_->{CA}} = $_->{CAName} foreach @$councils;

	return \%council_map;
}

# Conver YYYYMMDD into a DateTime object
sub _dt {
	my ($date) = @_;

	if ($date =~ /(\d{4})(\d{2})(\d{2})/) {
		return DateTime->new(year => $1, month => $2, day => $3);
	}

	return DateTime->now();
}

sub _color {
	my ($key) = @_;

	$key =~ s/\s+/_/g;

	my %map = (
		# Types
		deaths   => '#b3b3b3',
		negative => '#b2df8a',
		positive => 'ff7f00',

		# Locations
		Aberdeen_City         => '#33a02c',
		Aberdeenshire         => '#1f78b4',
		Angus                 => '#b2df8a',
		Argyll_and_Bute       => '#a6cee3',
		City_of_Edinburgh     => '#fb9a99',
		Clackmannanshire      => '#e31a1c',
		Dumfries_and_Galloway => '#fdbf6f',
		Dundee_City           => '#ff7f00',
		East_Ayrshire         => '#cab2d6',
		East_Dunbartonshire   => '#6a3d9a',
		East_Lothian          => '#ffff99',
		East_Renfrewshire     => '#b15928',
		Falkirk               => '#66c2a5',
		Fife                  => '#a6d854',

		# TODO: These need nicer colors
		Glasgow_City         => 'orangered',
		Highland             => 'blue',
		Inverclyde           => 'purple',
		Midlothian           => 'cyan',
		Moray                => 'pink',
		'Na_h-Eileanan_Siar' => 'burgandy',
		North_Ayrshire       => 'red',
		North_Lanarkshire    => 'yellow',
		Orkney_Islands       => 'lime',
		Perth_and_Kinross    => 'rebeccapurple',
		Renfrewshire         => 'brown',
		Scottish_Borders     => 'lightblue',
		Shetland_Islands     => 'navy',
		South_Ayrshire       => 'green',
		South_Lanarkshire    => 'orange',
		Stirling             => 'darkgreen',
		West_Dunbartonshire  => 'grey',
		West_Lothian         => 'magenta',
	);

	return $map{$key} || 'yellow';
}

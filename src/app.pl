use lib 'src/lib';

use Mojolicious::Lite;
use OpenData;
use DateTime;
use List::MoreUtils qw{uniq};
use Data::Dumper;

my $summary = get_summary();
get '/' => {
	template => 'index',
	summary  => $summary,
	date_fmt => '%d %b %Y'
};

get '/api/trend'     => { json => get_trend() };
get '/api/breakdown' => { json => get_breakdown() };
get '/api/locations' => { json => get_locations() };

app->start;


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
	my $odata = OpenData->new;

	my ($positive, $negative, $deaths);

	# There doesn't seem to be a good endpoint for getting total negatives
	# So use total_by_deprivation and total it manually
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
			label           => 'Breakdown',
			data            => [$positive, $negative, $deaths],
		}],
	}
}

sub get_locations {
	my $odata = OpenData->new;

	my $council_map   = _council_map();
	my $total_by_area = $odata->fetch('total_by_area');

	my @sets = ();
	foreach my $location ($total_by_area->{records}->@*) {
		push @sets, {
			x => $council_map->{$location->{CA}},
			y => $location->{TotalCases},
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
	}
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
	warn $key;

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
		Glasgow_City => 'orangered',
		Highland => 'blue',
		Inverclyde => 'purple',
		Midlothian => 'cyan',
		Moray => 'pink',
		'Na_h-Eileanan_Siar' => 'burgandy',
		North_Ayrshire => 'red',
		Orkney_Islands => 'lime',
		Perth_and_Kinross => 'rebeccapurple',
		Renfrewshire => 'brown',
		Scottish_Borders => 'yellow',
		Shetland_Islands => 'navy',
		South_Ayrshire => 'green',
		South_Lanarkshire => 'orange',
		Stirling => 'darkgreen',
		West_Dunbartonshire => 'grey',
		West_Lothian => 'magenta',
	);

	return $map{$key} || 'yellow';
}

# Basic interface to the NHS OpenData API

package OpenData;

use strict;
use warnings;
use 5.32.0;
use Mojo::UserAgent;
use Mojo::JSON qw{decode_json};
use Carp qw{carp};

my %resources = (
	councils             => '967937c4-8d67-4f39-974f-fd58c4acfda5',
	daily                => '287fc645-4352-4477-9c8c-55bc054b7e76', # Daily and Cumulative Cases
	total_by_area        => 'e8454cf0-1152-4bcb-b9da-4343f625dfef', # Total Cases By Council Area
	daily_by_area        => '427f9a25-db22-4014-a3bc-893b68243055', # Daily Case Trends By Council Area
	total_by_deprivation => 'a965ee86-0974-4c93-bbea-e839e27d7085', # Total Cases By Deprivation
);

sub new {
	my ($class) = @_;

	my $self = {
		BASE_URL => 'https://www.opendata.nhs.scot/en/api/3/action/datastore_search',
		UA       => Mojo::UserAgent->new,
	};

	return bless $self, $class;
}

sub fetch {
	my ($self, $resource, %filter) = @_;

	if (not exists $resources{$resource}) {
		carp("ERROR: Invalid resource passed: '$resource'");
		return;
	}
	
	my $url = $self->_build_url(resource_id => $resources{$resource}, %filter);
	my $res = $self->{UA}->get($url)->result;

	unless ($res->is_success) {
		carp("ERROR: OpenData request failed: " . $res->message);
		return;
	}

	my $parsed = decode_json($res->body);

	unless ($parsed->{success}) {
		carp("ERROR: OpenData returned failure response: " . $parsed->{help});
		return;
	}

	return $parsed->{result};
}

sub _build_url {
	my ($self, %qs) = @_;

	my $query = join(';', map { "$_=$qs{$_}" } keys %qs);

	return sprintf('%s?%s', $self->{BASE_URL}, $query);
}

1;

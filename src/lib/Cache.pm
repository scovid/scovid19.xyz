package Cache;

use strict;
use warnings;
use v5.32.0;

use Mojo::Cache;
use DateTime;

sub new {
	my ($class, $verbose) = @_;

	my $self = {
		MODE    => $ENV{MODE},
		CACHE   => Mojo::Cache->new,
		VERBOSE => $verbose,
	};

	return bless $self, $class;
}

sub set {
	my ($self, $key, $valid_for, $data) = @_;

	if ($self->{MODE} ne 'production') {
		warn "Cache::set - returning as mode is not production" if $self->{VERBOSE};
		return;
	}

	my $expiry = time() + $valid_for;

	my $store = {
		data   => $data,
		expiry => $expiry,
	};

	warn "Cache::set - set '$key' in cache" if $self->{VERBOSE};
	$self->{CACHE}->set($key => $store);
}

sub get {
	my ($self, $key) = @_;

	if ($self->{MODE} ne 'production') {
		warn "Cache::get - returning as mode is not production" if $self->{VERBOSE};
		return;
	}

	my $store = $self->{CACHE}->get($key);

	if ($store and ref $store eq 'HASH') {
		if ($store->{expiry} > time()) {
			warn "Cache::get - got '$key' from cache" if $self->{VERBOSE};
			return $store->{data};
		}

		warn "Cache::get - ignored '$key' as it was out of date" if $self->{VERBOSE};
		return undef;
	}
}

# Wraps a function call in a cache lookup
# Kinda like a poor mans memoize
sub wrap {
	my ($self, $key, $valid_for, $func, $args) = @_;

	if ($args and ref $args eq 'HASH') {
		$key = join ':', $key, map { "$_=$args->{$_}" } sort keys %$args;
	}

	if (my $res = $self->get($key)) {
		return $res;
	}

	my $res = $func->($args);
	$self->set($key, $valid_for, $res);
	return $res;
}

1;

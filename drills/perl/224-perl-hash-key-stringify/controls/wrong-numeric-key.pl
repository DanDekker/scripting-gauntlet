#!/usr/bin/env perl
# Plausible bug: coerces the lookup key to a number before looking it up, so "007"
# becomes 7 and "1.0" becomes 1 and neither matches the filed key.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my %inventory;
{
    open my $fh, '<', "$IN/inventory.txt" or die "cannot read inventory.txt: $!\n";
    while (my $line = <$fh>) {
        chomp $line;
        next if $line eq '';
        my ($key, $name) = split / /, $line, 2;
        $inventory{$key} = $name;
    }
    close $fh;
}

my @lookups;
{
    open my $fh, '<', "$IN/lookups.txt" or die "cannot read lookups.txt: $!\n";
    while (my $line = <$fh>) {
        chomp $line;
        next if $line eq '';
        push @lookups, $line;
    }
    close $fh;
}

my (@rows, $hits, $misses);
my $index = 0;
for my $lookup (@lookups) {
    $index++;
    # BUG: a hash key is a string; this changes 007 to 7 and 1.0 to 1.
    my $key = 0 + $lookup;
    if (exists $inventory{$key}) {
        $hits++;
        push @rows, [ $index, $lookup, 'hit', $inventory{$key} ];
    }
    else {
        $misses++;
        push @rows, [ $index, $lookup, 'miss', '' ];
    }
}

open my $out, '>', "$OUT/lookups.csv" or die "cannot write lookups.csv: $!\n";
print {$out} "index,lookup,status,name\n";
for my $row (@rows) {
    print {$out} join(',', @$row), "\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"lookups\":%d,\"hits\":%d,\"misses\":%d}\n",
    scalar(@rows), $hits, $misses;
close $sum;

#!/usr/bin/env perl
# 224-perl-hash-key-stringify — look the key up as the text that was read.
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
    if (exists $inventory{$lookup}) {
        $hits++;
        push @rows, [ $index, $lookup, 'hit', $inventory{$lookup} ];
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

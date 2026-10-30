#!/usr/bin/env perl
# 213-perl-truthy-zero — use perl's own truth test on the value.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

open my $fh, '<', "$IN/settings.txt" or die "cannot read settings.txt: $!\n";
my @rows;
my $index = 0;
while (my $line = <$fh>) {
    chomp $line;
    next if $line eq '';
    $index++;
    my ($name, $value) = split / /, $line, 2;
    $value = '' unless defined $value;
    # Perl's rule: only "" and "0" are false.
    my $state = $value ? 'on' : 'off';
    push @rows, [ $index, $name, $value, $state ];
}
close $fh;

my $on = 0;
for my $row (@rows) {
    $on++ if $row->[3] eq 'on';
}

open my $out, '>', "$OUT/settings.csv" or die "cannot write settings.csv: $!\n";
print {$out} "index,name,value,state\n";
for my $row (@rows) {
    print {$out} join(',', @$row), "\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"settings\":%d,\"on\":%d,\"off\":%d}\n",
    scalar(@rows), $on, scalar(@rows) - $on;
close $sum;

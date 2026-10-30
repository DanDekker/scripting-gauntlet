#!/usr/bin/env perl
# Plausible bug: decides falsiness with a regex over common "off" words, which is
# not perl's rule: false, no and 0.0 are all true strings in perl.
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
    # BUG: a hand-rolled rule, not perl's truth test.
    my $state = ($value eq '' || $value =~ /^(0|false|no|off)$/i) ? 'off' : 'on';
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

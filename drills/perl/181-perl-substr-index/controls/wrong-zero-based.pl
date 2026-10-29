#!/usr/bin/env perl
# Plausible bug: reports the 0-based index() result without converting to a 1-based column.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my @rows;
my $total_pairs = 0;

open my $fh, '<', "$IN/pairs.txt" or die "cannot read pairs.txt: $!\n";
while (my $line = <$fh>) {
    chomp $line;
    $line =~ s/^\s+//;
    $line =~ s/\s+$//;
    next if $line eq '' or $line =~ /^#/;

    my $first_eq  = index($line, '=');
    my $first     = $first_eq >= 0 ? substr($line, 0, $first_eq) : $line;

    my $last_start = rindex($line, ';') + 1;
    my $last_eq    = index($line, '=', $last_start);
    my $last       = $last_eq >= 0 ? substr($line, $last_start, $last_eq - $last_start) : '';

    my $pairs = () = $line =~ /=/g;
    $total_pairs += $pairs;

    my $second = $first_eq >= 0 ? index($line, '=', $first_eq + 1) : -1;
    my $second_eq = $second >= 0 ? $second : '';  # 0-based, reported as-is

    my $head = substr($line, 0, 5);

    push @rows, [ scalar(@rows) + 1, $first, $last, $pairs, $second_eq, $head ];
}
close $fh;

open my $out, '>', "$OUT/fields.csv" or die "cannot write fields.csv: $!\n";
print {$out} "line,first,last,pairs,second_eq,head\n";
for my $row (@rows) { print {$out} join(',', @$row), "\n" }
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"lines\":%d,\"pairs\":%d}\n", scalar(@rows), $total_pairs;
close $sum;

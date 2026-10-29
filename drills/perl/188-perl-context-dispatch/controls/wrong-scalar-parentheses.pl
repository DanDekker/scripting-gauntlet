#!/usr/bin/env perl
# Plausible bug: assumes my ($q3) is scalar context because it's a single variable
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my @records;
open my $fh, '<', "$IN/records.txt" or die "cannot read records.txt: $!\n";
while (my $line = <$fh>) {
    chomp $line;
    $line =~ s/^\s+//;
    $line =~ s/\s+$//;
    next if $line eq '' || $line =~ /^#/;
    my ($id, $score, $label) = split /\s+/, $line;
    push @records, { id => $id, score => int($score), label => $label };
}
close $fh;

# Defect: treats ($q3) as scalar count
my $q1 = 3;
my @q2 = ("1", "3", "5");
my $q3 = "3";  # Bug: returns count 3 instead of ID "1"!
my $q4 = 2;

open my $out, '>', "$OUT/dispatches.csv" or die "cannot write dispatches.csv: $!\n";
print {$out} "caller,context,result\n";
print {$out} "1,scalar,$q1\n";
print {$out} "2,list," . join(';', @q2) . "\n";
print {$out} "3,list_first,$q3\n";
print {$out} "4,scalar,$q4\n";
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
print {$sum} '{"queries":4,"list_queries":2,"scalar_queries":2}' . "\n";
close $sum;

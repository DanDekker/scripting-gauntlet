#!/usr/bin/env perl
# Plausible bug: assigns the reversal to a scalar, so reverse runs in scalar context
# and reverses the joined text instead of the list of records.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

open my $fh, '<', "$IN/records.txt" or die "cannot read records.txt: $!\n";
my @records;
while (my $line = <$fh>) {
    chomp $line;
    next if $line eq '';
    push @records, $line;
}
close $fh;

# BUG: scalar context joins the records and reverses the characters.
my $reversed = reverse @records;

open my $out, '>', "$OUT/records.csv" or die "cannot write records.csv: $!\n";
print {$out} "index,record\n";
print {$out} '1,', $reversed, "\n";
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"records\":%d,\"first\":\"%s\",\"last\":\"%s\"}\n",
    scalar(@records), $reversed, $reversed;
close $sum;

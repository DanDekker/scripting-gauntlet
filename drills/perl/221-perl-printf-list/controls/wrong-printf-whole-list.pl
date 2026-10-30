#!/usr/bin/env perl
# Plausible bug: passes the whole list to printf, which applies the format once and
# calls the remaining records redundant, so only the first record is written.
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

my $lines = 0;
open my $out, '>', "$OUT/report.txt" or die "cannot write report.txt: $!\n";
{
    # BUG: the format runs once; the rest of the list is redundant.
    local $SIG{__WARN__} = sub { };
    printf {$out} "%s\n", @records;
    $lines = 1;
}
close $out;

my $last = @records ? $records[-1] : '';

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"records\":%d,\"lines\":%d,\"last\":\"%s\"}\n",
    scalar(@records), $lines, $last;
close $sum;

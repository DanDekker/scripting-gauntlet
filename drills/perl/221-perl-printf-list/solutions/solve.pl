#!/usr/bin/env perl
# 221-perl-printf-list — one printf call per record, so one line per record.
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
for my $record (@records) {
    printf {$out} "%s\n", $record;   # one call per record
    $lines++;
}
close $out;

my $last = @records ? $records[-1] : '';

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"records\":%d,\"lines\":%d,\"last\":\"%s\"}\n",
    scalar(@records), $lines, $last;
close $sum;

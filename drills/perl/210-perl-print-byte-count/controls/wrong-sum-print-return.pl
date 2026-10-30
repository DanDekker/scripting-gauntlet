#!/usr/bin/env perl
# Plausible bug: adds up print's return value, which is 1 per successful call,
# so the reported size is the number of items (4) instead of the byte count (26).
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

open my $fh, '<', "$IN/items.txt" or die "cannot read items.txt: $!\n";
my @items;
while (my $line = <$fh>) {
    chomp $line;
    push @items, $line;
}
close $fh;

my $bytes = 0;
open my $out, '>', "$OUT/report.txt" or die "cannot write report.txt: $!\n";
for my $item (@items) {
    # BUG: print returns 1 per call, not the number of bytes written.
    $bytes += print {$out} "$item\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"items\":%d,\"bytes\":%d}\n", scalar(@items), $bytes;
close $sum;

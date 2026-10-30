#!/usr/bin/env perl
# 210-perl-print-byte-count — measure the bytes, do not count print's return value.
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
    my $text = "$item\n";
    print {$out} $text;
    $bytes += length($text);   # the text was read as bytes, so this is bytes
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"items\":%d,\"bytes\":%d}\n", scalar(@items), $bytes;
close $sum;

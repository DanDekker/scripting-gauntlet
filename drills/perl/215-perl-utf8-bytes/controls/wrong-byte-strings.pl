#!/usr/bin/env perl
# Plausible bug: reads the file as raw bytes, so length() counts bytes and uc only
# uppercases the ASCII letters.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my @names;
{
    # BUG: no encoding layer, so the strings stay bytes.
    open my $fh, '<', "$IN/names.txt" or die "cannot read names.txt: $!\n";
    while (my $line = <$fh>) {
        chomp $line;
        next if $line eq '';
        push @names, $line;
    }
    close $fh;
}

my $total = 0;
my $longest = 0;

open my $out, '>:encoding(UTF-8)', "$OUT/names.csv" or die "cannot write names.csv: $!\n";
print {$out} "index,name,chars\n";
my $index = 0;
for my $name (@names) {
    $index++;
    my $chars = length($name);        # BUG: bytes, not characters
    my $upper = uc $name;              # BUG: only the ASCII letters change
    $total += $chars;
    $longest = $chars if $chars > $longest;
    print {$out} $index, ',', $upper, ',', $chars, "\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"names\":%d,\"chars\":%d,\"longest\":%d}\n", scalar(@names), $total, $longest;
close $sum;

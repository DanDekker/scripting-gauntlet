#!/usr/bin/env perl
# 215-perl-utf8-bytes — decode on the way in, encode on the way out.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my @names;
{
    # The encoding layer decodes the bytes into characters.
    open my $fh, '<:encoding(UTF-8)', "$IN/names.txt" or die "cannot read names.txt: $!\n";
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
    my $chars = length($name);        # characters, because the string is decoded
    my $upper = uc $name;              # uppercases every character
    $total += $chars;
    $longest = $chars if $chars > $longest;
    print {$out} $index, ',', $upper, ',', $chars, "\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"names\":%d,\"chars\":%d,\"longest\":%d}\n", scalar(@names), $total, $longest;
close $sum;

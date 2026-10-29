#!/usr/bin/env perl
# Plausible bug: matches the value again inside the replacement block, which clobbers $1
# before it is used, so every key becomes the first character of its own value.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my @rows;
my $total = 0;

open my $fh, '<', "$IN/assignments.txt" or die "cannot read assignments.txt: $!\n";
while (my $line = <$fh>) {
    chomp $line;
    $line =~ s/^\s+//;
    $line =~ s/\s+$//;
    next if $line eq '' or $line =~ /^#/;

    my $count = ($line =~ s{(\w+)=(\S*)}{
        $2 =~ /(\w)/;                    # nested match: $1 is now the value's first char
        uc($1) . ":" . uc($2)
    }ge);

    $total += $count;
    push @rows, [ scalar(@rows) + 1, $line, $count ];
}
close $fh;

open my $out, '>', "$OUT/rewritten.csv" or die "cannot write rewritten.csv: $!\n";
print {$out} "line,text,substitutions\n";
for my $row (@rows) { print {$out} join(',', @$row), "\n" }
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"lines\":%d,\"substitutions\":%d}\n", scalar(@rows), $total;
close $sum;

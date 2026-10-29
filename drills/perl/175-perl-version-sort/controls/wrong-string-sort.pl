#!/usr/bin/env perl
# Plausible bug: sorts the version text with cmp instead of comparing components.
use strict;
use warnings;
use version;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my @rows;
my $lines   = 0;
my $invalid = 0;

open my $fh, '<', "$IN/releases.txt" or die "cannot read releases.txt: $!\n";
while (my $line = <$fh>) {
    chomp $line;
    $line =~ s/^\s+//;
    $line =~ s/\s+$//;
    next if $line eq '' or $line =~ /^#/;
    $lines++;

    my ($name, $ver) = split ' ', $line, 2;
    if (not defined $ver or $ver !~ /^[0-9]+(\.[0-9]+)*$/) {
        $invalid++;
        next;
    }
    push @rows, [ $name, $ver, version->parse($ver) ];
}
close $fh;

# newest first; ties by name
@rows = sort {
    $b->[1] cmp $a->[1] or $a->[0] cmp $b->[0]
} @rows;

open my $out, '>', "$OUT/ordered.csv" or die "cannot write ordered.csv: $!\n";
print {$out} "rank,name,version\n";
my $rank = 0;
for my $row (@rows) {
    $rank++;
    print {$out} "$rank,$row->[0],$row->[1]\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"lines\":%d,\"ordered\":%d,\"invalid\":%d,\"newest\":\"%s\"}\n",
    $lines, scalar(@rows), $invalid, (@rows ? $rows[0][0] : '');
close $sum;

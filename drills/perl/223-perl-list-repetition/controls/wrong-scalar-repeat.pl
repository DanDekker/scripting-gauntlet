#!/usr/bin/env perl
# Plausible bug: repeats a scalar with x, which concatenates the string, so the whole
# export collapses into one line.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my ($count, $template);
{
    open my $fh, '<', "$IN/spec.txt" or die "cannot read spec.txt: $!\n";
    while (my $line = <$fh>) {
        chomp $line;
        next if $line eq '';
        if ($line =~ /^count=(.*)$/) { $count = $1 + 0; }
        elsif ($line =~ /^template=(.*)$/) { $template = $1; }
    }
    close $fh;
}
$count  = 0 unless defined $count;
$template = '' unless defined $template;

# BUG: a scalar on the left of x repeats the string, so this is ONE element.
my @rows = $template x $count;

open my $out, '>', "$OUT/report.txt" or die "cannot write report.txt: $!\n";
for my $row (@rows) {
    print {$out} $row, "\n";
}
close $out;

my $chars = 0;
$chars += length($_) for @rows;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"count\":%d,\"lines\":%d,\"chars\":%d}\n",
    $count, scalar(@rows), $chars;
close $sum;

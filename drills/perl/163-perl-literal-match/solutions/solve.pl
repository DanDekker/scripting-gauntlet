#!/usr/bin/env perl
# 163-perl-literal-match — index() for literals, never /$pattern/.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my @rows;
my ($lines, $matched, $invalid) = (0, 0, 0);

open my $fh, '<', "$IN/queries.txt" or die "cannot read queries.txt: $!\n";
while (my $line = <$fh>) {
    chomp $line;
    $line =~ s/^\s+//;
    $line =~ s/\s+$//;
    next if $line eq '' or $line =~ /^#/;

    my $bar = index($line, '|');
    if ($bar < 0) {
        $invalid++;
        next;
    }
    my $pattern = substr($line, 0, $bar);
    my $subject = substr($line, $bar + 1);
    $pattern =~ s/^\s+//; $pattern =~ s/\s+$//;
    $subject =~ s/^\s+//; $subject =~ s/\s+$//;

    $lines++;
    my $first = length($pattern) ? index($subject, $pattern) : -1;
    my $count = 0;
    if (length($pattern)) {
        my $at = 0;
        while (($at = index($subject, $pattern, $at)) >= 0) {
            $count++;
            $at += length($pattern);    # non-overlapping
        }
    }
    my ($found, $position) = (0, '');
    if ($first >= 0) {
        $found = 1;
        $position = $first + 1;
        $matched++;
    }
    push @rows, [$pattern, $found, $position, $count];
}
close $fh;

open my $out, '>', "$OUT/matches.csv" or die "cannot write matches.csv: $!\n";
print {$out} "pattern,found,position,count\n";
for my $row (@rows) {
    print {$out} join(',', @$row), "\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"lines\":%d,\"matched\":%d,\"invalid\":%d}\n",
    $lines, $matched, $invalid;
close $sum;

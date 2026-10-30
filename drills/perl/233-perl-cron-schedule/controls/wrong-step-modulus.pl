#!/usr/bin/env perl
# Plausible bug: fails to handle */N step expressions properly, comparing equality instead of modulus.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my %target;
open my $tfh, '<', "$IN/target.ini" or die "cannot read target.ini: $!\n";
while (my $line = <$tfh>) {
    chomp $line;
    $line =~ s/\s*#.*//;
    if ($line =~ /^\s*(\w+)\s*=\s*(\d+)\s*$/) {
        $target{$1} = $2 + 0;
    }
}
close $tfh;

sub match_field {
    my ($spec, $val) = @_;
    return 1 if $spec eq '*';
    # BUG: treats */15 as testing equality with 15 rather than modulus
    if ($spec =~ m{^\*/(\d+)$}) {
        return ($val == $1);
    }
    for my $part (split /,/, $spec) {
        if ($part =~ /^(\d+)-(\d+)$/) {
            return 1 if $val >= $1 && $val <= $2;
        }
        elsif ($part =~ /^\d+$/) {
            return 1 if $val == $part;
        }
    }
    return 0;
}

my @matched;
my $total = 0;

open my $cfh, '<', "$IN/crontab.txt" or die "cannot read crontab.txt: $!\n";
while (my $line = <$cfh>) {
    chomp $line;
    $line =~ s/^\s+//;
    $line =~ s/\s+$//;
    next unless length $line;
    next if $line =~ /^#/;

    $total++;

    my @parts = split /\s+/, $line, 6;
    my ($f_min, $f_hour, $f_dom, $f_mon, $f_dow, $cmd) = @parts;

    if (match_field($f_min, $target{minute}) &&
        match_field($f_hour, $target{hour}) &&
        match_field($f_dom, $target{dom}) &&
        match_field($f_mon, $target{month}) &&
        match_field($f_dow, $target{dow})) {
        push @matched, $cmd;
    }
}
close $cfh;

open my $out, '>', "$OUT/matched.txt" or die "cannot write matched.txt: $!\n";
for my $cmd (@matched) {
    print {$out} "$cmd\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"total_entries\":%d,\"matched\":%d}\n", $total, scalar(@matched);
close $sum;

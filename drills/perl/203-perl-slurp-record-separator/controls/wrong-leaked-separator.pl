#!/usr/bin/env perl
# Plausible bug: slurps the config with a global $/ = undef and never restores
# it, so every later readline returns the whole notes file as one record.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

open my $cfh, '<', "$IN/config.ini" or die "cannot read config.ini: $!\n";
$/ = undef;                       # BUG: global, never restored
my $config = <$cfh>;
close $cfh;

my $config_lines = ($config =~ tr/\n//);

my $settings = 0;
for my $line (split /\n/, $config) {
    next if $line =~ /^\s*$/;
    next if $line =~ /^\s*#/;
    $settings++ if $line =~ /^\s*[A-Za-z_][A-Za-z0-9_]*=/;
}

my @rows;
my $total_lines = 0;
{
    open my $fh, '<', "$IN/notes.txt" or die "cannot read notes.txt: $!\n";
    my $index = 0;
    while (my $record = <$fh>) {
        # $/ is still undef, so this is the whole file in one string.
        chomp $record;
        next if $record eq '';
        $index++;
        my @lines = split /\n/, $record, -1;
        my $title = $lines[0];
        my $count = scalar @lines;
        $total_lines += $count;
        push @rows, [ $index, $title, $count ];
    }
    close $fh;
}

open my $out, '>', "$OUT/records.csv" or die "cannot write records.csv: $!\n";
print {$out} "index,title,lines\n";
for my $r (@rows) {
    print {$out} join(',', @$r), "\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"records\":%d,\"total_lines\":%d,\"config_lines\":%d,\"settings\":%d}\n",
    scalar(@rows), $total_lines, $config_lines, $settings;
close $sum;

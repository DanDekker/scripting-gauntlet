#!/usr/bin/env perl
# 230-perl-ini-config — parse INI configs with inline comments and fallback.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my %cfg;
my $cur = 'default';

open my $fh, '<', "$IN/config.ini" or die "cannot read config.ini: $!\n";
while (my $line = <$fh>) {
    chomp $line;
    # Strip comments (# or ;) and preceding whitespace
    $line =~ s/\s*[#;].*//;
    $line =~ s/^\s+//;
    $line =~ s/\s+$//;
    next unless length $line;

    if ($line =~ /^\[(\w+)\]$/) {
        $cur = $1;
    }
    elsif ($line =~ /^(\w+)\s*=\s*(.+)$/) {
        my ($k, $v) = ($1, $2);
        $v =~ s/\s+$//;
        $cfg{$cur}{$k} = $v;
    }
}
close $fh;

my @queries;
open my $qfh, '<', "$IN/queries.csv" or die "cannot read queries.csv: $!\n";
my $header = <$qfh>;
while (my $line = <$qfh>) {
    chomp $line;
    next if $line =~ /^\s*$/;
    my ($sec, $key) = split /,/, $line, 2;
    push @queries, [ $sec, $key ];
}
close $qfh;

my @rows;
my %counts = (section => 0, default => 0, none => 0);

for my $q (@queries) {
    my ($sec, $key) = @$q;
    my ($val, $source);

    if (exists $cfg{$sec} && exists $cfg{$sec}{$key}) {
        $val    = $cfg{$sec}{$key};
        $source = 'section';
    }
    elsif (exists $cfg{default} && exists $cfg{default}{$key}) {
        $val    = $cfg{default}{$key};
        $source = 'default';
    }
    else {
        $val    = 'MISSING';
        $source = 'none';
    }

    $counts{$source}++;
    push @rows, [ $sec, $key, $val, $source ];
}

open my $out, '>', "$OUT/answers.csv" or die "cannot write answers.csv: $!\n";
print {$out} "section,key,value,source\n";
for my $r (@rows) {
    print {$out} join(',', @$r), "\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"queries\":%d,\"section\":%d,\"default\":%d,\"missing\":%d}\n",
    scalar(@rows), $counts{section}, $counts{default}, $counts{none};
close $sum;

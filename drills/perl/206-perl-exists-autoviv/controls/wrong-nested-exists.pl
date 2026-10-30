#!/usr/bin/env perl
# Plausible bug: uses a nested exists to test for a key, which autovivifies the
# intermediate section hash and leaves an empty `cache` section in the config.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my %cfg;
{
    open my $fh, '<', "$IN/base.conf" or die "cannot read base.conf: $!\n";
    my $section;
    while (my $line = <$fh>) {
        chomp $line;
        $line =~ s/^\s+//;
        $line =~ s/\s+$//;
        next if $line eq '' || $line =~ /^#/;
        if ($line =~ /^\[(.+)\]$/) {
            $section = $1;
            $cfg{$section} = {} unless exists $cfg{$section};
            next;
        }
        next unless defined $section;
        if ($line =~ /^([^=]+)=(.*)$/) {
            $cfg{$section}{$1} = $2;
        }
    }
    close $fh;
}

my @rows;
my $present_count = 0;
{
    open my $fh, '<', "$IN/wanted.conf" or die "cannot read wanted.conf: $!\n";
    my $index = 0;
    while (my $line = <$fh>) {
        chomp $line;
        $line =~ s/^\s+//;
        $line =~ s/\s+$//;
        next if $line eq '' || $line =~ /^#/;
        my ($section, $key) = split /\./, $line, 2;
        $index++;

        # BUG: a nested exists creates $cfg{$section} when the section is missing.
        my $present = exists $cfg{$section}{$key} ? 1 : 0;
        my $status = $present ? 'present' : 'missing';
        $present_count++ if $present;
        push @rows, [ $index, $section, $key, $status ];
    }
    close $fh;
}

open my $out, '>', "$OUT/missing.csv" or die "cannot write missing.csv: $!\n";
print {$out} "index,section,key,status\n";
for my $r (@rows) {
    print {$out} join(',', @$r), "\n";
}
close $out;

open my $dump, '>', "$OUT/dump.csv" or die "cannot write dump.csv: $!\n";
print {$dump} "section,keys\n";
for my $section (sort keys %cfg) {
    print {$dump} $section, ',', scalar(keys %{ $cfg{$section} }), "\n";
}
close $dump;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"wanted\":%d,\"present\":%d,\"missing\":%d,\"sections\":%d}\n",
    scalar(@rows), $present_count, scalar(@rows) - $present_count, scalar(keys %cfg);
close $sum;

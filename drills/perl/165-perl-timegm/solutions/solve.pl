#!/usr/bin/env perl
# 165-perl-timegm — month is 0-based, year is 1900-based, and the round trip proves it.
use strict;
use warnings;
use Time::Local qw(timegm);

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my @rows;
my $lines = 0;
my $invalid = 0;

open my $fh, '<', "$IN/stamps.txt" or die "cannot read stamps.txt: $!\n";
while (my $line = <$fh>) {
    chomp $line;
    $line =~ s/^\s+//;
    $line =~ s/\s+$//;
    next if $line eq '' or $line =~ /^#/;
    $lines++;

    my ($year, $mon, $mday, $hour, $min, $sec) =
        $line =~ /^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})Z$/;
    if (not defined $year) {
        $invalid++;
        next;
    }

    # month is 0-based, and the year must go in as the 4-digit year: Time::Local maps
    # a years-since-1900 value in 0..99 to 2000..2099, so 1970-1900 would be 2070.
    my $epoch;
    my $ok = eval {
        $epoch = timegm($sec, $min, $hour, $mday, $mon - 1, $year);
        1;
    };
    if (not $ok) {
        $invalid++;
        next;
    }

    # round trip: the calendar rolled impossible dates forward, so compare the fields
    my @back = gmtime($epoch);
    if ($back[5] + 1900 != $year || $back[4] + 1 != $mon || $back[3] != $mday) {
        $invalid++;
        next;
    }

    push @rows, [$line, $epoch];
}
close $fh;

@rows = sort { $a->[1] <=> $b->[1] or $a->[0] cmp $b->[0] } @rows;

open my $out, '>', "$OUT/epochs.csv" or die "cannot write epochs.csv: $!\n";
print {$out} "stamp,epoch\n";
for my $row (@rows) {
    print {$out} "$row->[0],$row->[1]\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
my $first = @rows ? $rows[0][1]  : '""';
my $last  = @rows ? $rows[-1][1] : '""';
printf {$sum} "{\"lines\":%d,\"valid\":%d,\"invalid\":%d,\"first\":%s,\"last\":%s}\n",
    $lines, scalar(@rows), $invalid, $first, $last;
close $sum;

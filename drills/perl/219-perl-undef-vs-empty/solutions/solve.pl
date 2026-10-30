#!/usr/bin/env perl
# 219-perl-undef-vs-empty — exists tells absent apart from present-and-empty.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my %cfg;
{
    open my $fh, '<', "$IN/config.ini" or die "cannot read config.ini: $!\n";
    while (my $line = <$fh>) {
        chomp $line;
        next if $line eq '';
        my ($key, $value) = split /=/, $line, 2;
        $cfg{$key} = defined $value ? $value : '';
    }
    close $fh;
}

my @wanted;
{
    open my $fh, '<', "$IN/wanted.txt" or die "cannot read wanted.txt: $!\n";
    while (my $line = <$fh>) {
        chomp $line;
        next if $line eq '';
        push @wanted, $line;
    }
    close $fh;
}

my (@rows, $set, $empty, $missing);
my $index = 0;
for my $key (@wanted) {
    $index++;
    if (!exists $cfg{$key}) {
        $missing++;
        push @rows, [ $index, $key, 'missing', '' ];
    }
    elsif ($cfg{$key} eq '') {
        $empty++;
        push @rows, [ $index, $key, 'empty', '' ];
    }
    else {
        $set++;
        push @rows, [ $index, $key, 'set', $cfg{$key} ];
    }
}

open my $out, '>', "$OUT/settings.csv" or die "cannot write settings.csv: $!\n";
print {$out} "index,key,status,value\n";
for my $row (@rows) {
    print {$out} join(',', @$row), "\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"wanted\":%d,\"set\":%d,\"empty\":%d,\"missing\":%d}\n",
    scalar(@rows), $set, $empty, $missing;
close $sum;

#!/usr/bin/env perl
# 162-perl-numify — validate the text, then convert; never numify first.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my @rows;
my %count = (int => 0, decimal => 0, invalid => 0);

open my $fh, '<', "$IN/values.txt" or die "cannot read values.txt: $!\n";
while (my $line = <$fh>) {
    chomp $line;
    $line =~ s/^\s+//;
    $line =~ s/\s+$//;
    next if $line eq '';

    my $kind    = 'invalid';
    my $intpart = '';
    if ($line =~ /^[+-]?([0-9]+(\.[0-9]*)?|\.[0-9]+)$/) {
        $kind    = ($line =~ /\./) ? 'decimal' : 'int';
        $intpart = int($line);    # truncates toward zero
    }
    $count{$kind}++;
    push @rows, [$line, $kind, $intpart];
}
close $fh;

open my $out, '>', "$OUT/values.csv" or die "cannot write values.csv: $!\n";
print {$out} "token,kind,int_part\n";
for my $row (@rows) {
    print {$out} join(',', @$row), "\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"rows\":%d,\"int\":%d,\"decimal\":%d,\"invalid\":%d}\n",
    scalar(@rows), $count{int}, $count{decimal}, $count{invalid};
close $sum;

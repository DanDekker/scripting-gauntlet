#!/usr/bin/env perl
# Plausible bug: lets perl numify the token instead of checking the grammar, so
# '0x10' becomes the integer 0 and 'abc' becomes 0 as well.
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

    my $kind = ($line =~ /\./) ? 'decimal' : 'int';
    my $intpart = int($line + 0);
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

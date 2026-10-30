#!/usr/bin/env perl
# 214-perl-split-captures — split on whitespace with a pattern that captures nothing.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

open my $fh, '<', "$IN/access.log" or die "cannot read access.log: $!\n";
my @rows;
while (my $line = <$fh>) {
    chomp $line;
    next if $line =~ /^\s*$/;
    # No capture group, so the fields are the fields.
    my @fields = split ' ', $line;
    next if @fields < 4;
    push @rows, [ @fields[0 .. 3] ];
}
close $fh;

my $ok = 0;
my $errors = 0;

open my $out, '>', "$OUT/access.csv" or die "cannot write access.csv: $!\n";
print {$out} "index,timestamp,method,path,status\n";
my $index = 0;
for my $row (@rows) {
    $index++;
    print {$out} join(',', $index, @$row), "\n";
    if ($row->[3] =~ /^2/) { $ok++ } else { $errors++ }
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"records\":%d,\"ok\":%d,\"errors\":%d}\n", scalar(@rows), $ok, $errors;
close $sum;

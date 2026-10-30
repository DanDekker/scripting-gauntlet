#!/usr/bin/env perl
# 208-perl-crlf-strip — strip the whole CRLF terminator, not just the newline.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

open my $fh, '<', "$IN/measurements.csv" or die "cannot read measurements.csv: $!\n";
my $header = <$fh>;
my @rows;
while (my $line = <$fh>) {
    chomp $line;            # removes the "\n"
    $line =~ s/\r\z//;      # the file is CRLF: drop the carriage return too
    next if $line eq '';
    my ($sensor, $label, $value) = split /,/, $line, -1;
    my $status = ($value =~ /^[0-9]+\.[0-9]+$/) ? 'ok' : 'malformed';
    push @rows, [ $sensor, $label, $value, $status ];
}
close $fh;

my $valid = 0;
my $malformed = 0;
for my $r (@rows) {
    $r->[3] eq 'ok' ? $valid++ : $malformed++;
}

open my $out, '>', "$OUT/readings.csv" or die "cannot write readings.csv: $!\n";
print {$out} "sensor,label,value,status\n";
for my $r (@rows) {
    print {$out} join(',', @$r), "\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"readings\":%d,\"valid\":%d,\"malformed\":%d}\n",
    scalar(@rows), $valid, $malformed;
close $sum;

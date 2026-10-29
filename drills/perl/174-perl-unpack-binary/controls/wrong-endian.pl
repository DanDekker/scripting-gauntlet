#!/usr/bin/env perl
# Plausible bug: uses the little-endian template for the score.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

open my $fh, '<:raw', "$IN/records.bin" or die "cannot read records.bin: $!\n";
my $data = do { local $/; <$fh> };
close $fh;

my $total = length $data;
if ($total < 4 || substr($data, 0, 4) ne 'SRV1') {
    die "records.bin: bad magic (expected SRV1)\n";
}

my $offset = 4;
my @rows;
my $truncated = 0;

while ($offset < $total) {
    my $remaining = $total - $offset;
    if ($remaining < 8) {
        $truncated++;
        last;
    }
    my ($id, $score, $flags, $len) = unpack('N v C C', substr($data, $offset, 8));
    if ($remaining < 8 + $len) {
        $truncated++;
        last;
    }
    my $name = $len ? substr($data, $offset + 8, $len) : '';
    $offset += 8 + $len;
    push @rows, [$id, $score, $flags, $name];
}

@rows = sort { $a->[0] <=> $b->[0] } @rows;

open my $out, '>', "$OUT/records.csv" or die "cannot write records.csv: $!\n";
print {$out} "id,score,flags,name\n";
for my $row (@rows) {
    print {$out} join(',', @$row), "\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"records\":%d,\"truncated\":%d,\"bytes_read\":%d,\"bytes_total\":%d}\n",
    scalar(@rows), $truncated, $offset, $total;
close $sum;

#!/usr/bin/env perl
# 217-perl-reverse-context — reverse the LIST, not the joined text.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

open my $fh, '<', "$IN/records.txt" or die "cannot read records.txt: $!\n";
my @records;
while (my $line = <$fh>) {
    chomp $line;
    next if $line eq '';
    push @records, $line;
}
close $fh;

# List context: the list is reversed, one element per record.
my @reversed = reverse @records;

open my $out, '>', "$OUT/records.csv" or die "cannot write records.csv: $!\n";
print {$out} "index,record\n";
my $index = 0;
for my $record (@reversed) {
    $index++;
    print {$out} $index, ',', $record, "\n";
}
close $out;

my $first = @reversed ? $reversed[0] : '';
my $last  = @reversed ? $reversed[-1] : '';

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"records\":%d,\"first\":\"%s\",\"last\":\"%s\"}\n",
    scalar(@records), $first, $last;
close $sum;

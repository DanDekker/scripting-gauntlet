#!/usr/bin/env perl
# 193-perl-regex-lookaround — lookbehind for boundaries, lookahead for overlaps
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my @records;
my $curr_count = 0;
my $motif_count = 0;

open my $fh, '<', "$IN/stream.txt" or die "cannot read stream.txt: $!\n";
while (my $line = <$fh>) {
    chomp $line;
    $line =~ s/^\s+//;
    $line =~ s/\s+$//;
    next if $line eq '' || $line =~ /^#/;

    if ($line =~ /^(AUDIT\d+):(.*)$/) {
        my ($id, $rest) = ($1, $2);
        while ($rest =~ /(?<!\w)(USD|EUR|GBP)(\d+)(?=[,\s\.]|$)/g) {
            push @records, [ $id, "currency", $1, int($2) ];
            $curr_count++;
        }
    }
    elsif ($line =~ /^(MOTIF\d+):\s*target=(\S+)\s+seq=(\S+)/) {
        my ($id, $target, $seq) = ($1, $2, $3);
        while ($seq =~ /(?=(\Q$target\E))/g) {
            my $motif = $1;
            my $offset = $-[0] + 1; # 1-based offset
            push @records, [ $id, "motif", $motif, $offset ];
            $motif_count++;
        }
    }
}
close $fh;

open my $out, '>', "$OUT/extractions.csv" or die "cannot write extractions.csv: $!\n";
print {$out} "id,type,key,val\n";
for my $r (@records) {
    print {$out} join(',', @$r), "\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"records\":%d,\"currencies\":%d,\"motifs\":%d}\n",
    scalar(@records), $curr_count, $motif_count;
close $sum;

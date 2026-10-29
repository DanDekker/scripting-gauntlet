#!/usr/bin/env perl
# 161-perl-split-limits — the limit of -1 keeps trailing empty fields.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my @rows;
my ($rows, $empty_notes, $empty_scores, $invalid) = (0, 0, 0, 0);

open my $fh, '<', "$IN/rows.txt" or die "cannot read rows.txt: $!\n";
while (my $line = <$fh>) {
    chomp $line;
    $line =~ s/^\s+//;
    $line =~ s/\s+$//;
    next if $line eq '' or $line =~ /^#/;

    # -1 keeps the trailing empty field: without it, 'bob:user:ok:' is three fields
    my @field = split /:/, $line, -1;
    if (@field != 4) {
        $invalid++;
        next;
    }
    my ($name, $role, $note, $score) = @field;
    if ($name eq '' or $role eq '') {
        $invalid++;
        next;
    }
    if ($score ne '' and $score !~ /^[0-9]+$/) {
        $invalid++;
        next;
    }
    $rows++;
    $empty_notes++  if $note eq '';
    $empty_scores++ if $score eq '';
    push @rows, [$name, $role, $note, $score];
}
close $fh;

@rows = sort { $a->[0] cmp $b->[0] } @rows;

open my $out, '>', "$OUT/rows.csv" or die "cannot write rows.csv: $!\n";
print {$out} "name,role,note,score\n";
for my $row (@rows) {
    print {$out} join(',', @$row), "\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"rows\":%d,\"empty_notes\":%d,\"empty_scores\":%d,\"invalid\":%d}\n",
    $rows, $empty_notes, $empty_scores, $invalid;
close $sum;

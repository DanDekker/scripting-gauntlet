#!/usr/bin/env perl
# 188-perl-context-dispatch — context sensitivity with wantarray
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my @records;
open my $fh, '<', "$IN/records.txt" or die "cannot read records.txt: $!\n";
while (my $line = <$fh>) {
    chomp $line;
    $line =~ s/^\s+//;
    $line =~ s/\s+$//;
    next if $line eq '' || $line =~ /^#/;
    my ($id, $score, $label) = split /\s+/, $line;
    push @records, { id => $id, score => int($score), label => $label };
}
close $fh;

sub filter_scores {
    my ($threshold, @recs) = @_;
    my @matches = map { $_->{id} } grep { $_->{score} >= $threshold } @recs;

    if (!defined wantarray) {
        return;
    }
    return wantarray ? @matches : scalar @matches;
}

# 1. Scalar context: count
my $q1 = filter_scores(70, @records);

# 2. List context: all IDs
my @q2 = filter_scores(70, @records);

# 3. List context with single LHS var (parens force list context): first ID!
my ($q3) = filter_scores(70, @records);

# 4. Scalar context: count >= 90
my $q4 = filter_scores(90, @records);

open my $out, '>', "$OUT/dispatches.csv" or die "cannot write dispatches.csv: $!\n";
print {$out} "caller,context,result\n";
print {$out} "1,scalar,$q1\n";
print {$out} "2,list," . join(';', @q2) . "\n";
print {$out} "3,list_first,$q3\n";
print {$out} "4,scalar,$q4\n";
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
print {$sum} '{"queries":4,"list_queries":2,"scalar_queries":2}' . "\n";
close $sum;

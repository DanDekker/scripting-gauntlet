#!/usr/bin/env perl
# 228-perl-float-format — format the number; do not round it and format the rounded value.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my (@rows, $total, $max);
$total = 0;

{
    open my $fh, '<', "$IN/amounts.txt" or die "cannot read amounts.txt: $!\n";
    while (my $line = <$fh>) {
        chomp $line;
        $line =~ s/\A\s+//;
        $line =~ s/\s+\z//;
        next if $line eq '';
        next if $line =~ /\A#/;
        my ($label, $amount) = $line =~ /\A(\S+)\s+(\S+)\z/
            or die "cannot parse amounts.txt line: $line\n";

        my $value = $amount + 0;
        $total += $value;
        $max = $value if !defined $max || $value > $max;

        # plain: perl's default string context printing (15 significant digits).
        # cents: %.2f of the double, midpoint to even.
        # whole: %.0f of the double, midpoint to even.
        push @rows, [
            $label,
            sprintf('%s', $value),
            sprintf('%.2f', $value),
            sprintf('%.0f', $value),
        ];
    }
    close $fh;
}

open my $out, '>', "$OUT/amounts.csv" or die "cannot write amounts.csv: $!\n";
print {$out} "label,plain,cents,whole\n";
for my $row (@rows) {
    print {$out} join(',', @$row), "\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"amounts\":%d,\"total_cents\":\"%s\",\"max_plain\":\"%s\"}\n",
    scalar(@rows), sprintf('%.2f', $total), sprintf('%s', $max);
close $sum;

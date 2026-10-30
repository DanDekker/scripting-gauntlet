#!/usr/bin/env perl
# 235-perl-csv-parser — parse RFC 4180 CSV records with quotes.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

sub parse_csv_line {
    my ($line) = @_;
    my @fields;
    while ($line =~ /\G(?:^|,)(?:"([^"]*(?:""[^"]*)*)"|([^,]*))/g) {
        my $val = defined $1 ? $1 : (defined $2 ? $2 : '');
        $val =~ s/""/"/g;
        push @fields, $val;
    }
    return @fields;
}

my @valid_rows;
my $total_rows   = 0;
my $malformed    = 0;
my $total_amount = 0.0;

open my $fh, '<', "$IN/orders.csv" or die "cannot read orders.csv: $!\n";
my $header_line = <$fh>;
chomp $header_line;

while (my $line = <$fh>) {
    chomp $line;
    $line =~ s/\r$//;
    next if $line =~ /^\s*$/;

    $total_rows++;
    my @fields = parse_csv_line($line);

    if (scalar(@fields) != 5) {
        $malformed++;
        next;
    }

    push @valid_rows, \@fields;
    $total_amount += ($fields[3] + 0.0);
}
close $fh;

open my $out, '>', "$OUT/clean.tsv" or die "cannot write clean.tsv: $!\n";
print {$out} "order_id\tcustomer\tproduct\tamount\tnotes\n";
for my $r (@valid_rows) {
    print {$out} join("\t", @$r), "\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"total_rows\":%d,\"valid\":%d,\"malformed\":%d,\"total_amount\":%.2f}\n",
    $total_rows, scalar(@valid_rows), $malformed, $total_amount;
close $sum;

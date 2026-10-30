#!/usr/bin/env perl
# Plausible bug: sums the paid amounts with map in scalar context, which returns
# the number of elements generated, so the total comes out as the invoice count.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

open my $fh, '<', "$IN/invoices.csv" or die "cannot read invoices.csv: $!\n";
my $header = <$fh>;
my @rows;
while (my $line = <$fh>) {
    chomp $line;
    next if $line eq '';
    my ($id, $customer, $amount, $status) = split /,/, $line, -1;
    push @rows, { id => $id, customer => $customer, amount => $amount, status => $status };
}
close $fh;

my @paid = grep { $_->{status} eq 'paid' } @rows;
my $paid_count = scalar @paid;

# BUG: map in scalar context returns the count of generated elements.
my $paid_total = map { $_->{amount} } @paid;

my $largest_paid_id = '';
my $largest_amount;
for my $invoice (@paid) {
    if (!defined $largest_amount || $invoice->{amount} > $largest_amount) {
        $largest_amount = $invoice->{amount};
        $largest_paid_id = $invoice->{id};
    }
}

open my $out, '>', "$OUT/paid.csv" or die "cannot write paid.csv: $!\n";
print {$out} "id,amount\n";
for my $invoice (@paid) {
    print {$out} $invoice->{id}, ',', $invoice->{amount}, "\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"invoices\":%d,\"paid_count\":%d,\"paid_total\":%.2f,\"unpaid_count\":%d,\"largest_paid_id\":\"%s\"}\n",
    scalar(@rows), $paid_count, $paid_total, scalar(@rows) - $paid_count, $largest_paid_id;
close $sum;

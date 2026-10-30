#!/usr/bin/env perl
# 234-perl-jsonl-filter — stream JSON Lines and aggregate service metrics.
use strict;
use warnings;
use JSON::PP qw(decode_json);

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my %stats;
my $total_events = 0;
my $total_errors = 0;
my $total_duration = 0;

open my $fh, '<', "$IN/events.jsonl" or die "cannot read events.jsonl: $!\n";
while (my $line = <$fh>) {
    chomp $line;
    $line =~ s/^\s+//;
    $line =~ s/\s+$//;
    next unless length $line;

    my $obj = decode_json($line);
    my $svc = $obj->{service};
    my $dur = $obj->{duration_ms} + 0;
    my $is_err = ($obj->{level} eq 'ERROR') ? 1 : 0;

    $stats{$svc}{events}   += 1;
    $stats{$svc}{errors}   += $is_err;
    $stats{$svc}{duration} += $dur;

    $total_events++;
    $total_errors += $is_err;
    $total_duration += $dur;
}
close $fh;

# Sort: errors desc, events desc, service asc
my @sorted_svcs = sort {
    $stats{$b}{errors} <=> $stats{$a}{errors}
    or $stats{$b}{events} <=> $stats{$a}{events}
    or $a cmp $b
} keys %stats;

open my $out, '>', "$OUT/services.csv" or die "cannot write services.csv: $!\n";
print {$out} "service,events,errors,total_duration_ms,avg_duration_ms\n";
for my $svc (@sorted_svcs) {
    my $e = $stats{$svc}{events};
    my $err = $stats{$svc}{errors};
    my $tot = $stats{$svc}{duration};
    my $avg = $tot / $e;
    printf {$out} "%s,%d,%d,%d,%.1f\n", $svc, $e, $err, $tot, $avg;
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"total_events\":%d,\"total_errors\":%d,\"total_duration_ms\":%d,\"services_count\":%d}\n",
    $total_events, $total_errors, $total_duration, scalar(@sorted_svcs);
close $sum;

#!/usr/bin/env perl
# Plausible bug: assumes bytes is always digits (\d+), skipping lines where bytes is '-'
# such as 304 Not Modified and 401 Unauthorized responses.
use strict;
use warnings;

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my %ip_reqs;
my %ip_bytes;
my %status_counts = (s2xx => 0, s3xx => 0, s4xx => 0, s5xx => 0);
my $total_requests = 0;
my $total_bytes    = 0;

open my $fh, '<', "$IN/access.log" or die "cannot read access.log: $!\n";
while (my $line = <$fh>) {
    chomp $line;
    next if $line =~ /^\s*#/ || $line =~ /^\s*$/;

    # BUG: \d+ fails to match '-' for empty body responses!
    if ($line =~ /^(\S+)\s+\S+\s+\S+\s+\[[^\]]+\]\s+"[A-Z]+\s+\S+\s+HTTP\/[0-9.]+"\s+(\d{3})\s+(\d+)/) {
        my ($ip, $status, $bytes) = ($1, $2 + 0, $3 + 0);

        my $family = sprintf('s%dxx', int($status / 100));
        $status_counts{$family}++ if exists $status_counts{$family};

        $ip_reqs{$ip}  += 1;
        $ip_bytes{$ip} += $bytes;

        $total_requests++;
        $total_bytes += $bytes;
    }
}
close $fh;

my @sorted_ips = sort {
    $ip_reqs{$b} <=> $ip_reqs{$a}
    or $ip_bytes{$b} <=> $ip_bytes{$a}
    or $a cmp $b
} keys %ip_reqs;

open my $out, '>', "$OUT/clients.csv" or die "cannot write clients.csv: $!\n";
print {$out} "ip,requests,bytes\n";
for my $ip (@sorted_ips) {
    print {$out} "$ip,$ip_reqs{$ip},$ip_bytes{$ip}\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"requests\":%d,\"total_bytes\":%d,\"s2xx\":%d,\"s3xx\":%d,\"s4xx\":%d,\"s5xx\":%d}\n",
    $total_requests, $total_bytes,
    $status_counts{s2xx}, $status_counts{s3xx},
    $status_counts{s4xx}, $status_counts{s5xx};
close $sum;

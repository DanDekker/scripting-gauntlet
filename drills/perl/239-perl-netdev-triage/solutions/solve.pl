#!/usr/bin/env perl
use strict;
use warnings;
use File::Path qw(make_path);
use JSON::PP;

my $in_file = 'in/net_dev.txt';
open my $fh, '<', $in_file or die "Cannot open $in_file: $!";

my @interfaces;
my $total_traffic = 0;
my $healthy_count = 0;
my $degraded_count = 0;
my $down_count = 0;

while (my $line = <$fh>) {
    chomp $line;
    next unless $line =~ /:/;
    my ($iface, $data) = split(/:/, $line, 2);
    $iface =~ s/^\s+|\s+$//g;
    my @cols = split(' ', $data);
    next unless @cols >= 16;

    my $rx_bytes   = $cols[0];
    my $rx_packets = $cols[1];
    my $rx_errs    = $cols[2];
    my $rx_drop    = $cols[3];

    my $tx_bytes   = $cols[8];
    my $tx_packets = $cols[9];
    my $tx_errs    = $cols[10];
    my $tx_drop    = $cols[11];

    my $total_bytes   = $rx_bytes + $tx_bytes;
    my $total_packets = $rx_packets + $tx_packets;
    my $total_errors  = $rx_errs + $tx_errs;
    my $total_drops   = $rx_drop + $tx_drop;

    my $status;
    if ($total_bytes == 0) {
        $status = 'DOWN';
        $down_count++;
    } elsif ($total_errors > 0 || $total_drops > 0) {
        $status = 'DEGRADED';
        $degraded_count++;
    } else {
        $status = 'HEALTHY';
        $healthy_count++;
    }

    $total_traffic += $total_bytes;

    push @interfaces, {
        interface     => $iface,
        status        => $status,
        total_bytes   => $total_bytes,
        total_packets => $total_packets,
        total_errors  => $total_errors,
        total_drops   => $total_drops,
    };
}
close $fh;

# Sort: total_bytes descending, interface ascending
@interfaces = sort {
    $b->{total_bytes} <=> $a->{total_bytes}
    ||
    $a->{interface} cmp $b->{interface}
} @interfaces;

make_path('out');

open my $out_tsv, '>', 'out/interfaces.tsv' or die "Cannot open out/interfaces.tsv: $!";
print $out_tsv "interface\tstatus\ttotal_bytes\ttotal_packets\ttotal_errors\ttotal_drops\n";
for my $it (@interfaces) {
    print $out_tsv "$it->{interface}\t$it->{status}\t$it->{total_bytes}\t$it->{total_packets}\t$it->{total_errors}\t$it->{total_drops}\n";
}
close $out_tsv;

my $top_interface = @interfaces ? $interfaces[0]{interface} : "";

my %summary = (
    total_interfaces    => scalar(@interfaces),
    healthy_count       => $healthy_count,
    degraded_count      => $degraded_count,
    down_count          => $down_count,
    total_traffic_bytes => $total_traffic,
    top_interface       => $top_interface,
);

my $coder = JSON::PP->new->canonical(1);
open my $out_json, '>', 'out/summary.json' or die "Cannot open out/summary.json: $!";
print $out_json $coder->encode(\%summary);
close $out_json;

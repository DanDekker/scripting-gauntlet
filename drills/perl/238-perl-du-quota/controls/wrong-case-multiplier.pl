#!/usr/bin/env perl
use strict;
use warnings;
use File::Path qw(make_path);
use JSON::PP;

sub parse_bytes {
    my ($str) = @_;
    $str =~ s/^\s+|\s+$//g;
    # BUG: only matches uppercase [KMGTB], missing lowercase units like 'm' in '800m'
    if ($str =~ /^([0-9]+(?:\.[0-9]+)?)\s*([KMGTB]?)$/) {
        my ($val, $unit) = ($1, $2 // '');
        my $mult = 1;
        if ($unit eq 'K') {
            $mult = 1024;
        } elsif ($unit eq 'M') {
            $mult = 1024 * 1024;
        } elsif ($unit eq 'G') {
            $mult = 1024 * 1024 * 1024;
        } elsif ($unit eq 'T') {
            $mult = 1024 * 1024 * 1024 * 1024;
        }
        return int($val * $mult + 0.5);
    }
    # Falls back to val without multiplier if unit is lowercase
    if ($str =~ /^([0-9]+(?:\.[0-9]+)?)/) {
        return int($1 + 0.5);
    }
    die "Unrecognized size format: $str";
}

my %quotas;
open my $qfh, '<', 'in/quotas.tsv' or die "Cannot open in/quotas.tsv: $!";
while (my $line = <$qfh>) {
    chomp $line;
    next if $line =~ /^\s*#/ or $line =~ /^\s*$/;
    my ($path, $quota_str) = split(/\t/, $line, -1);
    next if $path eq 'path';
    $quotas{$path} = parse_bytes($quota_str);
}
close $qfh;

my $default_quota = $quotas{'DEFAULT'} // die "Missing DEFAULT quota";

my @alerts;
my $total_checked = 0;
my $total_overage = 0;

open my $ufh, '<', 'in/usage.txt' or die "Cannot open in/usage.txt: $!";
while (my $line = <$ufh>) {
    chomp $line;
    next if $line =~ /^\s*#/ or $line =~ /^\s*$/;
    my ($size_str, $path) = split(/\t/, $line, -1);
    next unless defined $path;
    $total_checked++;
    my $usage_bytes = parse_bytes($size_str);
    my $quota_bytes = exists $quotas{$path} ? $quotas{$path} : $default_quota;

    if ($usage_bytes > $quota_bytes) {
        my $overage = $usage_bytes - $quota_bytes;
        my $pct = sprintf("%.1f", ($usage_bytes / $quota_bytes) * 100);
        push @alerts, {
            path          => $path,
            usage_bytes   => $usage_bytes,
            quota_bytes   => $quota_bytes,
            overage_bytes => $overage,
            pct_used      => $pct,
        };
        $total_overage += $overage;
    }
}
close $ufh;

@alerts = sort {
    $b->{overage_bytes} <=> $a->{overage_bytes}
    ||
    $a->{path} cmp $b->{path}
} @alerts;

make_path('out');

open my $out_tsv, '>', 'out/alerts.tsv' or die "Cannot open out/alerts.tsv: $!";
print $out_tsv "path\tusage_bytes\tquota_bytes\toverage_bytes\tpct_used\n";
for my $a (@alerts) {
    print $out_tsv "$a->{path}\t$a->{usage_bytes}\t$a->{quota_bytes}\t$a->{overage_bytes}\t$a->{pct_used}\n";
}
close $out_tsv;

my $top_offender = @alerts ? $alerts[0]{path} : "";

my %summary = (
    total_checked       => $total_checked,
    over_quota_count    => scalar(@alerts),
    total_overage_bytes => $total_overage,
    top_offender        => $top_offender,
);

my $coder = JSON::PP->new->canonical(1);
open my $out_json, '>', 'out/summary.json' or die "Cannot open out/summary.json: $!";
print $out_json $coder->encode(\%summary);
close $out_json;

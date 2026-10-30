#!/usr/bin/env perl
use strict;
use warnings;
use File::Path qw(make_path);
use JSON::PP;

my $in_file = 'in/auth.log';
open my $fh, '<', $in_file or die "Cannot open $in_file: $!";

my %ip_failures;
my %ip_users;
my %user_counts;
my $total_failed = 0;

while (my $line = <$fh>) {
    chomp $line;
    next if $line =~ /^\s*#/ or $line =~ /^\s*$/;
    # BUG: captures "invalid" as the username instead of the actual account
    if ($line =~ /Failed password for (\S+).*?from (\S+) port (\d+)/) {
        my ($user, $ip) = ($1, $2);
        $total_failed++;
        $ip_failures{$ip}++;
        $ip_users{$ip}{$user} = 1;
        $user_counts{$user}++;
    }
}
close $fh;

make_path('out');

my @banned_ips = grep { $ip_failures{$_} >= 3 } keys %ip_failures;
@banned_ips = sort {
    $ip_failures{$b} <=> $ip_failures{$a}
    ||
    $a cmp $b
} @banned_ips;

open my $out_tsv, '>', 'out/bans.tsv' or die "Cannot open out/bans.tsv: $!";
print $out_tsv "ip\tfailures\tunique_users\tusers\n";
for my $ip (@banned_ips) {
    my @users = sort { $a cmp $b } keys %{ $ip_users{$ip} };
    my $unique_count = scalar @users;
    my $user_str = join(',', @users);
    print $out_tsv "$ip\t$ip_failures{$ip}\t$unique_count\t$user_str\n";
}
close $out_tsv;

my @all_users = sort {
    $user_counts{$b} <=> $user_counts{$a}
    ||
    $a cmp $b
} keys %user_counts;

my $top_user = @all_users ? $all_users[0] : "";

my %summary = (
    total_failed_events => $total_failed,
    unique_ips          => scalar(keys %ip_failures),
    banned_ips          => scalar(@banned_ips),
    top_target_user     => $top_user,
);

my $coder = JSON::PP->new->canonical(1);
open my $out_json, '>', 'out/summary.json' or die "Cannot open out/summary.json: $!";
print $out_json $coder->encode(\%summary);
close $out_json;

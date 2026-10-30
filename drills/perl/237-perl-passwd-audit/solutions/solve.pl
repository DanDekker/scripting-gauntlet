#!/usr/bin/env perl
use strict;
use warnings;
use File::Path qw(make_path);
use JSON::PP;

my $passwd_file = 'in/passwd';
my $group_file  = 'in/group';

my %users;
my @user_list;
my %uid_counts;
my %user_uids;
my %user_gids;

open my $pfh, '<', $passwd_file or die "Cannot open $passwd_file: $!";
while (my $line = <$pfh>) {
    chomp $line;
    next if $line =~ /^\s*#/ or $line =~ /^\s*$/;
    my @fields = split(/:/, $line, -1);
    next unless @fields == 7;
    my ($username, $pwd, $uid, $gid, $gecos, $home, $shell) = @fields;
    $users{$username} = 1;
    push @user_list, $username;
    $uid_counts{$uid}++;
    $user_uids{$username} = $uid;
    $user_gids{$username} = $gid;
}
close $pfh;

my %groups;
my @group_list;
my %group_members;

open my $gfh, '<', $group_file or die "Cannot open $group_file: $!";
while (my $line = <$gfh>) {
    chomp $line;
    next if $line =~ /^\s*#/ or $line =~ /^\s*$/;
    my @fields = split(/:/, $line, -1);
    next unless @fields == 4;
    my ($groupname, $pwd, $gid, $members_str) = @fields;
    $groups{$gid} = $groupname;
    push @group_list, $groupname;
    my @m = ($members_str ne '') ? split(/,/, $members_str) : ();
    $group_members{$groupname} = \@m;
}
close $gfh;

my @anomalies;
my $root_equiv_count = 0;
my $orphan_gid_count = 0;
my $dangling_count = 0;

for my $user (sort keys %users) {
    my $uid = $user_uids{$user};
    my $gid = $user_gids{$user};

    if ($uid == 0 && $user ne 'root') {
        push @anomalies, {
            category => 'ROOT_EQUIV',
            entity   => "user:$user",
            detail   => 'uid 0 assigned to non-root user',
        };
        $root_equiv_count++;
    }

    if ($uid_counts{$uid} > 1) {
        push @anomalies, {
            category => 'DUPLICATE_UID',
            entity   => "user:$user",
            detail   => "uid $uid is duplicated",
        };
    }

    if (!exists $groups{$gid}) {
        push @anomalies, {
            category => 'ORPHAN_GID',
            entity   => "user:$user",
            detail   => "gid $gid not found in group database",
        };
        $orphan_gid_count++;
    }
}

for my $group (sort keys %group_members) {
    for my $member (@{ $group_members{$group} }) {
        if (!exists $users{$member}) {
            push @anomalies, {
                category => 'DANGLING_MEMBER',
                entity   => "group:$group",
                detail   => "member $member not found in passwd database",
            };
            $dangling_count++;
        }
    }
}

@anomalies = sort {
    $a->{category} cmp $b->{category}
    ||
    $a->{entity} cmp $b->{entity}
    ||
    $a->{detail} cmp $b->{detail}
} @anomalies;

make_path('out');

open my $out_tsv, '>', 'out/anomalies.tsv' or die "Cannot open out/anomalies.tsv: $!";
print $out_tsv "category\tentity\tdetail\n";
for my $a (@anomalies) {
    print $out_tsv "$a->{category}\t$a->{entity}\t$a->{detail}\n";
}
close $out_tsv;

my %summary = (
    total_users      => scalar(keys %users),
    total_groups     => scalar(@group_list),
    total_anomalies  => scalar(@anomalies),
    root_equiv_users => $root_equiv_count,
    orphan_gid_users => $orphan_gid_count,
    dangling_members => $dangling_count,
);

my $coder = JSON::PP->new->canonical(1);
open my $out_json, '>', 'out/summary.json' or die "Cannot open out/summary.json: $!";
print $out_json $coder->encode(\%summary);
close $out_json;

#!/usr/bin/env perl
# 229-perl-log-retention — audit log files against retention policy.
use strict;
use warnings;
use Time::Local qw(timegm);

my $IN  = $ENV{IN}  or die "IN not set\n";
my $OUT = $ENV{OUT} or die "OUT not set\n";

my %policy;
open my $pfh, '<', "$IN/policy.ini" or die "cannot read policy.ini: $!\n";
while (my $line = <$pfh>) {
    chomp $line;
    $line =~ s/\s*#.*//;
    next if $line =~ /^\s*$/;
    if ($line =~ /^\s*(\w+)\s*=\s*(\S+)\s*$/) {
        $policy{$1} = $2;
    }
}
close $pfh;

my ($ty, $tm, $td) = split /-/, $policy{today};
# Time::Local::timegm takes month as 0..11
my $today_epoch = timegm(0, 0, 0, $td, $tm - 1, $ty);
my $compress_days = $policy{compress_days} + 0;
my $delete_days   = $policy{delete_days} + 0;

my $log_dir = "$IN/logs";
opendir my $dh, $log_dir or die "cannot open logs dir: $!\n";
my @files = grep { $_ ne '.' && $_ ne '..' && -f "$log_dir/$_" } readdir $dh;
closedir $dh;

@files = sort @files;

my @rows;
my %counts = (keep => 0, compress => 0, delete => 0, ignore => 0);

for my $file (@files) {
    my ($age_days, $action);

    if ($file =~ /\.tmp$/) {
        $age_days = '';
        $action   = 'delete';
    }
    elsif ($file =~ /^[a-z]+-(\d{4})-(\d{2})-(\d{2})\.log(?:\.gz)?$/) {
        my ($ly, $lm, $ld) = ($1, $2, $3);
        my $file_epoch = timegm(0, 0, 0, $ld, $lm - 1, $ly);
        my $diff_days = int(($today_epoch - $file_epoch) / 86400);
        $age_days = $diff_days;

        if ($diff_days >= $delete_days) {
            $action = 'delete';
        }
        elsif ($diff_days >= $compress_days && $file !~ /\.gz$/) {
            $action = 'compress';
        }
        else {
            $action = 'keep';
        }
    }
    else {
        $age_days = '';
        $action   = 'ignore';
    }

    $counts{$action}++;
    push @rows, [ $file, $age_days, $action ];
}

open my $out, '>', "$OUT/retention.csv" or die "cannot write retention.csv: $!\n";
print {$out} "file,age_days,action\n";
for my $r (@rows) {
    print {$out} join(',', @$r), "\n";
}
close $out;

open my $sum, '>', "$OUT/summary.json" or die "cannot write summary.json: $!\n";
printf {$sum} "{\"files\":%d,\"keep\":%d,\"compress\":%d,\"delete\":%d,\"ignore\":%d}\n",
    scalar(@rows), $counts{keep}, $counts{compress}, $counts{delete}, $counts{ignore};
close $sum;

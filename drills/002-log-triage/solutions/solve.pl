#!/usr/bin/env perl
use strict;
use warnings;
use JSON::PP qw(encode_json);
use File::Path qw(make_path);

my $input = $ENV{IN} // die "IN is missing\n";
my $output = $ENV{OUT} // die "OUT is missing\n";
make_path($output);

open my $log, '<', "$input/access.log" or die "access.log: $!\n";
my (%statuses, %paths);
my ($valid, $skipped) = (0, 0);
while (my $line = <$log>) {
    if ($line !~ /"\S+ (\S+) HTTP\/[\d.]+\s*"?\s*(\d{3})\b/) {
        $skipped++;
        next;
    }
    my ($path, $status) = ($1, $2);
    $path =~ s/\?.*//;
    $statuses{$status}++;
    $paths{$path}++;
    $valid++;
}
close $log;

open my $status_file, '>', "$output/status.csv" or die "status.csv: $!\n";
print {$status_file} "status,count\n";
for my $status (sort { $statuses{$b} <=> $statuses{$a} || $a <=> $b } keys %statuses) {
    print {$status_file} "$status,$statuses{$status}\n";
}
close $status_file;

open my $paths_file, '>', "$output/top_paths.csv" or die "top_paths.csv: $!\n";
print {$paths_file} "path,hits\n";
my @top = sort { $paths{$b} <=> $paths{$a} || $a cmp $b } keys %paths;
for my $path (@top[0 .. ($#top < 4 ? $#top : 4)]) {
    print {$paths_file} "$path,$paths{$path}\n";
}
close $paths_file;

open my $summary, '>', "$output/summary.json" or die "summary.json: $!\n";
print {$summary} encode_json({ valid => $valid, skipped => $skipped }), "\n";
close $summary;

#!/usr/bin/env ruby
# 183-ruby-encoding-scrub — label, validate, scrub; chars and bytes are different numbers.
require "json"

in_dir = ENV["IN"] or abort "IN not set"
out_dir = ENV["OUT"] or abort "OUT not set"

data = File.binread(File.join(in_dir, "raw.txt"))
lines = data.split("\n")
invalid = 0

File.open(File.join(out_dir, "lines.csv"), "w") do |fh|
  fh.puts "line,valid,chars,bytes,text"
  lines.each_with_index do |raw, index|
    text = raw.dup.force_encoding("UTF-8")
    valid = text.valid_encoding?
    invalid += 1 unless valid
    repaired = text.scrub("?")
    fh.puts "#{index + 1},#{valid},#{repaired.length},#{raw.bytesize},#{repaired}"
  end
end

File.write(File.join(out_dir, "summary.json"),
           JSON.generate({ "lines" => lines.length, "invalid" => invalid }) + "\n")

#!/usr/bin/env ruby
# Plausible bug: merges with `||`, so an explicit false falls back to the base value and a
# null override is treated as "no opinion" instead of a tombstone.
require "json"

in_dir = ENV["IN"] or abort "IN not set"
out_dir = ENV["OUT"] or abort "OUT not set"

base = JSON.parse(File.read(File.join(in_dir, "base.json")))
override = JSON.parse(File.read(File.join(in_dir, "override.json")))

merged = {}
base.each { |key, value| merged[key] = value }
override.each { |key, value| merged[key] = value || merged[key] }

File.open(File.join(out_dir, "merged.csv"), "w") do |fh|
  fh.puts "key,type,value"
  merged.keys.sort.each do |key|
    value = merged[key]
    type = case value
           when true, false then "bool"
           when Integer then "int"
           when Float then "float"
           else "string"
           end
    text = value == true ? "true" : value == false ? "false" : value.to_s
    fh.puts "#{key},#{type},#{text}"
  end
end

File.write(File.join(out_dir, "summary.json"),
           JSON.generate({ "keys" => merged.size, "from_override" => 0, "removed" => 0 }) + "\n")

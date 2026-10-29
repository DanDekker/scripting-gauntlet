#!/usr/bin/env ruby
# 168-ruby-truthiness — key? decides presence; nil means tombstone, false is a value.
require "json"

in_dir = ENV["IN"] or abort "IN not set"
out_dir = ENV["OUT"] or abort "OUT not set"

base = JSON.parse(File.read(File.join(in_dir, "base.json")))
override = JSON.parse(File.read(File.join(in_dir, "override.json")))

merged = {}
base.each { |key, value| merged[key] = value }

removed = 0
from_override = 0
override.each do |key, value|
  if value.nil?
    removed += 1
    merged.delete(key)
  else
    merged[key] = value
    from_override += 1
  end
end

File.open(File.join(out_dir, "merged.csv"), "w") do |fh|
  fh.puts "key,type,value"
  merged.keys.sort.each do |key|
    value = merged[key]
    type =
      case value
      when true, false then "bool"
      when Integer then "int"
      when Float then "float"
      else "string"
      end
    text = value == true ? "true" : value == false ? "false" : value.to_s
    fh.puts "#{key},#{type},#{text}"
  end
end

summary = { "keys" => merged.size, "from_override" => from_override, "removed" => removed }
File.write(File.join(out_dir, "summary.json"), JSON.generate(summary) + "\n")

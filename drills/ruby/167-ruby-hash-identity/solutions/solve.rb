#!/usr/bin/env ruby
# 167-ruby-hash-identity — 1 and 1.0 are different Hash keys; normalize before counting.
require "json"

in_dir = ENV["IN"] or abort "IN not set"
out_dir = ENV["OUT"] or abort "OUT not set"

counts = Hash.new(0)
events = 0
invalid = 0

File.foreach(File.join(in_dir, "events.jsonl")) do |line|
  text = line.strip
  next if text.empty?

  record = JSON.parse(text)
  unless record.key?("id") && !record["id"].nil?
    invalid += 1
    next
  end

  raw = record["id"]
  if raw.is_a?(String)
    key = ["string", raw]
  else
    # numeric: 1 and 1.0 are the same entity, and print as an integer
    number = raw.is_a?(Float) && raw == raw.floor ? raw.to_i : raw
    key = ["numeric", number.to_s]
  end
  counts[key] += 1
  events += 1
end

rows = counts.keys.sort_by { |kind, id_text| [id_text, kind] }
File.open(File.join(out_dir, "tally.csv"), "w") do |fh|
  fh.puts "id,kind,events"
  rows.each { |kind, id_text| fh.puts "#{id_text},#{kind},#{counts[[kind, id_text]]}" }
end

summary = { "ids" => rows.length, "events" => events, "invalid" => invalid }
File.write(File.join(out_dir, "summary.json"), JSON.generate(summary) + "\n")

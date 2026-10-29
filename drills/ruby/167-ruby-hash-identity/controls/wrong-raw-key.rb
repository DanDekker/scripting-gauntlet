#!/usr/bin/env ruby
# Plausible bug: uses the raw value as the hash key, so 1 and 1.0 land in separate rows
# even though they are the same entity.
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
  kind = raw.is_a?(String) ? "string" : "numeric"
  counts[[kind, raw.to_s]] += 1
  events += 1
end

rows = counts.keys.sort_by { |kind, id_text| [id_text, kind] }
File.open(File.join(out_dir, "tally.csv"), "w") do |fh|
  fh.puts "id,kind,events"
  rows.each { |kind, id_text| fh.puts "#{id_text},#{kind},#{counts[[kind, id_text]]}" }
end

File.write(File.join(out_dir, "summary.json"),
           JSON.generate({ "ids" => rows.length, "events" => events, "invalid" => invalid }) + "\n")

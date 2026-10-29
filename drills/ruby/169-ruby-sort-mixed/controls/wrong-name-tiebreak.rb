#!/usr/bin/env ruby
# Plausible bug: breaks ties by name, which reorders the three records that all score 10.
# because sort_by is not guaranteed stable.
require "json"

NUMERIC = /\A-?[0-9]+(\.[0-9]+)?\z/

in_dir = ENV["IN"] or abort "IN not set"
out_dir = ENV["OUT"] or abort "OUT not set"

records = []
lines = 0
invalid = 0

File.foreach(File.join(in_dir, "records.jsonl")) do |line|
  text = line.strip
  next if text.empty?
  lines += 1

  record = JSON.parse(text)
  name = record["name"]
  score = record["score"]

  if score.nil?
    records << [name, nil, records.length]
  elsif score.is_a?(String) && score !~ NUMERIC
    invalid += 1
  else
    records << [name, score.to_f, records.length]
  end
end

ranked = records.sort_by do |_name, score, _index|
  [score.nil? ? 1 : 0, score.nil? ? 0 : -score, _name]
end

File.open(File.join(out_dir, "ranked.csv"), "w") do |fh|
  fh.puts "rank,name,score"
  ranked.each_with_index do |(name, score, _index), position|
    text = score.nil? ? "" : (score == score.to_i ? score.to_i.to_s : score.to_s)
    fh.puts "#{position + 1},#{name},#{text}"
  end
end

missing = records.count { |_name, score, _index| score.nil? }
summary = { "lines" => lines, "ranked" => ranked.length, "invalid" => invalid, "missing" => missing }
File.write(File.join(out_dir, "summary.json"), JSON.generate(summary) + "\n")

#!/usr/bin/env ruby
# 189-ruby-lazy-pipeline — lazy streaming evaluation with early termination
require "json"

in_dir = ENV["IN"] or abort "IN not set"
out_dir = ENV["OUT"] or abort "OUT not set"

inspected = 0
target = 5
matches = []

File.open(File.join(in_dir, "stream.log"), "r") do |f|
  matches = f.each_line.lazy
    .map(&:strip)
    .reject { |line| line.empty? || line.start_with?("#") }
    .map { |line| inspected += 1; line }
    .select { |line| line.include?("[payment]") && (line.include?("WARN") || line.include?("ERROR")) }
    .map do |line|
      parts = line.split(/\s+/, 4)
      ts = parts[0]
      level = parts[1]
      code = line[/code=(\d+)/, 1]
      msg = line[/code=\d+\s+(.*)$/, 1] || ""
      [ts, level, code.to_i, msg]
    end
    .take(target)
    .force
end

File.open(File.join(out_dir, "matches.csv"), "w") do |fh|
  fh.puts "timestamp,level,code,message"
  matches.each do |m|
    fh.puts "#{m[0]},#{m[1]},#{m[2]},#{m[3]}"
  end
end

File.write(
  File.join(out_dir, "summary.json"),
  JSON.generate({ "inspected" => inspected, "matched" => matches.length, "target" => target }) + "\n"
)

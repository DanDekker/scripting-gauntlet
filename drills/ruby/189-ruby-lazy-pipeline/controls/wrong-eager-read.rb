#!/usr/bin/env ruby
# Plausible bug: eager read consumes all lines in file before taking first 5
require "json"

in_dir = ENV["IN"] or abort "IN not set"
out_dir = ENV["OUT"] or abort "OUT not set"

lines = File.readlines(File.join(in_dir, "stream.log"))
  .map(&:strip)
  .reject { |l| l.empty? || l.start_with?("#") }

inspected = lines.length # 10 instead of 8!
target = 5

matches = lines
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

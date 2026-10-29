#!/usr/bin/env ruby
# Plausible bug: formats the double directly instead of rounding the decimal value first, so
# 1.005 comes out as 1.00.
require "json"

NUMBER = /\A-?[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?\z/

in_dir = ENV["IN"] or abort "IN not set"
out_dir = ENV["OUT"] or abort "OUT not set"

rows = []
counts = Hash.new(0)

File.foreach(File.join(in_dir, "amounts.txt")) do |line|
  token = line.chomp.strip
  next if token.empty?

  if token =~ NUMBER
    if token.include?(".") || token =~ /[eE]/
      kind = "float"
      text = format("%.2f", Float(token))
    else
      kind = "int"
      text = Integer(token, 10).to_s
    end
  else
    kind = "invalid"
    text = ""
  end

  counts[kind] += 1
  rows << [token, kind, text]
end

File.open(File.join(out_dir, "formatted.csv"), "w") do |fh|
  fh.puts "raw,kind,formatted"
  rows.each { |row| fh.puts row.join(",") }
end

summary = { "lines" => rows.length, "int" => counts["int"], "float" => counts["float"], "invalid" => counts["invalid"] }
File.write(File.join(out_dir, "summary.json"), JSON.generate(summary) + "\n")
